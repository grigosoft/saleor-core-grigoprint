

class TipoPorto:
    ASSEGNATO = "A"
    FRANCO = "F"
    FRANCO_CON_ADDEBITO = "FAF"

    CHOICES = [
        (ASSEGNATO, "Assegnato"),
        (FRANCO, "Franco"),
        (FRANCO_CON_ADDEBITO, "Franco con addebito in fattura")
        #("Ritiro in azienda", ""),
    ]

class TipoVettore:
    DESTINATARIO = "D"
    MITTENTE = "M"
    VETTORE = "V"
    VETTORE_GLS = "VG"
    VETTORE_DHL = "VD"
    VETTORE_BRT = "VB"

    CHOICES = [
        (DESTINATARIO, "Destinatario"),
        (MITTENTE, "Mittente"),
        (VETTORE, "Vettore"),
        (VETTORE_GLS, "Vettore GLS"),
        (VETTORE_DHL, "Vettore DHL"),
        (VETTORE_BRT, "Vettore BRT"),
    ]

class TipoUtente:
    AZIENDA = "A"
    PRIVATO = "P"
    PUBBLICA_AMMINISTRAZIONE = "PA"
    AGENZIA = "R"

    CHOICES = [
        (AZIENDA, "Azienda"),
        (PRIVATO, "Privato"),
        (PUBBLICA_AMMINISTRAZIONE, "Pubblica Amministrazione"),
        (AGENZIA, "Agenzia Pubblicitaria"),
    ]

class TipoContatto:
    GENERICO = "G"
    FATTURAZIONE = "F"
    CONSEGNA = "C"
    NOTIFICHE = "N"

    CHOICES = [
        (GENERICO, "Generico"),
        (FATTURAZIONE, "Fatturazione"),
        (CONSEGNA, "Consegna"),
        (NOTIFICHE, "Notifiche"),
    ]