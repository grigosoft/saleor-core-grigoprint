import graphene
import pytest

from django.core.files import File

from saleor.graphql.tests.utils import (
    assert_graphql_error_with_message,
    assert_no_permission,
    get_graphql_content,
    get_graphql_content_from_response,
    get_multipart_request_body,
)
from saleor.permission.enums import AccountPermissions

from saleor.plugins.grigoprint.accountExtra.models import Iva, Listino

def assert_id_uguale_pk(id: str, pk: str):
    type, pk_id = graphene.Node.from_global_id(id)


ALIQUOTE_IVA_QUERY = """
    query aliquoteIva {
        aliquoteIva {
            id
            nome
            valore
            info
        }
    }
"""
ALIQUOTA_IVA_QUERY = """
    query aliquotaIva {
        aliquotaIva {
            id
            nome
            valore
            info
        }
    }
"""
LISTINI_QUERY = """
    query Listini {
        listini {
            id
            nome
            ricarico
            info
        }
    }
"""
LISTINO_QUERY = """
    query Listino {
        listino {
            id
            nome
            ricarico
            info
        }
    }
"""

def test_query_aliquote_iva(
        staff_api_client,
        permission_manage_users,
        permission_manage_staff
    ):
    # assert Iva.objects.all() is []

    iva = Iva.objects.create(
        nome = "22%",
        valore = 0.22,
        info = "info bla bla"
    )
    query = ALIQUOTE_IVA_QUERY
    
    staff_api_client.user.user_permissions.add(
        permission_manage_users, permission_manage_staff
    )
    response = staff_api_client.post_graphql(query)
    content = get_graphql_content(response)
    data = content["data"]["aliquoteIva"][0]
    # TODO serve un id ad andrea? aggiungere graphene.Node
    assert_id_uguale_pk(data["id"],iva.pk)
    assert data["nome"] == iva.nome
    assert data["valore"] == iva.valore
    assert data["info"] == iva.info
    
def test_query_listini(
        staff_api_client,
        permission_manage_users,
        permission_manage_orders
    ):

    listino = Listino.objects.create(
        nome = "pubblico",
        ricarico = 20,
        info = "listino pubblico"
    )
    query = LISTINI_QUERY
    
    staff_api_client.user.user_permissions.add(
        permission_manage_users, permission_manage_orders
    )
    response = staff_api_client.post_graphql(query)
    content = get_graphql_content(response)
    data = content["data"]["listini"][0]
    # TODO serve un id ad andrea? aggiungere graphene.Node
    assert_id_uguale_pk(data["id"],listino.pk)
    assert data["nome"] == listino.nome
    assert data["ricarico"] == listino.ricarico
    assert data["info"] == listino.info

# ------------------------------------------ MUTAZIONI
MUTATION_CREA_IVA = """
    mutation ivaCrea (
        $nome:String!,
        $valore:Float!,
        $info:String
    ){
        ivaCrea(
            input:{
                nome:$nome,
                valore:$valore,
                info:$info,
            }
        ){
            errors{
                field
                message
            }
            iva{
                id
                nome
                valore
                info
            }
        }
    }
"""
MUTATION_AGGIORNA_IVA = """
    mutation ivaAggiorna (
        $id:ID!,
        $nome:String,
        $valore:Float,
        $info:String
    ){
        ivaAggiorna(
            id:$id,
            input:{
                nome:$nome,
                valore:$valore,
                info:$info,
            }
        ){
            errors{
                field
                message
            }
            iva{
                id
                nome
                valore
                info
            }
        }
    }
"""
MUTATION_CANCELLA_IVA = """
    mutation ivaCancella (
        $id:ID!
    ){
        ivaCancella(
            id:$id
        ){
            errors{
                field
                message
            }
            iva{
                id
                nome
                valore
                info
            }
        }
    }
"""
def test_mutations_iva(
    staff_api_client,
    user_api_client,
    customer_user,
    permission_manage_users
):
    staff_api_client.user.user_permissions.add(
        permission_manage_users
    )
    # CREATE -------
    variables = {"nome":"22%",
                 "valore":0.22,
                 "telefono":"iva standard"
                 }
    response = staff_api_client.post_graphql(MUTATION_CREA_IVA, variables)
    content = get_graphql_content(response)
    data = content["data"]["ivaCrea"]["iva"]
    id_created = data["id"]
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    aliquoteIva = Iva.objects.filter(nome = variables["nome"])
    assert len(aliquoteIva) == 1
    aliquotaIva = aliquoteIva.first()
    assert aliquotaIva is not None
    assert_id_uguale_pk(id_created,aliquotaIva.pk)
    assert data["nome"] == aliquotaIva.nome
    assert data["valore"] == aliquotaIva.valore
    assert data["info"] == aliquotaIva.info
    # no access for normal user
    response_user = user_api_client.post_graphql(MUTATION_CREA_IVA, variables)
    assert_no_permission(response_user)
    # UPDATE -----
    variables = {"id":id_created,
                 "nome":"24%",
                 "valore":0.24,
                 "info":"speriamo di no"
                 }
    response = staff_api_client.post_graphql(MUTATION_AGGIORNA_IVA, variables)
    content = get_graphql_content(response)
    data = content["data"]["ivaAggiorna"]["iva"]
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    aliquoteIva = Iva.objects.filter(nome = variables["nome"])
    assert len(aliquoteIva) == 1
    aliquotaIva = aliquoteIva.first()
    assert aliquotaIva is not None
    assert data["nome"] == aliquotaIva.nome
    assert data["valore"] == aliquotaIva.valore
    assert data["info"] == aliquotaIva.info
     # no access for normal user
    response_user = user_api_client.post_graphql(MUTATION_AGGIORNA_IVA, variables)
    assert_no_permission(response_user)
    # DELETE -----
    variables = {"id": id_created}
    response = staff_api_client.post_graphql(MUTATION_CANCELLA_IVA, variables)
    content = get_graphql_content(response)
    data = content["data"]["ivaCancella"]["iva"]
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    aliquoteIva = Iva.objects.filter(nome = aliquotaIva.nome)
    assert len(aliquoteIva) == 0 
    # no access for normal user
    response_user = user_api_client.post_graphql(MUTATION_CANCELLA_IVA, variables)
    assert_no_permission(response_user)


MUTATION_CREA_LISTINO = """
    mutation listinoCrea (
        $nome:String!,
        $ricarico:Float!,
        $info:String
    ){
        listinoCrea(
            input:{
                nome:$nome,
                ricarico:$ricarico,
                info:$info,
            }
        ){
            errors{
                field
                message
            }
            listino{
                id
                nome
                ricarico
                info
            }
        }
    }
"""
MUTATION_AGGIORNA_LISTINO = """
    mutation listinoAggiorna (
        $id:ID!,
        $nome:String,
        $ricarico:Float,
        $info:String
    ){
        listinoAggiorna(
            id:$id,
            input:{
                nome:$nome,
                ricarico:$ricarico,
                info:$info,
            }
        ){
            errors{
                field
                message
            }
            listino{
                id
                nome
                ricarico
                info
            }
        }
    }
"""
MUTATION_CANCELLA_LISTINO = """
    mutation listinoCancella (
        $id:ID!
    ){
        listinoCancella(
            id:$id
        ){
            errors{
                field
                message
            }
            listino{
                id
                nome
                ricarico
                info
            }
        }
    }
"""
def test_mutations_listino(
    staff_api_client,
    user_api_client,
    customer_user,
    permission_manage_users
):
    staff_api_client.user.user_permissions.add(
        permission_manage_users
    )
    # CREATE -------
    variables = {"nome":"pubblico",
                 "ricarico":0.34,
                 "telefono":"cliente finale"
                 }
    response = staff_api_client.post_graphql(MUTATION_CREA_LISTINO, variables)
    content = get_graphql_content(response)
    data = content["data"]["listinoCrea"]["listino"]
    id_created = data["id"]
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    listini = Listino.objects.filter(nome = variables["nome"])
    assert len(listini) == 1
    listino = listini.first()
    assert listino is not None
    assert_id_uguale_pk(id_created,listino.pk)
    assert data["nome"] == listino.nome
    assert data["ricarico"] == listino.ricarico
    assert data["info"] == listino.info
    # no access for normal user
    response_user = user_api_client.post_graphql(MUTATION_CREA_LISTINO, variables)
    assert_no_permission(response_user)
    # UPDATE -----
    variables = {"id":id_created,
                 "nome":"agenzia",
                 "ricarico":0.12,
                 "info":"rivenditori"
                 }
    response = staff_api_client.post_graphql(MUTATION_AGGIORNA_LISTINO, variables)
    content = get_graphql_content(response)
    data = content["data"]["listinoAggiorna"]["listino"]
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    listini = Listino.objects.filter(nome = variables["nome"])
    assert len(listini) == 1
    listino = listini.first()
    assert listino is not None
    assert data["nome"] == listino.nome
    assert data["ricarico"] == listino.ricarico
    assert data["info"] == listino.info
     # no access for normal user
    response_user = user_api_client.post_graphql(MUTATION_AGGIORNA_LISTINO, variables)
    assert_no_permission(response_user)
    # DELETE -----
    variables = {"id": id_created}
    response = staff_api_client.post_graphql(MUTATION_CANCELLA_LISTINO, variables)
    content = get_graphql_content(response)
    data = content["data"]["listinoCancella"]["listino"]
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    listini = Listino.objects.filter(nome = listino.nome)
    assert len(listini) == 0 
    # no access for normal user
    response_user = user_api_client.post_graphql(MUTATION_CANCELLA_LISTINO, variables)
    assert_no_permission(response_user)