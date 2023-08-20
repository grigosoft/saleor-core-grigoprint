from django.forms import ValidationError
import graphene
from django.db.models import Q
from saleor.graphql.core.utils import from_global_id_or_error
from saleor.graphql.core.validators import validate_one_of_args_is_in_query
from saleor.plugins.grigoprint.accountExtra.graphql.util import accerta_cliente_del_rappresentante_or_error

from saleor.plugins.grigoprint.accountExtra.util import is_cliente_del_rappresentante, is_rappresentante
from saleor.plugins.grigoprint.preventivo.models import Preventivo

from .....graphql.core import ResolveInfo
from .....graphql.core.fields import FilterConnectionField, PermissionsField
from .....permission.enums import OrderPermissions, CheckoutPermissions

from . import type

class PreventivoQueries(graphene.ObjectType):
    preventivo = PermissionsField(
        type.Preventivo,
        id=graphene.Argument(graphene.ID, description="ID del Checkout collegato al preventivo."),
        
        permissions=[
            OrderPermissions.MANAGE_ORDERS,
            CheckoutPermissions.MANAGE_CHECKOUTS,
        ],
        description="Restituise un preventivo spefico tramite ID.",
    )
    preventivi = FilterConnectionField(
        type.PreventivoCountableConnection,
        description="Lista completa di prevetivi, in base a chi è loggato",
        #filter=PreventiviFilterInput(description="Filtro Preventivi"),
        #sort_by=PreventiviSortingInput(description="Ordinamento Preventivi"),
        permissions=[
            OrderPermissions.MANAGE_ORDERS,
            CheckoutPermissions.MANAGE_CHECKOUTS,
        ],
    )
    
    
    @staticmethod
    def resolve_preventivo(
        _root, info: ResolveInfo, id
    ):
        validate_one_of_args_is_in_query("id", id)
        # preventivo = Preventivo.objects.filter(checkout_id=id).first()
        # sembra che saleor tenga solo il token come primary key e bisogna cercare tramite quello
        _, token = from_global_id_or_error(id, only_type="Checkout")
        preventivo = Preventivo.objects.filter(checkout__token=token).first()
        if preventivo:
            requestor = info.context.user
            cliente = preventivo.checkout.user
            if is_rappresentante(requestor):
                accerta_cliente_del_rappresentante_or_error(requestor, cliente)
        return preventivo
    
    @staticmethod
    def resolve_preventivi(
        _root, info: ResolveInfo,
    ):
        requestor = info.context.user
        if requestor:
            if is_rappresentante(requestor):
                return Preventivo.objects.filter(checkout__user__extra__rappresentante=requestor)
            else:
                return Preventivo.objects.all()
        else:
            raise ValidationError("solo un utente può richiedere questa query")