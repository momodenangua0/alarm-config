"""Alarm Config integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.storage import Store

from .const import DOMAIN, STORAGE_KEY, STORAGE_VERSION

_LOGGER = logging.getLogger(__name__)

FRONTEND_FILE = {
    "filename": "alarm-config-card.js",
    "url": "/local/alarm-config/alarm-config-card.js",
}

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)


async def _load_people(store: Store) -> list[str]:
    data = await store.async_load()
    if not data:
        return []
    people = data.get("people", [])
    if not isinstance(people, list):
        return []
    return [str(p).strip() for p in people if str(p).strip()]


def _parse_people(people_raw: str | None) -> list[str]:
    if not people_raw:
        return []
    lines = [line.strip() for line in people_raw.splitlines()]
    return [line for line in lines if line]


async def _save_people(hass: HomeAssistant, people: list[str]) -> None:
    store: Store = hass.data[DOMAIN]["store"]
    await store.async_save({"people": people})
    hass.data[DOMAIN]["responsible_people"] = people

    sensor = hass.data[DOMAIN].get("sensor")
    if sensor is not None:
        sensor.set_people(people)


async def _init_resource(hass: HomeAssistant, url: str, ver: str) -> None:
    resources: ResourceStorageCollection = hass.data["lovelace"].resources
    await resources.async_get_info()

    url_with_version = f"{url}?v={ver}"

    for item in resources.async_items():
        if not item.get("url", "").startswith(url):
            continue
        if item["url"].endswith(ver):
            return
        if isinstance(resources, ResourceStorageCollection):
            await resources.async_update_item(
                item["id"], {"res_type": "module", "url": url_with_version}
            )
        else:
            item["url"] = url_with_version
        return

    if isinstance(resources, ResourceStorageCollection):
        await resources.async_create_item({"res_type": "module", "url": url_with_version})
    else:
        add_extra_js_url(hass, url_with_version)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    hass.data.setdefault(DOMAIN, {})

    store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    hass.data[DOMAIN]["store"] = store
    hass.data[DOMAIN]["responsible_people"] = await _load_people(store)

    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                FRONTEND_FILE["url"],
                hass.config.path(
                    "custom_components",
                    DOMAIN,
                    "dist",
                    FRONTEND_FILE["filename"],
                ),
                True,
            )
        ]
    )

    version = "0.1.0"
    await _init_resource(hass, FRONTEND_FILE["url"], version)

    async def handle_set_people(call: ServiceCall) -> None:
        people_raw = call.data.get("people", "")
        people = _parse_people(people_raw)
        await _save_people(hass, people)

    async def handle_clear_people(call: ServiceCall) -> None:
        await _save_people(hass, [])

    hass.services.async_register(
        DOMAIN, "set_responsible_people", handle_set_people
    )
    hass.services.async_register(
        DOMAIN, "clear_responsible_people", handle_clear_people
    )

    await async_load_platform(hass, "sensor", DOMAIN, {}, config)
    return True
