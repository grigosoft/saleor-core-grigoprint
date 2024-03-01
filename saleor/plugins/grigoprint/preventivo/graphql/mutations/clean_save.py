import graphene

from typing import Union, cast
from saleor.graphql.account.types import User
from saleor.graphql.core import ResolveInfo
from saleor.graphql.core.utils import from_global_id_or_error
from saleor.graphql.product.types.products import ProductVariant
from saleor.plugins.grigoprint.accountExtra.graphql.util import accerta_cliente_del_rappresentante_or_error
from saleor.plugins.grigoprint.accountExtra.util import is_rappresentante
from saleor.plugins.grigoprint.preventivo.graphql.util import controlla_o_crea_checkoutextra

from ... import models


def controllo_permessi_rappresentante_preventivo(cls, info: ResolveInfo, cliente:User):
    # if cliente:
    requestor = info.context.user
    if is_rappresentante(requestor):
        accerta_cliente_del_rappresentante_or_error(requestor, cliente)


def clean_preventivo(cls, info: ResolveInfo, instance, cleaned_input, data):
    user = cleaned_input["extra"].get("user",None)
    if user:
        cleaned_input["email"] = user.email
    


def save_preventivo(cls, info: ResolveInfo, instance, cleaned_input):
    preventivo = controlla_o_crea_checkoutextra(instance)
    user = cleaned_input["extra"]["user"]
    if user:
        instance.user = user
        instance.save()
    
    stato = cleaned_input["extra"]["stato"]
    if stato:
        preventivo.stato = stato
    preventivo.save()


# def clean_preventivo_linea(cls, info: ResolveInfo, checkout, linea, linee_correlate=None):
#   # controllo se le varianti sono tutte diverse, nelle linee inserite  
#   pass

def _save_single_preventivo_linea(checkout, linea_input, linea_correlata_su=None)->models.PreventivoLinea:    
    variant_id = cast(str, linea_input.get("variant_id"))
    metadata_list = linea_input.get("metadata")
    quantity = linea_input.get("quantity")

    _, variant_db_id = graphene.Node.from_global_id(variant_id)

    # temp, salta il salvataggio con tutti i controlli di saleor
    line_data = models.CheckoutLine.objects.create(
        checkout=checkout,
        variant_id=variant_db_id, 
        quantity=quantity
    )
    linea_preventivo = models.PreventivoLinea.objects.create(
        checkout_line=line_data
    )
    descrizione_forzata = linea_input.get("descrizioneForzata", None)
    if descrizione_forzata:
        linea_preventivo.descrizione_forzata = descrizione_forzata
    prezzoNetto_forzato = linea_input.get("prezzoNettoForzato", None)
    if prezzoNetto_forzato:
        linea_preventivo.prezzo_netto_forzato = prezzoNetto_forzato
    if linea_correlata_su:
        linea_preventivo.correlato_su = linea_correlata_su
    linea_preventivo.save()
    return linea_preventivo

def save_preventivo_linea(cls, info: ResolveInfo, checkout, linee_create,  linea, linee_correlate):
    linea_preventivo_principale = _save_single_preventivo_linea(checkout, linea)
    
    if linee_correlate:
        for linea_correlata in linee_correlate:
            _save_single_preventivo_linea(checkout, linea_correlata, linea_preventivo_principale)
