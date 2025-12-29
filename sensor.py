"""Sensor for Alarm Config."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup_platform(hass: HomeAssistant, config, async_add_entities, discovery_info=None):
    sensor = ResponsiblePeopleSensor(hass)
    hass.data[DOMAIN]["sensor"] = sensor
    async_add_entities([sensor])


class ResponsiblePeopleSensor(SensorEntity):
    _attr_icon = "mdi:account-group"
    _attr_name = "Alarm Config Responsible People"
    _attr_unique_id = "alarm_config_responsible_people"

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._people: list[str] = hass.data.get(DOMAIN, {}).get("responsible_people", [])

    @property
    def native_value(self) -> int:
        return len(self._people)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "people": self._people,
            "people_raw": "\n".join(self._people),
        }

    def set_people(self, people: list[str]) -> None:
        self._people = people
        self.async_write_ha_state()
