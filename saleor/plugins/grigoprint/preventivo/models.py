from django.db import models

from saleor.plugins.grigoprint.accountExtra.models import UserExtra
from saleor.plugins.grigoprint.prodottoPersonalizzato.models import ProdottoPersonalizzato



class PreventivoManager(models.Manager):
    pass
class Preventivo(models.Model):
    objects = PreventivoManager()

    # number = models.IntegerField(unique=True, default=get_preventivo_number, editable=False)
    
    user_extra = models.ForeignKey(
        UserExtra, 
        related_name="preventivi", 
        on_delete=models.CASCADE,
        null=False, blank=False
    )
    
    precedente = models.ForeignKey(
        "Preventivo", 
        related_name="successivo", 
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    billing_address = models.ForeignKey(
        "account.Address",
        related_name="+",
        editable=False,
        null=True,
        on_delete=models.SET_NULL,
    )
    shipping_address = models.ForeignKey(
        "account.Address",
        related_name="+",
        editable=False,
        null=True,
        on_delete=models.SET_NULL,
    )
    # TODO sendHistory (quando si invia un preventivo si registra una copia di quello inviato)

class PreventivoLine(models.Model):
    preventivo = models.ForeignKey(
        Preventivo, 
        related_name="lines", 
        on_delete=models.CASCADE,
        editable=False)

    variant = models.ForeignKey(
        "product.ProductVariant",
        related_name="+",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    # personalizzazione
    personalizzazione = models.ForeignKey(
        ProdottoPersonalizzato,
        related_name="preventivo_line",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    #visibile
    codice_prodotto = models.CharField()
    descrizione_prodotto = models.CharField()
    prezzo_netto = models.DecimalField()
    quantita = models.PositiveIntegerField(default=0)
    sconto = models.FloatField(default=0)
    iva = models.FloatField()
