"""Test the ComEd hourly pricing config entry."""

from unittest.mock import patch

from homeassistant.components.comed_hourly_pricing.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry


async def test_load_unload_config_entry(hass: HomeAssistant) -> None:
    """Test loading and unloading the integration."""
    entry = MockConfigEntry(
        domain=DOMAIN, data={"monitored_feed": "five_minute", "offset": 0.0}
    )
    entry.add_to_hass(hass)

    with patch(
        "homeassistant.components.comed_hourly_pricing.coordinator.ComedApiClient.get_data",
        return_value=0.025,
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.LOADED

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.NOT_LOADED  # type: ignore[comparison-overlap]
