import datetime
import json
import os
import re
from collections import defaultdict
from datetime import timedelta
from unittest.mock import ANY, MagicMock, Mock, call, patch
from urllib.parse import urlencode

import graphene
import pytest

from django.core.files import File

from ......account.models import Address, Group, User
from ......graphql.core.utils import str_to_enum, to_global_id_or_none

from ......graphql.tests.utils import (
    assert_graphql_error_with_message,
    assert_no_permission,
    get_graphql_content,
    get_graphql_content_from_response,
    get_multipart_request_body,
)

FULL_USER_QUERY = """
    query Utente($id: ID!) {
        utente(id: $id) {
            id
            email
            cf
            piva
            sdi
            contatti{
            email
            denominazione
            phone
            uso
            }
            rappresentante{
            email
            }
            isRappresentatnte
    
        }
    }
"""


def test_query_utente(
    staff_api_client,
    customer_user,
    gift_card_used,
    gift_card_expiry_date,
    address,
    permission_manage_users,
    permission_manage_orders,
    media_root,
    settings,
    checkout,
):
    user = customer_user
    user.default_shipping_address.country = "US"
    user.default_shipping_address.save()
    user.addresses.add(address.get_copy())

    avatar_mock = MagicMock(spec=File)
    avatar_mock.name = "image.jpg"
    user.avatar = avatar_mock
    #user extra
    user.extra.create(
        cf ="grgntnt34testok4",
        piva = "01628380238",
        sdi = "m5uxrd",
        
                      )
    user.save()


    query = FULL_USER_QUERY
    ID = graphene.Node.to_global_id("User", customer_user.id)
    variables = {"id": ID}
    staff_api_client.user.user_permissions.add(
        permission_manage_users, permission_manage_orders
    )
    response = staff_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    data = content["data"]["utente"]
    assert data["email"] == user.email
    assert data["cf"] == user.extra.cf
    assert data["lastName"] == user.last_name

    assert len(data["contatti"]) == user.extra.contatti.count()
    for contatti in data["contatti"]:
        contatto_id =  contatti["id"]

  
def test_query_clienti():
    pass

def test_query_staff_utenti():
    pass
def test_query_aliquote_iva():
    pass
def test_query_listini():
    pass