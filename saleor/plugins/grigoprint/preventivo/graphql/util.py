from typing import Optional

from saleor.checkout.models import Checkout
from ..models import Preventivo

def is_checkout_extra(checkout:Optional[Checkout]) -> bool:
    """Return Boolean
    controlla se il checkout ha la parte extra, intercettaneo le eccezzioni"""
    if not checkout:
        return False
    try:
        checkout.extra # type: ignore
        return True
    except Preventivo.DoesNotExist or Checkout.DoesNotExist:
        return False
        
def controlla_o_crea_checkoutextra(checkout: "Checkout") -> Preventivo:
    if is_checkout_extra(checkout):
        return checkout.extra # type: ignore
    else:
        print("creato un checkout senza extra, lo aggiungo")
        checkoutExtra = Preventivo.objects.create(checkout=checkout)
        checkoutExtra.save()
        checkout.extra = checkoutExtra # type: ignore #TODO serve??
        checkout.save()
        return checkoutExtra