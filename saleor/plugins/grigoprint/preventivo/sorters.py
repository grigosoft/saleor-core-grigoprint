import graphene
from django.db.models import CharField, ExpressionWrapper, OuterRef, QuerySet, Subquery

from saleor.graphql.core.types.sort_input import SortInputObjectType
from saleor.payment.models import Payment


class PreventivoSortField(graphene.Enum):
    STATO = ["stato", "email","pk"]
    EMAIL = ["email", "pk"]
    CREATION_DATE = ["checkout__created_at", "pk"]
    CUSTOMER = ["billing_address__last_name", "billing_address__first_name", "pk"]
    PAYMENT = ["last_charge_status", "pk"]

    @property
    def description(self):
        if self.name in PreventivoSortField.__enum__._member_names_:
            sort_name = self.name.lower().replace("_", " ")
            return f"Sort users by {sort_name}."
        raise ValueError("Unsupported enum value: %s" % self.value)

    @staticmethod
    def qs_with_payment(queryset: QuerySet, **_kwargs) -> QuerySet:
        subquery = Subquery(
            Payment.objects.filter(checkout_id=OuterRef("checkout__pk"))
            .order_by("-pk")
            .values_list("charge_status")[:1]
        )
        return queryset.annotate(
            last_charge_status=ExpressionWrapper(subquery, output_field=CharField())
        )

class PreventivoSortingInput(SortInputObjectType):
    class Meta:
        sort_enum = PreventivoSortField
        type_name = "Preventivo"