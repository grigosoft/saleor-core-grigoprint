
from typing import Optional
from saleor.account.error_codes import AccountErrorCode
from saleor.graphql.account.types import User
from django.core.exceptions import ValidationError

from saleor.plugins.grigoprint.accountExtra.enum import TipoUtente
from ...util import isUserExtra
from ...models import Contatto, Listino
from .... import util


PERMESSO_CAMPI_RAPPRESENTANTE=["commissione", "sconto"]
PERMESSO_CAMPI_ADMIN=PERMESSO_CAMPI_RAPPRESENTANTE.extend(["id_danea", "is_rappresentante"]) #TODO completa la lista

def accerta_user_extra_or_error(user:Optional["User"]) -> User:
    if not user or not isUserExtra(user):
        raise ValidationError(
            {
                "user": ValidationError(
                    f"User: '{user}' non ha la parte Extra",
                    code=AccountErrorCode.NOT_FOUND.value,
                )
            }
        )
    return user
def accerta_rappresentante_or_error(user:Optional["User"])-> User:
    user = accerta_user_extra_or_error(user)
    if not user.extra.is_rappresentante:
        raise ValidationError(
            {
                "user": ValidationError(
                    f"User'{user}' non è un rappresentante",
                    code=AccountErrorCode.INVALID.value,
                )
            }
        )
    return user
def accerta_cliente_del_rappresentante_or_error(rappresentante:Optional["User"], cliente:Optional["User"]):
    rappresentante = accerta_rappresentante_or_error(rappresentante)
    cliente = accerta_user_extra_or_error(cliente)
    is_cliente = rappresentante.clienti.filter(id=cliente.id).first()

    if not is_cliente:
        raise ValidationError(
            {
                "user": ValidationError(
                    f"Cliente'{cliente}' non è un cliente associato a '{rappresentante}'",
                    code=AccountErrorCode.INVALID.value,
                )
            }
        )
    return

# def save_contatto(user:"User", cleaned_data_contatto) -> Optional[Contatto]:
#     if cleaned_data_contatto:
#         print(user)
#         print(user.extra)
#         contatto = user.extra.contatti.create(
#             user_extra = user.extra,
#             denominazione = cleaned_data_contatto["denominazione"],
#             email = cleaned_data_contatto["email"],
#             telefono = cleaned_data_contatto["telefono"],
#             uso = cleaned_data_contatto["uso"],
#         )
    #     return contatto
    # return None
    
# def save_contatti(user:"User", cleaned_data_contatti):
#     if cleaned_data_contatti:
#         for cleaned_data_contatto in cleaned_data_contatti:
#             save_contatto(user=user, cleaned_data_contatto=cleaned_data_contatto)

def clean_contatto(user:"User", cleaned_input, data_contatto):
    pass

# def clean_contatti(user:"User", cleaned_input, data_contatti):
#     for data_contatto in data_contatti:
#         clean_contatto(user, cleaned_input, data_contatto)

def clean_is_rappresentante(user:"User", cleaned_input, data):
    is_rappresentante = cleaned_input.get("is_rappresentante", False)
    cleaned_input["is_rappresentante"] = is_rappresentante
    if is_rappresentante:
        pass #TODO aggiungo al gruppo permessi IS_RAPPRESENTANTE
def save_is_rappresentante(user:"User", cleaned_data):
    user.extra.commissione = cleaned_data.get("is_rappresentante", False)
    user.extra.commissione = cleaned_data.get("commissione", 0)
    user.extra.save(only_fields=["is_rappresentante","commissione"])

def clean_assegna_rappresentante(cls, info, user:"User", cleaned_input):
    rappresentante_id = cleaned_input.get("rappresentante_id", None)
    if rappresentante_id:
        rappresentante = cls.get_node_or_error(info, rappresentante_id, only_type=User)
        accerta_rappresentante_or_error(rappresentante)
        cleaned_input["rappresentante"] = rappresentante

def save_assegna_rappresentante(user:"User", cleaned_data):
    rappresentante = cleaned_data.get("rappresentante", None)
    if rappresentante:
        user.extra.rappresentante = rappresentante
        user.extra.save(only_fields=["rappresentante"])

def save_user_extra_base(user:"User", cleaned_data):
    """crea le informazioni base dell'UserExtra"""
    # if not isUserExtra(user):
    #     user.extra.create()
    user_extra = user.extra
    user_extra.denominazione=cleaned_data["denominazione"]
        # user_extra.tipo_utente=cleaned_data["tipo_utente"]
    user_extra.piva=cleaned_data.get("piva", "")
    user_extra.cf=cleaned_data.get("cf", "")
    user_extra.pec=cleaned_data.get("pec", "")
    user_extra.sdi=cleaned_data.get("sdi", "")
    user_extra.rif_amministrazione=cleaned_data.get("rif_amministrazione", "")
    user_extra.split_payment=cleaned_data.get("split_payment", False)
    user_extra.save()
        
def save_user_extra(user:"User", cleaned_data):
    """salva le informazioni dell'UserExtra, NON i contatti, NON is rappresentante"""
    save_user_extra_base(user, cleaned_data)
    user_extra = user.extra
    user_extra.id_danea = cleaned_data.get("id_danea", "")
    user_extra.tipo_utente = cleaned_data.get("tipo_utente", TipoUtente.AZIENDA)
    user_extra.iva = cleaned_data.get("iva", "")
    user_extra.porto = cleaned_data.get("porto", "")
    user_extra.vettore = cleaned_data.get("vettore", "")
    user_extra.pagamento = cleaned_data.get("pagamento", "")
    user_extra.listino = cleaned_data.get("listino", "")
    user_extra.sconto = cleaned_data.get("sconto", 0)
    user_extra.save()


def clean_user_extra_base(user:"User", cleaned_input, data):
    pass

def clean_user_extra(user:"User", cleaned_input, data):
    clean_user_extra_base(user,cleaned_input,data)
    # formattazione fatta a front-end
    # email = cleaned_input.get("email")
    # if email:
    #     cleaned_input["email"] = util.str_strip_lower(email)
    # first_name = cleaned_input.get("first_name")
    # if first_name:
    #     cleaned_input["first_name"] = util.str_strip_title(first_name)
    # last_name = cleaned_input.get("last_name")
    # if last_name:
    #     cleaned_input["last_name"] = util.str_strip_title(last_name)
    cleaned_input_extra = cleaned_input["extra"]
    listino_id = cleaned_input_extra.get("listino_id", None)
    if listino_id:
        cleaned_input_extra["listino"] = Listino.objects.filter(id=listino_id)
    iva_id = cleaned_input_extra.get("iva_id", None)
    if listino_id:
        cleaned_input_extra["listino"] = Listino.objects.filter(id=iva_id)

    # TODO aggiunta automatica al gruppo permessi dei rappresentanti
    # is_rappresentante = cleaned_input.get("is_rappresentante")
    # if is_rappresentante:
    pass
