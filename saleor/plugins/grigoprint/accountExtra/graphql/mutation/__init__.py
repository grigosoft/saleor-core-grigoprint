from .staff import AssegnaRappresentante, ClienteCrea, StaffCrea
from .tabelle import IvaAggiorna, IvaCancella, IvaCrea, ListinoAggiorna, ListinoCancella, ListinoCrea
from .contatto import ContattoCrea, ContattoAggiorna, ContattoCancella

class AccountExtraMutation():
    # STAFF ----------
    cliente_crea = ClienteCrea.Field()
    # cliente_aggiorna = 
    # cliente_cancella = 
    staff_crea = StaffCrea.Field()
    # staff_aggiorna = 
    # staff_cancella = #? probabilmente basta l'originale
    contatto_crea = ContattoCrea.Field()
    contatto_aggiorna = ContattoAggiorna.Field()
    contatto_cancella = ContattoCancella.Field()
    cliente_assegna_rappresentante = AssegnaRappresentante.Field()
    # tabelle
    iva_crea = IvaCrea.Field()
    iva_aggiorna = IvaAggiorna.Field()
    iva_cancella = IvaCancella.Field()
    listino_crea = ListinoCrea.Field()
    listino_aggiorna = ListinoAggiorna.Field()
    listino_cancella = ListinoCancella.Field()


    # ECOMMERCE ---------------
    # account_aggiorna = 
    # account_contatto_crea = 
    # account_contatto_aggiorna =
    # account_contatto_cancella = 
