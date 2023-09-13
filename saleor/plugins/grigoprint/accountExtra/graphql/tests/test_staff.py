# import datetime
# import json
# import os
# import re
# from collections import defaultdict
# from datetime import timedelta
# from unittest.mock import ANY, MagicMock, Mock, call, patch
# from urllib.parse import urlencode

import graphene
import pytest

from django.core.files import File
from saleor.account.models import User

# from ......account.models import Address, Group, User
# from ......graphql.core.utils import str_to_enum, to_global_id_or_none

from saleor.graphql.tests.utils import (
    assert_graphql_error_with_message,
    assert_no_permission,
    get_graphql_content,
)
from saleor.permission.enums import AccountPermissions

from saleor.plugins.grigoprint.accountExtra.models import Iva, Listino, UserExtra, TipoPorto, TipoVettore,TipoUtente, Contatto, TipoContatto


# ------------------------------------------------------- QUERY
FULL_USER_QUERY = """
    query Utente($id: ID!) {
        utente(id: $id) {
            id
            user{
                email
            }
            email
            denominazione
            idDanea
            tipoUtente
            isRappresentante
            rappresentante{
                email
            }
            commissione
            piva
            cf
            pec
            sdi
            rifAmmin
            splitPayment
            coordinateBancarie
            iva{
                nome
                valore
                info
            }
            porto
            vettore
            pagamento
            listino{
                nome
                ricarico
                info
            }
            sconto
            contatti{
                email
                denominazione
                telefono
                uso
            }
        }
    }
"""
CLIENTI_QUERY = """
    {
        clienti(first: 20) {
            edges {
                node {
                    email
                    user{
                        isStaff
                    }
                }
            }
        }
    }
    """
STAFF_UTENTI_QUERY = """
    {
        staffUtenti(first: 20) {
            edges {
                node {
                    email
                    user{
                        isStaff
                    }
                }
            }
        }
    }
    """
CONTATTO_QUERY = """
    query Contatto ($id: ID!) {
        contatto(id: $id){
            userExtra{
                email
            }
            email
            denominazione
            telefono
            uso
        }
    }
"""
CONTATTI_UTENTE_QUERY = """
    query ContattiUtente ($id: ID!) {
        contattiUtente(id: $id){
            userExtra{
                email
            }
            email
            denominazione
            telefono
            uso
        }
    }
"""

def test_query_utente_full(
    staff_api_client,
    user_api_client,
    permission_manage_users,
    permission_manage_orders,
):
    user = User.objects.create(email="customer1@test.it")
    #user extra
    user_extra = UserExtra.objects.create(
        user = user,
        denominazione = "denominazione",
        id_danea = "054",
        tipo_utente = TipoUtente.AGENZIA,
        is_rappresentante = False,
        # rappresentante = ,
        commissione = 0,
        piva = "01628380238",
        cf ="grgntnt34testok4",
        pec = "pec@pec.it",
        sdi = "m5uxrd",
        rif_ammin = "rif0154",
        split_payment = False,
        # iva = ,
        porto = TipoPorto.ASSEGNATO,
        vettore = TipoVettore.DESTINATARIO,
        # listino = ,
        coordinate_bancarie = "it01556261650000000021"
    )
    # userExtra = user.extra

    query = FULL_USER_QUERY
    # ricreo l'id di graphene per individuare l'untente in graphene
    ID = graphene.Node.to_global_id("User", user.pk)
    variables = {"id": ID}
    staff_api_client.user.user_permissions.add(
        permission_manage_users, permission_manage_orders
    )
    response = staff_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    data = content["data"]["utente"]
    assert data["id"] == ID
    assert data["email"] == user.email
    assert data["user"]["email"] == user.email
    assert data["denominazione"] == user_extra.denominazione
    assert data["idDanea"] == user_extra.id_danea
    assert data["tipoUtente"] == user_extra.tipo_utente
    assert data["isRappresentante"] == user_extra.is_rappresentante
    # assert data["rappresentante"] == user.extra.rappresentante
    assert data["commissione"] == user_extra.commissione
    assert data["piva"] == user_extra.piva
    assert data["cf"] == user_extra.cf
    assert data["pec"] == user_extra.pec
    assert data["sdi"] == user_extra.sdi
    assert data["rifAmmin"] == user_extra.rif_ammin
    assert data["splitPayment"] == user_extra.split_payment
    assert data["coordinateBancarie"] == user_extra.coordinate_bancarie
    #assert data["iva"] == user.extra.iva
    assert data["porto"] == user_extra.porto
    assert data["vettore"] == user_extra.vettore
    assert data["pagamento"] == user_extra.pagamento
    # assert data["listino"] == user.extra.listino
    assert data["sconto"] == user_extra.sconto

    # assert len(data["contatti"]) == user.extra.contatti.count()
    # for contatto in data["contatti"]:
    #     contatto_id =  contatto["id"]

    # no access for normal user
    response_user = user_api_client.post_graphql(MUTATION_CANCELLA_CONTATTO, variables)
    assert_no_permission(response_user)

def test_query_utente_minimum(
    staff_api_client,
    customer_user,
    permission_manage_users,
    permission_manage_orders
):
    user = customer_user
    #user extra
    UserExtra.objects.create(
        user = user
    )

    query = FULL_USER_QUERY
    # ricreo l'id di graphene per individuare l'untente in graphene
    ID = graphene.Node.to_global_id("User", customer_user.id)
    variables = {"id": ID}
    staff_api_client.user.user_permissions.add(
        permission_manage_users, permission_manage_orders
    )
    response = staff_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    data = content["data"]["utente"]
    assert data["email"] == user.email
    assert data["denominazione"] == user.extra.denominazione
    assert data["idDanea"] == user.extra.id_danea
    assert data["tipoUtente"] == TipoUtente.AZIENDA
    assert data["isRappresentante"] is False
    # assert data["rappresentante"] == user.extra.rappresentante
    assert data["commissione"] == 0
    assert data["piva"] == user.extra.piva
    assert data["cf"] == user.extra.cf
    assert data["pec"] == user.extra.pec
    assert data["sdi"] == user.extra.sdi
    assert data["rifAmmin"] == user.extra.rif_ammin
    assert data["splitPayment"] is False
    assert data["coordinateBancarie"] == user.extra.coordinate_bancarie
    #assert data["iva"] == user.extra.iva
    assert data["porto"] == TipoPorto.FRANCO_CON_ADDEBITO
    assert data["vettore"] == TipoVettore.VETTORE_GLS
    assert data["pagamento"] == user.extra.pagamento
    # assert data["listino"] == user.extra.listino
    assert data["sconto"] == 0

    # assert len(data["contatti"]) == user.extra.contatti.count()
    # for contatto in data["contatti"]:
    #     contatto_id =  contatto["id"]

  
def test_query_clienti(
        staff_api_client, 
        user_api_client, 
        permission_manage_users
    ):
    #creo gli utententi nel db
    staff1 = User.objects.create(email="staff1@test.it", is_staff=True)
    UserExtra.objects.create(user=staff1)
    user1 = User.objects.create(email="user1@test.it", is_staff=False)
    UserExtra.objects.create(user=user1)
    user2 = User.objects.create(email="user2@test.it", is_staff=False)
    UserExtra.objects.create(user=user2)
    
    # faccio la richiesta con graphql
    variables = {}
    response = staff_api_client.post_graphql(
        CLIENTI_QUERY, variables, permissions=[permission_manage_users]
    )
    content = get_graphql_content(response)
    data = content["data"]["clienti"]["edges"]
    assert len(data) == 2
    assert all([not user["node"]["user"]["isStaff"] for user in data])

    # check permissions
    response = user_api_client.post_graphql(CLIENTI_QUERY, variables)
    assert_no_permission(response)

def test_query_staff_utenti(
        staff_api_client, 
        user_api_client, 
        permission_manage_staff
):
    #creo gli utententi nel db
    staff1 = User.objects.create(email="staff1@test.it", is_staff=True)
    UserExtra.objects.create(user=staff1)
    staff2 = User.objects.create(email="staff2@test.it", is_staff=True)
    UserExtra.objects.create(user=staff2)
    user1 = User.objects.create(email="user1@test.it", is_staff=False)
    UserExtra.objects.create(user=user1)
    
    # faccio la richiesta con graphql
    variables = {}
    response = staff_api_client.post_graphql(
        STAFF_UTENTI_QUERY, variables, permissions=[permission_manage_staff]
    )
    content = get_graphql_content(response)
    data = content["data"]["staffUtenti"]["edges"]
    assert len(data) == 2
    assert all([user["node"]["user"]["isStaff"] for user in data])

    # check permissions
    response = user_api_client.post_graphql(STAFF_UTENTI_QUERY, variables)
    assert_no_permission(response)


def test_query_contatto(
    staff_api_client,
    user_api_client,
    customer_user,
    permission_manage_users,
    permission_manage_orders
):
    user = customer_user
    #user extra
    user_extra = UserExtra.objects.create(
        user = user
    )
    contatto1 = Contatto.objects.create(
        user_extra = user_extra,
        denominazione = "antonio grigolini",
        telefono = "3473462414",
        uso = TipoContatto.FATTURAZIONE,
        email = "grig.griganto@gmail.com"
    )

    # ricreo l'id di graphene per individuare l'untente in graphene
    ID = graphene.Node.to_global_id("Contatto", contatto1.id)
    variables = {"id": ID}
    staff_api_client.user.user_permissions.add(
        permission_manage_users, permission_manage_orders
    )
    response = staff_api_client.post_graphql(CONTATTO_QUERY, variables)
    content = get_graphql_content(response)
    data = content["data"]["contatto"]
    assert data["denominazione"] == contatto1.denominazione
    assert data["userExtra"]["email"] == contatto1.user_extra.user.email
    assert data["telefono"] == contatto1.telefono
    assert data["uso"] == contatto1.uso
    # no access for normal user
    response_user = user_api_client.post_graphql(CONTATTO_QUERY, variables)
    assert_no_permission(response_user)

def test_query_contatti(
    staff_api_client,
    user_api_client,
    customer_user,
    permission_manage_users,
    permission_manage_orders
):
    user = customer_user
    #user extra
    user_extra = UserExtra.objects.create(
        user = user
    )
    contatto1 = Contatto.objects.create(
        user_extra = user_extra,
        denominazione = "antonio grigolini",
        telefono = "3473462414",
        uso = TipoContatto.FATTURAZIONE,
        email = "grig.griganto@gmail.com"
    )
    contatto2 = Contatto.objects.create(
        user_extra = user_extra,
        denominazione = "antonio grigolini 2",
        telefono = "3518882958",
        uso = TipoContatto.CONSEGNA,
        email = "griganto.games@gmail.com"
    )

    # ricreo l'id di graphene per individuare l'untente in graphene
    user_id = graphene.Node.to_global_id("Contatto", user.id)
    variables = {"id": user_id}
    staff_api_client.user.user_permissions.add(
        permission_manage_users, permission_manage_orders
    )
    response = staff_api_client.post_graphql(CONTATTI_UTENTE_QUERY, variables)
    content = get_graphql_content(response)
    data = content["data"]["contatti"]
    assert len(data) == 2
    assert data[0]["denominazione"] == contatto1.denominazione
    assert data[0]["userExtra"]["email"] == contatto1.user_extra.user.email
    assert data[0]["telefono"] == contatto1.telefono
    assert data[0]["uso"] == contatto1.uso
    assert data[1]["denominazione"] == contatto2.denominazione
    assert data[1]["userExtra"]["email"] == contatto2.user_extra.user.email
    assert data[1]["telefono"] == contatto2.telefono
    assert data[1]["uso"] == contatto2.uso
    # no access for normal user
    response_user = user_api_client.post_graphql(CONTATTI_UTENTE_QUERY, variables)
    assert_no_permission(response_user)
    

# ------------------------------------------------------- MUTATIONS

MUTATION_CREA_CONTATTO = """
    mutation crea_contatto (
        $userId: ID!,
        $denominazione:String!,
        $email:String!,
        $telefono:String,
        $uso:TipoContattoEnum
        
    ){
        contattoCrea(
            input:{
                userId:$userId,
                denominazione:$denominazione,
                email:$email,
                telefono:$telefono,
                uso:$uso
            }
        ){
            errors{
                field
                message
            }
            contatto{
                id
                userExtra{
                    id
                    email
                }
                email
                denominazione
                telefono
                uso
            }
        }
    }
"""
MUTATION_AGGIORNA_CONTATTO = """
    mutation aggiorna_contatto (
        $id: ID!,
        $denominazione:String,
        $email:String,
        $telefono:String,
        $uso:TipoContattoEnum
    ){
        contattoAggiorna(
            id:$id,
            input:{
                denominazione:$denominazione,
                email:$email,
                telefono:$telefono,
                uso:$uso
            }
        ){
            errors{
                field
                message
            }
            contatto{
                id
                userExtra{
                    id
                    email
                }
                email
                denominazione
                telefono
                uso
            }
        }
    }
"""
MUTATION_CANCELLA_CONTATTO = """
    mutation cancella_contatto (
        $id: ID!){
        contattoCancella(
            id:$id
        ){
            errors{
                field
                message
            }
            contatto{
                id
                userExtra{
                    id
                    email
                }
                email
                denominazione
                telefono
                uso
            }
        }
    }
"""

def test_mutations_contatto(
    staff_api_client,
    user_api_client,
    customer_user,
    permission_manage_users
):
    user = customer_user
    #user extra
    user_extra = UserExtra.objects.create(
        user = user
    )
    # mi accerto che non ci siamo contatti in questo Utente
    assert len(Contatto.objects.filter(user_extra=user_extra)) == 0

    staff_api_client.user.user_permissions.add(
        permission_manage_users
    )
    # CREATE -------
    ID = graphene.Node.to_global_id("User", user.pk)
    variables = {"userId": ID, 
                 "denominazione":"test denominazione contatto",
                 "email":"contatto@test.it",
                 "telefono":"+390457834054",
                 "uso":TipoContatto.FATTURAZIONE
                 }
    response = staff_api_client.post_graphql(MUTATION_CREA_CONTATTO, variables)
    content = get_graphql_content(response)
    data = content["data"]["contattoCrea"]["contatto"]
    assert content["data"]["contattoCrea"]["errors"] == []
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    contatti = Contatto.objects.filter(user_extra = user_extra)
    assert len(contatti) == 1
    contatto = contatti.first()
    assert contatto is not None
    assert data["denominazione"] == variables["denominazione"]
    assert data["email"] == variables["email"]
    assert data["telefono"] == variables["telefono"]
    assert data["uso"] == variables["uso"]
    assert data["userExtra"]["email"] == user_extra.user.email
    # no access for normal user
    response_user = user_api_client.post_graphql(MUTATION_CREA_CONTATTO, variables)
    assert_no_permission(response_user)
    # UPDATE -----
    ID = graphene.Node.to_global_id("Contatto", contatto.pk)
    variables = {"id": ID, 
                 "denominazione":"modificata denominazione",
                 "email":"contatto.modificato@test.it",
                 "telefono":"+390456520415",
                 "uso":TipoContatto.CONSEGNA
                 }
    response = staff_api_client.post_graphql(MUTATION_AGGIORNA_CONTATTO, variables)
    content = get_graphql_content(response)
    data = content["data"]["contattoAggiorna"]["contatto"]
    assert content["data"]["contattoAggiorna"]["errors"] == []
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    contatti = Contatto.objects.filter(user_extra = user_extra)
    assert len(contatti) == 1
    contatto = contatti.first()
    assert contatto is not None
    assert data["denominazione"] == variables["denominazione"]
    assert data["email"] == variables["email"]
    assert data["telefono"] == variables["telefono"]
    assert data["uso"] == variables["uso"]
    assert data["userExtra"]["email"] == user_extra.user.email
     # no access for normal user
    response_user = user_api_client.post_graphql(MUTATION_AGGIORNA_CONTATTO, variables)
    assert_no_permission(response_user)
    # DELETE -----
    ID = graphene.Node.to_global_id("Contatto", contatto.pk)
    variables = {"id": ID}
    response = staff_api_client.post_graphql(MUTATION_CANCELLA_CONTATTO, variables)
    content = get_graphql_content(response)
    data = content["data"]["contattoCancella"]["contatto"]
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    contatti = Contatto.objects.filter(user_extra = user_extra)
    assert len(contatti) == 0 
    # no access for normal user
    response_user = user_api_client.post_graphql(MUTATION_CANCELLA_CONTATTO, variables)
    assert_no_permission(response_user)

MUTATION_CREA_CLIENTE = """
    mutation clienteCrea (
        $email:String!,
        $denominazione:String!,
        $piva:String,
        $cf:String,
        $pec:String,
        $sdi:String,
        $rifAmmin:String,
        $splitPayment:Boolean,
        $coordinateBancarie:String,
        $idDanea:String,
        $rappresentanteId:ID,
        $tipoUtente:TipoUtenteEnum,
        $ivaId:ID,
        $porto:TipoPortoEnum,
        $vettore:TipoVettoreEnum,
        $pagamento:String,
        $listinoId:ID,
        $sconto:Float
        
    ){
        clienteCrea(
        input:{
            email:$email,
            extra:{
                denominazione:$denominazione,
                piva:$piva,
                cf:$cf,
                pec:$pec,
                sdi:$sdi,
                rifAmmin:$rifAmmin,
                splitPayment:$splitPayment,
                coordinateBancarie:$coordinateBancarie,
                idDanea:$idDanea,
                rappresentanteId:$rappresentanteId,
                tipoUtente:$tipoUtente,
                ivaId:$ivaId,
                porto:$porto,
                vettore:$vettore,
                pagamento:$pagamento,
                listinoId:$listinoId,
                sconto:$sconto
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
                piva
                cf
                pec
                sdi
                rifAmmin,
                splitPayment
                coordinateBancarie
                idDanea
                rappresentante{
                    id
                    email
                }
                isRappresentante
                tipoUtente
                iva{
                    nome
                    valore
                    info
                }
                porto
                vettore
                pagamento
                listino{
                    nome
                    ricarico
                    info
                }
                sconto
            }
        }
    }
"""
MUTATION_AGGIORNA_CLIENTE = """
    mutation clienteAggiorna (
        $id:ID!
        $email:String!
        $denominazione:String!,
        $piva:String,
        $cf:String,
        $pec:String,
        $sdi:String,
        $rifAmmin:String,
        $splitPayment:Boolean,
        $coordinateBancarie:String,
        $idDanea:String,
        $rappresentanteId:ID,
        $tipoUtente:TipoUtenteEnum,
        $ivaId:ID,
        $porto:TipoPortoEnum,
        $vettore:TipoVettoreEnum,
        $pagamento:String,
        $listinoId:ID,
        $sconto:Float
        
    ){
        clienteAggiorna(
        id:$id
        input:{
            email:$email,
            extra:{
                denominazione:$denominazione,
                piva:$piva,
                cf:$cf,
                pec:$pec,
                sdi:$sdi,
                rifAmmin:$rifAmmin,
                splitPayment:$splitPayment,
                coordinateBancarie:$coordinateBancarie,
                idDanea:$idDanea,
                rappresentanteId:$rappresentanteId,
                tipoUtente:$tipoUtente,
                ivaId:$ivaId,
                porto:$porto,
                vettore:$vettore,
                pagamento:$pagamento,
                listinoId:$listinoId,
                sconto:$sconto
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
                piva
                cf
                pec
                sdi
                rifAmmin,
                splitPayment
                coordinateBancarie
                idDanea
                rappresentante{
                    id
                    email
                }
                isRappresentante
                tipoUtente
                iva{
                    nome
                    valore
                    info
                }
                porto
                vettore
                pagamento
                listino{
                    nome
                    ricarico
                    info
                }
                sconto
            }
        }
    }
"""
MUTATION_CANCELLA_CLIENTE = """
    mutation customerDelete (
        $id:ID!
    ){
        customerDelete(
        id:$id
        ){
            user{
                id
                email
            }
        }
    }
"""
MUTATION_CANCELLA_CLIENTI = """
    mutation customerBulkDelete (
        $ids:ID!
    ){
        customerBulkDelete(ids:[$ids]){
            errors{
                field
                message
            }
            count
        }
    }
"""
def test_mutations_cliente(
    staff_api_client,
    user_api_client,
    staff_user,
    permission_manage_users
):
    staff_api_client.user.user_permissions.add(
        permission_manage_users
    )
    # CREATE -------
    email = "utente.crea@test.it"
    # creo rappresentante
    rappresentante = UserExtra.objects.create(user=staff_user, is_rappresentante=True, denominazione="nome rappresentante")
    rappresentante_id = graphene.Node.to_global_id("User", rappresentante.user.pk)
    iva = Iva.objects.create(nome="22%",valore=0.22,info="standard 22%")
    iva_id = graphene.Node.to_global_id("Iva", iva.pk)
    listino = Listino.objects.create(nome="pubblico",ricarico=0.34,info="Cliente finale")
    listino_id = graphene.Node.to_global_id("Listino", listino.pk)
    variables = {
                    "email":email,
                    "denominazione":"den test",
                    "piva":"01628380238",
                    "cf":"gngntnt28d26s4",
                    "pec":"bandieregrigolni@pec.it",
                    "sdi":"m5uecc",
                    "rifAmmin":"rif ammin",
                    "splitPayment":False,
                    "coordinateBancarie":"it01iban di prova zzz",
                    "idDanea":"1",
                    "rappresentanteId":rappresentante_id,
                    "tipoUtente":TipoUtente.AZIENDA,
                    "ivaId":iva_id,
                    "porto":TipoPorto.ASSEGNATO,
                    "vettore":TipoVettore.VETTORE_BRT,
                    "pagamento":"bonifico posticipato??",
                    "listinoId":listino_id,
                    "sconto":0.1
                }
    response = staff_api_client.post_graphql(MUTATION_CREA_CLIENTE, variables)
    content = get_graphql_content(response)
    data = content["data"]["clienteCrea"]["userExtra"]
    assert content["data"]["clienteCrea"]["errors"] == []
    assert not content["data"]["clienteCrea"]["user"]["isStaff"]
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    users = UserExtra.objects.filter(user__email = email)
    assert len(users) == 1
    user = users.first()
    assert user is not None
    assert data["email"] == variables["email"]
    assert data["denominazione"] == variables["denominazione"]
    assert data["piva"] == variables["piva"]
    assert data["cf"] == variables["cf"]
    assert data["pec"] == variables["pec"]
    assert data["sdi"] == variables["sdi"]
    assert data["rifAmmin"] == variables["rifAmmin"]
    assert data["splitPayment"] == variables["splitPayment"]
    assert data["coordinateBancarie"] == variables["coordinateBancarie"]
    assert data["idDanea"] == variables["idDanea"]
    assert user.rappresentante and data["rappresentante"]["email"] == user.rappresentante.email
    assert data["tipoUtente"] == variables["tipoUtente"]
    assert user.iva and data["iva"]["nome"] == user.iva.nome
    assert user.listino and data["listino"]["nome"] == user.listino.nome
    assert data["porto"] == variables["porto"]
    assert data["vettore"] == variables["vettore"]
    assert data["pagamento"] == variables["pagamento"]
    assert data["sconto"] == variables["sconto"]
    
    # no access for normal user
    response_user = user_api_client.post_graphql(MUTATION_CREA_CLIENTE, variables)
    assert_no_permission(response_user)
    
    # UPDATE -----
    iva = Iva.objects.create(nome="0%",valore=0,info="esportazione")
    iva_id = graphene.Node.to_global_id("Iva", iva.pk)
    listino = Listino.objects.create(nome="agenzie",ricarico=0.12,info="rivenditori")
    listino_id = graphene.Node.to_global_id("Listino", listino.pk)
    user_id = graphene.Node.to_global_id("User", user.pk)
    variables = {
                    "id":user_id,
                    "email":email,
                    "denominazione":"aggiorna  test",
                    "piva":"01628380239",
                    "cf":"gngntnt28d26s5",
                    "pec":"bandieregrigolni2@pec.it",
                    "sdi":"m5uecxc",
                    "rifAmmin":"rif amminn2",
                    "splitPayment":True,
                    "coordinateBancarie":"it01iban modificato di prova zzz",
                    "idDanea":"2",
                    "rappresentanteId":rappresentante_id,
                    "tipoUtente":TipoUtente.AZIENDA,
                    "ivaId":iva_id,
                    "porto":TipoPorto.ASSEGNATO,
                    "vettore":TipoVettore.VETTORE_BRT,
                    "pagamento":"bonifico posticipato??",
                    "listinoId":listino_id,
                    "sconto":0.1
                }
    response = staff_api_client.post_graphql(MUTATION_AGGIORNA_CLIENTE, variables)
    content = get_graphql_content(response)
    data = content["data"]["clienteAggiorna"]["userExtra"]
    assert content["data"]["clienteAggiorna"]["errors"] == []
    assert not content["data"]["clienteAggiorna"]["user"]["isStaff"]
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    users = UserExtra.objects.filter(user__email = email)
    assert len(users) == 1
    user = users.first()
    assert user is not None
    assert data["email"] == variables["email"]
    assert data["denominazione"] == variables["denominazione"]
    assert data["piva"] == variables["piva"]
    assert data["cf"] == variables["cf"]
    assert data["pec"] == variables["pec"]
    assert data["sdi"] == variables["sdi"]
    assert data["rifAmmin"] == variables["rifAmmin"]
    assert data["splitPayment"] == variables["splitPayment"]
    assert data["coordinateBancarie"] == variables["coordinateBancarie"]
    assert data["idDanea"] == variables["idDanea"]
    assert user.rappresentante and data["rappresentante"]["email"] == user.rappresentante.email
    assert data["tipoUtente"] == variables["tipoUtente"]
    assert user.iva and data["iva"]["nome"] == user.iva.nome
    assert user.listino and data["listino"]["nome"] == user.listino.nome
    assert data["porto"] == variables["porto"]
    assert data["vettore"] == variables["vettore"]
    assert data["pagamento"] == variables["pagamento"]
    assert data["sconto"] == variables["sconto"]
    
    # no access for normal user
    response_user = user_api_client.post_graphql(MUTATION_AGGIORNA_CLIENTE, variables)
    assert_no_permission(response_user)

    #DELETE
    # mi assicuro che funziona la delete originale di saleor
    variables = {"id": user_id}
    response = staff_api_client.post_graphql(MUTATION_CANCELLA_CLIENTE, variables)
    content = get_graphql_content(response)
    data = content["data"]["customerDelete"]["user"]
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    users = UserExtra.objects.filter(user__email = email)
    assert len(users) == 0
    #BULK DELETE
    user = User.objects.create(email="bulk1@test.it")
    userEx = UserExtra.objects.create(user=user, denominazione="test blulk delete")
    users_pk = [graphene.Node.to_global_id("User", userEx.user.pk)]
    users_id = ",".join(users_pk)
    variables = {"ids": users_id}
    response = staff_api_client.post_graphql(MUTATION_CANCELLA_CLIENTI, variables)
    content = get_graphql_content(response)
    data = content["data"]["customerBulkDelete"]
    assert data["errors"] == []
    assert data["count"] == 1


MUTATION_CREA_STAFF = """
    mutation staffCrea (
        $email:String!
        $denominazione:String!,
        $piva:String,
        $cf:String,
        $pec:String,
        $sdi:String,
        $rifAmmin:String,
        $splitPayment:Boolean,
        $coordinateBancarie:String,
        $idDanea:String,
        $rappresentanteId:ID,
        $tipoUtente:TipoUtenteEnum,
        $ivaId:ID,
        $porto:TipoPortoEnum,
        $vettore:TipoVettoreEnum,
        $pagamento:String,
        $listinoId:ID,
        $sconto:Float
        
    ){
        staffCrea(
        input:{
            email:$email,
            extra:{
                denominazione:$denominazione,
                piva:$piva,
                cf:$cf,
                pec:$pec,
                sdi:$sdi,
                rifAmmin:$rifAmmin,
                splitPayment:$splitPayment,
                coordinateBancarie:$coordinateBancarie,
                idDanea:$idDanea,
                rappresentanteId:$rappresentanteId,
                tipoUtente:$tipoUtente,
                ivaId:$ivaId,
                porto:$porto,
                vettore:$vettore,
                pagamento:$pagamento,
                listinoId:$listinoId,
                sconto:$sconto
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
                piva
                cf
                pec
                sdi
                rifAmmin,
                splitPayment
                coordinateBancarie
                idDanea
                rappresentante{
                    id
                    email
                }
                isRappresentante
                tipoUtente
                iva{
                    nome
                    valore
                    info
                }
                porto
                vettore
                pagamento
                listino{
                    nome
                    ricarico
                    info
                }
                sconto
            }
        }
    }
"""
MUTATION_AGGIORNA_STAFF = """
    mutation staffAggiorna (
        $id:ID!
        $email:String!
        $denominazione:String!,
        $piva:String,
        $cf:String,
        $pec:String,
        $sdi:String,
        $rifAmmin:String,
        $splitPayment:Boolean,
        $coordinateBancarie:String,
        $idDanea:String,
        $rappresentanteId:ID,
        $tipoUtente:TipoUtenteEnum,
        $ivaId:ID,
        $porto:TipoPortoEnum,
        $vettore:TipoVettoreEnum,
        $pagamento:String,
        $listinoId:ID,
        $sconto:Float
        
    ){
        staffAggiorna(
        id:$id
        input:{
            email:$email,
            extra:{
                denominazione:$denominazione,
                piva:$piva,
                cf:$cf,
                pec:$pec,
                sdi:$sdi,
                rifAmmin:$rifAmmin,
                splitPayment:$splitPayment,
                coordinateBancarie:$coordinateBancarie,
                idDanea:$idDanea,
                rappresentanteId:$rappresentanteId,
                tipoUtente:$tipoUtente,
                ivaId:$ivaId,
                porto:$porto,
                vettore:$vettore,
                pagamento:$pagamento,
                listinoId:$listinoId,
                sconto:$sconto
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
                piva
                cf
                pec
                sdi
                rifAmmin,
                splitPayment
                coordinateBancarie
                idDanea
                rappresentante{
                    id
                    email
                }
                isRappresentante
                tipoUtente
                iva{
                    nome
                    valore
                    info
                }
                porto
                vettore
                pagamento
                listino{
                    nome
                    ricarico
                    info
                }
                sconto
            }
        }
    }
"""
MUTATION_CANCELLA_STAFF = """
    mutation staffDelete (
        $id:ID!
    ){
        staffDelete(
        id:$id
        ){
            user{
                id
                email
            }
        }
    }
"""
def test_mutations_staff(
    staff_api_client,
    user_api_client,
    staff_user,
    permission_manage_users,
    permission_manage_staff
):
    staff_api_client.user.user_permissions.add(
        permission_manage_staff,
        permission_manage_users
    )
    # CREATE -------
    email = "staff.crea@test.it"
    # creo rappresentante
    rappresentante = UserExtra.objects.create(user=staff_user, is_rappresentante=True, denominazione="nome rappresentante")
    rappresentante_id = graphene.Node.to_global_id("User", rappresentante.user.pk)
    iva = Iva.objects.create(nome="22%",valore=0.22,info="standard 22%")
    iva_id = graphene.Node.to_global_id("Iva", iva.pk)
    listino = Listino.objects.create(nome="pubblico",ricarico=0.34,info="Cliente finale")
    listino_id = graphene.Node.to_global_id("Listino", listino.pk)
    variables = {
                    "email":email,
                    "denominazione":"den test",
                    "piva":"01628380238",
                    "cf":"gngntnt28d26s4",
                    "pec":"bandieregrigolni@pec.it",
                    "sdi":"m5uecc",
                    "rifAmmin":"rif ammin",
                    "splitPayment":False,
                    "coordinateBancarie":"it01iban di prova zzz",
                    "idDanea":"1",
                    "rappresentanteId":rappresentante_id,
                    "tipoUtente":TipoUtente.AZIENDA,
                    "ivaId":iva_id,
                    "porto":TipoPorto.ASSEGNATO,
                    "vettore":TipoVettore.VETTORE_BRT,
                    "pagamento":"bonifico posticipato??",
                    "listinoId":listino_id,
                    "sconto":0.1
                }
    response = staff_api_client.post_graphql(MUTATION_CREA_STAFF, variables)
    content = get_graphql_content(response)
    data = content["data"]["staffCrea"]["userExtra"]
    assert content["data"]["staffCrea"]["errors"] == []
    assert content["data"]["staffCrea"]["user"]["isStaff"]
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    users = UserExtra.objects.filter(user__email = email)
    assert len(users) == 1
    user = users.first()
    assert user is not None
    assert data["email"] == variables["email"]
    assert data["denominazione"] == variables["denominazione"]
    assert data["piva"] == variables["piva"]
    assert data["cf"] == variables["cf"]
    assert data["pec"] == variables["pec"]
    assert data["sdi"] == variables["sdi"]
    assert data["rifAmmin"] == variables["rifAmmin"]
    assert data["splitPayment"] == variables["splitPayment"]
    assert data["coordinateBancarie"] == variables["coordinateBancarie"]
    assert data["idDanea"] == variables["idDanea"]
    assert not user.rappresentante
    assert data["tipoUtente"] == variables["tipoUtente"]
    assert user.iva and data["iva"]["nome"] == user.iva.nome
    assert user.listino and data["listino"]["nome"] == user.listino.nome
    assert data["porto"] == variables["porto"]
    assert data["vettore"] == variables["vettore"]
    assert data["pagamento"] == variables["pagamento"]
    assert data["sconto"] == variables["sconto"]
    
    # no access for normal user
    response_user = user_api_client.post_graphql(MUTATION_CREA_STAFF, variables)
    assert_no_permission(response_user)
    
    # UPDATE -----
    iva = Iva.objects.create(nome="0%",valore=0,info="esportazione")
    iva_id = graphene.Node.to_global_id("Iva", iva.pk)
    listino = Listino.objects.create(nome="agenzie",ricarico=0.12,info="rivenditori")
    listino_id = graphene.Node.to_global_id("Listino", listino.pk)
    user_id = graphene.Node.to_global_id("User", user.pk)
    variables = {
                    "id":user_id,
                    "email":email,
                    "denominazione":"aggiorna  test",
                    "piva":"01628380239",
                    "cf":"gngntnt28d26s5",
                    "pec":"bandieregrigolni2@pec.it",
                    "sdi":"m5uecxc",
                    "rifAmmin":"rif amminn2",
                    "splitPayment":True,
                    "coordinateBancarie":"it01iban modificato di prova zzz",
                    "idDanea":"2",
                    "rappresentanteId":rappresentante_id,
                    "tipoUtente":TipoUtente.AZIENDA,
                    "ivaId":iva_id,
                    "porto":TipoPorto.ASSEGNATO,
                    "vettore":TipoVettore.VETTORE_BRT,
                    "pagamento":"bonifico posticipato??",
                    "listinoId":listino_id,
                    "sconto":0.1
                }
    response = staff_api_client.post_graphql(MUTATION_AGGIORNA_STAFF, variables)
    content = get_graphql_content(response)
    data = content["data"]["staffAggiorna"]["userExtra"]
    assert content["data"]["staffAggiorna"]["errors"] == []
    assert content["data"]["staffAggiorna"]["user"]["isStaff"]
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    users = UserExtra.objects.filter(user__email = email)
    assert len(users) == 1
    user = users.first()
    assert user is not None
    assert data["email"] == variables["email"]
    assert data["denominazione"] == variables["denominazione"]
    assert data["piva"] == variables["piva"]
    assert data["cf"] == variables["cf"]
    assert data["pec"] == variables["pec"]
    assert data["sdi"] == variables["sdi"]
    assert data["rifAmmin"] == variables["rifAmmin"]
    assert data["splitPayment"] == variables["splitPayment"]
    assert data["coordinateBancarie"] == variables["coordinateBancarie"]
    assert data["idDanea"] == variables["idDanea"]
    assert not user.rappresentante
    assert data["tipoUtente"] == variables["tipoUtente"]
    assert user.iva and data["iva"]["nome"] == user.iva.nome
    assert user.listino and data["listino"]["nome"] == user.listino.nome
    assert data["porto"] == variables["porto"]
    assert data["vettore"] == variables["vettore"]
    assert data["pagamento"] == variables["pagamento"]
    assert data["sconto"] == variables["sconto"]
    
    # no access for normal user
    response_user = user_api_client.post_graphql(MUTATION_AGGIORNA_STAFF, variables)
    assert_no_permission(response_user)

    #DELETE
    # mi assicuro che funziona la delete originale di saleor
    variables = {"id": user_id}
    response = staff_api_client.post_graphql(MUTATION_CANCELLA_STAFF, variables)
    content = get_graphql_content(response)
    data = content["data"]["staffDelete"]["user"]
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    users = UserExtra.objects.filter(user__email = email)
    assert len(users) == 0

MUTATION_FORZA_PASSWORD = """
    mutation forzaPassword (
        $id:ID!
        $password:string!
    ){
        staffDelete(
        id:$id
        password:$password
        ){
            errors{
                code
                field
            }
        }
    }
"""

# def test_mutations_forza_password(
#     staff_user,
#     customer_user,
#     staff_api_client,
#     user_api_client,
#     permission_manage_users,
#     permission_manage_staff,
#     superuser_api_client
# ):
    
#     # creo un utente da modificare
#     email = "staff.forza.password@test.it"
#     # creo rappresentante
#     ut_sal = User.objects.create(email=email)
#     utente = UserExtra.objects.create(user=ut_sal, denominazione="metti la password", active=True)
#     variables = {
#                     "email":email,
#                     "password":"test password"
#                 }
#     response = superuser_api_client.post_graphql(MUTATION_FORZA_PASSWORD, variables)
#     content = get_graphql_content(response)
#     data = content["data"]["forzaPAssword"]["errors"]
#     assert data == []
#     #controllo se l'utente esegue il login con la nuova password
#     # TODO

#     # no access for normal user
#     response_user = user_api_client.post_graphql(MUTATION_FORZA_PASSWORD, variables)
#     assert_no_permission(response_user)
#     staff_api_client.user.user_permissions.add(
#         permission_manage_staff,
#         permission_manage_users,
#     )
#     response_staff = staff_api_client.post_graphql(MUTATION_FORZA_PASSWORD, variables)
#     assert_no_permission(response_staff)