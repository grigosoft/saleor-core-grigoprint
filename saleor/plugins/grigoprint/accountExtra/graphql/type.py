import graphene
from graphene_django import DjangoObjectType
from saleor.core.exceptions import PermissionDenied
from saleor.graphql.core.fields import PermissionsField
from saleor.graphql.core.types.common import NonNullList

from saleor.permission.enums import AccountPermissions

from ...graphql_util import get_user_extra_or_None

from .....graphql.core.types import (
    ModelObjectType,
)
from .....graphql.core.federation import federated_entity
from .....graphql.core.connection import CountableConnection
from ...util import choices_to_enum

# from .....graphql.decorators import permission_required
# from .....core.permissions import AccountPermissions

from .....graphql.account.types import User, ObjectWithMetadata, UserCountableConnection
# from ...gestioneAzienda.graphql.type import Ferie, Notifica
# from ...gestioneAzienda import models as gestioneAziendaModels
from .. import models
# from django.contrib.auth import models as auth_models



TipoContattoEnum = choices_to_enum(models.TipoContatto)
TipoVettoreEnum = choices_to_enum(models.TipoVettore)
TipoPortoEnum = choices_to_enum(models.TipoPorto)
TipoUtenteEnum = choices_to_enum(models.TipoUtente)

class Contatto(DjangoObjectType):
    user_extra = graphene.Field("saleor.plugins.grigoprint.accountExtra.graphql.type.UserExtra", required=True)
    user = graphene.Field(User)

    class Meta:
        description = "Represents user contacts"
        interfaces = [graphene.relay.Node,]
        model = models.Contatto
        convert_choices_to_enum = ["uso",]
        fields = ("email","denominazione","telefono","uso")
   
    @staticmethod
    def resolve_user(root: models.Contatto, _info, **_kwargs):
        return root.user_extra.user
    @staticmethod
    def resolve_userExtra(root: models.Contatto, _info, **_kwargs):
        return root.user_extra

class ContattoCountableConnection(CountableConnection):
    class Meta:
        node = Contatto

class Listino(DjangoObjectType):
    class Meta:
        description = "Listino"
        interfaces = [graphene.relay.Node,]
        model = models.Listino
        fields = ("id","nome","ricarico","info") #"__all__"
    
class Iva(DjangoObjectType):
    class Meta:
        description = "Iva"
        interfaces = [graphene.relay.Node,]
        model = models.Iva
        fields = ("id","nome","valore","info") #"__all__"


class UserExtra(ModelObjectType[models.UserExtra]):
    id = graphene.ID(required=True, description="ID dell'oggetto User di saleor")
    
    user = graphene.Field(User, description="Collegamento ad oggetto User di saleor")
    
    email = graphene.String(description="collegamento diretto ad oggetto User.email di saleor")
    denominazione = graphene.String()
    id_danea = PermissionsField(graphene.String, permissions=[AccountPermissions.MANAGE_USERS, AccountPermissions.MANAGE_STAFF])
    tipo_utente= TipoUtenteEnum()
    # info prese dall'indirizzo di fatturazione
    # tel = graphene.String()
    # cell = graphene.String()
    # si potrebbe continuare con altri campi dell'indirizzo

    is_rappresentante = PermissionsField(graphene.Boolean, permissions=[AccountPermissions.MANAGE_USERS, AccountPermissions.MANAGE_STAFF])
    rappresentante = graphene.Field(User, description="Rappresentante assegnato a questo utente/cliente")
    commissione = PermissionsField(graphene.Float, permissions=[AccountPermissions.MANAGE_USERS, AccountPermissions.MANAGE_STAFF])

    #dati azienda
    piva = graphene.String()
    cf = graphene.String()
    pec = graphene.String()
    sdi = graphene.String(description="Codice destinatario per fatturazione elettronica: SDI o pec")
    # pubblica amministrazione
    rif_ammin = graphene.String()
    split_payment = graphene.Boolean()

    coordinate_bancarie = graphene.String()
    iva = graphene.Field(Iva, description="iva di default di questo cliente")
    porto = TipoPortoEnum()
    vettore = TipoVettoreEnum()
    pagamento = graphene.String()
    listino = PermissionsField(Listino, description="listino di questo cliente", permissions=[AccountPermissions.MANAGE_USERS, AccountPermissions.MANAGE_STAFF])
    sconto = graphene.Float()

    contatti = NonNullList(Contatto, description="List of all user's contacts.")
    # ferie = graphene.List(Ferie, description="ferie richieste di un cliente")
    # notifiche = graphene.List(Notifica, description="notifiche inviate da un cliente")
    class Meta:
        description = "Represents user data."
        interfaces = [graphene.relay.Node,]
        model = models.UserExtra
        convert_choices_to_enum = ["porto","vettore","tipo_cliente"]

    @staticmethod
    def resolve_id(root: models.UserExtra, _info, **_kwargs):
        return graphene.Node.to_global_id("User", root.user.pk)
    
    @staticmethod
    def resolve_user(root: models.UserExtra, _info, **_kwargs):
        return root.user
    @staticmethod
    def resolve_email(root: models.UserExtra, _info, **_kwargs):
        return root.user.email
    @staticmethod
    def resolve_denominazione(root: models.UserExtra, _info, **_kwargs):
        return root.denominazione 
    @staticmethod
    def resolve_id_danea(root: models.UserExtra, _info, **_kwargs):
        return root.id_danea 
    @staticmethod
    def resolve_tipo_utente(root: models.UserExtra, _info, **_kwargs):
        return root.tipo_utente
    @staticmethod
    def resolve_is_rappresentante(root: models.UserExtra, _info, **_kwargs):
        return root.is_rappresentante
    @staticmethod
    def resolve_rappresentante(root: models.UserExtra, _info, **_kwargs):
        return root.rappresentante 
    @staticmethod
    def resolve_commissione(root: models.UserExtra, _info, **_kwargs):
        return root.commissione
    @staticmethod
    def resolve_piva(root: models.UserExtra, _info, **_kwargs):
        return root.piva
    @staticmethod
    def resolve_cf(root: models.UserExtra, _info, **_kwargs):
        return root.cf
    @staticmethod
    def resolve_pec(root: models.UserExtra, _info, **_kwargs):
        return root.pec
    @staticmethod
    def resolve_sdi(root: models.UserExtra, _info, **_kwargs):
        return root.sdi
    @staticmethod
    def resolve_rif_amministrazione(root: models.UserExtra, _info, **_kwargs):
        return root.rif_ammin
    @staticmethod
    def resolve_split_paymet(root: models.UserExtra, _info, **_kwargs):
        return root.split_payment
    @staticmethod
    def resolve_iva(root: models.UserExtra, _info, **_kwargs):
        return root.iva
    @staticmethod
    def resolve_porto(root: models.UserExtra, _info, **_kwargs):
        return root.porto 
    @staticmethod
    def resolve_vettore(root: models.UserExtra, _info, **_kwargs):
        return root.vettore
    @staticmethod
    def resolve_pagamento(root: models.UserExtra, _info, **_kwargs):
        return root.pagamento
    @staticmethod
    def resolve_coordinate_bancarie(root: models.UserExtra, _info, **_kwargs):
        return root.coordinate_bancarie
    @staticmethod
    def resolve_listino(root: models.UserExtra, _info, **_kwargs):
        return root.listino
    @staticmethod
    def resolve_sconto(root: models.UserExtra, _info, **_kwargs):
        return root.sconto
    @staticmethod
    def resolve_contatti(root: models.UserExtra, _info, **_kwargs):
        return models.Contatto.objects.filter(user_extra=root)
    
    # @staticmethod
    # def resolve_ferie(root: models.UserExtra, _info, **_kwargs):
    #     if root.is_staff:
    #         # return root.ferie
    #         return gestioneAziendaModels.Ferie.objects.filter(utente=root.id)
    #     return None
    # @staticmethod
    # def resolve_notifiche(root: models.UserExtra, _info, **_kwargs):
    #     if root.is_staff:
    #         return gestioneAziendaModels.Notifica.objects.filter(mittente=root.id)
    #     return None


class UserExtraCountableConnection(UserCountableConnection):
    class Meta:
        node = UserExtra
        
