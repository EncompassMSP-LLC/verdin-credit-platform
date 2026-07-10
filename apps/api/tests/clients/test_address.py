"""Client mailing address formatting tests."""

from api.modules.clients.address import format_client_mailing_address
from api.modules.clients.models import Client, ClientStatus


def test_format_client_mailing_address_multiline() -> None:
    client = Client(
        display_name="Jane Consumer",
        status=ClientStatus.ACTIVE,
        mailing_address_line1="123 Main St",
        mailing_address_line2="Apt 4B",
        mailing_city="Atlanta",
        mailing_state="GA",
        mailing_postal_code="30301",
    )
    assert format_client_mailing_address(client) == "123 Main St\nApt 4B\nAtlanta, GA 30301"


def test_format_client_mailing_address_returns_none_when_missing() -> None:
    client = Client(display_name="Jane Consumer", status=ClientStatus.ACTIVE)
    assert format_client_mailing_address(client) is None
