import graphene
import pytest

from saleor.graphql.tests.utils import get_graphql_content, assert_no_permission

from saleor.plugins.grigoprint.preventivo.models import Preventivo, StatoPreventivo

PREVENTIVO_QUERY = """
    query Preventivo($id: ID!) {
        preventivo(id: $id) {
            id
            checkout
            number
            precedente
        }
    }
"""

def test_query_utente_full(
    staff_api_client,
    user_api_client,
    checkout,
    permission_manage_checkouts,
):
    preventivo = Preventivo.objects.create(checkout=checkout, stato=StatoPreventivo.BOZZA)
    

    query = PREVENTIVO_QUERY
    # ricreo l'id di graphene per individuare l'untente in graphene
    ID = graphene.Node.to_global_id("Preventivo", preventivo.pk)
    variables = {"id": ID}
    staff_api_client.user.user_permissions.add(
        permission_manage_checkouts
    )
    response = staff_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    data = content["data"]["preventivo"]
    assert data["id"] == ID
    assert data["stato"] == preventivo.stato
    # assert len(data["contatti"]) == user.extra.contatti.count()
    # for contatto in data["contatti"]:
    #     contatto_id =  contatto["id"]

    # no access for normal user
    response_user = user_api_client.post_graphql(PREVENTIVO_QUERY, variables)
    assert_no_permission(response_user)