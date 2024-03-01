
from typing import Optional
from saleor.account.error_codes import AccountErrorCode
from saleor.graphql.account.types import User
from django.core.exceptions import ValidationError
from saleor.graphql.core import ResolveInfo
from saleor.graphql.core.utils import from_global_id_or_error

from saleor.permission.enums import AccountPermissions
from saleor.plugins.grigoprint.accountExtra.enum import TipoUtente
from saleor.plugins.grigoprint.accountExtra.graphql.mutation.user import add_user_extra_search_document_value
from saleor.plugins.grigoprint.accountExtra.graphql.util import accerta_rappresentante_or_error, accerta_cliente_del_rappresentante_or_error, is_rappresentante
from saleor.plugins.grigoprint.permissions import GrigoprintPermissions
# from ...util import isUserExtra, controllaOCreaUserExtra
from ... import models
from .. import type
from .... import util


PERMESSO_CAMPI_RAPPRESENTANTE=["commissione", "sconto"]
PERMESSO_CAMPI_ADMIN=PERMESSO_CAMPI_RAPPRESENTANTE.extend(["id_danea", "is_rappresentante"]) #TODO completa la lista


def clean_contatto(cls, info: ResolveInfo, user:"User", cleaned_input, data):
    requestor = info.context.user
    if is_rappresentante(requestor):
        accerta_cliente_del_rappresentante_or_error(requestor, user)
    

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
    user.extra.save()#only_fields=["is_rappresentante","commissione"])

def clean_assegna_rappresentante(cls, info, user:"User", cleaned_input):
    """
    casistiche assegna rappresentante:
    permessi: manage_users (per forza)
    + se il requestor è rappresentante, può assegnare solo se stesso
    + se il requestor ha il permesso di gestire i rappresentanti: manage_rappresentanti
    """
    rappresentante = cleaned_input.get("rappresentante", None)
    if rappresentante:
        requestor = info.context.user
        if requestor:
            # rappresentante = cls.get_node_or_error(info, rappresentante_id, only_type=User)
            accerta_rappresentante_or_error(rappresentante)
            if (
                (requestor.extra.is_rappresentante and requestor.id == rappresentante.id) or 
                requestor.has_perm(GrigoprintPermissions.MANAGE_RAPPRESENTANTI)
                ):
                cleaned_input["rappresentante"] = rappresentante
                
            else:
                raise ValidationError(
                    {
                        "user": ValidationError(
                            f"User'{requestor}' può assegnare solo se stesso o deve avere il permesso '{GrigoprintPermissions.MANAGE_RAPPRESENTANTI}'",
                            code=AccountErrorCode.INVALID.value,
                        )
                    }
                )
        else:
            raise ValidationError(
                    {
                        "user": ValidationError(
                            f"Requestor '{requestor}' deve essere un istanza di User",
                            code=AccountErrorCode.INVALID.value,
                        )
                    }
                )

def save_assegna_rappresentante(user:"User", cleaned_data):
    rappresentante = cleaned_data.get("rappresentante", None)
    if rappresentante:
        user.extra.rappresentante = rappresentante
        user.extra.save(update_fields=["rappresentante"])

def save_user_extra_base(user:"User", cleaned_data):
    """crea le informazioni base dell'UserExtra"""
    # if not isUserExtra(user):
    #     user.extra.create()
    user_extra = user.extra
    user_extra.denominazione=cleaned_data["denominazione"]
        # user_extra.tipo_utente=cleaned_data["tipo_utente"]
    piva = cleaned_data.get("piva", None)
    user_extra.piva = piva if piva != "" else None
    cf = cleaned_data.get("cf", None)
    user_extra.cf = cf if cf != "" else None
    user_extra.pec=cleaned_data.get("pec", "")
    user_extra.sdi=cleaned_data.get("sdi", "")
    user_extra.coordinate_bancarie=cleaned_data.get("coordinate_bancarie", "")
    user_extra.rif_ammin=cleaned_data.get("rif_ammin", "")
    user_extra.split_payment=cleaned_data.get("split_payment", False)
    user_extra.save()
    #search vector
    user_extra.user.search_document = add_user_extra_search_document_value(user_extra)
    user_extra.user.save(update_fields=["search_document", "updated_at"])
        
def save_user_extra(user:"User", cleaned_data):
    """salva le informazioni dell'UserExtra, NON i contatti, NON is rappresentante"""
    save_user_extra_base(user, cleaned_data)
    user_extra = user.extra
    user_extra.id_danea = cleaned_data.get("id_danea", None)
    user_extra.tipo_utente = cleaned_data.get("tipo_utente", TipoUtente.AZIENDA)
    user_extra.iva = cleaned_data.get("iva", None)
    user_extra.porto = cleaned_data.get("porto", "")
    user_extra.vettore = cleaned_data.get("vettore", "")
    user_extra.pagamento = cleaned_data.get("pagamento", "")
    user_extra.listino = cleaned_data.get("listino", None)
    user_extra.sconto = cleaned_data.get("sconto", 0)
    user_extra.save()


def clean_user_extra_base(user:"User", cleaned_input_extra, data):
    pass

def clean_user_extra(user:"User", cleaned_input_extra, data):
    clean_user_extra_base(user,cleaned_input_extra,data)
    # formattazione fatta a front-end?
    # email = cleaned_input.get("email")
    # if email:
    #     cleaned_input["email"] = util.str_strip_lower(email)
    # first_name = cleaned_input.get("first_name")
    # if first_name:
    #     cleaned_input["first_name"] = util.str_strip_title(first_name)
    # last_name = cleaned_input.get("last_name")
    # if last_name:
    #     cleaned_input["last_name"] = util.str_strip_title(last_name)

    # listino_id = cleaned_input_extra.get("listino_id", None)
    # if listino_id:
    #     _model, listino_id = from_global_id_or_error(listino_id, type.Listino)
    #     cleaned_input_extra["listino"] = models.Listino.objects.filter(pk=listino_id).first()
    # iva_id = cleaned_input_extra.get("iva_id", None)
    # if iva_id:
    #     _model, iva_id = from_global_id_or_error(iva_id, type.Iva)
    #     cleaned_input_extra["iva"] = models.Iva.objects.filter(pk=iva_id).first()

    # TODO aggiunta automatica al gruppo permessi dei rappresentanti
    # is_rappresentante = cleaned_input.get("is_rappresentante")
    # if is_rappresentante:
    pass
