"""
Verify that all required testing and compatibility packages are importable.
These tests will fail if Flask or Hypothesis are missing.
"""


def test_flask_importable():
    import flask

    assert flask.__version__


def test_hypothesis_importable():
    import hypothesis

    assert hypothesis.__version__
