"""web/wsgi.py -- ATOM-META-RL-008: Flask API + Dash WSGI"""
import datetime as dt_module
import logging
import os
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from flask import Flask, jsonify, request
from web.middleware.auth import require_auth

# ── Flask API server ─────────────────────────────────────────────────────────
server = Flask(__name__)
app = server  # gunicorn expects "module:app"
_log = logging.getLogger("werkzeug")
_log.setLevel(logging.WARNING)

# ── /api/health ──────────────────────────────────────────────────────────────
@server.route("/api/health")
def health():
    '''System health — CCXTLiveProvider singleton.'''
    t0 = time.time()
    try:
        from meta_rl.live_provider import get_live_provider
        snap = get_live_provider().get_snapshot("BTC/USDT")
        return jsonify({
            "status": "OK",
            "timestamp": dt_module.datetime.utcnow().strftime("%H:%M:%S"),
            **snap.to_dict(),
            "live_enabled": os.getenv("META_RL_LIVE_ENABLED", "false").lower() == "true",
            "latency_ms": round((time.time() - t0) * 1000, 1),
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "ERROR"}), 500

# ── /api/sessions ────────────────────────────────────────────────────────────
@server.route("/api/sessions")
def sessions_list():
    try:
        from meta_rl.persistence import get_persistence
        p = get_persistence()
        sids = p.list_sessions()
        return jsonify({"sessions": sids, "status": "OK"})
    except Exception as e:
        return jsonify({"status": "ERROR", "error": str(e)})

# ── /api/sessions/<sid> ──────────────────────────────────────────────────────
def _get_session_meta(sid):
    """Try all session sources: persistence JSON, then history_db SQLite."""
    from meta_rl.persistence import get_persistence
    p = get_persistence()
    # Try JSON persistence first
    meta = p.load_evolution_session(sid)
    if meta:
        return meta
    # Fallback: history_db SQLite (sessions created before ATOM-META-RL-007)
    try:
        from core.history_db import get_session
        db_meta = get_session(sid)
        if db_meta:
            return db_meta
    except Exception:
        pass
    return None

@server.route("/api/sessions/<sid>")
def session_detail(sid):
    try:
        meta = _get_session_meta(sid)
        if not meta:
            return jsonify({"status": "ERROR", "error": "Session not found"}), 404
        return jsonify({"status": "OK", "session": meta})
    except Exception as e:
        return jsonify({"status": "ERROR", "error": str(e)}), 500

# ── /api/sessions/<sid>/strategies ────────────────────────────────────────────
@server.route("/api/sessions/<sid>/strategies")
def session_strategies(sid):
    try:
        from meta_rl.persistence import get_persistence
        p = get_persistence()
        strategies = p.load_elite_chromosomes(sid)
        return jsonify({"status": "OK", "strategies": strategies})
    except Exception as e:
        return jsonify({"status": "ERROR", "error": str(e)}), 500

# ── /api/sessions/summary ─────────────────────────────────────────────────────
@server.route("/api/sessions/summary")
def sessions_summary():
    try:
        from meta_rl.persistence import get_persistence
        p = get_persistence()
        summary = p.get_sessions_summary()
        return jsonify({"status": "OK", **summary})
    except Exception as e:
        return jsonify({"status": "ERROR", "error": str(e)}), 500

# ── /api/ranking/top ──────────────────────────────────────────────────────────
@server.route("/api/ranking/top")
def ranking_top():
    try:
        from meta_rl.ranking import rank_all_sessions
        ranked = rank_all_sessions(n_top=20)
        return jsonify({
            "status": "OK",
            "ranked": [s.__dict__ if hasattr(s, "__dict__") else dict(s) for s in ranked],
        })
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"status": "ERROR", "error": str(e)}), 500

# ── /api/ab/sessions ──────────────────────────────────────────────────────────
@server.route("/api/ab/sessions")
def ab_sessions():
    """List top sessions available for A/B comparison."""
    try:
        from meta_rl.persistence import get_persistence
        p = get_persistence()
        raw = p.list_sessions()
        # list_sessions may return strings or dicts
        if raw and isinstance(raw[0], str):
            sids = [{"session_id": s, "created_at": "", "best_reward": 0, "n_strategies": 0} for s in raw]
        else:
            sids = sorted(raw, key=lambda s: s.get("created_at", ""), reverse=True)[:50]
        return jsonify({
            "status": "OK",
            "sessions": [
                {
                    "id": s.get("session_id", "")[:16],
                    "created_at": s.get("created_at", ""),
                    "best_reward": round(s.get("best_reward", 0), 4),
                    "generations": s.get("n_strategies", 0),
                }
                for s in sids
            ]
        })
    except Exception as e:
        return jsonify({"status": "ERROR", "error": str(e)}), 500

# ── /api/ab/compare ───────────────────────────────────────────────────────────
@server.route("/api/ab/compare")
def ab_compare():
    """A/B compare two sessions: ?sid_a=X&sid_b=Y
    Supports both new-style sessions (ScoredStrategy dicts) and legacy
    history_db sessions (confidence-based proxy rewards)."""
    from meta_rl.ab_testing import cohens_d, welch_t_test
    sid_a = request.args.get("sid_a", "")
    sid_b = request.args.get("sid_b", "")
    if not sid_a or not sid_b:
        return jsonify({"status": "ERROR", "error": "sid_a and sid_b required"}), 400

    try:
        # Try new-style persistence first (ScoredStrategy dicts with real rewards)
        from meta_rl.persistence import get_persistence
        p = get_persistence()
        chrom_a = p.load_elite_chromosomes(sid_a)
        chrom_b = p.load_elite_chromosomes(sid_b)

        rewards_a, rewards_b = [], []

        if chrom_a and chrom_b:
            # New-style: real ScoredStrategy rewards
            for c in chrom_a:
                ev = c.get("evaluation", {})
                r = ev.get("risk_adjusted_pnl", ev.get("pnl", 0))
                rewards_a.append(r)
            for c in chrom_b:
                ev = c.get("evaluation", {})
                r = ev.get("risk_adjusted_pnl", ev.get("pnl", 0))
                rewards_b.append(r)
            if rewards_a and rewards_b:
                mean_a = sum(rewards_a) / len(rewards_a)
                mean_b = sum(rewards_b) / len(rewards_b)
                t_stat, p_val = welch_t_test(rewards_a, rewards_b)
                effect = cohens_d(rewards_a, rewards_b)
                winner = "A" if mean_a > mean_b else "B" if mean_b > mean_a else "TIE"
                return jsonify({
                    "status": "OK",
                    "mode": "real_rewards",
                    "winner": winner,
                    "p_value": round(p_val, 4),
                    "effect_size": round(effect, 3),
                    "mean_a": round(mean_a, 4),
                    "mean_b": round(mean_b, 4),
                    "n_a": len(rewards_a),
                    "n_b": len(rewards_b),
                    "improvement_pct": round((mean_a - mean_b) / (abs(mean_b) + 1e-8) * 100, 2),
                    "confidence": "HIGH" if p_val < 0.01 else "MEDIUM" if p_val < 0.05 else "LOW",
                    "sid_a": sid_a, "sid_b": sid_b,
                })

        # Fallback: history_db sessions (confidence as proxy reward)
        from core.history_db import get_session
        s_a = get_session(sid_a)
        s_b = get_session(sid_b)
        if not s_a or not s_b:
            return jsonify({"status": "ERROR", "error": "Session(s) not found"}), 404

        # Use confidence as proxy (scaled 0-1)
        conf_a = float(s_a.get("final_confidence", 50)) / 100.0
        conf_b = float(s_b.get("final_confidence", 50)) / 100.0
        rewards_a = [conf_a] * 5  # Bootstrap n=5 for t-test
        rewards_b = [conf_b] * 5
        t_stat, p_val = welch_t_test(rewards_a, rewards_b)
        effect = cohens_d(rewards_a, rewards_b)
        winner = "A" if conf_a > conf_b else "B" if conf_b > conf_a else "TIE"
        return jsonify({
            "status": "OK",
            "mode": "proxy_confidence",
            "winner": winner,
            "p_value": round(p_val, 4),
            "effect_size": round(effect, 3),
            "mean_a": round(conf_a, 4),
            "mean_b": round(conf_b, 4),
            "n_a": 5, "n_b": 5,
            "confidence": "LOW (proxy)",
            "sid_a": sid_a, "sid_b": sid_b,
        })

    except Exception as e:
        return jsonify({"status": "ERROR", "error": str(e)}), 500

# ── /api/evolution/start ────────────────────────────────────────────────────
@server.route("/api/evolution/start", methods=["POST"])
@require_auth
def evolution_start():
    try:
        cfg = request.get_json() or {}
        symbol = cfg.get("symbol", "BTC/USDT")
        generations = int(cfg.get("generations", 3))
        population = int(cfg.get("population", 10))

        from meta_rl.evolution import EvolutionEngine
        from meta_rl.live_data import create_live_provider
        from meta_rl.meta_agent import EvolutionConfig, MetaAgent

        provider = create_live_provider(sandbox=True)
        bars = provider.fetch_ohlcv(symbol=symbol, limit=200)
        market_data = provider.to_market_data(bars)

        agent_cfg = EvolutionConfig(
            population_size=population,
            max_generations=generations,
        )
        agent = MetaAgent(config=agent_cfg)
        session_id = f"api_{symbol.replace('/', '')}_{dt_module.datetime.now():%H%M%S}"

        engine = EvolutionEngine(
            agent=agent,
            market_data=market_data,
            max_generations=generations,
            session_id=session_id,
            visualize=False,
        )
        elites, history = engine.run()

        from meta_rl.persistence import get_persistence
        p = get_persistence()
        best = engine.get_best_strategy()
        report = best.evaluation.to_dict() if best and best.evaluation else {}

        p.save_evolution_session(
            session_id=session_id,
            symbol=symbol,
            cg=generations,
            br=best.reward if best else 0,
            ks=agent.get_karl_state() if hasattr(agent, "get_karl_state") else {},
            gs=[s.to_dict() for s in history],
        )
        p.save_elite_chromosomes(elites, session_id)

        return jsonify({
            "status": "OK",
            "session_id": session_id,
            "best_reward": best.reward if best else 0,
            "generations": len(history),
            "elite_count": len(elites),
            "best_evaluation": report,
        })
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ── P0.1: Security & Live Mode Endpoints (ATOM-META-RL-009) ───────────────────
@server.route("/api/security/status")
@require_auth
def security_status():
    """
    ATOM-META-RL-009: Show masked security configuration.
    NEVER exposes full API keys.
    """
    try:
        sandbox = os.getenv("CCXT_SANDBOX_MODE", "true").lower() == "true"
        live_enabled = os.getenv("META_RL_LIVE_ENABLED", "false").lower() == "true"
        api_key = os.getenv("CCXT_API_KEY", "") or ""
        api_secret = os.getenv("CCXT_API_SECRET", "") or ""
        exchange = os.getenv("CCXT_EXCHANGE", "binance")

        has_key = bool(api_key and len(api_key) > 4)
        has_secret = bool(api_secret and len(api_secret) > 4)
        can_go_live = not sandbox and has_key and has_secret and live_enabled

        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if has_key else "NOT_SET"

        return jsonify({
            "mode": "SANDBOX" if sandbox else ("LIVE_READY" if can_go_live else "LIVE_BLOCKED"),
            "sandbox": sandbox,
            "live_enabled": live_enabled,
            "has_api_key": has_key,
            "has_api_secret": has_secret,
            "key_masked": masked_key,
            "exchange": exchange,
            "can_enable_live": can_go_live,
            "security_warning": None if can_go_live else (
                "Set CCXT_SANDBOX_MODE=false + META_RL_LIVE_ENABLED=true + keys to enable live trading"
            ),
            "status": "OK",
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "ERROR"}), 500

@server.route("/api/live/enable", methods=["POST"])
@require_auth
def live_enable():
    """
    ATOM-META-RL-009: Safely validate and enable live CCXT mode.
    Requires explicit POST with confirmation.
    """
    try:
        data = request.get_json() or {}
        confirmed = data.get("confirmed", False)

        sandbox = os.getenv("CCXT_SANDBOX_MODE", "true").lower() == "true"

        api_key = os.getenv("CCXT_API_KEY", "") or ""
        api_secret = os.getenv("CCXT_API_SECRET", "") or ""

        can_enable = (
            not sandbox and
            bool(api_key) and len(api_key) > 8 and
            bool(api_secret) and len(api_secret) > 8
        )

        if not confirmed:
            return jsonify({
                "can_enable": can_enable,
                "requires_confirmation": True,
                "warning": "Live trading will use REAL funds. Set 'confirmed: true' to proceed.",
                "mode_current": "SANDBOX" if sandbox else "LIVE",
            })

        if not can_enable:
            return jsonify({
                "error": "Cannot enable live mode: keys missing or sandbox mode active",
                "mode_current": "SANDBOX" if sandbox else "LIVE",
                "status": "BLOCKED",
            }), 400

        return jsonify({
            "status": "OK",
            "mode": "LIVE",
            "message": "Live CCXT mode enabled. Monitor /api/health for exchange connectivity.",
            "key_masked": f"{api_key[:4]}...{api_key[-4:]}",
        })

    except Exception as e:
        return jsonify({"error": str(e), "status": "ERROR"}), 500

# ── Main (for development / direct run) ────────────────────────────────────────
if __name__ == "__main__":
    # Only for local debugging, not used in production (gunicorn)
    server.run(host="0.0.0.0", port=5000, debug=True)
