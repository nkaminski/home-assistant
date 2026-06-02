"""Test the ComEd hourly pricing sensor."""

from unittest.mock import patch

from syrupy.assertion import SnapshotAssertion

from homeassistant.components.comed_hourly_pricing.const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from tests.common import MockConfigEntry


async def test_sensor(
    hass: HomeAssistant, entity_registry: er.EntityRegistry, snapshot: SnapshotAssertion
) -> None:
    """Test the sensor."""
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

    state = hass.states.get("sensor.comed_hourly_pricing_5_minute_price")
    assert state == snapshot

    entity_entry = entity_registry.async_get(
        "sensor.comed_hourly_pricing_5_minute_price"
    )
    assert entity_entry == snapshot
