import graphene
import pytest
from saleor.checkout.models import Checkout

from saleor.graphql.tests.utils import get_graphql_content, assert_no_permission

from saleor.plugins.grigoprint.preventivo.models import Preventivo, StatoPreventivo

PREVENTIVO_QUERY = """
    query Preventivo($id: ID!) {
        preventivo(id: $id) {
            id
            stato
            checkout{
                id
                user{
                    email
                }
            }
            number
            precedente{
                id
            }
        }
    }
"""

def test_query_preventivo(
    staff_api_client,
    user_api_client,
    checkout,
    permission_manage_checkouts,
):
    staff_api_client.user.user_permissions.add(
        permission_manage_checkouts
    )
    preventivo = Preventivo.objects.create(checkout=checkout, stato=StatoPreventivo.BOZZA)
    

    query = PREVENTIVO_QUERY
    # ricreo l'id di graphene per individuare il Preventivo in graphene
    ID = graphene.Node.to_global_id("Checkout", checkout.pk)
    variables = {"id": ID}
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


PREVENTIVI_QUERY = """
    query Preventivi {
        preventivi(first:10){
            edges{
                node{
                    id
                    stato
                    checkout{
                                id
                    }
                }
            }
        }
    }
"""
def test_query_preventivi(
        staff_api_client, 
        user_api_client, 
        customer_user,
        permission_manage_checkouts,
        channel_USD,
    ):
    staff_api_client.user.user_permissions.add(
        permission_manage_checkouts
    )
    query = PREVENTIVI_QUERY
    #creo gli utententi nel db
    checkout1 = Checkout.objects.create(email=customer_user.email, user=customer_user, channel=channel_USD)
    Preventivo.objects.create(checkout=checkout1)
    checkout2 = Checkout.objects.create(email=customer_user.email, user=customer_user, channel=channel_USD)
    Preventivo.objects.create(checkout=checkout2, stato=StatoPreventivo.BOZZA)
    checkout3 = Checkout.objects.create(email="checkout1@test.it", channel=channel_USD)
    Preventivo.objects.create(checkout=checkout3)
    
    # faccio la richiesta con graphql
    variables = {}
    response = staff_api_client.post_graphql(
        query, variables
    )
    content = get_graphql_content(response)
    data = content["data"]["preventivi"]["edges"]
    assert len(data) == 3

    # check permissions
    response = user_api_client.post_graphql(query, variables)
    assert_no_permission(response)

