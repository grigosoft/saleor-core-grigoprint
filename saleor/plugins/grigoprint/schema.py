# richiamare in saleor.graphql.api


from .preventivo.graphql.mutations import PreventivoMutation
from .preventivo.graphql.schema import PreventivoQueries
from .accountExtra.graphql.mutation import AccountExtraMutation
from .accountExtra.graphql.schema import AccountExtraQueries
from .prodottoPersonalizzato.graphql.schema import ProdottoPersonalizzatoQueries
from .prodottoPersonalizzato.graphql.mutations import ProdottoPersonalizzatoMutation
# from .gestioneAzienda.graphql.mutation import FerieAggiorna, FerieConferma, FerieCrea, FerieElimina, FerieRichiedi, NotificaAggiorna, NotificaConferma, NotificaCrea, NotificaElimina, SettoreCrea, SettoreAggiorna, SettoreElimina
# from .gestioneAzienda.graphql.schema import GestioneAziendaQueries

class GrigoprintQueries(
    AccountExtraQueries,
    PreventivoQueries,
    # GestioneAziendaQueries,
    ProdottoPersonalizzatoQueries,
):
    pass


class GrigoprintMutations(
        AccountExtraMutation,
        PreventivoMutation,
        ProdottoPersonalizzatoMutation,
        ):
    pass
