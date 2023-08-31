from .preventivo import PreventivoCrea, PreventivoCancella


class PreventivoMutation():
    # STAFF ----------

    preventivo_crea = PreventivoCrea.Field()
    preventivo_cancella = PreventivoCancella.Field()
    pass