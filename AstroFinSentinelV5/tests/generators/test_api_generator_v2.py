from generators.api_generator import extract_api


def test_extract_api_with_docstring_and_types():
    source = '''
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
'''

    result = extract_api(source, module_name="math_utils")

    fn = result["functions"][0]

    assert fn["name"] == "add"
    assert fn["docstring"] == "Add two numbers."
    assert fn["returns"] == "int"

    assert fn["args"] == [
        {
            "name": "a",
            "annotation": "int",
        },
        {
            "name": "b",
            "annotation": "int",
        },
    ]
