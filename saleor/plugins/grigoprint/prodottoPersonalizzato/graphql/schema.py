import graphene
from saleor.graphql.core import ResolveInfo
from saleor.graphql.core.fields import PermissionsField
from saleor.permission.enums import ProductPermissions
from . import type
from .. import models


class ProdottoPersonalizzatoQueries(graphene.ObjectType):
    tipiStampa = graphene.List(
        type.TipoStampa,
        description="elenco tipi stampa",
    )
    def resolve_tipiStampa(_root, info):
        return models.TipoStampa.objects.all()
    
    tessuti = graphene.List(
        type.Tessuto,
        description="elenco tessuti",
    )
    def resolve_tessuti(_root, info):
        return models.Tessuto.objects.all()
    
    tessutiStampati = graphene.List(
        type.TessutoStampato,
        description="elenco combinazioni tra tipoStampa e tessuto",
    )
    def resolve_tessuti_stampati(_root, info):
        return models.TessutoStampato.objects.all()
    
    macro = PermissionsField(
        type.Macro,
        permissions=[
            # ProductPermissions.MANAGE_PRODUCTS
        ],
        description="elenco tipi stampa",
    )
    def resolve_macro(_root, info: ResolveInfo, **kwargs):
        return models.Macro.objects.all()
    
    particolri = PermissionsField(
        type.Particolare,
        permissions=[
            # ProductPermissions.MANAGE_PRODUCTS
        ],
        description="elenco tipi stampa",
    )
    def resolve_particolari(_root, info: ResolveInfo, **kwargs):
        return models.Particolare.objects.all()
    
    dati = PermissionsField(
        type.Dato,
        permissions=[
            # ProductPermissions.MANAGE_PRODUCTS
        ],
        description="elenco tipi stampa",
    )
    def resolve_dati(_root, info: ResolveInfo, **kwargs):
        return models.Dato.objects.all()
    
    particolariMacro = PermissionsField(
        type.ParticolareMacro,
        permissions=[
            # ProductPermissions.MANAGE_PRODUCTS
        ],
        description="elenco tipi stampa",
    )
    def resolve_particolari_macro(_root, info: ResolveInfo, **kwargs):
        return models.ParticolareMacro.objects.all()
    
    datiParticolari = PermissionsField(
        type.DatoParticolare,
        permissions=[
            # ProductPermissions.MANAGE_PRODUCTS
        ],
        description="elenco tipi stampa",
    )
    def resolve_dati_particolari(_root, info: ResolveInfo, **kwargs):
        return models.DatoParticolare.objects.all()