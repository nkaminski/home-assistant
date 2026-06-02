"""Configuration flow for the ComEd hourly pricing integration."""

from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_OFFSET
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig

from .const import (
    CONF_CURRENT_HOUR_AVERAGE,
    CONF_FIVE_MINUTE,
    CONF_MONITORED_FEED,
    DEFAULT_OFFSET,
    DOMAIN,
)
from .coordinator import ComedApiClient

_SELECT_FEED_CONFIG = SelectSelectorConfig(
    options=[CONF_CURRENT_HOUR_AVERAGE, CONF_FIVE_MINUTE],
    translation_key=CONF_MONITORED_FEED,
)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MONITORED_FEED): SelectSelector(_SELECT_FEED_CONFIG),
        vol.Optional(CONF_OFFSET, default=DEFAULT_OFFSET): vol.Coerce(float),
    }
)


class ComedConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configuration flow for the ComEd hourly pricing integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Process the user config flow step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_MONITORED_FEED])
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            client = ComedApiClient(session)
            try:
                await client.get_data(user_input[CONF_MONITORED_FEED])
            except TimeoutError, aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                friendly_title = (
                    user_input[CONF_MONITORED_FEED].replace("_", " ").title()
                )
                return self.async_create_entry(title=friendly_title, data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
