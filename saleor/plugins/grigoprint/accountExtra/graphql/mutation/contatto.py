import graphene
from saleor.account.error_codes import AccountErrorCode
from saleor.core.tracing import traced_atomic_transaction

from saleor.graphql.core import ResolveInfo
from django.core.exceptions import ValidationError
from saleor.graphql.core.mutations import BaseMutation, ModelDeleteMutation, ModelMutation, ModelDeleteMutation
from saleor.graphql.account.i18n import I18nMixin
from saleor.graphql.core.types.common import AccountError
from saleor.permission.enums import AccountPermissions
from ....permissions import GrigoprintPermissions
from ... import models
from .. import type
from . import clean_save


class ContattoInput(graphene.InputObjectType):
    denominazione = graphene.String()
    email = graphene.String()
    telefono = graphene.String()
    uso = type.TipoContattoEnum()
class ContattoCreaInput(ContattoInput):
    user_id = graphene.ID(description="id dell'utente (saleor)", required=True)
        

class ContattoCrea(ModelMutation):
    # user =  graphene.Field(
    #     type.User, description="A user instance for which the Contatto was created."
    # )
    
    class Arguments:
        input = ContattoCreaInput(
            description="Fields required to create un contatto.", required=True
        )
    class Meta:
        description = "Creates a new contatto."
        permissions = (AccountPermissions.MANAGE_USERS,GrigoprintPermissions.IS_RAPPRESENTANTE)
        error_type_class = AccountError
        error_type_field = "account_errors"
        model = models.Contatto
        object_type = type.Contatto
    # @classmethod
    # def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        
    #     response = super().perform_mutation(_root, info, data=data)
    #     # TODO
    #     return response
    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        
        user_id = data.get("user_id")
        user = cls.get_node_or_error(info, user_id, only_type=type.User)
        clean_save.accerta_user_extra_or_error(user)
        cleaned_input["user_extra"] = user.extra
        clean_save.clean_contatto(user,cleaned_input,data)
        
        return cleaned_input
    

class ContattoAggiorna(ModelMutation):
    class Arguments:
        id = graphene.ID(description="id del contatto da modificare", required=True)
        input = ContattoInput(
            description="Fields required to create un contatto.", required=True
        )
    class Meta:
        description = "Creates a new contatto."
        permissions = (AccountPermissions.MANAGE_USERS,GrigoprintPermissions.IS_RAPPRESENTANTE)
        error_type_class = AccountError
        error_type_field = "account_errors"
        model = models.Contatto
        object_type = type.Contatto
    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        
        clean_save.clean_contatto(instance.user_extra.user,cleaned_input,data)
        
        return cleaned_input

class ContattoCancella(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(description="id del contatto da cancellare", required=True)
        
    class Meta:
        description = "Cancella un contatto."
        permissions = (AccountPermissions.MANAGE_USERS,GrigoprintPermissions.IS_RAPPRESENTANTE)
        error_type_class = AccountError
        error_type_field = "account_errors"
        model = models.Contatto
        object_type = type.Contatto
    @classmethod
    def clean_instance(cls, _info: ResolveInfo, _instance, /):
        # TODO logica permessi rappresentante-cliente
        print("TODO logica permessi rappresentante-cliente")
        pass