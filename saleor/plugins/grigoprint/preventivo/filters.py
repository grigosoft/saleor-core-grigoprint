import django_filters
import graphene

from django.db.models import Count

from django.db.models import Q, Exists, OuterRef

from saleor.graphql.core.descriptions import ADDED_IN_38
from saleor.graphql.core.filters import (
    EnumFilter,
    GlobalIDMultipleChoiceFilter,
    ListObjectTypeFilter,
    MetadataFilterBase,
    ObjectTypeFilter,
)
from saleor.graphql.core.types import DateRangeInput, DateTimeRangeInput, IntRangeInput, FilterInputObjectType
from saleor.graphql.utils.filters import filter_range_field
from saleor.plugins.grigoprint.accountExtra.models import UserExtra
from saleor.plugins.grigoprint.preventivo.graphql.type import StatoPreventivoEnum
from saleor.plugins.grigoprint.preventivo.models import Preventivo

def filter_user_id(qs, _, value):
    if value:
        qs = qs.filter(checkout__user_id=value)
    return qs
def filter_rappresentante_id(qs, _, value):
    if value:
        qs = qs.filter(checkout__user__extra__rappresentante_id=value)
    return qs

def filter_cliente(qs, _, value):
    users = UserExtra.objects.filter(
        Q(email__ilike=value) | Q(denominazione__ilike=value)
    ).values("pk")

    return qs.filter(Q(Exists(users.filter(id=OuterRef("checkout__user__extra__id")))))

def filter_preventivo_status(qs, _, value):
    if value:
        qs = qs.filter(status__in=value)
    return qs

def search_users(qs, value):
    if value:
        lookup = Q()
        for val in value.split():
            lookup &= Q(user__search_document__ilike=val.lower())
        qs = qs.filter(lookup)
    return qs

def filter_preventivo_search(qs, _, value):
    raise NotImplementedError("non ancora implementato") # TODO
    return search_users(qs, value)

def filter_boolean_field(qs, field, value):
    if field and value:
        lookup = {f"{field}": value}
        qs = qs.filter(**lookup)
    return qs

def filter_is_checkout(qs, _, value):
    return filter_boolean_field(qs, "is_checkout", value)



class PreventivoFilter(MetadataFilterBase):
    user_id = django_filters.CharFilter(method=filter_user_id)
    rappresentante_id = django_filters.CharFilter(method=filter_rappresentante_id)

    stato = ListObjectTypeFilter(
        input_class=StatoPreventivoEnum, method=filter_preventivo_status
    )
    cliente = django_filters.CharFilter(method=filter_cliente)
    is_checkout = ObjectTypeFilter(
        input_class=graphene.Boolean, method=filter_is_checkout
    )
    search = django_filters.CharFilter(method=filter_preventivo_search)

    class Meta:
        model = Preventivo
        fields = [
            "user_id",
            "rappresentante_id",
            # "stato",
            "cliente",
            "search",
        ]
    
class PreventivoFilterInput(FilterInputObjectType):
    class Meta:
        # doc_category = DOC_CATEGORY_CHECKOUT
        filterset_class = PreventivoFilter