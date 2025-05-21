import os
import importlib
import pytest


def test_email_service_config(monkeypatch):
    # Set environment variables for test
    monkeypatch.setenv('EMAIL_SERVICE_URL', 'http://localhost:1234')
    monkeypatch.setenv('EMAIL_API_KEY', 'secretkey')

    # Reload the config module to pick up environment changes
    import d4_auth_svc.config as config
    importlib.reload(config)

    assert config.EMAIL_SERVICE_URL == 'http://localhost:1234'
    assert config.EMAIL_API_KEY == 'secretkey'


def test_email_service_config_defaults(monkeypatch):
    # Unset environment variables to test default behavior
    monkeypatch.delenv('EMAIL_SERVICE_URL', raising=False)
    monkeypatch.delenv('EMAIL_API_KEY', raising=False)

    import d4_auth_svc.config as config
    importlib.reload(config)

    # When not set, the values should be None
    assert config.EMAIL_SERVICE_URL is None
    assert config.EMAIL_API_KEY is None
