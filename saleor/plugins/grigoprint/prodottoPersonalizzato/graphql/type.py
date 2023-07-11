import graphene
from graphene_django import DjangoObjectType

from .. import models

class TipoStampa(DjangoObjectType):
    class Meta:
        description = "TipoStampa"
        model = models.TipoStampa
        fields = "__all__"

class Tessuto(DjangoObjectType):
    class Meta:
        description = "Tessuto"
        model = models.Tessuto
        fields = "__all__"

class TessutoStampato(DjangoObjectType):
    class Meta:
        description = "Collegamento tra Tessuto e Stampa"
        model = models.TessutoStampato
        fields = "__all__"

class Macro(DjangoObjectType):
    class Meta:
        description = "Finitura Macro"
        model = models.Macro
        fields = "__all__"

class Particolare(DjangoObjectType):
    class Meta:
        description = "Particolare della finiutra macro"
        model = models.Particolare
        fields = "__all__"

class Dato(DjangoObjectType):
    class Meta:
        description = "Possibili dati del particolare della finitura macro"
        model = models.Dato
        fields = "__all__"

class ParticolareMacro(DjangoObjectType):
    class Meta:
        description = "Collegamento tra Particolare e Macro"
        model = models.ParticolareMacro
        fields = "__all__"

class DatoParticolare(DjangoObjectType):
    class Meta:
        description = "collegamento tra Dato e Particolare"
        model = models.DatoParticolare
        fields = "__all__"
        