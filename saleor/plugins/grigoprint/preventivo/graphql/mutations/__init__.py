from .preventivo import PreventivoCrea, PreventivoCancella
from .preventivo_lines import PreventivoLineaAggiungi, PreventivoLineaCancella

class PreventivoMutation():
    # STAFF ----------
    # Preventivo
    preventivo_crea = PreventivoCrea.Field()
    preventivo_cancella = PreventivoCancella.Field()

    # Preventivo Line
    preventivo_linea_aggiungi = PreventivoLineaAggiungi.Field()
    preventivo_linea_cancella = PreventivoLineaCancella.Field()