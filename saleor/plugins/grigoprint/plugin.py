
from typing import Any, List, Union
from saleor.account.models import Address, User
from saleor.checkout.fetch import CheckoutInfo, CheckoutLineInfo
from saleor.order.models import Order, OrderLine
from saleor.product.models import Product, ProductVariant
from .accountExtra.util import controlla_o_crea_userextra
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
        controlla_o_crea_userextra(customer)
    def staff_created(self, staff: "User", previous_value: Any) -> Any:
        controlla_o_crea_userextra(staff)

    ### calcola prezzi con prodotto personalizzato
    def calculate_checkout_line_unit_price(self, 
            checkoutInfo:"CheckoutInfo", 
            linesInfo:List["CheckoutLineInfo"], 
            address:Union["Address", None],
            other
        )->TaxedMoney:
        raise Exception("TODO: not implemented yet")
    ### controllo prezzi di linee con padre e figlio
    def calculate_checkout_line_total(self, 
            checkoutInfo:"CheckoutInfo", 
            linesInfo:List["CheckoutLineInfo"], 
            address:Union["Address", None],
            taxed_money:TaxedMoney,
            other
        )->TaxedMoney:
        raise Exception("TODO: not implemented yet")

    ### calcola prezzi con prodotto personalizzato
    def calculate_order_line_unit(self,
            order:"Order", 
            orderLine:"OrderLine", 
            productVariant:"ProductVariant", 
            product:"Product", 
            taxedMoney:"TaxedMoney"
        )->TaxedMoney:
        raise Exception("TODO: not implemented yet")
    ### controllo prezzi di linee con padre e figlio
    def calculate_order_line_total(self,
            order:"Order", 
            orderLine:"OrderLine", 
            productVariant:"ProductVariant", 
            product:"Product", 
            taxedMoney:"TaxedMoney"
        )->TaxedMoney:
        raise Exception("TODO: not implemented yet")