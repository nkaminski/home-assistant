"""Test the ComEd hourly pricing coordinator."""

from unittest.mock import patch

import aiohttp
import pytest

from homeassistant import config_entries
from homeassistant.components.comed_hourly_pricing.const import DOMAIN
from homeassistant.components.comed_hourly_pricing.coordinator import (
    ComedApiClient,
    ComedDataUpdateCoordinator,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from tests.common import MockConfigEntry


@pytest.mark.parametrize(
    ("monitored_feed", "offset", "expected"),
    [
        ("five_minute", 0.0, 0.025),
        ("five_minute", 0.1, 0.125),
    ],
    ids=["success", "with_offset"],
)
async def test_coordinator_success(
    hass: HomeAssistant, monitored_feed: str, offset: float, expected: float
) -> None:
    """Test successful data update."""
    entry = MockConfigEntry(
        domain=DOMAIN, data={"monitored_feed": monitored_feed, "offset": offset}
    )
    entry.add_to_hass(hass)

    client = ComedApiClient(aiohttp.ClientSession())

    entry.mock_state(hass, config_entries.ConfigEntryState.SETUP_IN_PROGRESS)
    with patch.object(client, "get_data", return_value=0.025):
        coordinator = ComedDataUpdateCoordinator(hass, entry, client)
        await coordinator.async_config_entry_first_refresh()

    assert coordinator.data == expected


@pytest.mark.parametrize(
    "side_effect",
    [
        TimeoutError("Timeout"),
        aiohttp.ClientError("Error"),
        ValueError("Parse error"),
    ],
    ids=["timeout", "client_error", "value_error"],
)
async def test_coordinator_errors(hass: HomeAssistant, side_effect: Exception) -> None:
    """Test coordinator handles errors."""
    entry = MockConfigEntry(
        domain=DOMAIN, data={"monitored_feed": "five_minute", "offset": 0.0}
    )
    entry.add_to_hass(hass)

    client = ComedApiClient(aiohttp.ClientSession())

    entry.mock_state(hass, config_entries.ConfigEntryState.SETUP_IN_PROGRESS)
    with patch.object(client, "get_data", side_effect=side_effect):
        coordinator = ComedDataUpdateCoordinator(hass, entry, client)
        with pytest.raises(ConfigEntryNotReady):
            await coordinator.async_config_entry_first_refresh()
