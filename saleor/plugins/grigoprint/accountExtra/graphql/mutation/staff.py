from email.mime import base
from email.policy import default
from secrets import choice
import graphene
from saleor.core.tracing import traced_atomic_transaction
from saleor.graphql.account.i18n import I18nMixin
from saleor.graphql.core import ResolveInfo

from saleor.graphql.core.types.common import NonNullList, StaffError
from saleor.plugins.grigoprint.accountExtra.enum import TipoUtente

from saleor.graphql.core.mutations import BaseMutation, ModelMutation

from saleor.checkout import AddressType

from saleor.graphql.account.types import AddressInput

from saleor.permission.enums import AccountPermissions

from saleor.graphql.core.enums import AccountErrorCode

from saleor.graphql.account.mutations.staff import StaffCreateInput, StaffInput, AddressCreate, AddressUpdate, CustomerCreate, CustomerUpdate, StaffCreate, StaffUpdate, StaffUpdateInput
from saleor.graphql.account.mutations.account import AccountError
from saleor.graphql.account.mutations.base import (
    SHIPPING_ADDRESS_FIELD,
    BILLING_ADDRESS_FIELD,
    CustomerInput,
    UserCreateInput,
    UserInput,
)
from django.core.exceptions import ValidationError

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
        clean_save.accerta_user_extra_or_error(instance)
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

    aggiungi_contatti = NonNullList(ContattoInput, description="Contatti da aggiungere al cliente")

class ClienteCreaInput(CustomerInput):
    extra = ClienteExtraInput(required=True)

class ClienteCrea(CustomerCreate):
    # user = graphene.Field(
    #     type.User, description="A userExtra instance"
    # )
    user_extra = graphene.Field(
        type.UserExtra, description="A userExtra instance"
    )
    class Arguments:
        input = ClienteCreaInput(
            description="Fields required to create a staff user.", required=True
        )

    class Meta:
        description = ("Crea un nuovo cliente ")
        exclude = ["password","is_rappresentante","commissione"]
        model = models.User
        object_type = type.User
        permissions = (AccountPermissions.MANAGE_USERS,) # TODO permessi rappresentante
        error_type_class = StaffError
        error_type_field = "staff_errors"

    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        cleaned_input_extra = cleaned_input["extra"]
        cleaned_input_extra["is_staff"] = False
        clean_save.clean_user_extra(instance, cleaned_input_extra, data)
        clean_save.clean_assegna_rappresentante(cls, info, instance, cleaned_input_extra)
        print("super")
        return cleaned_input

    @classmethod
    def _save_extra(cls, info: ResolveInfo, instance, cleaned_data):
        cleaned_data_extra = cleaned_data["extra"]
        with traced_atomic_transaction():
            clean_save.controllaOCreaUserExtra(instance)
            # salvo le informazioni in userExtra
            clean_save.save_user_extra(instance, cleaned_data_extra)
            clean_save.save_assegna_rappresentante(instance, cleaned_data_extra)
    
    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        instance = cls.get_instance(info, **data)
        data = data.get("input")
        cleaned_input = cls.clean_input(info, instance, data)
        metadata_list = cleaned_input.pop("metadata", None)
        private_metadata_list = cleaned_input.pop("private_metadata", None)
        instance = cls.construct_instance(instance, cleaned_input)

        cls.validate_and_update_metadata(instance, metadata_list, private_metadata_list)
        cls.clean_instance(info, instance)
        cls.save(info, instance, cleaned_input)
        cls._save_m2m(info, instance, cleaned_input)
        cls._save_extra(info, instance, cleaned_input) # tutto uguale all'originale, tranne questo
        cls.post_save_action(info, instance, cleaned_input)
        return ClienteCrea(user_extra = instance.extra)

class StaffRappresentanteInput(graphene.InputObjectType):
    is_rappresentante = graphene.Boolean(description="se è un rappresentante", default = False)
    commissione = graphene.Float()

class StaffExtraInput(graphene.InputObjectType):
    extra = StaffRappresentanteInput()

class StaffCreaInput(StaffCreateInput, StaffExtraInput):
    pass
class StaffAggiornaInput(StaffUpdateInput, StaffExtraInput):
    pass

class StaffCrea(StaffCreate):
    class Arguments:
        input = StaffCreaInput(
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
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        cleaned_input_extra = cleaned_input["extra"]
        cleaned_input_extra["is_staff"] = False
        clean_save.clean_user_extra(instance, cleaned_input_extra, data)
        clean_save.clean_assegna_rappresentante(cls, info, instance, cleaned_input_extra)
        clean_save.clean_is_rappresentante(instance, cleaned_input_extra,data)
        # cleaned_input["tipo_utente"] = TipoUtente.PRIVATO
        return cleaned_input
        
    @classmethod
    def _save_m2m(cls, info: ResolveInfo, instance, cleaned_data):
        cleaned_data_extra = cleaned_data["extra"]
        with traced_atomic_transaction():
            super()._save_m2m(info, instance, cleaned_data)
            clean_save.accerta_user_extra_or_error(instance)
            # salvo le informazioni in userExtra
            clean_save.save_user_extra(instance, cleaned_data_extra)
            clean_save.save_assegna_rappresentante(instance, cleaned_data_extra)
            clean_save.save_is_rappresentante(instance,cleaned_data)
            










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




class ClienteInput2(UserCreateInput):
    denominazione = graphene.String(description="nome completo")
    id_danea = graphene.String(description="id cliene nel programma DaneaEsayfatt")
    tipo_cliente = graphene.String(choice = models.TipoUtente.CHOICES, default = models.TipoUtente.AZIENDA)

    tel = graphene.String(description="telefono dell'utente")
    cell = graphene.String(description="cellulare dell'utente")
    
    #is_no_login = models.BooleanField(default=False) # sostituito per 
    rappresentante = graphene.String(description="email del rappresentate")
    # dati azienda
    piva = graphene.String()
    cf = graphene.String()
    # ragione sociale nel nome
    pec = graphene.String()
    sdi = graphene.String()
    #Pubblica amministrazione
    rif_ammin = graphene.String()
    split_payment = graphene.Boolean(default=False)

    # addresses = graphene.List(AddressInput)
    # contatti = graphene.List(ContattoInput)

    iva = graphene.String()
    porto = graphene.String(choice = models.TipoPorto.CHOICES, default = models.TipoPorto.FRANCO_CON_ADDEBITO) # franco, assegnato, ecc
    vettore = graphene.String(choice = models.TipoVettore.CHOICES, default = models.TipoVettore.VETTORE_GLS) # franco, assegnato, ecc
    pagamento = graphene.String()
    coordinate_bancarie = graphene.String()
    listino = graphene.String()
    sconto = graphene.Float()
class StaffInput2(ClienteInput2):
    #rappresentante
    is_staff = graphene.Boolean(defult = False, description="se questo utente è uno staff.")
    is_rappresentante = graphene.Boolean(defult = False, description="se questo staff è un rappresentante. DEVE essere anche STAFF!")
    commissione = graphene.Float(default = 0, description="compenso che ha il prappresentante con i suoi clienti")
           
    
class ClienteCrea2(CustomerCreate):
    class Arguments:
        input = ClienteInput2(
            description="Fields required to create a customer.", required=True
        )
    class Meta:
        description = "Creates a new customer."
        exclude = ["password"]
        permissions = (AccountPermissions.MANAGE_USERS,)
        error_type_class = AccountError
        error_type_field = "account_errors"
        model = models.UserExtra
        object_type = type.UserExtra

    @classmethod
    def clean_input(cls, info, instance, data):
        billing = data.get(BILLING_ADDRESS_FIELD, None)
        billing_vuoto = True
        if billing:
            for c in billing:
                if billing[c]:
                    billing_vuoto = False
        if billing_vuoto:
            data.pop(BILLING_ADDRESS_FIELD, None) #elimino da data BILLING cosi non da errore di field obbligatori vuoti
        cleaned_input = super().clean_input(info, instance, data)

        return clean_account_extra_input(cls, info, instance, data, cleaned_input)



class ClienteAggiorna(CustomerUpdate):
    class Arguments:
        id = graphene.ID(description="ID of a customer to update.", required=True)
        input = ClienteInput2(
            description="Fields required to update a customer.", required=True
        )
    class Meta:
        model = models.UserExtra
        object_type = type.UserExtra
        description = "Updates an existing customer."
        exclude = ["password"]
        permissions = (AccountPermissions.MANAGE_USERS,)
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)
        return clean_account_extra_input(cls, info, instance, data, cleaned_input)

class StaffCrea2(StaffCreate):
    class Arguments:
        input = StaffInput(
            description="Fields required to create un utente staff.", required=True
        )
    class Meta:
        description = "Creates a new staff."
        exclude = ["password"]
        permissions = (AccountPermissions.MANAGE_STAFF,)
        error_type_class = AccountError
        error_type_field = "account_errors"
        model = models.UserExtra
        object_type = type.UserExtra

    @classmethod
    def clean_input(cls, info, instance, data):
        billing = data.get(BILLING_ADDRESS_FIELD, None)
        billing_vuoto = True
        if billing:
            for c in billing:
                if billing[c]:
                    billing_vuoto = False
        if billing_vuoto:
            data.pop(BILLING_ADDRESS_FIELD, None)
        cleaned_input = super().clean_input(info, instance, data)
        cleaned_input["is_staff"] = True
        return cleaned_input
class StaffAggiorna(StaffUpdate):
    class Arguments:
        id = graphene.ID(description="ID of a staff to update.", required=True)
        input = StaffInput(
            description="Fields required to update a staff.", required=True
        )
    class Meta:
        model = models.UserExtra
        object_type = type.UserExtra
        description = "Updates an existing Staff."
        exclude = ["password"]
        permissions = (AccountPermissions.MANAGE_STAFF,)
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)
        return clean_account_extra_input(cls, info, instance, data, cleaned_input)


# class IndirizzoCrea(ModelMutation):
#     user = graphene.Field(
#         type.UserExtra, description="A user instance for which the address was created."
#     )
#     class Arguments:
#         user_id = graphene.ID(
#             description="ID of a user to create address for.", required=True
#         )
#         input = AddressInput(
#             description="Fields required to create address.", required=True
#         )

#     class Meta:
#         description = "Creates user address."
#         model = models_saleor.Address
#         permissions = (AccountPermissions.MANAGE_USERS,)
#         error_type_class = AccountError
#         error_type_field = "account_errors"

#     @classmethod
#     def perform_mutation(cls, root, info, **data):
#         user_id = data["user_id"]
#         user = cls.get_node_or_error(info, user_id, field="user_id", only_type=type.UserExtra)
#         response = super().perform_mutation(root, info, **data)
#         if not response.errors:
#             address = info.context.plugins.change_user_address(
#                 response.address, None, user
#             )
#             user.addresses.add(address)
#             response.user = user
#         return response
# class IndirizzoAggiorna(AddressUpdate):
#     class Meta:
#         description = "Updates an address."
#         model = models_saleor.Address
#         permissions = (AccountPermissions.MANAGE_USERS,)
#         error_type_class = AccountError
#         error_type_field = "account_errors"
