
from django.db import models
from django.db.models import Q, Exists, OuterRef, UniqueConstraint
from typing import Union
from saleor.account.models import Group


class Settore(models.Model):
    
    nome = models.TextField(primary_key=True)
    gruppo_permessi = models.ForeignKey(Group, models.SET_NULL, null=True, blank=True)
    # stati = models.JSONField(default=dict)
    precedente = models.ForeignKey("self", related_name="successivo",on_delete=models.SET_NULL, null=True)

class Stato(models.Model):
    nome = models.TextField(primary_key=True)
    precedente = models.ForeignKey("self", related_name="successivo", null=True, on_delete=models.SET_NULL)
    settore = models.ForeignKey(Settore, related_name="stati", on_delete=models.CASCADE)

    @property
    def slug(self) -> str:
        return "_".join([self.settore.nome, self.nome])
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['settore', 'nome'], name='unique_stato_settore_nome'
            )
        ]
# class WorkFlow(models.Model):
#     prodotto = models.ForeignKey(ProdottoPersonalizzato, related_name="workflows", on_delete=models.CASCADE)
#     settori = models.ManyToManyField(Settore)
