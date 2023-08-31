

from saleor.graphql.account.types import User
from saleor.graphql.core import ResolveInfo
from saleor.plugins.grigoprint.accountExtra.graphql.util import accerta_cliente_del_rappresentante_or_error
from saleor.plugins.grigoprint.accountExtra.util import is_rappresentante
from saleor.plugins.grigoprint.preventivo.graphql.util import controlla_o_crea_checkoutextra



def controllo_permessi_rappresentante_preventivo(cls, info: ResolveInfo, cliente:User):
    if cliente:
        requestor = info.context.user
        if is_rappresentante(requestor):
            accerta_cliente_del_rappresentante_or_error(requestor, cliente)


def clean_preventivo(cls, info: ResolveInfo, instance, cleaned_input, data):
    user = cleaned_input["extra"].get("user",None)
    if user:
        user = cls.get_node_or_error(info, user, only_type=User)
        cleaned_input["extra"]["user"] = user
        cleaned_input["email"] = user.email
    


def save_preventivo(cls, info: ResolveInfo, instance, cleaned_input):
    preventivo = controlla_o_crea_checkoutextra(instance)
    user = cleaned_input["extra"]["user"]
    if user:
        instance.user = user
        instance.save()
    
    stato = cleaned_input["extra"]["stato"]
    if stato:
        preventivo.stato = stato
    preventivo.save()

