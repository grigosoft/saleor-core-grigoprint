
from typing import Optional
from django.forms import ValidationError
from saleor.account.models import User
from saleor.graphql.core.enums import AccountErrorCode
from saleor.permission.enums import AccountPermissions

from saleor.plugins.grigoprint.accountExtra.models import UserExtra
from saleor.plugins.grigoprint.accountExtra.util import is_cliente_del_rappresentante, is_rappresentante, is_user_extra

def accerta_user_extra_or_error(user:Optional["User"]) -> UserExtra:
    if user and is_user_extra(user):
        return user.extra # type: ignore
    
    raise ValidationError(
        {
            "user": ValidationError(
                f"User: '{user}' non ha la parte Extra",
                code=AccountErrorCode.NOT_FOUND.value,
            )
        }
    )

def accerta_rappresentante_or_error(user:Optional["User"])-> UserExtra:
    if is_rappresentante(user):
        return user.extra # type: ignore
    
    raise ValidationError(
        {
            "user": ValidationError(
                f"User'{user}' non è un rappresentante",
                code=AccountErrorCode.INVALID.value,
            )
        }
    )

def accerta_cliente_del_rappresentante_or_error(
        rappresentante:Optional["User"], 
        cliente:Optional["User"]
        )-> UserExtra:
   
    if is_cliente_del_rappresentante(rappresentante,cliente):
        return cliente.extra # type: ignore
    
    raise ValidationError(
        {
            "user": ValidationError(
                f"Cliente'{cliente}' non è un cliente associato al rappresentante '{rappresentante}'",
                code=AccountErrorCode.INVALID.value,
            )
        }
    )
