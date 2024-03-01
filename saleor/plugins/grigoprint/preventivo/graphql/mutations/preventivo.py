import graphene
from saleor.core.tracing import traced_atomic_transaction
from saleor.graphql.checkout.mutations.checkout_create import CheckoutCreate, CheckoutCreateInput, CheckoutLineInput
from saleor.graphql.checkout.types import Checkout
from saleor.graphql.core import ResolveInfo

from saleor.graphql.core.mutations import ModelDeleteMutation, ModelMutation
from saleor.graphql.core.types.common import CheckoutError, NonNullList
from saleor.permission.enums import CheckoutPermissions
from saleor.plugins.grigoprint.graphql_util import ModelExtraMutation

from . import clean_save
from .. import type
from ... import models

class PreventivoStatoInput(graphene.InputObjectType):
    stato = type.StatoPreventivoEnum(required=False)

class PreventivoInput(PreventivoStatoInput):
    precedente = graphene.ID(description="id del preventivo collegato (riordino)")
    user = graphene.ID(description="id del cliente associato al Preventivo/checkout.")
    
class PreventivoCreaInput(CheckoutCreateInput):
    extra = PreventivoInput()
    lines = NonNullList( # Solo per required=False
        CheckoutLineInput,
        description=(
            "NON USARE!"
        ),
        required=False,
    )

class PreventivoCrea(CheckoutCreate, ModelExtraMutation):
    preventivo  = graphene.Field(
        type.Preventivo, description="Instance: Preventivo"
    )
    class Arguments:
        input = PreventivoCreaInput(
            description="Fields required to create Preventivo.", required=True
        )
    class Meta:
        description = "Creates a new preventivo."
        permissions = (CheckoutPermissions.MANAGE_CHECKOUTS,)
        model = models.Checkout
        object_type = Checkout
        return_field_name = "checkout"
        error_type_class = CheckoutError
        error_type_field = "checkout_errors"
    
    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        cleaned_input["extra"] = cls.clean_input_extra(info, data)
        # controllo che la mail non sia settata
        # DEVE essere associato un cliente
        # no line input?
        clean_save.clean_preventivo(cls, info, instance, cleaned_input,data)
        cliente = cleaned_input["extra"].get("user",None)
        clean_save.controllo_permessi_rappresentante_preventivo(cls, info, cliente)
        
        
        return cleaned_input
    @classmethod
    @traced_atomic_transaction()
    def save(cls, info: ResolveInfo, instance, cleaned_input):
        super().save(info, instance, cleaned_input)
        
        clean_save.save_preventivo(instance, info, instance, cleaned_input)
    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        response = super().perform_mutation(_root,info,**data)
        response.preventivo = response.checkout.extra
        return response
    

# class ContattoAggiorna(ModelMutation):
#     class Arguments:
#         id = graphene.ID(description="id del contatto da modificare", required=True)
#         input = ContattoInput(
#             description="Fields required to create un contatto.", required=True
#         )
#     class Meta:
#         description = "Creates a new contatto."
#         permissions = (CheckoutPermissions.MANAGE_CHECKOUTS,)
#         model = models.Checkout
#         object_type = Checkout
#         return_field_name = "checkout"
#         error_type_class = CheckoutError
#         error_type_field = "checkout_errors"
#     @classmethod
#     def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
#         cleaned_input = super().clean_input(info, instance, data, **kwargs)
        
#         clean_save.clean_contatto(cls, info, instance.user_extra.user, cleaned_input,data)
        
#         return cleaned_input

class PreventivoCancella(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(description="id del preventivo da cancellare", required=True)
        
    class Meta:
        description = "Cancella un preventivo."
        permissions = (CheckoutPermissions.MANAGE_CHECKOUTS,)
        model = models.Checkout
        object_type = Checkout
        return_field_name = "checkout"
        error_type_class = CheckoutError
        error_type_field = "checkout_errors"

    @classmethod
    def clean_instance(cls, info: ResolveInfo, instance, /):
        clean_save.controllo_permessi_rappresentante_preventivo(cls, info, instance.user)
        instance.id = instance.token