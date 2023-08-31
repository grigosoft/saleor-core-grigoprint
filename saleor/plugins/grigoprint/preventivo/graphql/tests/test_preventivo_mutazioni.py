import graphene

from saleor.graphql.tests.utils import assert_no_permission, get_graphql_content
from saleor.plugins.grigoprint.accountExtra.models import UserExtra
from saleor.plugins.grigoprint.preventivo.models import Preventivo, StatoPreventivo


MUTATION_CREA_PREVENTIVO = """
    mutation preventivoCrea (
        $email:String,
        $channel:String!,
        $stato:StatoPreventivoEnum,
        $user_id:ID!,
        $precedente_id:ID
    ){
        preventivoCrea(
        input:{
            email:$email
            channel:$channel
            extra:{
                stato:$stato
                user:$user_id
                precedente:$precedente_id
            }
        }){
            errors{
                field
                message
            }
            checkout{
                id
                email
                user{
                    id
                    email
                }
            }
            preventivo{
                id
                stato
                checkout{
                    id
                    email
                    user{
                        id
                        email
                    }
                }
            }
        }
    }
"""
MUTATION_CANCELLA_PREVENTIVO = """
    mutation preventivoCancella (
        $id:ID!,
    ){
        preventivoCancella(
            id:$id
        ){
            errors{
                field
                message
            }
            checkout{
                email
                user{
                    id
                    email
                }
            }
        }
    }
"""
def test_mutations_preventivo(
    staff_api_client,
    user_api_client,
    staff_user,
    customer_user,
    permission_manage_checkouts,
    permission_manage_users,
    channel_USD
):
    staff_api_client.user.user_permissions.add(
        permission_manage_checkouts,
        permission_manage_users
    )
    # CREATE -------
    email = "preventivo.crea@test.it"
    UserExtra.objects.create(user=customer_user)
    # creo rappresentante
    user_id = graphene.Node.to_global_id("User", customer_user.pk)
    variables = {
                    "user_id":user_id,
                    "channel":channel_USD.slug,
                    "stato":StatoPreventivo.BOZZA
    }
    response = staff_api_client.post_graphql(MUTATION_CREA_PREVENTIVO, variables)
    content = get_graphql_content(response)
    data = content["data"]["preventivoCrea"]["preventivo"]
    assert content["data"]["preventivoCrea"]["errors"] == []
    #controllo  i dati restituiti dalla mutazione con quelli delle variabili inserite
    checkout_id = data["id"]
    assert data["checkout"]["email"] == customer_user.email
    assert data["checkout"]["user"]["email"] == customer_user.email
    assert data["stato"] == variables["stato"]
    
    # no access for normal user
    response_user = user_api_client.post_graphql(MUTATION_CREA_PREVENTIVO, variables)
    assert_no_permission(response_user)
    

    #DELETE
    # mi assicuro che funziona la delete originale di saleor
    variables = {"id": checkout_id}
    response = staff_api_client.post_graphql(MUTATION_CANCELLA_PREVENTIVO, variables)
    content = get_graphql_content(response)
    data = content["data"]["preventivoCancella"]
    assert data["errors"] == []
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    users = Preventivo.objects.filter(checkout__user__email = email)
    assert len(users) == 0