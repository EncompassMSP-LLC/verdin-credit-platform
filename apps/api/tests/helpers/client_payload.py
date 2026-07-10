"""Shared client create payloads for API integration tests."""


def sample_client_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "display_name": "Test Client",
        "mailing_address_line1": "123 Main St",
        "mailing_city": "Atlanta",
        "mailing_state": "GA",
        "mailing_postal_code": "30301",
    }
    payload.update(overrides)
    return payload
