from saleor.account.models import User
from .models import UserExtra
from typing import Optional

def isUserExtra(user:Optional[User]) -> bool:
    """Return Boolean
    controlla se l'utente ha la parte extra, intercettaneo le eccezzioni"""
    if not user:
        return False
    try:
        user.extra # type: ignore
        return True
    except UserExtra.DoesNotExist or User.DoesNotExist:
        return False
        
def controllaOCreaUserExtra(user: "User"):
    if not isUserExtra(user):
        print("creato un user senza extra, lo aggiungo")
        userExtra = UserExtra.objects.create(user=user)
        userExtra.save()
        user.extra = userExtra # type: ignore #TODO serve??
        user.save()