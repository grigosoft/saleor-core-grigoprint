import graphene
from ...graphql.core.enums import str_to_enum

from numbers import Number


def str_strip_lower (str: str) -> str:
    return str.strip().lower() if str else ""

def str_strip_title (str: str) -> str:
    return str.strip().title() if str else ""

def random_str(len:Number) -> str:
    return "name"
def random_email() ->str:
    return "em@test.it"
def random_phone() -> str:
    return "+39 0457834054"




# ------- GRAPHENE

def choices_to_enum(enum_cls, *, type_name=None, **options) -> graphene.Enum:
    def description(choices, value) -> str:
        if not value:
            return ""
        for code, name in choices:
            if code == value.value:
                return name
        return "Valore sconosciuto"
    deprecation_reason = getattr(enum_cls, "__deprecation_reason__", None)
    if deprecation_reason:
        options.setdefault("deprecation_reason", deprecation_reason)

    type_name = type_name or (enum_cls.__name__ + "Enum")
    enum_data = [(str_to_enum(code.upper()), code) for code, name in enum_cls.CHOICES]
    return graphene.Enum(type_name, 
                         enum_data, 
                         **options,
                         description=lambda v: description(enum_cls.CHOICES, v)
                            #  enum_cls.CHOICES.get(enum_data.index(v))[1] if v in enum_data else 'Sconosciuto'
                         
                         )
