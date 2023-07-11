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

from saleor.plugins.grigoprint.accountExtra.models import UserExtra, TipoPorto, TipoVettore,TipoUtente, Iva, Listino

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
IVA_QUERY = """
    query Iva {
        aliquoteIva {
            nome
            valore
            info
        }
    }
"""
LISTINI_QUERY = """
    query Listini {
        listini {
            nome
            ricarico
            info
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
                    isStaff
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
    assert all([user["node"]["isStaff"] for user in data])

    # check permissions
    response = user_api_client.post_graphql(query, variables)
    assert_no_permission(response)

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
    query = IVA_QUERY
    
    staff_api_client.user.user_permissions.add(
        permission_manage_users, permission_manage_staff
    )
    response = staff_api_client.post_graphql(query)
    content = get_graphql_content(response)
    data = content["data"]["aliquoteIva"][0]
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
    print(data)
    assert data["nome"] == listino.nome
    assert data["ricarico"] == listino.ricarico
    assert data["info"] == listino.info