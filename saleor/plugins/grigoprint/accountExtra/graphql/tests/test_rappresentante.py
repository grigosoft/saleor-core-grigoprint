import graphene
import pytest

from saleor.graphql.tests.utils import assert_no_permission, get_graphql_content
from saleor.permission.models import Permission
from saleor.plugins.grigoprint.accountExtra.models import UserExtra, User
from saleor.plugins.grigoprint.permissions import GrigoprintPermissions

# @pytest.fixture
# def permission_manage_rappresentanti():
#     return Permission.objects.get(codename="manage_rappresentanti")

# ------- QUERY

QUERY_CLIENTI = """
    {
        clienti(first: 20) {
            edges {
                node {
                    email
                    user{
                        isStaff
                    }
                    rappresentante{
                        email
                    }
                }
            }
        }
    }
    """
def test_query_clienti_rappresentante(
    staff_api_client,
    user_api_client,
    permission_manage_users,
    staff_user
):
    query = QUERY_CLIENTI
    staff_api_client.user.user_permissions.add(
        permission_manage_users
    )
    # creo rappresentante
    rappresentante = UserExtra.objects.create(user=staff_user, is_rappresentante = True)
    # il test senza utenti non funziona, da 0 clienti, 'staff_user' non è a database?
    
    # creo gli utententi nel db
    staff1 = User.objects.create(email="staff1@test.it", is_staff=True)
    UserExtra.objects.create(user=staff1)
    user1 = User.objects.create(email="user1@test.it", is_staff=False)
    UserExtra.objects.create(user=user1)
    user2 = User.objects.create(email="user2@test.it", is_staff=False)
    UserExtra.objects.create(user=user2, rappresentante=staff_user)
    user3 = User.objects.create(email="user3@test.it", is_staff=False)
    UserExtra.objects.create(user=user3, rappresentante=staff_user)
    
    # faccio la richiesta con graphql: da un rappresentante
    response = staff_api_client.post_graphql(
        query, {}
    )
    content = get_graphql_content(response)
    data = content["data"]["clienti"]["edges"]
    assert len(data) == 2
    assert all([not user["node"]["user"]["isStaff"] for user in data])
    assert all([user["node"]["rappresentante"]["email"] == rappresentante.user.email for user in data])
    # faccio la richiesta con graphql: da un amministratore, NON rappresentante
    rappresentante.is_rappresentante = False
    rappresentante.save()
    response = staff_api_client.post_graphql(
        query, {}
    )
    content = get_graphql_content(response)
    data = content["data"]["clienti"]["edges"]
    assert len(data) == 3
    assert all([not user["node"]["user"]["isStaff"] for user in data])
    
    # check permissions
    response = user_api_client.post_graphql(query, {})
    assert_no_permission(response)


# ------- MUTATIONS
MUTATION_CREA_CLIENTE = """
    mutation clienteCrea (
        $email:String!,
        $denominazione:String!,
        $rappresentanteId:ID,
        $piva:String
        
    ){
        clienteCrea(
        input:{
            email:$email,
            extra:{
                denominazione:$denominazione,
                rappresentanteId:$rappresentanteId,
                piva:$piva
            }
        }){
            errors{
                field
                message
            }
            user{
                id
                email
                isStaff
            }
            userExtra{
                id
                email
                denominazione
                rappresentante{
                    id
                    email
                }
            }
        }
    }
"""
MUTATION_AGGIORNA_CLIENTE = """
    mutation clienteAggiorna (
        $id:ID!
        $denominazione:String!,
        $rappresentanteId:ID
        
    ){
        clienteAggiorna(
        id:$id
        input:{
            extra:{
                denominazione:$denominazione,
                rappresentanteId:$rappresentanteId
            }
        }){
            errors{
                field
                message
            }
            user{
                id
                email
                isStaff
            }
            userExtra{
                id
                email
                denominazione
                rappresentante{
                    id
                    email
                }
            }
        }
    }
"""
def test_mutantion_crea_cliente_rappresentante(
    staff_api_client,
    user_api_client,
    staff_user,
    permission_manage_users,
    # permission_manage_rappresentanti
):
    staff_api_client.user.user_permissions.add(
        permission_manage_users
    )
    # CREATE -------

    # creo rappresentanti
    requester = UserExtra.objects.create(user=staff_user, is_rappresentante=True, denominazione="nome requester")
    requester_id = graphene.Node.to_global_id("User", requester.user.pk)
    staff_user_2 = User.objects.create(email = "rappresentante.2@test.it")
    rappresentante_2 = UserExtra.objects.create(user=staff_user_2, is_rappresentante=True, denominazione="nome rappresentante")
    rappresentante_id_2 = graphene.Node.to_global_id("User", rappresentante_2.user.pk)
    # test creazione cliente: creo assegnando me stesso rappresentante, 
    # io sono rappresentante
    print("creo assegnando me stesso rappresentante, io sono rappresentante")
    variables = {
                    "email":"utente.crea.1@test.it",
                    "denominazione":"den test 1",
                    "rappresentanteId":requester_id
                }
    response = staff_api_client.post_graphql(MUTATION_CREA_CLIENTE, variables)
    content = get_graphql_content(response)
    print("\t", content["data"]["clienteCrea"])
    data = content["data"]["clienteCrea"]["userExtra"]
    assert content["data"]["clienteCrea"]["errors"] == []
    assert data["rappresentante"]["email"] == staff_user.email

    # test creazione cliente: creo assegnando me stesso rappresentante, 
    # io NON sono rappresentante
    print("creo assegnando me stesso rappresentante, io NON sono rappresentante")
    requester.is_rappresentante = False
    requester.save(update_fields = ["is_rappresentante"])
    variables = {
                    "email":"utente.crea.2@test.it",
                    "denominazione":"den test 2",
                    "rappresentanteId":requester_id
                }
    response = staff_api_client.post_graphql(MUTATION_CREA_CLIENTE, variables)
    content = get_graphql_content(response)
    print("\t", content["data"]["clienteCrea"])
    data = content["data"]["clienteCrea"]["errors"]
    assert len(data) >= 1
    assert data[0]["field"] == "user"

    # test creazione cliente: creo assegnando un altro rappresentante, 
    # io sono rappresentante
    print("creo assegnando un altro rappresentante, io sono rappresentante")
    requester.is_rappresentante = True
    requester.save()
    variables = {
                    "email":"utente.crea.3@test.it",
                    "denominazione":"den test 3",
                    "rappresentanteId":rappresentante_id_2
                }
    response = staff_api_client.post_graphql(MUTATION_CREA_CLIENTE, variables)
    content = get_graphql_content(response)
    print("\t", content["data"]["clienteCrea"])
    data = content["data"]["clienteCrea"]["errors"]
    assert len(data) >= 1
    assert data[0]["field"] == "user"

    # test creazione cliente: creo assegnando un altro rappresentante, 
    # io NON sono rappresentante
    print("creo assegnando un altro rappresentante, io NON sono rappresentante")
    requester.is_rappresentante = False
    requester.save()
    variables = {
                    "email":"utente.crea.4@test.it",
                    "denominazione":"den test 4",
                    "rappresentanteId":rappresentante_id_2
                }
    response = staff_api_client.post_graphql(MUTATION_CREA_CLIENTE, variables)
    content = get_graphql_content(response)
    print("\t", content["data"]["clienteCrea"])
    data = content["data"]["clienteCrea"]["errors"]
    assert len(data) >= 1
    assert data[0]["field"] == "user"

    # test creazione cliente:
    print("creo assegnando un altro rappresentante, io NON sono rappresentante ma ho i permessi")
    requester.is_rappresentante = False
    requester.save()
    staff_api_client.user.user_permissions.add(
        Permission.objects.get(codename="manage_rappresentanti")
    )
    variables = {
                    "email":"utente.crea.4@test.it",
                    "denominazione":"den test 4",
                    "rappresentanteId":rappresentante_id_2
                }
    response = staff_api_client.post_graphql(MUTATION_CREA_CLIENTE, variables)
    content = get_graphql_content(response)
    print("\t", content["data"]["clienteCrea"])
    data = content["data"]["clienteCrea"]["userExtra"]
    assert content["data"]["clienteCrea"]["errors"] == []
    assert data["rappresentante"]["email"] == staff_user_2.email

    # check permissions
    response = user_api_client.post_graphql(MUTATION_CREA_CLIENTE, variables)
    assert_no_permission(response)
