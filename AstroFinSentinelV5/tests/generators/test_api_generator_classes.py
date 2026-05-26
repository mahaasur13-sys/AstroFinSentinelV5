from generators.api_generator import extract_api


def test_extract_class_with_methods():
    source = '''
class MathAgent:
    """Performs math operations."""

    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
'''

    result = extract_api(source, module_name="agents.math")

    assert len(result["classes"]) == 1

    cls = result["classes"][0]

    assert cls["name"] == "MathAgent"
    assert cls["docstring"] == "Performs math operations."

    assert len(cls["methods"]) == 1

    method = cls["methods"][0]

    assert method["name"] == "add"
    assert method["returns"] == "int"
