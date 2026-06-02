"""The comed_hourly_pricing component."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import PLATFORMS
from .coordinator import ComedApiClient, ComedDataUpdateCoordinator

type ComedConfigEntry = ConfigEntry[ComedDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: ComedConfigEntry) -> bool:
    """Set up comed_hourly_pricing integration from a ConfigEntry."""
    session = async_get_clientsession(hass)
    client = ComedApiClient(session)

    coordinator = ComedDataUpdateCoordinator(
        hass,
        entry,
        client,
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    # Forward the setup to the sensor platform.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ComedConfigEntry) -> bool:
    """Unload an instance of the comed_hourly_pricing integration."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
