
import graphene

from saleor.graphql.core.types.common import NonNullList

from .. import type


class AccountExtraBaseInput(graphene.InputObjectType):
    denominazione = graphene.String(required=True)
    
    piva = graphene.String()
    cf = graphene.String()
    pec = graphene.String()
    sdi = graphene.String(description="Codice destinatario per fatturazione elettronica: SDI o pec")
    # pubblica amministrazione
    rif_ammin = graphene.String()
    split_payment = graphene.Boolean()
