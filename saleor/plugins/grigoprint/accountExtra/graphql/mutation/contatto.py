import graphene

from saleor.graphql.core import ResolveInfo
from saleor.graphql.core.mutations import ModelDeleteMutation, ModelMutation, ModelDeleteMutation
from saleor.graphql.account.i18n import I18nMixin
from saleor.graphql.core.types.common import AccountError
from saleor.permission.enums import AccountPermissions
from saleor.plugins.grigoprint.accountExtra.graphql.util import accerta_user_extra_or_error
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
        permissions = (AccountPermissions.MANAGE_USERS,)
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
        accerta_user_extra_or_error(user)
        cleaned_input["user_extra"] = user.extra
        clean_save.clean_contatto(cls, info,user,cleaned_input,data)
        
        return cleaned_input
    

class ContattoAggiorna(ModelMutation):
    class Arguments:
        id = graphene.ID(description="id del contatto da modificare", required=True)
        input = ContattoInput(
            description="Fields required to create un contatto.", required=True
        )
    class Meta:
        description = "Creates a new contatto."
        permissions = (AccountPermissions.MANAGE_USERS,)
        error_type_class = AccountError
        error_type_field = "account_errors"
        model = models.Contatto
        object_type = type.Contatto
    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        
        clean_save.clean_contatto(cls, info, instance.user_extra.user, cleaned_input,data)
        
        return cleaned_input

class ContattoCancella(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(description="id del contatto da cancellare", required=True)
        
    class Meta:
        description = "Cancella un contatto."
        permissions = (AccountPermissions.MANAGE_USERS,)
        error_type_class = AccountError
        error_type_field = "account_errors"
        model = models.Contatto
        object_type = type.Contatto
    @classmethod
    def clean_instance(cls, info: ResolveInfo, instance, /):
        clean_save.clean_contatto(cls, info, instance.user_extra.user, None,None)
        
