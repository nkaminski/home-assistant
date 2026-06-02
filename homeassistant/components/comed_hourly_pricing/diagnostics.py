"""Diagnostics support for ComEd Hourly Pricing."""

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import ComedConfigEntry

TO_REDACT: set[str] = {"title"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ComedConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data

    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "data": coordinator.data,
    }
