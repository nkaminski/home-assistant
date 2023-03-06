"""Configuration flow for the ComEd hourly pricing integration."""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig

from .const import (
    CONF_CURRENT_HOUR_AVERAGE,
    CONF_FIVE_MINUTE,
    CONF_MONITORED_FEED,
    CONF_OFFSET,
    DEFAULT_OFFSET,
    DOMAIN,
)

_SELECT_FEED_CONFIG: SelectSelectorConfig = {
    "options": [CONF_CURRENT_HOUR_AVERAGE, CONF_FIVE_MINUTE],
    "translation_key": CONF_MONITORED_FEED,
}

DATA_SCHEMA = {
    CONF_MONITORED_FEED: SelectSelector(_SELECT_FEED_CONFIG),
    vol.Optional(CONF_OFFSET, default=DEFAULT_OFFSET): vol.Coerce(float),
}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configuration flow for the ComEd hourly pricing integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Process the user config flow step for the comed_hourly_pricing integration."""
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_MONITORED_FEED])
            self._abort_if_unique_id_configured()
            friendly_title = user_input[CONF_MONITORED_FEED].replace("_", " ")
            return self.async_create_entry(title=friendly_title, data=user_input)

        return self.async_show_form(step_id="user", data_schema=vol.Schema(DATA_SCHEMA))
