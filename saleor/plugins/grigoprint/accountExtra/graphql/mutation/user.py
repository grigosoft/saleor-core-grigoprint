
import graphene

from saleor.graphql.core.types.common import NonNullList
from django.db.models import prefetch_related_objects

from .. import type
from ...models import UserExtra

class AccountExtraBaseInput(graphene.InputObjectType):
    denominazione = graphene.String(required=True)
    
    piva = graphene.String()
    cf = graphene.String()
    pec = graphene.String()
    sdi = graphene.String(description="Codice destinatario per fatturazione elettronica: SDI o pec")
    coordinate_bancarie = graphene.String()
    # pubblica amministrazione
    rif_ammin = graphene.String()
    split_payment = graphene.Boolean()


USER_EXTRA_SEARCH_FIELDS = ["denominazione", "piva", "cf", "pec"]
CONTATTI_SEARCH_FIELDS = ["denominazione", "telefono", "mail"]
def add_user_extra_search_document_value(
    user_extra: "UserExtra"
):
    """
    Aggiungo i campi di user extra e contatto al vettore di ricerca
    """
    search_document = user_extra.user.search_document
    search_document_extra = "\n".join([getattr(user_extra, field) for field in USER_EXTRA_SEARCH_FIELDS if getattr(user_extra, field)])
    search_document += search_document_extra
    prefetch_related_objects(
        [user_extra],
        "contatti",
    )
    for contatto in user_extra.contatti.all(): # type: ignore
        search_document += "\n".join([getattr(contatto, field) for field in CONTATTI_SEARCH_FIELDS if getattr(contatto, field)])
    
    return search_document.lower()
