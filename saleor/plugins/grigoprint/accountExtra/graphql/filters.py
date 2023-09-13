import django_filters
import graphene

from django.db.models import Count

from django.db.models import Q

from saleor.account.models import User
from saleor.graphql.core.descriptions import ADDED_IN_38
from saleor.graphql.core.filters import (
    EnumFilter,
    GlobalIDMultipleChoiceFilter,
    MetadataFilterBase,
    ObjectTypeFilter,
)
from saleor.graphql.core.types import DateRangeInput, DateTimeRangeInput, IntRangeInput
from saleor.graphql.core.types.filter_input import FilterInputObjectType
from saleor.graphql.utils.filters import filter_range_field


def filter_date_joined(qs, _, value):
    return filter_range_field(qs, "user__date_joined__date", value)


def filter_updated_at(qs, _, value):
    return filter_range_field(qs, "updated_at", value)


def filter_number_of_orders(qs, _, value):
    qs = qs.annotate(total_orders=Count("user__orders"))
    return filter_range_field(qs, "total_orders", value)


def filter_placed_orders(qs, _, value):
    return filter_range_field(qs, "user__orders__created_at__date", value)

def search_users(qs, value):
    if value:
        lookup = Q()
        for val in value.split():
            lookup &= Q(user__search_document__ilike=val.lower())
        qs = qs.filter(lookup)
    return qs

def filter_user_search(qs, _, value):
    return search_users(qs, value)

def filter_boolean_field(qs, field, value):
    if field and value:
        lookup = {f"{field}": value}
        qs = qs.filter(**lookup)
    return qs

def filter_is_rappresentante(qs, _, value):
    return filter_boolean_field(qs, "is_rappresentante", value)



class ClientiFilter(MetadataFilterBase):
    ids = GlobalIDMultipleChoiceFilter(
        field_name="id", help_text=f"Filter by ids. {ADDED_IN_38}"
    )
    date_joined = ObjectTypeFilter(
        input_class=DateRangeInput, method=filter_date_joined
    )
    updated_at = ObjectTypeFilter(
        input_class=DateTimeRangeInput, method=filter_updated_at
    )
    number_of_orders = ObjectTypeFilter(
        input_class=IntRangeInput, method=filter_number_of_orders
    )
    placed_orders = ObjectTypeFilter(
        input_class=DateRangeInput, method=filter_placed_orders
    )
    is_rappresentante = ObjectTypeFilter(
        input_class=graphene.Boolean, method=filter_is_rappresentante
    )
    search = django_filters.CharFilter(method=filter_user_search)

    class Meta:
        model = User
        fields = [
            "date_joined",
            "number_of_orders",
            "placed_orders",
            "is_rappresentante",
            "search",
        ]

    
class ClientiFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = ClientiFilter

class StaffFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = ClientiFilter