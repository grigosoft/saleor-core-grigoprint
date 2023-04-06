from typing import Any, Optional

from django.core.management import BaseCommand, CommandError

from ...danea_firebird import import_anagrafica



class Command(BaseCommand):
    help = "Importa da danea gli utenti"

    
    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        import_anagrafica()
        return 
