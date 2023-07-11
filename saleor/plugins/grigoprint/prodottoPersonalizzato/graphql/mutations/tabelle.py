import graphene

from saleor.graphql.core.mutations import ModelDeleteMutation, ModelMutation
from saleor.graphql.core.types.common import ProductError
from saleor.permission.enums import ProductPermissions

from ... import models
from .. import type


#----- TipoStampa

class TipoStampaInput(graphene.InputObjectType):
    nome = graphene.String(required=True)
    stampante = graphene.String()
    fornitore = graphene.String()

class TipoStampaCrea(ModelMutation):

    class Arguments:
        input = TipoStampaInput(
            description="Fields required to create a TipoStampa.", required=True
        )
    class Meta:
        description = "Creates a new TipoStampa."
        # permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        model = models.TipoStampa
        object_type = type.TipoStampa
        error_type_class = ProductError
        error_type_field = "product_errors"

class TipoStampaAggiorna(ModelMutation):

    class Arguments:
        id = graphene.ID(description="ID of Iva to update", required=True)
        input = TipoStampaInput(
            description="Fields required to create a TipoStampa.", required=True
        )
    class Meta:
        description = "Update a new TipoStampa."
        # permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        model = models.TipoStampa
        object_type = type.TipoStampa
        error_type_class = ProductError
        error_type_field = "product_errors"

class TipoStampaCancella(ModelDeleteMutation):

    class Arguments:
        id = graphene.ID(description="ID of TipoStampa to delete", required=True)
    class Meta:
        description = "Delete a TipoStampa."
        # permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        model = models.TipoStampa
        object_type = type.TipoStampa
        error_type_class = ProductError
        error_type_field = "product_errors"

#----- Tessuto

class TessutoInput(graphene.InputObjectType):
    nome = graphene.String(required=True)
    grammi = graphene.Int()
    altezza = graphene.Int()
    fornitore = graphene.String()

class TessutoCrea(ModelMutation):

    class Arguments:
        input = TessutoInput(
            description="Fields required to create a Tessuto.", required=True
        )
    class Meta:
        description = "Creates a new Tessuto."
        # permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        model = models.Tessuto
        object_type = type.Tessuto
        error_type_class = ProductError
        error_type_field = "product_errors"

class TessutoAggiorna(ModelMutation):

    class Arguments:
        id = graphene.ID(description="ID of Tessuto to update", required=True)
        input = TessutoInput(
            description="Fields required to create a Tessuto.", required=True
        )
    class Meta:
        description = "Update a new Tessuto."
        # permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        model = models.Tessuto
        object_type = type.Tessuto
        error_type_class = ProductError
        error_type_field = "product_errors"

class TessutoCancella(ModelDeleteMutation):

    class Arguments:
        id = graphene.ID(description="ID of Tessuto to delete", required=True)
    class Meta:
        description = "Delete a Tessuto."
        # permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        model = models.Tessuto
        object_type = type.Tessuto
        error_type_class = ProductError
        error_type_field = "product_errors"


#----- TessutoStampato

class TessutoStampatoInput(graphene.InputObjectType):
    tipo_stampa = graphene.ID(required=True)
    tessuto = graphene.ID(required=True)
    velocita_stampa = graphene.Decimal()
    velocita_calandra = graphene.Decimal()
    carta_protezione = graphene.Int()
    note = graphene.String()

class TessutoStampatoCrea(ModelMutation):

    class Arguments:
        input = TessutoStampatoInput(
            description="Fields required to create a TessutoStampato.", required=True
        )
    class Meta:
        description = "Creates a new TessutoStampato."
        # permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        model = models.TessutoStampato
        object_type = type.TessutoStampato
        error_type_class = ProductError
        error_type_field = "product_errors"

    @classmethod
    def clean_input(cls, info: graphene.ResolveInfo, instance, data, *, input_cls=None):
        tipo_stampa_id = data.pop("tipo_stampa")
        tessuto_id = data.pop("tessuto")
        cleaned_input = super().clean_input(info, instance, data)
        cleaned_input["tipo_stampa"] = models.TipoStampa.objects.get(pk=tipo_stampa_id)
        cleaned_input["tessuto"] = models.Tessuto.objects.get(pk=tessuto_id)
        return cleaned_input

class TessutoStampatoAggiorna(ModelMutation):

    class Arguments:
        id = graphene.ID(description="ID of TessutoStampato to update", required=True)
        input = TessutoStampatoInput(
            description="Fields required to create a TessutoStampato.", required=True
        )
    class Meta:
        description = "Update a new TessutoStampato."
        # permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        model = models.TessutoStampato
        object_type = type.TessutoStampato
        error_type_class = ProductError
        error_type_field = "product_errors"

class TessutoStampatoCancella(ModelDeleteMutation):

    class Arguments:
        id = graphene.ID(description="ID of TessutoStampato to delete", required=True)
    class Meta:
        description = "Delete a TessutoStampato."
        # permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        model = models.TessutoStampato
        object_type = type.TessutoStampato
        error_type_class = ProductError
        error_type_field = "product_errors"

