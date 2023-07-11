from decimal import Decimal
from django.db import models

from saleor.plugins.grigoprint.accountExtra.models import UserExtra


# -----------------riferimenti per elenco finiture e stampa (NO SALVATAGGIO PRODOTTI)
class TipoStampa(models.Model):
    nome = models.CharField(max_length=256, unique=True)
    stampante = models.CharField(max_length=256, blank=True)
    fornitore = models.CharField(max_length=256, blank=True)


class Tessuto(models.Model):
    nome = models.CharField(max_length=256, unique=True)
    grammi = models.PositiveSmallIntegerField(default=0)
    altezza = models.PositiveSmallIntegerField(default=0)
    fornitore = models.CharField(max_length=256, blank=True)
    # tipi_stampa ? multi-multi

class TessutoStampato(models.Model):
    tipo_stampa = models.ForeignKey(
        TipoStampa,
        related_name="tessuti",
        on_delete=models.CASCADE
    )
    tessuto = models.ForeignKey(
        Tessuto,
        related_name="tipi_stampa",
        on_delete=models.CASCADE
    )
    velocita_stampa = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal("0.0"),
        null=True, blank=True
    )
    velocita_calandra = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.0"),
        null=True, blank=True
    )
    carta_protezione = models.PositiveSmallIntegerField(default=0)
    note = models.TextField(null=True, blank=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['tipo_stampa', 'tessuto'], name='unique_stampa_tessuto_combination'
            )
        ]

class Macro(models.Model):
    nome = models.CharField(max_length=256, unique=True)
    descrizione = models.TextField()
    # prodotti
    # categoria?
    # img
class Particolare(models.Model):
    nome = models.CharField(max_length=256, unique=True)
    descrizione = models.TextField(null=True, blank=True)
    # img
class Dato(models.Model):
    nome = models.CharField(max_length=256, unique=True)
    tipo = models.CharField(max_length=256) # string numero bool ecc
    # img
class ParticolareMacro(models.Model):
    particolare = models.ForeignKey(
        Particolare,
        related_name="macro",
        on_delete=models.CASCADE
    )
    finitura = models.ForeignKey(
        Macro,
        related_name="particolari",
        on_delete=models.CASCADE
    )
    # img
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['particolare', 'finitura'], name='unique_particolare_finitura_combination'
            )
        ]
class DatoParticolare(models.Model):
    particolare = models.ForeignKey(
        Particolare,
        related_name="dati",
        on_delete=models.CASCADE
    )
    dato = models.ForeignKey(
        Dato,
        related_name="particolari",
        on_delete=models.CASCADE
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['particolare', 'dato'], name='unique_particolare_dato_combination'
            )
        ]

# class Posizione(models.Model):
#     nome = models.CharField()

    
# ---------------- SALVATAGGIO PRODOTTI

class ProdottoPersonalizzato(models.Model):
    variante = models.ForeignKey(
        "product.ProductVariant",
        related_name="+",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    tessuto_stampato = models.ForeignKey(
        TessutoStampato,
        related_name="+",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    #finiture = models.ManyToOneRel()
    # files grafici
    # files altri?
    # anteprima

    #collegamento ai vari documenti
    # linea_preventivo
    # linea_checkout
    # linea_ordine


class File(models.Model):
    prodotto_personalizzato = models.ForeignKey(
        ProdottoPersonalizzato,
        related_name="files",
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
    )
    quantita = models.PositiveIntegerField(default=1)
    #anteprima
    #indirizzo su disco

class Finitura(models.Model):
    prodottoPersonalizzato = models.ForeignKey(
        ProdottoPersonalizzato,
        related_name="finiture",
        on_delete=models.CASCADE
    )
    finitura = models.ForeignKey(
        ParticolareMacro,
        related_name="+",
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
    )
    dati_finitura = models.JSONField()
    # posizione = models.ForeignKey( # TODO forse in enum basta
    #     Posizione,
    #     related_name="+",
    #     on_delete=models.SET_NULL
    # )
