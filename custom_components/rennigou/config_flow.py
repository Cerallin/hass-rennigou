import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

from .const import DOMAIN
from .rennigou import RennigouClient, RennigouLoginFail

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class RennigouConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            # Validate username and password
            try:
                client = RennigouClient(
                    user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
                )
                await client.login()

                return self.async_create_entry(
                    title=f"{client.username} (uid: {client.uid})",
                    data=user_input,
                )
            except RennigouLoginFail:
                errors["base"] = "invalid_auth"

        return self.async_show_form(
            data_schema=USER_SCHEMA,
            errors=errors,
        )
