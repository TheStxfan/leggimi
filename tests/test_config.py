import pytest
from leggimi.config import get_openrouter_key


def test_controlla_esistenza_openrouter_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(EnvironmentError):
        get_openrouter_key()
