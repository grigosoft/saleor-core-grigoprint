import graphene
from django.db.models import Q
from saleor.graphql.core.types.common import AccountError

from saleor.graphql.core.types.filter_input import FilterInputObjectType
from saleor.graphql.utils import get_user_or_app_from_context
from saleor.permission.utils import has_one_of_permissions

from .....graphql.core import ResolveInfo
from .....core.exceptions import PermissionDenied
from .....permission.enums import AccountPermissions, OrderPermissions, GrigoprintPermissions
from .....graphql.core.tracing import traced_resolver
from .....graphql.core.utils import from_global_id_or_error
from .....graphql.core.fields import FilterConnectionField, PermissionsField
from .....graphql.core.connection import create_connection_slice, filter_connection_queryset
from .....graphql.account.resolvers import (
    resolve_address,
    resolve_address_validation_rules,
    resolve_customers,
    resolve_users,
    resolve_permission_group,
    resolve_permission_groups,
    resolve_staff_users,
    resolve_user,
)
from ..util import isUserExtra
from .....graphql.core.validators import validate_one_of_args_is_in_query
from .sorters import UserExtraSortingInput
from .filters import ClientiFilter

from ...graphql_util import get_user_extra_or_None

from .....graphql.core.fields import FilterConnectionField

from .....graphql.decorators import staff_member_or_app_required

from .. import models
from . import type

@traced_resolver
def resolve_user_con_rappresentante(info, id=None, email=None, external_reference=None):
    requester = get_user_or_app_from_context(info.context)
    if requester:
        filter_kwargs = {}
        if id:
            _model, filter_kwargs["pk"] = from_global_id_or_error(id, type.User)
        if email:
            filter_kwargs["email"] = email
        if external_reference:
            filter_kwargs["external_reference"] = external_reference
        if requester.has_perms(
            [AccountPermissions.MANAGE_STAFF, AccountPermissions.MANAGE_USERS]
        ):
            return models.UserExtra.objects.filter(**filter_kwargs).first()
        if requester.has_perm(AccountPermissions.MANAGE_STAFF):
            return models.UserExtra.objects.staff().filter(**filter_kwargs).first()
        if has_one_of_permissions(
            requester, [AccountPermissions.MANAGE_USERS, OrderPermissions.MANAGE_ORDERS]
        ):
            rappresentante = info.context.user.extra if isUserExtra(info.context.user) and info.context.user.extra.is_rappresentante else None # type: ignore
            return models.UserExtra.objects.clienti(rappresentante).filter(**filter_kwargs).first()
    return PermissionDenied(
        permissions=[
            AccountPermissions.MANAGE_STAFF,
            AccountPermissions.MANAGE_USERS,
            OrderPermissions.MANAGE_ORDERS,
        ]
    )
    
    

@traced_resolver
def resolve_users_con_rappresentante(info, ids=None, emails=None):
    """
    copia con aggiunta di filtro per rappresentante della funzione
    'resolve_users' in saleor.graphql.account.resolvers.py
    """
    requester = get_user_or_app_from_context(info.context)
    if not requester:
        return models.UserExtra.objects.none()
    
    
    if requester.has_perms(
        [AccountPermissions.MANAGE_STAFF, AccountPermissions.MANAGE_USERS]
    ):
        qs = models.UserExtra.objects.all()
    elif requester.has_perm(AccountPermissions.MANAGE_STAFF):
        qs = models.UserExtra.objects.staff()
    elif requester.has_perm(AccountPermissions.MANAGE_USERS):
        # controllo se il richiedente è un rappresentante
        rappresentante = info.context.user.extra if isUserExtra(info.context.user) and info.context.user.extra.is_rappresentante else None # type: ignore
        qs = models.UserExtra.objects.clienti(rappresentante) # se non None, filtro i clienti legati al rappresentante
    elif requester.id:
        # If user has no access to all users, we can only return themselves, but
        # only if they are authenticated and one of requested users
        qs = models.User.objects.filter(id=requester.id)
    else:
        qs = models.User.objects.none()

    if ids:
        ids = {from_global_id_or_error(id, type.User, raise_error=True)[1] for id in ids}

    if ids and emails:
        return qs.filter(Q(id__in=ids) | Q(email__in=emails))
    elif ids:
        return qs.filter(id__in=ids)
    return qs.filter(email__in=emails)



def resolve_clienti_con_rappresentante(info):
    user = info.context.user
    # se l'utente è un rappresentate senza altri permessi, mostro solo i suoi clienti
    if user and isUserExtra(user) and user.extra.is_rappresentante:
        return user.clienti
    else:
        return models.UserExtra.objects.clienti()


def resolve_staff(_info):
    return models.UserExtra.objects.staff()

class ClientiFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = ClientiFilter

class AccountExtraQueries(graphene.ObjectType):
    utente = PermissionsField(
        type.UserExtra,
        id=graphene.Argument(graphene.ID, description="ID of the user."),
        email=graphene.Argument(
            graphene.String, description="Email address of the user."
        ),
        permissions=[
            AccountPermissions.MANAGE_STAFF,
            AccountPermissions.MANAGE_USERS,
            OrderPermissions.MANAGE_ORDERS,
        ],
        description="Look up a user by ID or email address.",
    )
    clienti = FilterConnectionField(
        type.UserExtraCountableConnection,
        description="Lista completa di utenti, in base a chi è loggato",
        filter=ClientiFilterInput(description="Filtering options for customers."),
        sort_by=UserExtraSortingInput(description="Sort customers."),
        permissions=[
            OrderPermissions.MANAGE_ORDERS,
            AccountPermissions.MANAGE_USERS,
        ],
    )
    
    staff_utenti = FilterConnectionField(
        type.UserExtraCountableConnection,
        # filter=StaffUserInput(description="Filtering options for staff users."),
        # sort_by=UserSortingInput(description="Sort staff users."),
        description="List of the shop's staff users.",
        permissions=[AccountPermissions.MANAGE_STAFF],
    )
    contatto = PermissionsField(
        type.Contatto,
        id=graphene.Argument(graphene.ID, description="ID del contatto."),
        description="Contatto singolo da ID",
        name = "contatto",
        permissions=[AccountPermissions.MANAGE_STAFF, AccountPermissions.MANAGE_USERS],
    )
    contatti_utente = FilterConnectionField(
        type.ContattoCountableConnection,
        id=graphene.Argument(graphene.ID, description="ID of the user."),
        description="lista dei contatti di un cliente da ID cliente",
        name = "contatti_utente",
        permissions=[AccountPermissions.MANAGE_STAFF, AccountPermissions.MANAGE_USERS],
    )
    # contatti = graphene.List(
    #     type.Contatto,
    #     description="lista dei contatti di un cliente",
    #     name = "contatti_utente",
    #     filter=ContattiFilterInput(description="Filtering options for contatti."),
    #     sort_by=ContattiSortingInput(description="Sort contatti."),
    #     permissions=[AccountPermissions.MANAGE_STAFF, AccountPermissions.MANAGE_USERS],
    # )
    aliquote_iva = graphene.List(
        type.Iva,
        description="lista delle aliquote iva disponibili",
        name = "aliquoteIva"
    )
    listini = PermissionsField(
        graphene.List(type.Listino),
        description="listini disponibili",
        name = "listini",
        permissions=[AccountPermissions.MANAGE_STAFF, AccountPermissions.MANAGE_USERS],
    )
    # gruppi = graphene.List(
    #     type.Gruppo,
    #     description="gruppi di permessi",
    #     name = "gruppi"
    # )
    
    @staticmethod
    def resolve_utente(
        _root, info: ResolveInfo, *, id=None, email=None, external_reference=None
    ):
        validate_one_of_args_is_in_query(
            "id", id, "email", email, "external_reference", external_reference
        )
        return resolve_user_con_rappresentante(info, id, email, external_reference)
    @staticmethod
    def resolve_clienti(_root, info: ResolveInfo, **kwargs):
        qs = resolve_clienti_con_rappresentante(info)
        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(qs, info, kwargs, type.UserExtraCountableConnection)
    @staticmethod
    def resolve_staff_utenti(_root, info: ResolveInfo, **kwargs):
        qs = resolve_staff(info)
        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(qs, info, kwargs, type.UserExtraCountableConnection)

    @staticmethod
    def resolve_contatto(
        _root, info: ResolveInfo, *, id=None
    ):
        validate_one_of_args_is_in_query(
            "id", id
        )
        requester = get_user_or_app_from_context(info.context)
        if requester:
            filter_kwargs = {}
            if id:
                _model, filter_kwargs["pk"] = from_global_id_or_error(id, type.Contatto)
            if has_one_of_permissions(requester,
                [AccountPermissions.MANAGE_STAFF, AccountPermissions.MANAGE_USERS, OrderPermissions.MANAGE_ORDERS]
            ):
                return models.Contatto.objects.filter(**filter_kwargs).first()
            # if requester.has_perm(AccountPermissions.MANAGE_STAFF):
            #     return models.User.objects.staff().filter(**filter_kwargs).first()
            # if has_one_of_permissions(
            #     requester, [AccountPermissions.MANAGE_USERS, OrderPermissions.MANAGE_ORDERS]
            # ):
            #     return models.User.objects.customers().filter(**filter_kwargs).first()
        return PermissionDenied(
            permissions=[
                AccountPermissions.MANAGE_STAFF,
                AccountPermissions.MANAGE_USERS,
                OrderPermissions.MANAGE_ORDERS,
            ]
        )
    @staticmethod
    def resolve_contatti(
        _root, info: ResolveInfo, *, id=None
    ):
        validate_one_of_args_is_in_query(
            "id", id
        )
        return #resolve_user_con_rappresentante(info, id, email, external_reference)
    @staff_member_or_app_required
    def resolve_aliquote_iva(self, info, **kwargs):
        return models.Iva.objects.all()
        
    @staff_member_or_app_required
    def resolve_listini(self, info, **kwargs):
        return models.Listino.objects.all()
    # @staff_member_or_app_required
    # def resolve_gruppi(self, info, **kwargs):
    #     return auth_models.Group.objects.all()

