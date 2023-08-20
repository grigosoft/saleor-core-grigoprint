import datetime
from django.db import models, connection
from django.core.validators import MinValueValidator
from saleor.checkout.models import Checkout, CheckoutLine

from saleor.plugins.grigoprint.accountExtra.models import UserExtra
from saleor.plugins.grigoprint.prodottoPersonalizzato.models import ProdottoPersonalizzato

def get_numero_preventivo():
    with connection.cursor() as cursor:
        cursor.execute("SELECT nextval('preventivo_preventivo_number_seq')")
        result = cursor.fetchone()
        return result[0]
def get_anno():
    currentDateTime = datetime.datetime.now()
    date = currentDateTime.date()
    return date.year


class StatoPreventivo:
    CHECKOUT = "C"
    BOZZA = "B"
    INVIATO = "I"
    APPROVATO_DAL_CLIENE = "A"

    CHOICES = [
        (CHECKOUT, "Checkout"),
        (BOZZA, "Bozza, non inviato"),
        (INVIATO, "Preventivo"),
        (APPROVATO_DAL_CLIENE, "Approvato dal cliente"),
    ]

class PreventivoManager(models.Manager):
    pass

class Preventivo(models.Model):
    """A shopping checkout or Preventivo."""
    objects = PreventivoManager()

    checkout = models.OneToOneField(Checkout, on_delete=models.CASCADE, related_name="extra", primary_key=True)
    number = models.IntegerField(unique=True, default=get_numero_preventivo, editable=False)
    anno = models.PositiveSmallIntegerField(default=get_anno, editable=False)

    stato = models.CharField(max_length=1, choices=StatoPreventivo.CHOICES, default=StatoPreventivo.CHECKOUT)
    
    # user_extra = models.ForeignKey(
    #     UserExtra, 
    #     related_name="preventivi", 
    #     on_delete=models.CASCADE,
    #     null=False, blank=False
    # )
    
    precedente = models.ForeignKey(
        "Preventivo", 
        related_name="successivo", 
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    class Meta:
        ordering = ("-number",)
        constraints = [
            models.UniqueConstraint(
                fields=['number', 'anno'], name='unique_preventivo_number_anno'
            )
        ]

    def is_checkout(self)->bool:
        return self.stato == StatoPreventivo.CHECKOUT
    
    def is_preventivo(self)->bool:
        return not self.is_checkout()
    # TODO sendHistory (quando si invia un preventivo si registra una copia di quello inviato)

class PreventivoLine(models.Model):
    checkout_line = models.OneToOneField(CheckoutLine, on_delete=models.CASCADE, related_name="extra", primary_key=True)
    
    # personalizzazione
    personalizzazione = models.ForeignKey(
        ProdottoPersonalizzato,
        related_name="preventivo_line",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    #visibile
    
    sconto = models.FloatField(default=0)
    # iva = models.FloatField()
