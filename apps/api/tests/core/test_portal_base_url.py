"""Settings: portal base URL must not stay on localhost when PUBLIC_APP_URL is https."""

from api.core.config import Settings


def test_lrp_portal_base_url_falls_back_from_https_public_app_url() -> None:
    settings = Settings(
        secret_key="test-secret-key-at-least-32-characters-long",
        public_app_url="https://app.lrpartners.net",
        lrp_portal_base_url="http://localhost:3100",
        app_env="staging",
    )
    assert settings.lrp_portal_base_url == "https://app.lrpartners.net"


def test_lrp_portal_base_url_keeps_explicit_https() -> None:
    settings = Settings(
        secret_key="test-secret-key-at-least-32-characters-long",
        public_app_url="https://app.lrpartners.net",
        lrp_portal_base_url="https://portal.example.com",
        app_env="staging",
    )
    assert settings.lrp_portal_base_url == "https://portal.example.com"


def test_lrp_portal_base_url_keeps_localhost_in_local_dev() -> None:
    settings = Settings(
        secret_key="test-secret-key-at-least-32-characters-long",
        public_app_url="http://localhost:8080",
        lrp_portal_base_url="http://localhost:3100",
        app_env="development",
    )
    assert settings.lrp_portal_base_url == "http://localhost:3100"
