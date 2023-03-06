"""Support for ComEd Hourly Pricing data."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import json
import logging

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_OFFSET, CURRENCY_DOLLAR, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    CONF_CURRENT_HOUR_AVERAGE,
    CONF_FIVE_MINUTE,
    CONF_MONITORED_FEED,
    CONF_MONITORED_FEEDS,
    CONF_SENSOR_TYPE,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)
_RESOURCE = "https://hourlypricing.comed.com/api"
_NATIVE_UNIT = f"{CURRENCY_DOLLAR}/{UnitOfEnergy.KILO_WATT_HOUR}"
_SUGGESTED_DISPLAY_PRECISION = 3


SCAN_INTERVAL = timedelta(minutes=5)

SENSOR_TYPES = {
    CONF_FIVE_MINUTE: SensorEntityDescription(
        key=CONF_FIVE_MINUTE,
        name="ComEd 5 Minute Price",
        native_unit_of_measurement=_NATIVE_UNIT,
        suggested_display_precision=_SUGGESTED_DISPLAY_PRECISION,
    ),
    CONF_CURRENT_HOUR_AVERAGE: SensorEntityDescription(
        key=CONF_CURRENT_HOUR_AVERAGE,
        name="ComEd Current Hour Average Price",
        native_unit_of_measurement=_NATIVE_UNIT,
        suggested_display_precision=_SUGGESTED_DISPLAY_PRECISION,
    ),
}

SENSOR_KEYS = [SENSOR_TYPES.keys()]

TYPES_SCHEMA = vol.In(SENSOR_KEYS)

SENSORS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SENSOR_TYPE): TYPES_SCHEMA,
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_OFFSET, default=0.0): vol.Coerce(float),
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_MONITORED_FEEDS): [SENSORS_SCHEMA]}
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the ComEd Hourly Pricing sensor from YAML configuration."""
    websession = async_get_clientsession(hass)

    entities = [
        ComedHourlyPricingSensor(
            websession,
            variable[CONF_OFFSET],
            variable.get(CONF_NAME),
            SENSOR_TYPES[variable[CONF_SENSOR_TYPE]],
        )
        for variable in config[CONF_MONITORED_FEEDS]
    ]

    async_add_entities(entities, True)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the ComEd Hourly Pricing sensor from a configuration entry."""
    websession = async_get_clientsession(hass)
    entities = [
        ComedHourlyPricingSensor(
            websession,
            config.data[CONF_OFFSET],
            None,
            SENSOR_TYPES[config.data[CONF_MONITORED_FEED]],
        )
    ]

    async_add_entities(entities, True)


class ComedHourlyPricingSensor(SensorEntity):
    """Implementation of a ComEd Hourly Pricing sensor."""

    _attr_attribution = "Data provided by ComEd Hourly Pricing service"

    def __init__(
        self, websession, offset, name, description: SensorEntityDescription
    ) -> None:
        """Initialize the sensor."""
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self.websession = websession
        if name:
            self._attr_name = name
        self.offset = offset

    async def async_update(self) -> None:
        """Get the ComEd Hourly Pricing data from the web service."""
        try:
            sensor_type = self.entity_description.key
            if sensor_type in (CONF_FIVE_MINUTE, CONF_CURRENT_HOUR_AVERAGE):
                url_string = _RESOURCE
                if sensor_type == CONF_FIVE_MINUTE:
                    url_string += "?type=5minutefeed"
                else:
                    url_string += "?type=currenthouraverage"

                async with async_timeout.timeout(60):
                    response = await self.websession.get(url_string)
                    # The API responds with MIME type 'text/html'
                    text = await response.text()
                    data = json.loads(text)
                    self._attr_native_value = (
                        float(data[0]["price"]) / 100.0 + self.offset
                    )

            else:
                self._attr_native_value = None

        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error("Could not get data from ComEd API: %s", err)
        except (ValueError, KeyError):
            _LOGGER.warning("Could not update status for %s", self.name)
