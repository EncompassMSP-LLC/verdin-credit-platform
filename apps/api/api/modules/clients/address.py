"""Format client mailing addresses for documents and display."""

from __future__ import annotations

from api.modules.clients.models import Client


def format_client_mailing_address(client: Client) -> str | None:
    line1 = (client.mailing_address_line1 or "").strip()
    if not line1:
        return None

    parts = [line1]
    line2 = (client.mailing_address_line2 or "").strip()
    if line2:
        parts.append(line2)

    city = (client.mailing_city or "").strip()
    state = (client.mailing_state or "").strip()
    postal = (client.mailing_postal_code or "").strip()
    city_state = ", ".join(part for part in (city, state) if part)
    if city_state and postal:
        parts.append(f"{city_state} {postal}")
    elif city_state:
        parts.append(city_state)
    elif postal:
        parts.append(postal)

    return "\n".join(parts)
