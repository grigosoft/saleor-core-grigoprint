import graphene
from saleor.graphql.checkout.types import Checkout, CheckoutLine
from saleor.graphql.core import ResolveInfo
from saleor.graphql.core.descriptions import RICH_CONTENT
from saleor.graphql.core.fields import JSONString, PermissionsField
from saleor.graphql.core.types.common import NonNullList
from saleor.plugins.grigoprint.util import choices_to_enum

from .....graphql.core.types import (
    ModelObjectType,
    Money
)
from .....graphql.core.connection import CountableConnection


from .. import models



StatoPreventivoEnum = choices_to_enum(models.StatoPreventivo)

class PreventivoLine(ModelObjectType[models.PreventivoLine]):
    id = graphene.GlobalID(required=True, description="The ID of the checkout line.")
    checkout_line = graphene.Field(CheckoutLine)
    descrizione_forzata = JSONString(description="Descrizione forzata, sovrascrive descrizione del prodotto." + RICH_CONTENT)
    prezzo_netto_forzato = graphene.Float(
        description="Prezzo che sovrascrive il prezzo del prodotto, sconti ecc"
    )
    class Meta:
        description = "Rappresenta una linea nel preventivo."
        interfaces = [graphene.relay.Node,]
        model = models.PreventivoLine
    
    @staticmethod
    def resolve_id(root: models.PreventivoLine, _info: ResolveInfo):
        return graphene.Node.to_global_id("CheckoutLine", root.checkout_line.pk)


class Preventivo(ModelObjectType[models.Preventivo]):
    id = graphene.ID(required=True, description="ID dell'oggetto Checkout di saleor")
    checkout = graphene.Field(Checkout,description="Collegamento ad oggetto Checkout di saleor")
    numero = graphene.String(description="anno + id incrementale")
    
    lines = NonNullList(
        PreventivoLine,
        description=(
            "A list of checkout lines, each containing information about "
            "an item in the checkout."
        ),
        required=True,
    )

    stato = StatoPreventivoEnum(description="StatoPreventivo: se NON CHECKOUT allora è preventivo")
    precedente = graphene.Field("saleor.plugins.grigoprint.preventivo.graphql.type.Preventivo")

    class Meta:
        description = "Rappresenta un preventivo-checkout"
        interfaces = [graphene.relay.Node,]
        model = models.Preventivo

    @staticmethod
    def resolve_id(root: models.Preventivo, _info, **_kwargs):
        return graphene.Node.to_global_id("Checkout", root.checkout.pk)
    

class PreventivoCountableConnection(CountableConnection):
    class Meta:
        node = Preventivo