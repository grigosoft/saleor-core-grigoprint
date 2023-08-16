
        
from saleor.permission.enums import BasePermissionEnum


# attenzione! per andare l'import di queste classi
# deve essere fatto dopo la creazione in saleor di BasePermissionEnum
# quando si aggiora guardare se cambia posto

class GrigoprintPermissions(BasePermissionEnum):
    MANAGE_RAPPRESENTANTI = "grigoprint.manage_rappresentanti" 