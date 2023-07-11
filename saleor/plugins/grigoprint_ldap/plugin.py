from django.core.exceptions import ValidationError
from saleor.plugins.base_plugin import BasePlugin, ConfigurationTypeField, PluginConfiguration

from typing import Any
from saleor.account.models import User

from .ldapUtil import aggiungiUtenteLDAP

class GrigoprintLdapPlugin(BasePlugin):

    PLUGIN_ID = "plugin.grigoprint_ldap"  # plugin identifier
    PLUGIN_NAME = "LDAP data Loader"  # display name of plugin
    PLUGIN_DESCRIPTION = "Carica le anagrafiche in un server LDAP esterno"
    CONFIG_STRUCTURE = {
        "server": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "IP of server LDAP",
            "label": "IP Server LDAP",
        },
        "login": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Provide your login name",
            "label": "Username or account",
        },
        "password": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Provide your password",
            "label": "Password",
        }
    }
    DEFAULT_CONFIGURATION = [
        {"name": "server", "value": None},
        {"name": "login", "value": None},
        {"name": "password", "value": None},
    ]
    DEFAULT_ACTIVE = False
    CONFIGURATION_PER_CHANNEL = False

    @classmethod
    def validate_plugin_configuration(cls, plugin_configuration: "PluginConfiguration"):
        """Validate if provided configuration is correct."""
        missing_fields = []
        configuration = plugin_configuration.configuration
        configuration = {item["name"]: item["value"] for item in configuration}
        if not configuration["server"]:
            missing_fields.append("server IP")
        if not configuration["login"]:
            missing_fields.append("username or account")
        if not configuration["password"]:
            missing_fields.append("password or API token")

        if plugin_configuration.active and missing_fields:
            error_msg = (
                "To enable a plugin, you need to provide values for the "
                "following fields: "
            )
            raise ValidationError(error_msg + ", ".join(missing_fields))
        


    def customer_created(self, customer: "User", previous_value: Any) -> Any:
        aggiungiUtenteLDAP(customer)
    def staff_created(self, staff: "User", previous_value: Any) -> Any:
        aggiungiUtenteLDAP(staff)