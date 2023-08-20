import graphene
from saleor.graphql.checkout.types import Checkout
from saleor.graphql.core.fields import PermissionsField
from saleor.plugins.grigoprint.util import choices_to_enum

from .....graphql.core.types import (
    ModelObjectType,
)
from .....graphql.core.connection import CountableConnection


from .....graphql.account.types import User

from .. import models



StatoPreventivoEnum = choices_to_enum(models.StatoPreventivo)

class Preventivo(ModelObjectType[models.Preventivo]):
    id = graphene.ID(required=True, description="ID dell'oggetto Checkout di saleor")
    checkout = graphene.Field(Checkout,description="Collegamento ad oggetto Checkout di saleor")
    number = graphene.String(description="anno + id incrementale")
    
    stato = StatoPreventivoEnum(description="StatoPreventivo: se NON CHECKOUT allora è preventivo")

    precedente = graphene.Field("saleor.plugins.grigoprint.preventivo.graphql.type.Preventivo")

    class Meta:
        description = "Rappresenta un preventivo-checkout"
        interfaces = [graphene.relay.Node,]
        model = models.Preventivo

    @staticmethod
    def resolve_id(root: models.Preventivo, _info, **_kwargs):
        return graphene.Node.to_global_id("Preventivo", root.checkout.pk)
    @staticmethod
    def resolve_number(root: models.Preventivo, _info, **_kwargs):
        return "{root.anno}/{root.number}"

class PreventivoCountableConnection(CountableConnection):
    class Meta:
        node = Preventivo