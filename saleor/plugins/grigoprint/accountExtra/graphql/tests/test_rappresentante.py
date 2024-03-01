import graphene
import pytest

from saleor.graphql.tests.utils import assert_no_permission, get_graphql_content
from saleor.permission.models import Permission
from saleor.plugins.grigoprint.accountExtra.enum import TipoContatto
from saleor.plugins.grigoprint.accountExtra.graphql.tests.test_staff import MUTATION_AGGIORNA_CONTATTO, MUTATION_CANCELLA_CONTATTO, MUTATION_CREA_CONTATTO, CONTATTO_QUERY
from saleor.plugins.grigoprint.accountExtra.models import Contatto, UserExtra, User
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
        QUERY_CLIENTI, {}
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
        QUERY_CLIENTI, {}
    )
    content = get_graphql_content(response)
    data = content["data"]["clienti"]["edges"]
    assert len(data) == 3
    assert all([not user["node"]["user"]["isStaff"] for user in data])
    
    # check permissions
    response = user_api_client.post_graphql(QUERY_CLIENTI, {})
    assert_no_permission(response)

def test_query_contatto_rappresentante(
    staff_api_client,
    user_api_client,
    permission_manage_users,
    staff_user
):
    staff_api_client.user.user_permissions.add(
        permission_manage_users
    )
    # creo rappresentante
    rappresentante = UserExtra.objects.create(user=staff_user,is_rappresentante = True)
    
    # creo gli utententi nel db
    staff1 = User.objects.create(email="staff1@test.it", is_staff=True)
    staff1_extra = UserExtra.objects.create(user=staff1, is_rappresentante=True)
    user1 = User.objects.create(email="user1@test.it", is_staff=False)
    user1_extra = UserExtra.objects.create(user=user1)
    user2 = User.objects.create(email="user2@test.it", is_staff=False)
    user2_extra = UserExtra.objects.create(user=user2, rappresentante=staff_user)
    user3 = User.objects.create(email="user3@test.it", is_staff=False)
    user3_extra = UserExtra.objects.create(user=user3, rappresentante=staff1)
    # creo i contatti
    contatto1 = Contatto.objects.create(
        user_extra = user1_extra,
        denominazione = "contatto senza rappresentante",
        telefono = "3473462414",
        uso = TipoContatto.FATTURAZIONE,
        email = "grig.griganto@gmail.com"
    )
    contatto2 = Contatto.objects.create(
        user_extra = user2_extra,
        denominazione = "contatto di cliente staff_user",
        telefono = "3518882958",
        uso = TipoContatto.CONSEGNA,
        email = "griganto.games@gmail.com"
    )

    contatto3 = Contatto.objects.create(
        user_extra = user3_extra,
        denominazione = "contatto di cliente staff1",
        telefono = "3518882958",
        uso = TipoContatto.CONSEGNA,
        email = "griganto.games@gmail.com"
    )
    contatto1_id = graphene.Node.to_global_id("Contatto", contatto1.pk)
    contatto2_id = graphene.Node.to_global_id("Contatto", contatto2.pk)
    contatto3_id = graphene.Node.to_global_id("Contatto", contatto3.pk)
    
    # faccio la richiesta con graphql: da un rappresentante verso un cliente senza rappresentante
    var= {"id":contatto1_id}
    response = staff_api_client.post_graphql(
        CONTATTO_QUERY, var
    )
    assert_no_permission(response)
    # faccio la richiesta con graphql: da un rappresentante verso un suo cliente
    var= {"id":contatto2_id}
    response = staff_api_client.post_graphql(
        CONTATTO_QUERY, var
    )
    content = get_graphql_content(response)
    data = content["data"]["contatto"]
    assert data["id"] == contatto2_id # verifico al volo se lo recupera
    assert data["email"] == contatto2.email
    # faccio la richiesta con graphql: da un rappresentante verso un NON suo cliente
    var= {"id":contatto3_id}
    response = staff_api_client.post_graphql(
        CONTATTO_QUERY, var
    )
    assert_no_permission(response)
    # faccio la richiesta con graphql: da un amministratore, NON rappresentante
    rappresentante.is_rappresentante = False
    rappresentante.save()
    # faccio la richiesta con graphql: da un admin verso un cliente di un altro rappresentante
    var= {"id":contatto3_id}
    response = staff_api_client.post_graphql(
        CONTATTO_QUERY, var
    )
    content = get_graphql_content(response)
    data = content["data"]["contatto"]
    assert data["id"] == contatto3_id # verifico al volo se lo recupera
    assert data["email"] == contatto3.email
    # faccio la richiesta con graphql: da un admin verso un cliente senza rappresentante
    var= {"id":contatto1_id}
    response = staff_api_client.post_graphql(
        CONTATTO_QUERY, var
    )
    content = get_graphql_content(response)
    data = content["data"]["contatto"]
    assert data["id"] == contatto1_id # verifico al volo se lo recupera
    assert data["email"] == contatto1.email
    # faccio la richiesta con graphql: da un rappresentante verso un NON suo cliente
    var= {"id":contatto1_id}
    response = staff_api_client.post_graphql(
        CONTATTO_QUERY, var
    )
    
    # check permissions
    response = user_api_client.post_graphql(CONTATTO_QUERY, {"id":""})
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
                rappresentante:$rappresentanteId,
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
        $rappresentante:ID
        
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
    print("creo assegnando un altro rappresentante, io NON sono rappresentante e NON ho i permessi")
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
    # print("creo assegnando un altro rappresentante, io NON sono rappresentante ma ho i permessi")
    # requester.is_rappresentante = False
    # requester.save()
    # staff_api_client.user.user_permissions.add(
    #     Permission.objects.get(codename="manage_rappresentanti") # TODO come lo includo nei permessi caricati?
    # )
    # variables = {
    #                 "email":"utente.crea.4@test.it",
    #                 "denominazione":"den test 4",
    #                 "rappresentanteId":rappresentante_id_2
    #             }
    # response = staff_api_client.post_graphql(MUTATION_CREA_CLIENTE, variables)
    # content = get_graphql_content(response)
    # print("\t", content["data"]["clienteCrea"])
    # data = content["data"]["clienteCrea"]["userExtra"]
    # assert content["data"]["clienteCrea"]["errors"] == []
    # assert data["rappresentante"]["email"] == staff_user_2.email

    # check permissions
    response = user_api_client.post_graphql(MUTATION_CREA_CLIENTE, variables)
    assert_no_permission(response)

# MUTATION_ASSEGNA_RAPPRESENTANTE = """
#     mutation assegnaRappresentanteACliente (
#         $id:ID!,
#         $rappresentanteId:ID
        
#     ){
#         assegnaRappresentanteACliente(
#         id:$id
#         input:{
#             rappresentante:$rappresentanteId
#         }){
#             errors{
#                 field
#                 message
#             }
#             user{
#                 id
#                 email
#                 isStaff
#             }
#             userExtra{
#                 id
#                 email
#                 denominazione
#                 rappresentante{
#                     id
#                     email
#                 }
#             }
#         }
#     }
# """
# def test_assegna_rappresentante_a_cliente(
#     staff_api_client,
#     user_api_client,
#     staff_user,
#     customer_user,
#     permission_manage_users,
#     # permission_manage_rappresentanti
# ):
#     staff_api_client.user.user_permissions.add(
#         permission_manage_users
#     )
#     # CREATE -------

#     # creo rappresentanti
#     cliente = UserExtra.objects.create(user=customer_user, denominazione="nome user")
#     cliente_id = graphene.Node.to_global_id("User", cliente.user.pk)
#     rappresentante = UserExtra.objects.create(user=staff_user, is_rappresentante=True, denominazione="nome rappresentante")
#     rappresentante_id = graphene.Node.to_global_id("User", rappresentante.user.pk)

#     variables = {
#                     "id":cliente_id,
#                     "rappresentanteId":rappresentante_id
#                 }
#     response = staff_api_client.post_graphql(MUTATION_ASSEGNA_RAPPRESENTANTE, variables)
#     content = get_graphql_content(response)
#     data = content["data"]["assegnaRappresentanteACliente"]["userExtra"]
#     assert content["data"]["assegnaRappresentanteACliente"]["errors"] == []
#     assert data["rappresentante"]["email"] == staff_user.email



# CONTATTI
def controlla_casistiche_mutazioni_contatto(nome_mutazione, mutazione, variables1,variables2, staff_api_client,user_extra, staff_extra):
    """variables2 serve per la delete, per cancellare il 2° contatto"""
    staff_extra.is_rappresentante = True
    staff_extra.save()
    user_extra.rappresentante = staff_extra.user
    user_extra.save()
    response = staff_api_client.post_graphql(mutazione, variables1)
    content = get_graphql_content(response)
    assert content["data"][nome_mutazione]["contatto"]
    assert content["data"][nome_mutazione]["errors"] == []

    staff_extra.is_rappresentante = True
    staff_extra.save()
    user_extra.rappresentante = None
    user_extra.save()
    response = staff_api_client.post_graphql(mutazione, variables1)
    content = get_graphql_content(response)
    assert not content["data"][nome_mutazione]["contatto"]
    assert len(content["data"][nome_mutazione]["errors"]) == 1

    staff_extra.is_rappresentante = False
    staff_extra.save()
    user_extra.rappresentante = None
    user_extra.save()
    response = staff_api_client.post_graphql(mutazione, variables2)
    content = get_graphql_content(response)
    assert content["data"][nome_mutazione]["contatto"]
    assert content["data"][nome_mutazione]["errors"] == []

def test_mutations_crea_contatto_rappresentante(
    staff_api_client,
    customer_user,
    staff_user,
    permission_manage_users
):
    staff_api_client.user.user_permissions.add(
        permission_manage_users
    )
    user_extra = UserExtra.objects.create(
        user = customer_user
    )
    staff_extra = UserExtra.objects.create(
        user = staff_user
    )

    # CREATE -------
    ID = graphene.Node.to_global_id("User", customer_user.pk)
    variables = {"userId": ID, 
                 "denominazione":"test denominazione contatto",
                 "email":"contatto@test.it",
                 "telefono":"+390457834054",
                 "uso":TipoContatto.FATTURAZIONE
                 }
    
    controlla_casistiche_mutazioni_contatto("contattoCrea", 
                                            MUTATION_CREA_CONTATTO, 
                                            variables,
                                            variables, 
                                            staff_api_client,
                                            user_extra, 
                                            staff_extra
                                            )

def test_mutations_aggiorna_contatto_rappresentante(
    staff_api_client,
    staff_user,
    customer_user,
    permission_manage_users
):    
    staff_api_client.user.user_permissions.add(
        permission_manage_users
    )
    user_extra = UserExtra.objects.create(
        user = customer_user
    )
    staff_extra = UserExtra.objects.create(
        user = staff_user
    )
    contatto = Contatto.objects.create(user_extra = user_extra,
                            denominazione="den",
                            email="contatto@test.it",
                            telefono="34734",
                            uso=TipoContatto.FATTURAZIONE)
    # UPDATE -----
    ID = graphene.Node.to_global_id("Contatto", contatto.pk)
    variables = {"id": ID, 
                 "denominazione":"modificata denominazione",
                 "email":"contatto.modificato@test.it",
                 "telefono":"+390456520415",
                 "uso":TipoContatto.CONSEGNA
                 }
    
    controlla_casistiche_mutazioni_contatto("contattoAggiorna", 
                                            MUTATION_AGGIORNA_CONTATTO, 
                                            variables, 
                                            variables,
                                            staff_api_client,
                                            user_extra, 
                                            staff_extra
                                            )

def test_mutations_cancella_contatto_rappresentante(
    staff_api_client,
    staff_user,
    customer_user,
    permission_manage_users
):
    staff_api_client.user.user_permissions.add(
        permission_manage_users
    )
    user_extra = UserExtra.objects.create(
        user = customer_user
    )
    staff_extra = UserExtra.objects.create(
        user = staff_user
    )
    contatto1 = Contatto.objects.create(user_extra = user_extra,
                            denominazione="den",
                            email="contatto@test.it",
                            telefono="34734",
                            uso=TipoContatto.FATTURAZIONE)
    contatto2 = Contatto.objects.create(user_extra = user_extra,
                            denominazione="den 2",
                            email="contatto2@test.it",
                            telefono="34734",
                            uso=TipoContatto.FATTURAZIONE)
    # DELETE -----
    id1 = graphene.Node.to_global_id("Contatto", contatto1.pk)
    id2 = graphene.Node.to_global_id("Contatto", contatto2.pk)
    variables1 = {"id": id1}
    variables2 = {"id": id2}
    controlla_casistiche_mutazioni_contatto("contattoCancella", 
                                            MUTATION_CANCELLA_CONTATTO, 
                                            variables1,
                                            variables2,
                                            staff_api_client,
                                            user_extra, 
                                            staff_extra
                                            )