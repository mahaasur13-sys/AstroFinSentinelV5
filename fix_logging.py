import re

filepath = "orchestration/sentinel_v5.py"
with open(filepath, "r") as f:
    content = f.read()

# Правила замены f-строк на structlog key=value
replacements = [
    # run_technical_flow
    (r'logger\.error\(f"\[TechFlow\] Agent \{name\} failed: \{r\}"\)',
     r'logger.error("agent.technical_flow_failed", agent=name, error=str(r))'),
    # run_macro_flow
    (r'logger\.error\(f"\[MacroFlow\] Agent \{name\} failed: \{r\}"\)',
     r'logger.error("agent.macro_flow_failed", agent=name, error=str(r))'),
    # _fetch_price debug
    (r'logger\.debug\(f"\[Price\] \{symbol\} = \{price\}"\)',
     r'logger.debug("price.fetched", symbol=symbol, price=price)'),
    (r'logger\.warning\(f"\[Price\] Invalid price for \{symbol\}: \{price\}"\)',
     r'logger.warning("price.invalid", symbol=symbol, price=price)'),
    (r'logger\.warning\(f"\[Price\] Attempt \{attempt\+1\}/\{max_retries\} connection error: \{e\}"\)',
     r'logger.warning("price.fetch_error", attempt=attempt+1, max_retries=max_retries, error_type="connection", error=str(e))'),
    (r'logger\.warning\(f"\[Price\] Attempt \{attempt\+1\}/\{max_retries\} timeout: \{e\}"\)',
     r'logger.warning("price.fetch_error", attempt=attempt+1, max_retries=max_retries, error_type="timeout", error=str(e))'),
    (r'logger\.warning\(f"\[Price\] Attempt \{attempt\+1\}/\{max_retries\} HTTP error: \{e\}"\)',
     r'logger.warning("price.fetch_error", attempt=attempt+1, max_retries=max_retries, error_type="http", error=str(e))'),
    (r'logger\.warning\(f"\[Price\] Attempt \{attempt\+1\}/\{max_retries\} unexpected: \{e\}"\)',
     r'logger.warning("price.fetch_error", attempt=attempt+1, max_retries=max_retries, error_type="unexpected", error=str(e))'),
    (r'logger\.error\(f"\[Price\] All \{max_retries\} attempts failed for \{symbol\}, using fallback \{fallback_price\}"\)',
     r'logger.error("price.all_attempts_failed", symbol=symbol, max_retries=max_retries, fallback_price=fallback_price)'),
    # router
    (r'logger\.info\(f"\[Router\] Query type: \{route_output\.query_type\.value\}"\)',
     r'logger.info("router.query_type", query_type=route_output.query_type.value)'),
    (r'logger\.info\(f"\[Router\] Symbols: \{route_output\.symbols\}"\)',
     r'logger.info("router.symbols", symbols=route_output.symbols)'),
    # Thompson
    (r'logger\.info\(f"\[Thompson\] technical: \{technical_selected\}"\)',
     r'logger.info("thompson.technical_selection", agents=technical_selected)'),
    (r'logger\.info\(f"\[Thompson\] astro:     \{astro_selected\}"\)',
     r'logger.info("thompson.astro_selection", agents=astro_selected)'),
    # Synthesis
    (r'logger\.error\(f"\[SynthesisAgent\] Skipped — agent unavailable: \{e\}"\)',
     r'logger.error("synthesis.skipped", error=str(e))'),
    # run_sentinel_v5 summary
    (r'logger\.info\(f"\[Sentinel\] Session \{session_id\} completed: \{len\(state\[.all_signals.\]\)\} signals"\)',
     r'logger.info("sentinel.session_completed", session_id=session_id, signal_count=len(state["all_signals"]))'),
    # KARL DB messages (2 f-строки)
    (r'logger\.info\(f"\[DB\] PostgreSQL tables initialized"\)',
     r'logger.info("db.postgresql_tables_initialized")'),
    (r'logger\.info\(f"\[DB\] PostgreSQL connected"\)',
     r'logger.info("db.postgresql_connected")'),
    (r'logger\.info\(f"\[DB\] PostgreSQL not available, using SQLite"\)',
     r'logger.info("db.postgresql_unavailable_using_sqlite")'),
    (r'logger\.warning\(f"\[DB\] Init failed: \{e\}, using SQLite"\)',
     r'logger.warning("db.init_failed", error=str(e))'),
    (r'logger\.info\(f"\[DB\] PostgreSQL not configured, using SQLite"\)',
     r'logger.info("db.postgresql_not_configured_using_sqlite")'),
    # KARL router (2 f-строки)
    (r'logger\.info\(f"\[Router\] Query type: \{route_output\.query_type\.value\}"\)',
     r'logger.info("router.query_type", query_type=route_output.query_type.value)'),
    (r'logger\.info\(f"\[Router\] Symbols: \{route_output\.symbols\}"\)',
     r'logger.info("router.symbols", symbols=route_output.symbols)'),
    # KARL Thompson (2 f-строки) — уже есть выше, но повторим для KARL
    (r'logger\.info\(f"\[Thompson\] technical: \{technical_selected\}"\)',
     r'logger.info("thompson.technical_selection", agents=technical_selected)'),
    (r'logger\.info\(f"\[Thompson\] astro:     \{astro_selected\}"\)',
     r'logger.info("thompson.astro_selection", agents=astro_selected)'),
    # KARL OAP
    (r'logger\.warning\(f"\[OAP\] disabled due to error: \{e\}"\)',
     r'logger.warning("oap.disabled", error=str(e))'),
    # KARL synthesis fallback
    (r'logger\.error\(f"\[KARLSynthesisAgent\] Fell back to base synthesis: \{e\}"\)',
     r'logger.error("karl_synthesis.fallback", error=str(e))'),
    # KARL summary
    (r'logger\.info\(f"\[KARL\] Session \{session_id\} completed: \{len\(state\[.all_signals.\]\)\} signals"\)',
     r'logger.info("karl.session_completed", session_id=session_id, signal_count=len(state["all_signals"]))'),
]

for pattern, repl in replacements:
    content = re.sub(pattern, repl, content)

with open(filepath, "w") as f:
    f.write(content)

print("✅ sentinel_v5.py updated with structlog key=value patterns")
