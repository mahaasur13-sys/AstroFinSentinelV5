from pathlib import Path

from generators.api_generator import extract_api


def test_parse_sentinel_v5():
    path = Path("orchestration/sentinel_v5.py")

    source = path.read_text(encoding="utf-8")

    result = extract_api(
        source,
        module_name="sentinel_v5",
    )

    assert result["module"] == "sentinel_v5"

    total = (
        len(result["functions"])
        + len(result["classes"])
    )

    assert total > 0

