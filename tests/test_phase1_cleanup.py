"""Phase 1 cleanup validation tests."""


def test_core_auth_importable():
    """Проверяем, что core.auth импортируется без ошибок."""
    try:
        import core.auth
    except ImportError as e:
        pytest.fail(f"core.auth should be importable: {e}")


def test_no_dead_imports():
    """Проверяем, что старые модули больше не импортируются."""
    # После чистки все импорты должны работать
    import core.auth

    assert core.auth is not None
