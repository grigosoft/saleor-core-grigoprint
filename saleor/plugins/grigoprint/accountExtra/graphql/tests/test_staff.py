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
    get_graphql_content_from_response,
    get_multipart_request_body,
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

def test_query_utente_full(
    staff_api_client,
    customer_user,
    permission_manage_users,
    permission_manage_orders,
):
    user = customer_user
    #user extra
    UserExtra.objects.create(
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
    ID = graphene.Node.to_global_id("User", customer_user.id)
    variables = {"id": ID}
    staff_api_client.user.user_permissions.add(
        permission_manage_users, permission_manage_orders
    )
    response = staff_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    data = content["data"]["utente"]
    assert data["email"] == user.email
    assert data["user"]["email"] == user.email
    assert data["denominazione"] == user.extra.denominazione
    assert data["idDanea"] == user.extra.id_danea
    assert data["tipoUtente"] == user.extra.tipo_utente
    assert data["isRappresentante"] == user.extra.is_rappresentante
    # assert data["rappresentante"] == user.extra.rappresentante
    assert data["commissione"] == user.extra.commissione
    assert data["piva"] == user.extra.piva
    assert data["cf"] == user.extra.cf
    assert data["pec"] == user.extra.pec
    assert data["sdi"] == user.extra.sdi
    assert data["rifAmmin"] == user.extra.rif_ammin
    assert data["splitPayment"] == user.extra.split_payment
    assert data["coordinateBancarie"] == user.extra.coordinate_bancarie
    #assert data["iva"] == user.extra.iva
    assert data["porto"] == user.extra.porto
    assert data["vettore"] == user.extra.vettore
    assert data["pagamento"] == user.extra.pagamento
    # assert data["listino"] == user.extra.listino
    assert data["sconto"] == user.extra.sconto

    # assert len(data["contatti"]) == user.extra.contatti.count()
    # for contatto in data["contatti"]:
    #     contatto_id =  contatto["id"]

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

  
def test_query_clienti():
    pass

def test_query_staff_utenti(staff_api_client, user_api_client, staff_user, admin_user, permission_manage_staff
):
    query = """
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
    #come faccio a farli avere tutti la parte Extra?
    variables = {}
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_staff]
    )
    content = get_graphql_content(response)
    data = content["data"]["staffUtenti"]["edges"]
    assert len(data) == 2
    staff_emails = [user["node"]["email"] for user in data]
    assert sorted(staff_emails) == [admin_user.email, staff_user.email]
    assert all([user["node"]["user"]["isStaff"] for user in data])

    # check permissions
    response = user_api_client.post_graphql(query, variables)
    assert_no_permission(response)


def test_query_contatto(
    staff_api_client,
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

    query = CONTATTO_QUERY
    # ricreo l'id di graphene per individuare l'untente in graphene
    ID = graphene.Node.to_global_id("Contatto", contatto1.id)
    variables = {"id": ID}
    staff_api_client.user.user_permissions.add(
        permission_manage_users, permission_manage_orders
    )
    response = staff_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    data = content["data"]["contatto"]
    assert data["denominazione"] == contatto1.denominazione
    assert data["userExtra"]["email"] == contatto1.user_extra.user.email
    assert data["telefono"] == contatto1.telefono
    assert data["uso"] == contatto1.uso
    

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
                 "telefono":"+39 0457834054",
                 "uso":TipoContatto.FATTURAZIONE
                 }
    response = staff_api_client.post_graphql(MUTATION_CREA_CONTATTO, variables)
    content = get_graphql_content(response)
    data = content["data"]["contattoCrea"]["contatto"]
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    contatti = Contatto.objects.filter(user_extra = user_extra)
    assert len(contatti) == 1
    contatto = contatti.first()
    assert contatto is not None
    assert data["denominazione"] == contatto.denominazione
    assert data["email"] == contatto.email
    assert data["telefono"] == contatto.telefono
    assert data["uso"] == contatto.uso
    assert data["userExtra"]["email"] == contatto.user_extra.user.email
    # no access for normal user
    response_user = user_api_client.post_graphql(MUTATION_CREA_CONTATTO, variables)
    assert_no_permission(response_user)
    # UPDATE -----
    ID = graphene.Node.to_global_id("Contatto", contatto.pk)
    variables = {"id": ID, 
                 "denominazione":"modificata denominazione",
                 "email":"contatto.modificato@test.it",
                 "telefono":"+39 0456520415",
                 "uso":TipoContatto.CONSEGNA
                 }
    response = staff_api_client.post_graphql(MUTATION_AGGIORNA_CONTATTO, variables)
    content = get_graphql_content(response)
    data = content["data"]["contattoAggiorna"]["contatto"]
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    contatti = Contatto.objects.filter(user_extra = user_extra)
    assert len(contatti) == 1
    contatto = contatti.first()
    assert contatto is not None
    assert data["denominazione"] == contatto.denominazione
    assert data["email"] == contatto.email
    assert data["telefono"] == contatto.telefono
    assert data["uso"] == contatto.uso
    assert data["userExtra"]["email"] == contatto.user_extra.user.email
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
    mutation crea_cliente (
        $email:String!
        $denominazione:String!,
        $piva:String,
        $cf:String,
        $pec:String,
        $sdi:String,
        $rifAmmin:String,
        $splitPayment:Boolean,
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
            }
            userExtra{
                email
                denominazione
                piva
                cf
                pec
                sdi
                rifAmmin,
                splitPayment
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
    iva_id = iva.pk
    listino = Listino.objects.create(nome="pubblico",ricarico=0.34,info="Cliente finale")
    listino_id = listino.pk
    variables = {
                    "email":email,
                    "denominazione":"den test",
                    "piva":"01628380238",
                    "cf":"gngntnt28d26s4",
                    "pec":"bandieregrigolni@pec.it",
                    "sdi":"m5uecc",
                    "rifAmmin":"rif ammin",
                    "splitPayment":False,
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
    #controllo corrispondenza a database con i dati restituiti dalla mutazione
    users = UserExtra.objects.filter(user__email = email)
    assert len(users) == 1
    user = users.first()
    assert user is not None
    assert data["email"] == user.user.email
    #TODO testare altri campi, dare come ritorno alla mutazione un oggetto utenteExtra

    # no access for normal user
    response_user = user_api_client.post_graphql(MUTATION_CREA_CLIENTE, variables)
    assert_no_permission(response_user)
    
    # UPDATE -----
    