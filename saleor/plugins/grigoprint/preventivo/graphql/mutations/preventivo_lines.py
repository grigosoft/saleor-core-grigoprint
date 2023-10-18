import graphene
from saleor.graphql.checkout.mutations.checkout_line_delete import CheckoutLineDelete
from saleor.graphql.checkout.mutations.checkout_lines_delete import CheckoutLinesDelete
from saleor.graphql.checkout.mutations.checkout_lines_add import CheckoutLinesAdd, CheckoutLineInput
from saleor.graphql.checkout.mutations.checkout_lines_update import CheckoutLinesUpdate
from saleor.graphql.checkout.mutations.utils import get_checkout
from saleor.graphql.core import ResolveInfo

from saleor.graphql.core.mutations import ModelDeleteMutation
from saleor.graphql.core.scalars import PositiveDecimal
from saleor.graphql.core.types.base import BaseInputObjectType
from saleor.graphql.core.types.common import CheckoutError, NonNullList
from saleor.permission.enums import CheckoutPermissions

from ... import models
from .. import type
from . import clean_save


class PreventivoLineInput(BaseInputObjectType):
    prezzo_netto_forzato = PositiveDecimal(
        required=False,
        description=(
            "Prezzo forzato. Sovrascrive e usa 'price' di saleor"
        ),
    )
    descrizione_forzata = graphene.String(
        required=False,
        description=(
            "Descrizione personalizzata per questa lineaPreventivo, "
            "sovrascrive quella automatica del prodotto"
        ),
    )

class PreventivoLineeAggiungiInput(CheckoutLineInput):
    extra = graphene.Field(PreventivoLineInput)

class PreventivoLineaAggiungi(CheckoutLinesAdd):
    preventivo = graphene.Field(type.Preventivo, description="An updated Preventivo.")

    class Arguments:
        id = graphene.ID(
            description="The checkout's ID.",
            required=True,
        )
        linea = PreventivoLineeAggiungiInput(
            required=True,
            description=(
                "Linea Preventivo da aggiungere al Preventivo"
            ),
        )
        linee_correlate = graphene.List(
            PreventivoLineeAggiungiInput,
            required=False,
            description=(
                "Lista di prodotti correlati alla linea pricipale"
            ),
        )

    class Meta:
        description = (
            "aggiunge una linea ad un preventivo esistente"
            "se il prodotto è personalizzato imposta in automatico 'force_new_line=true'"
            "la linea può avere più linee di prodotti correlati (basi, strutture, ecc)"
            "le linee correlate hanno la stessa quantità del prodotto principale"
        )
        error_type_class = CheckoutError
        error_type_field = "checkout_errors"
    
    @classmethod
    def perform_mutation(  # type: ignore[override]
        cls,
        _root,
        info: ResolveInfo,
        /,
        *,
        linea,
        linee_correlate=None,
        id,
    ):
        checkout = cls.get_node_or_error(
            info, id, only_type=type.Checkout, field="id"
        )
        if checkout and checkout.user:
            clean_save.controllo_permessi_rappresentante_preventivo(cls, info, checkout.user)
        #clean_save.clean_preventivo_linea(cls, info, checkout, linea, linee_correlate)
        # old_lines = checkout.lines
        # lines = [linea]
        # if linee_correlate:
        #     lines.extend(linee_correlate)
        # for line in lines:
        #     line["force_new_line"] = True
        # aggiungo le linee con il metodo originale saleor
        # response = super().perform_mutation(_root,info, lines=lines,id=id)
        # new_lines = response.checkout.lines
        # linee_create = [line for line in new_lines if line not in old_lines]
        linee_create = None
        clean_save.save_preventivo_linea(cls, info, checkout, linee_create, linea, linee_correlate)
        response = PreventivoLineaAggiungi(checkout=checkout)
        response.preventivo = response.checkout.extra
        return response

class PreventivoLineaAggiornaInput(CheckoutLineInput):
    extra = graphene.Field(PreventivoLineInput)
    quantity = graphene.Int(
        required=False,
        description=(
            "The number of items purchased. "
            "Optional for apps, required for any other users."
        ),
    )
    line_id = graphene.ID(
        description="ID of the line.",
        required=True,
    )

class PreventivoLineaAggiorna(CheckoutLinesUpdate):
    preventivo = graphene.Field(type.Preventivo, description="An updated Preventivo.")

    class Arguments:
        id = graphene.ID(
            description="The checkout's ID.",
            required=True,
        )
        linea = graphene.Field(
            PreventivoLineaAggiornaInput, 
            required=True,
            description=(
                "Linea Preventivo da aggiornare"
            ),
        )

    class Meta:
        description = (
            "Aggiorna una linea-preventivo"
        )
        error_type_class = CheckoutError
        error_type_field = "checkout_errors"
    
    @classmethod
    def perform_mutation(  # type: ignore[override]
        cls,
        _root,
        info: ResolveInfo,
        /,
        *,
        linea,
        linee_correlate,
        id=None,
    ):
        checkout = cls.get_node_or_error(
            info, id, only_type=type.Checkout, field="id"
        )
        if checkout and checkout.user:
            clean_save.controllo_permessi_rappresentante_preventivo(cls, info, checkout.user)
        clean_save.clean_preventivo_linea(cls, info, checkout, linea)
        lines = [linea]
        if linee_correlate:
            lines.extend(linee_correlate)
        # aggiungo le linee con il metodo originale saleor
        response = super().perform_mutation(_root,info, lines=lines,id=id)
        response.preventivo = response.checkout.extra
        return response


class PreventivoLineaCancella(CheckoutLineDelete):
    preventivo = graphene.Field(type.Preventivo, description="An updated Preventivo.")

    class Arguments:
        id = graphene.ID(description="id del Preventivo a cui appartiene la linea", required=True)
        line_id = graphene.ID(description="ID della LineaPreventivo da eliminare")

    class Meta:
        description = "Cancella una preventivoLine."
        # permissions = (CheckoutPermissions.MANAGE_CHECKOUTS,)
        return_field_name = "checkout"
        error_type_class = CheckoutError

    
    @classmethod
    def perform_mutation(  # type: ignore[override]
        cls,
        _root,
        info: ResolveInfo,
        /,
        *,
        checkout_id=None,
        id=None,
        line_id,
        token=None,
    ):
        # checkout = get_checkout(cls, info, checkout_id=checkout_id, token=token, id=id)
        checkout = cls.get_node_or_error(
            info, id, only_type=type.Checkout, field="id"
        )
        if checkout and checkout.user:
            clean_save.controllo_permessi_rappresentante_preventivo(cls, info, checkout.user)
        # instance.id = instance.token # serve solo nel checkut in teoria

        response = super().perform_mutation(_root,info, id=id,line_id=line_id)
        response.preventivo = response.checkout.extra
        return response