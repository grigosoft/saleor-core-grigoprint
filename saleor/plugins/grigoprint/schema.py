# richiamare in saleor.graphql.api


from .accountExtra.graphql.mutation import AccountExtraMutation
from .accountExtra.graphql.schema import AccountQueries
# from .prodottoPersonalizzato.graphql.schema import ProdottoPersonalizzatoQueries
# from .gestioneAzienda.graphql.mutation import FerieAggiorna, FerieConferma, FerieCrea, FerieElimina, FerieRichiedi, NotificaAggiorna, NotificaConferma, NotificaCrea, NotificaElimina, SettoreCrea, SettoreAggiorna, SettoreElimina
# from .gestioneAzienda.graphql.schema import GestioneAziendaQueries
# from .prima_configurazione_saleor import PrimaConfigurazioneSaleor

class GrigoprintQueries(
    AccountQueries,
    # GestioneAziendaQueries,
    # ProdottoPersonalizzatoQueries
):
    pass


class GrigoprintMutations(AccountExtraMutation):
    pass
