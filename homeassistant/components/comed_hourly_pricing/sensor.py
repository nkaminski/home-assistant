"""Support for ComEd Hourly Pricing data."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import CURRENCY_DOLLAR, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ComedConfigEntry
from .const import CONF_CURRENT_HOUR_AVERAGE, CONF_FIVE_MINUTE, DOMAIN
from .coordinator import ComedDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0
_NATIVE_UNIT = f"{CURRENCY_DOLLAR}/{UnitOfEnergy.KILO_WATT_HOUR}"
_SUGGESTED_DISPLAY_PRECISION = 3

SENSOR_TYPES: dict[str, SensorEntityDescription] = {
    CONF_FIVE_MINUTE: SensorEntityDescription(
        key=CONF_FIVE_MINUTE,
        translation_key=CONF_FIVE_MINUTE,
        native_unit_of_measurement=_NATIVE_UNIT,
        suggested_display_precision=_SUGGESTED_DISPLAY_PRECISION,
        device_class=SensorDeviceClass.MONETARY,
    ),
    CONF_CURRENT_HOUR_AVERAGE: SensorEntityDescription(
        key=CONF_CURRENT_HOUR_AVERAGE,
        translation_key=CONF_CURRENT_HOUR_AVERAGE,
        native_unit_of_measurement=_NATIVE_UNIT,
        suggested_display_precision=_SUGGESTED_DISPLAY_PRECISION,
        device_class=SensorDeviceClass.MONETARY,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ComedConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the ComEd Hourly Pricing sensor from a configuration entry."""
    coordinator = entry.runtime_data

    description = SENSOR_TYPES[coordinator.sensor_type]

    async_add_entities([ComedHourlyPricingSensor(coordinator, description)])


class ComedHourlyPricingSensor(
    CoordinatorEntity[ComedDataUpdateCoordinator], SensorEntity
):
    """Implementation of a ComEd Hourly Pricing sensor."""

    _attr_attribution = "Data provided by ComEd Hourly Pricing service"
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ComedDataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            manufacturer="ComEd",
            name="ComEd Hourly Pricing",
        )

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data
