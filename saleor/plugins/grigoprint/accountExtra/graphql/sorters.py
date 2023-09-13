import graphene
from django.db.models import Count, QuerySet, Value

from .....graphql.core.types.sort_input import SortInputObjectType


class UserExtraSortField(graphene.Enum):
    DENOMINAZIONE = ["denominazione", "pk"]
    RAPPRESENTANTE = ["rappresentante", "denominazione", "pk"]
    LISTINO = ["listino", "denominazione", "pk"]
    SCONTO = ["sconto", "denominazione", "pk"] #?
    EMAIL = ["user__email"]
    ORDER_COUNT = ["order_count", "email"]
    PROVINCIA = ["user__default_billing_address__city_area","user__default_billing_address__city","denominazione","pk"]

    @property
    def description(self):
        if self.name in UserExtraSortField.__enum__._member_names_:
            sort_name = self.name.lower().replace("_", " ")
            return f"Sort users by {sort_name}."
        raise ValueError("Unsupported enum value: %s" % self.value)

    @staticmethod
    def qs_with_order_count(queryset: QuerySet, **_kwargs) -> QuerySet:
        return queryset.annotate(order_count=Count("user__orders__id"))

class ClientiSortingInput(SortInputObjectType):
    class Meta:
        sort_enum = UserExtraSortField
        type_name = "usersExtra"

class StaffSortingInput(SortInputObjectType):
    class Meta:
        sort_enum = UserExtraSortField
        type_name = "usersExtra"