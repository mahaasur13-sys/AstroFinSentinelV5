from generators.api_generator import extract_api


def test_extract_api_basic_module():
    source = """
def add(a: int, b: int) -> int:
    return a + b
"""

    result = extract_api(source, module_name="sample")

    assert result["module"] == "sample"
    assert len(result["functions"]) == 1
    assert result["functions"][0]["name"] == "add"
