"""Test ComEd Hourly Pricing diagnostics."""

from unittest.mock import patch

from syrupy.assertion import SnapshotAssertion
from syrupy.filters import props

from homeassistant.components.comed_hourly_pricing.const import DOMAIN
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry
from tests.components.diagnostics import get_diagnostics_for_config_entry
from tests.typing import ClientSessionGenerator


async def test_entry_diagnostics(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    snapshot: SnapshotAssertion,
) -> None:
    """Test config entry diagnostics."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        entry_id="test_entry_id",
        data={"monitored_feed": "five_minute", "offset": 0.0},
    )
    entry.add_to_hass(hass)

    with patch(
        "homeassistant.components.comed_hourly_pricing.coordinator.ComedApiClient.get_data",
        return_value=0.025,
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert await get_diagnostics_for_config_entry(hass, hass_client, entry) == snapshot(
        exclude=props("created_at", "modified_at")
    )
