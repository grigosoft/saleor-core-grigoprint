
from typing import Any
from saleor.account.models import User
from .accountExtra.util import controllaOCreaUserExtra
from ..base_plugin import BasePlugin
from prices import TaxedMoney


class GrigoprintPlugin(BasePlugin):
    PLUGIN_ID = "plugin.grigoprint"
    PLUGIN_NAME = "Grigoprint"
    DEFAULT_ACTIVE = True
    PLUGIN_DESCRIPTION = "aggiunta funzionalita per Azienda Ombrellificio Grigolini"
    CONFIGURATION_PER_CHANNEL = False

    #
    def customer_created(self, customer: "User", previous_value: Any) -> Any:
        controllaOCreaUserExtra(customer)
    def staff_created(self, staff: "User", previous_value: Any) -> Any:
        controllaOCreaUserExtra(staff)

    ### calcola prezzi con prodotto personalizzato
    def calculate_checkout_line_unit_price(checkoutInfo, linesInfo, address, discount, other)->TaxedMoney:
        raise Exception("TODO: not implemented yet")
    ### controllo prezzi di linee con padre e figlio
    def calculate_checkout_line_total(checkoutInfo, linesInfo, address, discount, other)->TaxedMoney:
        raise Exception("TODO: not implemented yet")

    ### calcola prezzi con prodotto personalizzato
    def calculate_order_line_unit(order, orderLine, productVariant, product, taxedMoney)->TaxedMoney:
        raise Exception("TODO: not implemented yet")
    ### controllo prezzi di linee con padre e figlio
    def calculate_order_line_total(order, orderLine, productVariant, product, taxedMoney)->TaxedMoney:
        raise Exception("TODO: not implemented yet")