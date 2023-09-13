import graphene

from saleor.graphql.tests.utils import assert_no_permission, get_graphql_content
from saleor.plugins.grigoprint.accountExtra.models import UserExtra
from saleor.plugins.grigoprint.preventivo.models import Preventivo, StatoPreventivo


MUTATION_AGGIUNGI_PREVENTIVO_LINE = """
    mutation preventivoLineaAggiungi (
        $id:ID!,
        $prezzo_netto_forzato:PositiveDecimal,
        $descrizione_forzata:String,
        $quantity:Int!,
        $variant_id:ID!
    ){
        preventivoLineaAggiungi(
        id:$id
        linea:{
            quantity:$quantity
            variantId:$variant_id
            extra:{
                prezzoNettoForzato:$prezzo_netto_forzato
                descrizioneForzata:$descrizione_forzata
            }
            
        }
        
        ){
            errors{
                field
                message
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
                linee{
                    id
                    checkoutLine{
                        variant{
                            id
                        }
                        quantity
                    }
                }
            }
        }
    }
"""
MUTATION_CANCELLA_PREVENTIVO_LINEA = """
    mutation preventivoLineaCancella (
        $id:ID!,
        $line_id:ID!,
    ){
        preventivoLineaCancella(
            id:$id
            lineId:$line_id
        ){
            errors{
                field
                message
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
                linee{
                    id
                    checkoutLine{
                        variant{
                            id
                        }
                        quantity
                    }
                }
            }
        }
    }
"""
def test_mutations_preventivo_linea(
    staff_api_client,
    user_api_client,
    staff_user,
    customer_user,
    permission_manage_checkouts,
    permission_manage_users,
    channel_USD,
    checkout,
    product,
):
    staff_api_client.user.user_permissions.add(
        permission_manage_checkouts,
        permission_manage_users
    )
    # CREATE -------
    # creo rappresentante



    UserExtra.objects.create(user=customer_user)
    preventivo = Preventivo.objects.create(checkout=checkout, stato=StatoPreventivo.BOZZA)
    preventivo_id = graphene.Node.to_global_id("Checkout", preventivo.checkout.pk)
    variant_id = graphene.Node.to_global_id("ProductVariant",  product.variants.first().pk)
    variables = {
                    "id":preventivo_id,
                    "quantity":2,
                    "variant_id":variant_id
    }
    response = staff_api_client.post_graphql(MUTATION_AGGIUNGI_PREVENTIVO_LINE, variables)
    content = get_graphql_content(response)
    data = content["data"]["preventivoLineaAggiungi"]["preventivo"]
    assert content["data"]["preventivoLineaAggiungi"]["errors"] == []
    #controllo  i dati restituiti dalla mutazione con quelli delle variabili inserite
    assert len(data["linee"]) == 1
    assert data["linee"][0]["checkoutLine"]["variant"]["id"] == variant_id
    
    # no access for normal user
    # response_user = user_api_client.post_graphql(MUTATION_AGGIUNGI_PREVENTIVO_LINE, variables)
    # assert_no_permission(response_user)
    

    #DELETE
    # mi assicuro che funziona la delete originale di saleor
    assert len(checkout.lines.all()) > 0
    line_id = graphene.Node.to_global_id("CheckoutLine", checkout.lines.first().pk)
    variables = {"id": preventivo_id,
                 "line_id":line_id}
    response = staff_api_client.post_graphql(MUTATION_CANCELLA_PREVENTIVO_LINEA, variables)
    content = get_graphql_content(response)
    data = content["data"]["preventivoLineaCancella"]
    assert data["errors"] == []
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    assert len(checkout.lines.all()) == 0 # type: ignore
    assert len(data["preventivo"]["linee"]) == 0
    # no access for normal user
    # response_user = user_api_client.post_graphql(MUTATION_CANCELLA_PREVENTIVO_LINEA, variables)
    # assert_no_permission(response_user)