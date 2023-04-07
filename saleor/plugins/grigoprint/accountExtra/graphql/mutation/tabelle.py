import graphene

from saleor.graphql.core import ResolveInfo
from saleor.graphql.core.mutations import BaseMutation, ModelDeleteMutation, ModelMutation
from saleor.graphql.account.i18n import I18nMixin
from saleor.graphql.core.types.common import AccountError
from saleor.permission.enums import AccountPermissions
from ... import models
from .. import type


class IvaInput(graphene.InputObjectType):
    nome = graphene.String()
    valore = graphene.Float()
    info = graphene.String()

class IvaCrea(ModelMutation):

    class Arguments:
        input = IvaInput(
            description="Fields required to create a Iva.", required=True
        )
    class Meta:
        description = "Creates a new Iva."
        permissions = (AccountPermissions.MANAGE_USERS,)
        model = models.Iva
        object_type = type.Iva
        error_type_class = AccountError
        error_type_field = "account_errors"

class IvaAggiorna(ModelMutation):

    class Arguments:
        id = graphene.ID(description="ID of Iva to update", required=True)
        input = IvaInput(
            description="Fields required to create a Iva.", required=True
        )
    class Meta:
        description = "Update a new Iva."
        permissions = (AccountPermissions.MANAGE_USERS,)
        model = models.Iva
        object_type = type.Iva
        error_type_class = AccountError
        error_type_field = "account_errors"

class IvaCancella(ModelDeleteMutation):

    class Arguments:
        id = graphene.ID(description="ID of Iva to delete", required=True)
    class Meta:
        description = "Delete a Iva."
        permissions = (AccountPermissions.MANAGE_USERS,)
        model = models.Iva
        object_type = type.Iva
        error_type_class = AccountError
        error_type_field = "account_errors"
        

class ListinoInput(graphene.InputObjectType):
    nome = graphene.String()
    ricarico = graphene.Float()
    info = graphene.String()

class ListinoCrea(ModelMutation):

    class Arguments:
        input = ListinoInput(
            description="Fields required to create a Listino.", required=True
        )
    class Meta:
        description = "Creates a new Listino."
        permissions = (AccountPermissions.MANAGE_USERS,)
        model = models.Listino
        object_type = type.Listino
        error_type_class = AccountError
        error_type_field = "account_errors"

class ListinoAggiorna(ModelMutation):

    class Arguments:
        id = graphene.ID(description="ID of Listino to update", required=True)
        input = ListinoInput(
            description="Fields required to create a Listino.", required=True
        )
    class Meta:
        description = "Update a new Listino."
        permissions = (AccountPermissions.MANAGE_USERS,)
        model = models.Listino
        object_type = type.Listino
        error_type_class = AccountError
        error_type_field = "account_errors"

class ListinoCancella(ModelDeleteMutation):
    """Base mutation for customer create used by staff and account."""

    class Arguments:
        id = graphene.ID(description="ID of Listino to delete", required=True)
    class Meta:
        description = "Delete a Listino."
        permissions = (AccountPermissions.MANAGE_USERS,)
        model = models.Listino
        object_type = type.Listino
        error_type_class = AccountError
        error_type_field = "account_errors"
        