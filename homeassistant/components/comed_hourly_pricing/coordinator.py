"""DataUpdateCoordinator for ComEd Hourly Pricing."""

import asyncio
from datetime import timedelta
import json
import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_OFFSET
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_CURRENT_HOUR_AVERAGE,
    CONF_FIVE_MINUTE,
    CONF_MONITORED_FEED,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

_RESOURCE = "https://hourlypricing.comed.com/api"

_URL_MAP = {
    CONF_FIVE_MINUTE: "5minutefeed",
    CONF_CURRENT_HOUR_AVERAGE: "currenthouraverage",
}


class ComedApiClient:
    """ComEd API Client."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize."""
        self._session = session

    async def get_data(self, sensor_type: str) -> float:
        """Get data from the API."""
        if sensor_type not in _URL_MAP:
            raise ValueError(f"Unknown sensor type: {sensor_type}")

        url_string = f"{_RESOURCE}?type={_URL_MAP[sensor_type]}"

        async with asyncio.timeout(10):
            response = await self._session.get(url_string)
            response.raise_for_status()
            text = await response.text()
            data = json.loads(text)
            return float(data[0]["price"]) / 100.0


class ComedDataUpdateCoordinator(DataUpdateCoordinator[float]):
    """Class to manage fetching ComEd data."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        client: ComedApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        self.sensor_type = config_entry.data[CONF_MONITORED_FEED]
        self.offset: float = config_entry.data.get(CONF_OFFSET, 0.0)

        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self) -> float:
        """Update data via API."""
        try:
            price = await self.client.get_data(self.sensor_type)
            return price + self.offset
        except TimeoutError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="api_timeout",
            ) from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="api_error",
            ) from err
        except (ValueError, KeyError, IndexError) as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="parse_error",
            ) from err
