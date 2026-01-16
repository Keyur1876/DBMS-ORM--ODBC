from dbConnect import sessionLoader
from mapper import Ersatzteil, Montage, Auftrag

def getErsatzteilListe():
    """Zeigt alle Ersatzteile an (EtId, EtBezeichnung, EtPreis, EtAnzLager, EtHersteller)."""

    session = sessionLoader()

    try:
        teile = session.query(Ersatzteil).order_by(Ersatzteil.EtId).all()
    except Exception as e:
        print("Fehler bei der Abfrage der Ersatzteile.")
        print("Fehlerdetails:", e)
        session.close()
        return

    if len(teile) == 0:
        print("Keine Ersatzteile vorhanden.")
        session.close()
        return

    print("Ersatzteilliste:")
    print("-" * 95)
    print(f"{'EtId':<6} {'Bezeichnung':<40} {'Preis':<10} {'Anzahl':<8} {'Hersteller'}")
    print("-" * 95)

    for t in teile:
        print(f"{t.EtId:<6} {t.EtBezeichnung:<40} {t.EtPreis:<10.2f} {t.EtAnzLager:<8} {t.EtHersteller}")

    print("-" * 95)
    session.close()

    
def getErsatzteilForAuftrag(p_aufnr) :
    """ Definition der Funktion getErsatzteilForAuftrag().
    Diese Funktion ist im Rahmen des Praktikums zu implementieren.
    
    :param p_aufnr - Auftragsnummer
    
    """
    print('Zu implementieren.')


def getErsatzteilForAuftrag(p_aufnr):
    """Gibt alle verbauten Ersatzteile zu einem Auftrag aus (EtId, EtBezeichnung, Anzahl)."""

    session = sessionLoader()

    # check if order exists
    auftrag = session.query(Auftrag).get(p_aufnr)
    if auftrag is None:
        print(f"Auftrag {p_aufnr} existiert nicht.")
        session.close()
        return

    # Montage + Ersatzteil for this order
    rows = (
        session.query(Montage, Ersatzteil)
        .join(Ersatzteil, Ersatzteil.EtId == Montage.EtId)
        .filter(Montage.AufNr == p_aufnr)
        .order_by(Montage.EtId)
        .all()
    )

    if len(rows) == 0:
        print("Hinweis: Zu diesem Auftrag wurden keine Ersatzteile verbaut.")
        session.close()
        return

    print(f"Ersatzteile für Auftrag {p_aufnr}:")
    print("-" * 70)
    print(f"{'EtId':<6} {'Bezeichnung':<40} {'Anzahl':<8}")
    print("-" * 70)

    for m, e in rows:
        print(f"{e.EtId:<6} {e.EtBezeichnung:<40} {m.Anzahl:<8}")

    print("-" * 70)
    session.close()