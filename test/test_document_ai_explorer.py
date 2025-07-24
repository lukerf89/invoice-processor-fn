import pytest

from document_ai_explorer import setup_client


def test_setup_client_invalid_environment_variables():
    with pytest.raises(ValueError):
        setup_client()
