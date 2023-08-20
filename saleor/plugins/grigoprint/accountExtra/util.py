from saleor.account.models import User
from .models import UserExtra
from typing import Optional

def is_user_extra(user:Optional[User]) -> bool:
    """Return Boolean
    controlla se l'utente ha la parte extra, intercettaneo le eccezzioni"""
    if not user:
        return False
    try:
        user.extra # type: ignore
        return True
    except UserExtra.DoesNotExist or User.DoesNotExist:
        return False
        
def controlla_o_crea_userextra(user: "User"):
    if not is_user_extra(user):
        print("creato un user senza extra, lo aggiungo")
        userExtra = UserExtra.objects.create(user=user)
        userExtra.save()
        user.extra = userExtra # type: ignore #TODO serve??
        user.save()

def is_rappresentante(user:Optional[User]) -> bool:
    return is_user_extra(user) and user.extra.is_rappresentante # type: ignore

def is_cliente_del_rappresentante(
        rappresentante:Optional["User"], 
        cliente:Optional["User"]
        )-> bool:
    if is_rappresentante(rappresentante) and is_user_extra(cliente):
        if cliente.extra.rappresentante: # type: ignore
            return cliente.extra.rappresentante.pk == rappresentante.pk # type: ignore
        else:
            # controllo se è se stesso, tutti sono rappresentanti di se stessi
            return cliente.pk == rappresentante.pk # type: ignore
    return False