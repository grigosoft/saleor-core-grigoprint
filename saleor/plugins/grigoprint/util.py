

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