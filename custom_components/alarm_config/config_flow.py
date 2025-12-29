"""Config flow for Alarm Config."""
from __future__ import annotations

from homeassistant import config_entries

from .const import DOMAIN


class AlarmConfigConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Alarm Config."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="Alarm Config", data={})
