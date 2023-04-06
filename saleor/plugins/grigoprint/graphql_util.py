from typing import Union
from ...account.models import User, App



def get_user_extra_or_None(root: User):
    if isinstance(root, User):
        try:
            return root.extra
        except: # root.extra.DoesNotExist:
            return None
    return None