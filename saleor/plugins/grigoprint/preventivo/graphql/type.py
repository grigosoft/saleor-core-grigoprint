import graphene
from saleor.graphql.core.fields import PermissionsField

from saleor.permission.enums import AccountPermissions, GrigoprintPermissions

from ...graphql_util import get_user_extra_or_None

from .....graphql.core.types import (
    ModelObjectType,
)
from .....graphql.core.federation import federated_entity
from .....graphql.core.connection import CountableConnection
from .....graphql.core.enums import to_enum


from .....graphql.account.types import User, ObjectWithMetadata, UserCountableConnection

from .. import models
from ...accountExtra.graphql.type import UserExtra



StatoPreventivoEnum = to_enum(models.StatoPreventivo)

class Preventivo(ModelObjectType[models.Preventivo]):
    user_extra = graphene.Field(UserExtra, required=True)
    user = graphene.Field(User, required=True)
    
    stato = StatoPreventivoEnum()

    class Meta:
        description = "Rappresenta un preventivo"
        interfaces = [graphene.relay.Node,]
        model = models.Preventivo

    @staticmethod
    def resolve_user_extra(root: models.Preventivo, _info, **_kwargs):
        return root.user_extra
    @staticmethod
    def resolve_user(root: models.Preventivo, _info, **_kwargs):
        return root.user_extra.user

class PreventivoCountableConnection(CountableConnection):
    class Meta:
        node = Preventivo