from django.forms import ValidationError
import graphene
from django.db.models import Q
from saleor.graphql.checkout.resolvers import resolve_checkouts
from saleor.graphql.core.connection import create_connection_slice, filter_connection_queryset
from saleor.graphql.core.utils import from_global_id_or_error
from saleor.graphql.core.validators import validate_one_of_args_is_in_query
from saleor.plugins.grigoprint.accountExtra.graphql.util import accerta_cliente_del_rappresentante_or_error

from saleor.plugins.grigoprint.accountExtra.util import is_cliente_del_rappresentante, is_rappresentante
from saleor.plugins.grigoprint.preventivo.filters import PreventivoFilterInput
from saleor.plugins.grigoprint.preventivo.models import Preventivo
from saleor.plugins.grigoprint.preventivo.sorters import PreventivoSortingInput

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
        channel=graphene.String(
            description="Slug of a channel for which the data should be returned."
        ),
        filter=PreventivoFilterInput(),
        sort_by=PreventivoSortingInput(description="Ordinamento Preventivi"),
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
    def resolve_preventivi(_root, info: ResolveInfo, *, channel=None, **kwargs):
        qs = Preventivo.objects.all()
        if channel:
            qs = qs.filter(checkout__channel__slug=channel)
        requestor = info.context.user
        if requestor:
            if is_rappresentante(requestor):
                qs.filter(checkout__user__extra__rappresentante=requestor)
        else:
            raise ValidationError("solo un utente può richiedere questa query")
        

        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(qs, info, kwargs, type.PreventivoCountableConnection)
