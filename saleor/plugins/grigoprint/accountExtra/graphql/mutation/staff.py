from email.mime import base
from email.policy import default
from secrets import choice
import graphene

from django.contrib.auth import password_validation
from django.core.exceptions import ObjectDoesNotExist

from saleor.core.exceptions import PermissionDenied
from saleor.core.tracing import traced_atomic_transaction
from saleor.graphql.account.i18n import I18nMixin
from saleor.graphql.app.dataloaders import get_app_promise
from saleor.graphql.core import ResolveInfo

from saleor.graphql.core.types.common import NonNullList, StaffError
from saleor.plugins.grigoprint.accountExtra.enum import TipoUtente

from saleor.graphql.core.mutations import BaseMutation, ModelMutation

from saleor.checkout import AddressType

from saleor.graphql.account.types import AddressInput

from saleor.permission.enums import AccountPermissions
from saleor.account import events as account_events

from saleor.graphql.core.enums import AccountErrorCode

from saleor.graphql.account.mutations.staff.staff_create import StaffCreateInput, StaffCreate
from saleor.graphql.account.mutations.staff.customer_update import CustomerCreate, CustomerUpdate
from saleor.graphql.account.mutations.staff.staff_update import  StaffUpdate, StaffUpdateInput
# from saleor.graphql.account.mutations.staff.address_create import AddressCreate
# from saleor.graphql.account.mutations.staff.address_update import AddressUpdate

from saleor.graphql.core.types.common import AccountError

from saleor.graphql.account.mutations.base import (
    SHIPPING_ADDRESS_FIELD,
    BILLING_ADDRESS_FIELD,
    CustomerInput,
    UserCreateInput,
    UserInput,
)
from django.core.exceptions import ValidationError
from saleor.plugins.grigoprint.accountExtra.graphql.util import accerta_user_extra_or_error
from saleor.plugins.grigoprint.accountExtra.util import controlla_o_crea_userextra

from saleor.plugins.grigoprint.permissions import GrigoprintPermissions

from .contatto import ContattoInput

from ... import models
from .. import type
from . import clean_save
from ......account import models as models_saleor
from .user import AccountExtraBaseInput



class AssegnaRappresentanteInput(graphene.InputObjectType):
    rappresentante_id = graphene.ID(description="Id del Rappresentante assegnato a questo utente/cliente")

class AssegnaRappresentante(BaseMutation):
    """Assegna rappresentante ad un utente"""

    class Arguments:
        id = graphene.ID(description="Id Utente da aggiornare")
        input = AssegnaRappresentanteInput(
            description="Fields necessari da assegnare un rappresentante.", required=True
        )
    class Meta:
        description = "Assegna rappresentante ad un utente"
        permissions = (AccountPermissions.MANAGE_USERS,)
        error_type_class = AccountError
        error_type_field = "account_errors"
    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        accerta_user_extra_or_error(instance)
        # controllo se l'ID è di un rappresentante
        clean_save.clean_assegna_rappresentante(cls,info,instance,cleaned_input)
        return cleaned_input
    @classmethod
    def save(cls, info: ResolveInfo, instance, cleaned_data):
        with traced_atomic_transaction():
            # salvo le informazioni in userExtra
            clean_save.save_assegna_rappresentante(instance, cleaned_data)
    
class ClienteExtraInput(AssegnaRappresentanteInput, AccountExtraBaseInput):
    id_danea = graphene.String()
    tipo_utente = type.TipoUtenteEnum()
    
    iva_id = graphene.ID(description="id dell'aliquta iva di questo cliente")
    porto = type.TipoPortoEnum()
    vettore = type.TipoVettoreEnum()
    pagamento = graphene.String()
    listino_id = graphene.ID(description="id del listino assegnato a questo cliente")
    sconto = graphene.Float()

    # aggiungi_contatti = NonNullList(ContattoInput, description="Contatti da aggiungere al cliente")

class ClienteInput(CustomerInput):
    extra = ClienteExtraInput(required=True, description="Campi per informazioni aggiuntive")

class ClienteCrea(CustomerCreate):
    user_extra = graphene.Field(
        type.UserExtra, description="A userExtra instance"
    )
    class Arguments:
        input = ClienteInput(
            description="Campi per creare un utente CLIENTE", required=True
        )

    class Meta:
        description = ("Crea un nuovo cliente ")
        exclude = ["password","is_rappresentante","commissione"]
        model = models.User
        object_type = type.User
        permissions = (AccountPermissions.MANAGE_USERS,) # TODO permessi rappresentante
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        cleaned_input_extra = cleaned_input["extra"]
        cleaned_input_extra["is_staff"] = False
        clean_save.clean_user_extra(instance, cleaned_input_extra, data)
        clean_save.clean_assegna_rappresentante(cls, info, instance, cleaned_input_extra)
        return cleaned_input

    @classmethod
    @traced_atomic_transaction()
    def save(cls, info: ResolveInfo, instance, cleaned_input):
        super().save(info, instance, cleaned_input)
        cleaned_input_extra = cleaned_input["extra"]
        controlla_o_crea_userextra(instance)
        # salvo le informazioni in userExtra
        clean_save.save_user_extra(instance, cleaned_input_extra)
        clean_save.save_assegna_rappresentante(instance, cleaned_input_extra)
    
    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        response = super().perform_mutation(_root,info,**data)
        response.user_extra = response.user.extra
        return response

class ClienteAggiorna(CustomerUpdate):
    user_extra = graphene.Field(
        type.UserExtra, description="A userExtra instance"
    )
    class Arguments:
        id = graphene.ID(description="ID di Saleor-USER da aggiornare", required=True)
        input = ClienteInput(
            description="Fields required to update a customer.", required=True
        )
    class Meta:
        model = models.User
        object_type = type.User
        description = "Updates an existing customer."
        exclude = ["password","is_rappresentante","commissione"]
        permissions = (AccountPermissions.MANAGE_USERS,)
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        cleaned_input_extra = cleaned_input["extra"]
        cleaned_input_extra["is_staff"] = False
        clean_save.clean_user_extra(instance, cleaned_input_extra, data)
        clean_save.clean_assegna_rappresentante(cls, info, instance, cleaned_input_extra)
        # print("super")
        return cleaned_input

    @classmethod
    @traced_atomic_transaction()
    def save(cls, info: ResolveInfo, instance, cleaned_input):
        super().save(info, instance, cleaned_input)
        cleaned_input_extra = cleaned_input["extra"]
        accerta_user_extra_or_error(instance)
        # salvo le informazioni in userExtra
        clean_save.save_user_extra(instance, cleaned_input_extra)
        clean_save.save_assegna_rappresentante(instance, cleaned_input_extra)
    
    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        response = super().perform_mutation(_root,info,**data)
        response.user_extra = response.user.extra
        return response



class StaffExtraRappresentanteInput(ClienteExtraInput):
    is_rappresentante = graphene.Boolean(description="se è un rappresentante", default = False)
    commissione = graphene.Float()

class StaffExtraInput(StaffCreateInput):
    extra = StaffExtraRappresentanteInput()

class StaffCrea(StaffCreate):
    user_extra = graphene.Field(
        type.UserExtra, description="A userExtra instance"
    )
    class Arguments:
        input = StaffExtraInput(
            description="Fields required to create a staff user.", required=True
        )

    class Meta:
        description = (
            "Creates a new staff user. "
            "Apps are not allowed to perform this mutation."
        )
        exclude = ["password"]
        model = models.User
        object_type = type.User
        permissions = (AccountPermissions.MANAGE_STAFF,)
        error_type_class = StaffError
        error_type_field = "staff_errors"

    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        data.pop("rappresentante_id",None) # ignoro questo input
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        cleaned_input_extra = cleaned_input["extra"]
        cleaned_input_extra["is_staff"] = True
        clean_save.clean_user_extra(instance, cleaned_input_extra, data)
        # clean_save.clean_assegna_rappresentante(cls, info, instance, cleaned_input_extra)
        clean_save.clean_is_rappresentante(instance, cleaned_input_extra,data)
        # cleaned_input["tipo_utente"] = TipoUtente.PRIVATO
        return cleaned_input
        
    @classmethod
    @traced_atomic_transaction()
    def save(cls, info: ResolveInfo, user, cleaned_input, send_notification=True):
        super().save(info, user, cleaned_input, send_notification)
        cleaned_input_extra = cleaned_input["extra"]
        controlla_o_crea_userextra(user)
        # salvo le informazioni in userExtra
        clean_save.save_user_extra(user, cleaned_input_extra)
        # clean_save.save_assegna_rappresentante(user, cleaned_input_extra)
        clean_save.save_is_rappresentante(user,cleaned_input)
    
    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        response = super().perform_mutation(_root,info,**data)
        response.user_extra = response.user.extra
        return response

class StaffAggiorna(StaffUpdate):
    user_extra = graphene.Field(
        type.UserExtra, description="A userExtra instance"
    )
    class Arguments:
        id = graphene.ID(description="ID di Saleor-USER da aggiornare", required=True)
        input = StaffExtraInput(
            description="Fields required to update a staff.", required=True
        )
    class Meta:
        model = models.User
        object_type = type.User
        description = "Updates an existing STAFF."
        exclude = ["password"]
        permissions = (AccountPermissions.MANAGE_USERS,)
        error_type_class = AccountError
        error_type_field = "account_errors"
    
    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        data.pop("rappresentante_id",None) # ignoro questo input
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        cleaned_input_extra = cleaned_input["extra"]
        cleaned_input_extra["is_staff"] = True
        clean_save.clean_user_extra(instance, cleaned_input_extra, data)
        # clean_save.clean_assegna_rappresentante(cls, info, instance, cleaned_input_extra)
        clean_save.clean_is_rappresentante(instance, cleaned_input_extra,data)
        # cleaned_input["tipo_utente"] = TipoUtente.PRIVATO
        return cleaned_input
        
    @classmethod
    @traced_atomic_transaction()
    def save(cls, info: ResolveInfo, user, cleaned_input, send_notification=True):
        super().save(info, user, cleaned_input, send_notification)
        cleaned_input_extra = cleaned_input["extra"]
        accerta_user_extra_or_error(user)
        # salvo le informazioni in userExtra
        clean_save.save_user_extra(user, cleaned_input_extra)
        # clean_save.save_assegna_rappresentante(user, cleaned_input_extra)
        clean_save.save_is_rappresentante(user,cleaned_input)
    
    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        response = super().perform_mutation(_root,info,**data)
        response.user_extra = response.user.extra
        return response
    


# class ForzaPassword(BaseMutation):
#     class Arguments:
#         id = graphene.ID(description="ID of a user.")
#         email = graphene.String( description="Email of a user.")
#         password = graphene.String(required=True, description="Password of a user.")

#     class Meta:
#         description = (
#             "Forza una password ad un utente. Solo un superUser può farlo"
#         )
#         error_type_class = AccountError
#         error_type_field = "account_errors"

#     @classmethod
#     def check_permissions(cls, context, permissions=None):
#         # controllo che il richiedente non sia un app
        
#         app = get_app_promise(context).get()
#         if app:
#             raise PermissionDenied(
#                 message="Apps are not allowed to perform this mutation."
#             )
#         # controllo che il richiedente sia un super user
#         #TODO
#         return super().check_permissions(context, permissions)

#     @classmethod
#     def perform_mutation(cls, _root, _info: ResolveInfo, /):
#         raise NotImplementedError() 
#         # TODO clean input
#         # _set_password_for_user(email, password):
#         return ForzaPassword()

#     @classmethod
#     def _set_password_for_user(cls, email, password):
#         try:
#             user = models.User.objects.get(email=email)
#         except ObjectDoesNotExist:
#             raise ValidationError(
#                 {
#                     "email": ValidationError(
#                         "User doesn't exist", code=AccountErrorCode.NOT_FOUND.value
#                     )
#                 }
#             )
#         try:
#             password_validation.validate_password(password, user)
#         except ValidationError as error:
#             raise ValidationError({"password": error})
#         user.set_password(password)
#         user.save(update_fields=["password", "updated_at"])
#         # TODO account_events.customer_password_reset_event(user=user)







ADDRESSES_FIELD = "addresses"
RAPPRESENTANTE_FIELD = "rappresentante"
PIVA_FIELD = "piva"
CF_FIELD = "cf"
IDDANEA_FIELD = "id_danea"
ISSTAFF_FIELD = "is_staff"
ISRAPPRESENTANTE_FIELD = "is_rappresentante"


def clean_account_extra_input(cls, info, instance, data, cleaned_input):
    addresses_data = data.pop(ADDRESSES_FIELD, None)
    rappresentate_data = data.pop(RAPPRESENTANTE_FIELD, None)
    piva = data.pop(PIVA_FIELD, None)
    cleaned_input[PIVA_FIELD] = piva if piva else None
    cf = data.pop(CF_FIELD, None)
    cleaned_input[CF_FIELD] = cf if cf else None
    idanea = data.pop(IDDANEA_FIELD, None)
    cleaned_input[IDDANEA_FIELD] = idanea if idanea else None
    idanea = data.pop(IDDANEA_FIELD, None)
    cleaned_input[IDDANEA_FIELD] = idanea if idanea else None

    # rappresentante
    if rappresentate_data:
        rapp = models.UserExtra.objects.filter(email=rappresentate_data).first()
        if rapp and rapp.is_rappresentante:
            cleaned_input[RAPPRESENTANTE_FIELD] = rapp
        else:
            raise ValidationError(
                {
                    "rappresentante": ValidationError(
                        "rappresentante non valido %s"%rappresentate_data, code="value", params={"rappresentante":rappresentate_data}
                    )
                })
    is_staff = data.pop(ISSTAFF_FIELD, None)
    is_rappresentante = data.pop(ISRAPPRESENTANTE_FIELD, None)
    cleaned_input[ISRAPPRESENTANTE_FIELD] = is_staff and is_rappresentante # se non è anche staff non può diventare rappresentante

    # indirizzi
    if addresses_data:
        cleaned_addresses = []
        for address_data in addresses_data:
            address_data_cleaned = cls.validate_address(
                address_data,
                address_type=AddressType.SHIPPING,
                instance=getattr(instance, SHIPPING_ADDRESS_FIELD),
                info=info,
            )
            cleaned_addresses.append(address_data_cleaned)
        cleaned_input[ADDRESSES_FIELD] = cleaned_addresses

    if cleaned_input.get("sconto"):
        if cleaned_input.get("sconto") not in range(0, 50):
            raise ValidationError(
                {
                    "sconto": ValidationError(
                        "Sconto da 0% e 50%", code="value", params={"sconto":cleaned_input.get("sconto")}
                    )
                })

    return cleaned_input
