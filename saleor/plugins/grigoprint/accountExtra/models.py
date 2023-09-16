
from django.db import models
from django.db.models import Q, Exists, OuterRef, UniqueConstraint
from typing import Union

from saleor.order.models import Order

from ....account.models import PossiblePhoneNumberField, User, UserManager

from .enum import TipoUtente, TipoContatto,TipoPorto,TipoVettore


class Iva(models.Model):
    nome = models.CharField(max_length=256, blank=False,null=True, unique=True)
    valore = models.FloatField()
    info = models.TextField(blank=True, default="")
class Listino(models.Model):
    nome = models.CharField(max_length=256, blank=False,null=False, unique=True)
    ricarico = models.FloatField(default=0)
    info = models.TextField(blank=True, default="")

# ## il manager aggiunge funzionalità a NomeModello.objects
class UserExtraManager(models.Manager["UserExtra"]):
    def staff(self):
        return self.get_queryset().filter(user__is_staff=True)

    def rappresentanti(self):
        return self.get_queryset().filter(
            Q(user__is_staff=True) & Q(is_rappresentante=True)
        )
    
    # def userExtrafromUser(self, user):
    #     return self.get_queryset().filter(user=user.id).first()

    def clienti(self, rappresentante:Union["UserExtra",None] = None):
        if rappresentante and rappresentante.is_rappresentante:
            clienti = self.get_queryset().filter(rappresentante=rappresentante)
        else:
            orders = Order.objects.values("user_id")
            clienti = self.get_queryset().filter(
                Q(user__is_staff=False)
                | (Q(user__is_staff=True) & (Exists(orders.filter(user_id=OuterRef("user__pk")))))
            )

        return clienti

class UserExtra(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="extra", primary_key=True)
    objects = UserExtraManager() # "userManager"
    
    denominazione = models.TextField(null=True, blank=True)
    id_danea = models.TextField(null=True, blank=True, unique=True)
    tipo_utente = models.CharField(max_length=9,
                  choices=TipoUtente.CHOICES,
                  default=TipoUtente.AZIENDA)

    # tel = PossiblePhoneNumberField(null=True,blank=True, default="", db_index=True)
    # cell = PossiblePhoneNumberField(null=True,blank=True, default="", db_index=True)
    # TODO contatto_default = models.ForeignKey(Contatto, related_name="-", , null=True, blank=True, on_delete=models.SET_NULL)

    #is_no_login = models.BooleanField(default=False) # sostituito per 
    #rappresentante
    is_rappresentante = models.BooleanField(default=False,null=False)
    rappresentante = models.ForeignKey(User, related_name="clienti", null=True,blank=True, on_delete=models.SET_NULL)
    #nome_rappresentante = models.CharField(max_length=256, blank=True) # nel caso si cancellasse il riferimento esterno al rappresentante
    commissione = models.FloatField(default=0,null=False, blank=True)
    # dati azienda
    piva = models.TextField(null=True, blank=True, unique=True, default=None)
    cf = models.TextField(null=True, blank=True, unique=True)
    pec = models.EmailField(null=True, blank=True)
    sdi = models.TextField(null=True, blank=True)
    #Pubblica amministrazione
    rif_ammin = models.TextField(null=True, blank=True)
    split_payment = models.BooleanField(default=False)

    iva = models.ForeignKey(Iva, null=True,blank=True, on_delete=models.SET_NULL)
    porto = models.CharField(null=True, blank=True, max_length=3,
                  choices=TipoPorto.CHOICES,
                  default=TipoPorto.FRANCO_CON_ADDEBITO)
    vettore = models.CharField(null=True, blank=True, max_length=2,
                  choices=TipoVettore.CHOICES,
                  default=TipoVettore.VETTORE_GLS)
    pagamento = models.TextField(null=True, blank=True, default = "Bonifico anticipato")
    coordinate_bancarie = models.TextField(null=True, blank=True)
    listino = models.ForeignKey(Listino, null=True,blank=True, on_delete=models.SET_NULL)
    sconto = models.FloatField(default=0,null=False, blank=True)



# class ContattoManager(models.Manager):
#     pass
class Contatto(models.Model):
    # objects = ContattoManager()
    
    UniqueConstraint(fields=['user_extra', 'email', 'telefono'], name='unique_contatto')
    
    user_extra = models.ForeignKey(UserExtra, related_name="contatti", on_delete=models.CASCADE,null=False, blank=False)
    email = models.EmailField(unique=False, db_index=True)
    denominazione = models.CharField(max_length=256, blank=True)
    telefono = PossiblePhoneNumberField(blank=True, default="", db_index=True)
    uso  = models.CharField(null=False, blank=False, max_length=1,
                  choices=TipoContatto.CHOICES,
                  default=TipoContatto.GENERICO)


