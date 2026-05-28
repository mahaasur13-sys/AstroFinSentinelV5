import re

filepath = "orchestration/sentinel_v5_mas.py"
with open(filepath, "r") as f:
    content = f.read()

# Добавляем импорт логгера, если ещё не добавлен
if "import logging" not in content:
    content = "import logging\nlogger = logging.getLogger(__name__)\n" + content

# Правила замены print на structlog
replacements = [
    (r'print\("[MASFactory] Query:", user_query\)',
     r'logger.info("masfactory.query", query=user_query)'),
    (r'print\("[Router] Query type:", route_output\.query_type\.value\)',
     r'logger.info("router.query_type", query_type=route_output.query_type.value)'),
    (r'print\(\)',
     r'pass  # removed empty print'),
    (r'print\("[MASFactory] Building topology..."\)',
     r'logger.info("masfactory.building_topology")'),
    (r'print\("[MASFactory] Topology:", topology\.hash\[:8\]\)',
     r'logger.info("masfactory.topology_hash", hash=topology.hash[:8])'),
    (r'print\("[MASFactory] Roles:", \[r\.name for r in topology\.roles\]\)',
     r'logger.info("masfactory.roles", roles=[r.name for r in topology.roles])'),
    (r'print\("[MASFactory] Switches:", len\(topology\.switch_nodes\)\)',
     r'logger.info("masfactory.switches_count", count=len(topology.switch_nodes))'),
    (r'print\("\[MetaQuestioning\] Generating meta-questions..."\)',
     r'logger.info("metaquestioning.generating")'),
    (r'print\("\[MetaQuestioning\] Generated", len\(questions\), "questions"\)',
     r'logger.info("metaquestioning.generated", count=len(questions))'),
    (r'print\("\[MetaQuestioning\] Self-questioning FAILED"\)',
     r'logger.error("metaquestioning.failed")'),
    (r'print\("\[Executor\] Running topology..."\)',
     r'logger.info("executor.running_topology")'),
    (r'print\("\[SynthesisAgent\] Error:", e\)',
     r'logger.error("synthesis.error", error=str(e))'),
    (r'print\("\[DB\] PostgreSQL save failed:", e\)',
     r'logger.error("db.save_failed", error=str(e))'),
    (r'print\(sep\)',
     r'pass  # removed separator print'),
    (r'print\("ASTROFIN SENTINEL v5 -- MASFACTORY MODE"\)',
     r'logger.info("masfactory.mode_start")'),
    (r'print\(sep\)',
     r'pass  # removed separator print'),
    (r'print\(\)',
     r'pass  # removed empty print'),
    (r'print\(sep\)',
     r'pass  # removed separator print'),
    (r'print\("RESULT:", sig, "conf=", conf\)',
     r'logger.info("masfactory.result", signal=sig, confidence=conf)'),
    (r'print\("Topology:", result\["topology_hash"\]\[:8\]\)',
     r'logger.info("masfactory.topology_result", hash=result["topology_hash"][:8])'),
    (r'print\("Roles:", len\(result\["flows_run"\]\["roles"\]\)\)',
     r'logger.info("masfactory.roles_count", count=len(result["flows_run"]["roles"]))'),
    (r'print\("Steps:", len\(result\["execution_log"\]\)\)',
     r'logger.info("masfactory.steps_count", count=len(result["execution_log"]))'),
]

for pattern, repl in replacements:
    content = re.sub(pattern, repl, content)

# Удаляем возможные двойные pass
content = re.sub(r'pass  # removed.*\n\s*pass  # removed.*\n', '', content)

with open(filepath, "w") as f:
    f.write(content)

print("✅ sentinel_v5_mas.py updated with structlog")
