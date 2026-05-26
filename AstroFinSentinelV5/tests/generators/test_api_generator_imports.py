import ast


def _extract_args(args) -> list[dict]:
    result = []

    for arg in args.args:
        result.append(
            {
                "name": arg.arg,
                "annotation": (
                    ast.unparse(arg.annotation)
                    if arg.annotation
                    else None
                ),
            }
        )

    return result


def _extract_imports(tree: ast.AST) -> list[str]:
    imports = []

    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(
                    f"{module}.{alias.name}" if module else alias.name
                )

    return imports


def extract_api(source: str, module_name: str = "unknown") -> dict:
    tree = ast.parse(source)

    result = {
        "module": module_name,
        "imports": [],
        "functions": [],
        "classes": [],
    }

    result["imports"] = _extract_imports(tree)

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            result["functions"].append(
                {
                    "name": node.name,
                    "args": _extract_args(node.args),
                    "returns": (
                        ast.unparse(node.returns)
                        if node.returns
                        else None
                    ),
                    "docstring": ast.get_docstring(node),
                    "async": False,   # FIX HERE
                }
            )

        elif isinstance(node, ast.AsyncFunctionDef):
            result["functions"].append(
                {
                    "name": node.name,
                    "args": _extract_args(node.args),
                    "returns": (
                        ast.unparse(node.returns)
                        if node.returns
                        else None
                    ),
                    "docstring": ast.get_docstring(node),
                    "async": True,   # FIX HERE
                }
            )

        elif isinstance(node, ast.ClassDef):
            cls = {
                "name": node.name,
                "docstring": ast.get_docstring(node),
                "methods": [],
            }

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    cls["methods"].append(
                        {
                            "name": item.name,
                            "args": _extract_args(item.args),
                            "returns": (
                                ast.unparse(item.returns)
                                if item.returns
                                else None
                            ),
                            "docstring": ast.get_docstring(item),
                            "async": False,
                        }
                    )

                elif isinstance(item, ast.AsyncFunctionDef):
                    cls["methods"].append(
                        {
                            "name": item.name,
                            "args": _extract_args(item.args),
                            "returns": (
                                ast.unparse(item.returns)
                                if item.returns
                                else None
                            ),
                            "docstring": ast.get_docstring(item),
                            "async": True,
                        }
                    )

            result["classes"].append(cls)

    return result
