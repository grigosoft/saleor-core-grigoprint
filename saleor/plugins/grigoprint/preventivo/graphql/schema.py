import graphene
from django.db.models import Q

from .....graphql.core import ResolveInfo
from .....graphql.core.fields import FilterConnectionField, PermissionsField
from .....permission.enums import OrderPermissions

from . import type

class PreventivoQueries(graphene.ObjectType):
    preventivo = PermissionsField(
        type.Preventivo,
        id=graphene.Argument(graphene.ID, description="ID del preventivo."),
        
        permissions=[
            OrderPermissions.MANAGE_ORDERS,
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
        ],
    )
    
    
    @staticmethod
    def resolve_preventivo(
        _root, info: ResolveInfo, *, id=None, email=None, external_reference=None
    ):
        raise Exception("Not Implemented yet")
    
    @staticmethod
    def resolve_preventivi(
        _root, info: ResolveInfo, *, id=None, email=None, external_reference=None
    ):
        raise Exception("Not Implemented yet")
    