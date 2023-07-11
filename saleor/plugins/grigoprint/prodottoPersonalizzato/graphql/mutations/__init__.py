from .tabelle import TessutoAggiorna, TessutoCancella, TessutoCrea, TessutoStampatoAggiorna, TessutoStampatoCancella, TessutoStampatoCrea, TipoStampaCrea, TipoStampaAggiorna,TipoStampaCancella

class ProdottoPersonalizzatoMutation():
    # STAFF ----------

    # tabelle
    tipo_stampa_crea = TipoStampaCrea.Field()
    tipo_stampa_aggiorna = TipoStampaAggiorna.Field()
    tipo_stampa_cancella = TipoStampaCancella.Field()
    tessuto_crea = TessutoCrea.Field()
    tessuto_aggiorna = TessutoAggiorna.Field()
    tessuto_cancella = TessutoCancella.Field()
    tessuto_stampato_crea = TessutoStampatoCrea.Field()
    tessuto_stampato_aggiorna = TessutoStampatoAggiorna.Field()
    tessuto_stampato_cancella = TessutoStampatoCancella.Field()

