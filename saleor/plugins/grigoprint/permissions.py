
from saleor.permission.enums import BasePermissionEnum


# attenzione! per andare l'import di queste classi
# deve essere fatto dopo la creazione in saleor di BasePermissionEnum
# quando si aggiora guardare se cambia posto

class GrigoprintPermissions(BasePermissionEnum):
    MANAGE_RAPPRESENTANTI = "grigoprint.manage_rappresentanti"

    MANAGE_STATE_CHANGE = "grigoprint.mange_state_change"
    VISUALIZZA_LAVORAZIONI_SETTORE = "grigoprint.visualizza_lavorazioni_settore"
    VISUALIZZA_LAVORAZIONI_TUTTE = "grigoprint.visualizza_lavorazioni_tutte"
