import datetime
from decimal import Decimal
from django.conf import settings
from django.db import models, connection
from django.core.validators import MinValueValidator
from saleor.checkout.models import Checkout, CheckoutLine

from saleor.plugins.grigoprint.accountExtra.models import UserExtra
from saleor.plugins.grigoprint.prodottoPersonalizzato.models import ProdottoPersonalizzato

def get_numero_preventivo():
    reset = False
    ultimo_preventivo = Preventivo.objects.last()
    if not ultimo_preventivo or ultimo_preventivo.anno < get_anno():
        reset = True
    with connection.cursor() as cursor:
        if reset:
            cursor.execute("SELECT setval('preventivo_preventivo_number_seq',1)")
        else:
            cursor.execute("SELECT nextval('preventivo_preventivo_number_seq')")
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            raise ConnectionError("Select a DB della sequenza preventivo fallita.", cursor.db.errors_occurred)
    
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
    number = models.IntegerField(default=get_numero_preventivo, editable=False)
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
        ordering = ("-anno","-number",)
        constraints = [
            models.UniqueConstraint(
                fields=['number', 'anno'], name='unique_preventivo_number_anno'
            )
        ]

    @property
    def is_checkout(self)->bool:
        return self.stato == StatoPreventivo.CHECKOUT
    @property
    def is_preventivo(self)->bool:
        return not self.is_checkout
    @property
    def numero(self)->str:
        return f"{self.anno}/{self.number}"
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
    
    descrizione_forzata = models.TextField(null=True, blank=True)
    prezzo_netto_forzato = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        null=True,blank=True
    )
    sconto = models.FloatField(default=0)
    # iva = models.FloatField()
