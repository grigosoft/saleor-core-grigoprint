from django.db import models
from typing import Union
from saleor.graphql.core import ResolveInfo

from saleor.graphql.core.mutations import ModelMutation, ModelMutationOptions
from ...account.models import User, App

from django.core.exceptions import (
    NON_FIELD_ERRORS,
    ImproperlyConfigured,
    ValidationError,
)

def get_user_extra_or_None(root: User):
    if isinstance(root, User):
        try:
            return root.extra
        except: # root.extra.DoesNotExist:
            return None
    return None

# TODO generalizzare i models con extra mettendo "saleor"/"parent" ( non in nome particolare "user"/"checkout")
# def get_extra_or_create(root: models.Model, extra_model: models.Model):
#     try:
#         return root.extra
#     except: # root.extra.DoesNotExist:
#         return extra_model.objects.create()




class ModelExtraMutation(ModelMutation):
    class Meta:
        abstract = True
    # def __init_subclass_with_meta__(
    #     cls,
    #     model_extra=None,
    #     _meta=None,
    #     **options,
    # ):
    #     if not model_extra:
    #         raise ImproperlyConfigured("model_extra is required for ModelExtraMutation")  # noqa: F821
    #     if not _meta:
    #         _meta = ModelMutationOptions(cls)
    #     _meta.model_extra = model_extra
    #     super().__init_subclass_with_meta__(_meta=_meta, **options)

    # @classmethod
    # def get_instance_extra(cls, info: ResolveInfo, instance):
    @classmethod
    def _get_attr_arguments_extra(cls):
        input = getattr(cls.Arguments, "input")
        return getattr(input, "extra")
    @classmethod
    def clean_input_extra(cls, info: ResolveInfo, data):
        input_cls = cls._get_attr_arguments_extra()
        data_extra = data.get("extra")
        return ModelMutation.clean_input(info, None, data_extra, input_cls= input_cls)
    # @classmethod
    # def save_extra(cls, info: ResolveInfo, instance, cleaned_input, /):
    #     cls.save(info, instance, cleaned_input)

    # @classmethod
    # def post_save_action(cls, info: ResolveInfo, instance, cleaned_input):
    #     """Perform an action after saving an object and its m2m."""
    #     instance_extra = cls.get_instance_extra(info, instance)
    #     cleaned_input_extra = cls.clean_input_extra(info, cleaned_input["extra"])

    #     instance_extra = super().construct_instance(instance_extra, cleaned_input_extra)
    #     super().clean_instance(info, instance_extra)
    #     cls.save_extra(info, instance_extra, cleaned_input_extra)
