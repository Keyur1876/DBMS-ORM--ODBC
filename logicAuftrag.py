from dbConnect import sessionLoader
from mapper import Mitarbeiter, Auftrag, Kunde, Montage, Ersatzteil
from checker import handleInputInteger, handleInputDatum
import datetime
from sqlalchemy import exc, or_

def getAuftrag(p_mitnr):
    """ Definition der Funktion getMitarbeiter
    Die Funktion ruft alle Aufträge des Mitarbeiter für die übergebene Mitarbeiternummer 
    der kommenden Kalenderwoche ab und gibt sie tabellarisch aus.

    :param  p_mitnr - Mitarbeiternummer
    :return eingabe_aufnr - Auftragsnummer, die vom Benutzer eingegeben wurde
    :rtype  int
    """
    jetzt = datetime.datetime.now()  # ermitteln des aktuellen Datums
    aktuelle_woche = jetzt.isocalendar()[1]  # ermitteln der aktuellen Kalenderwoche
    naechste_woche = aktuelle_woche + 1  # ermitteln der nächsten Kalenderwoche
    anz_auftraege = 0

    session = sessionLoader()
    # Abruf der Mitarbeiterdaten zur übergebenen Mitarbeiternummer
    mitarbeiter = session.query(Mitarbeiter).get(p_mitnr)
    # Überprüfung, ob der Mitarbeiter in der vorher ausgewählten Niederlassung tätig ist, ist nicht nötig, da
    # in getMitarbeiter nur Mitarbeiternummern der Niederlassung eingegeben werden können.
    
    # Abbruch, falls der Mitarbeiter nicht vorhanden ist
    if isinstance(mitarbeiter, type(None)):
        print(f'Mitarbeiter mit der MitNr: {p_mitnr} existiert nicht in der Datenbank.')
        session.close()
        return 0 
    
    # Ausgabe der Mitarbeiterdaten
    print(f'{mitarbeiter.Name}, {mitarbeiter.Vorname} - {mitarbeiter.Geburtsdatum.strftime(format="%d.%m.%Y")}, {mitarbeiter.Job}')
    print()
    
    # Task 7.2: Liste der gültigen Auftragsnummern, die angezeigt wurden
    liste_aufnr = [0]  # 0 bedeutet "zurück" / keine Auswahl
    # Alle Aufträge des Mitarbeiters ermitteln
    if len(mitarbeiter.ListeAuftrag) > 0:  # Überprüfung, ob Aufträge ermittelt werden konnten
        print(f'Die Aufträge des Mitarbeiters {mitarbeiter.Name} in den Kalenderwochen {aktuelle_woche} und {naechste_woche}:')

        anz_auftraege = 0

        for auf in mitarbeiter.ListeAuftrag:
            # Vergleich, ob das Erledigungsdatum in dieser oder der kommenden Kalenderwoche liegt

            # Task 7.2 / Stabilität: Erledigungsdatum kann NULL sein -> überspringen
            if auf.Erledigungsdatum is None:
                continue

            if auf.Erledigungsdatum.isocalendar()[1] in (aktuelle_woche, naechste_woche):
                # Zugriff auf die Kundendaten über die Beziehung, die in Klasse Auftrag definiert ist
                print(f'{auf.AufNr} - {auf.MitId} {auf.Erledigungsdatum} {auf.Kunde.Name} {auf.Kunde.Plz} {auf.Kunde.Ort}')
                anz_auftraege += 1  # Anzahl der ausgegebenen Aufträge hochzählen

                # Task 7.2: Auftragsnummer merken, damit nur gültige Nummern auswählbar sind
                liste_aufnr.append(int(auf.AufNr))

        # Falls keine Aufträge ausgegeben wurden (keine Aufträge in der kommenden Woche liegen)
        if anz_auftraege == 0:
            print('Der Mitarbeiter hat in dieser Zeit keine Aufträge')
    print('-----------------------------------------------------------------')
    print()
    
    # Task 7.2: Auftragsnummer zur Anzeige der Ersatzteile auswählen
    # Wenn keine Aufträge angezeigt wurden, ist liste_aufnr nur [0] -> dann wird sofort 0 akzeptiert
    eingabe_aufnr = -1
    while eingabe_aufnr not in liste_aufnr:
        eingabe_aufnr = handleInputInteger('Auftragsnummer eingeben (0 = zurück)')

    session.close()
    return eingabe_aufnr  # Task 7.2: Return anpassen


def anlegenAuftrag():
    """ Definition der Funktion anlegenAuftrag
    Die Funktion legt einen neuen Autrag an. Wenn es sich um einen neuen Kunden handelt,
    wird auch der Kunde neu angelegt.
    """
    session = sessionLoader()
    eingabe_kunname = input('Name des Kunden: ')
    # Nachschlagen der Kunden mit diesem Namen
    menge_kun = session.query(Kunde).filter(Kunde.Name == eingabe_kunname).all()
    # falls es Kunden mit diesem Namen gibt
    if len(menge_kun) > 0:
        liste_kunnr = [0]  # Liste der Kundennummern mit dem ersten Element 0 anlegen
        for kun in menge_kun:
            print(f' {kun.KunNr} - {kun.Name}, {kun.Ort}')
            liste_kunnr.append(kun.KunNr)  # Kundennummer zur Liste hinzufügen
        # Eingabe der Kundennummer, wobei diese Eingabe solange wiederholt wird, bis einer der gerade
        # angezeigten Kundennummern eingegeben wird
        eingabe_kunnr = -1
        while eingabe_kunnr not in liste_kunnr:
            eingabe_kunnr = handleInputInteger('Kundenummer auswählen - neuer Kunde bitte 0 eingeben')
    else:
        eingabe_kunnr = 0
        
    # falls ein neuer Kunde angelegt werden soll -> Eingabe der Daten
    if eingabe_kunnr == 0:
        eingabe_kunname = input('Name: ')
        eingabe_kunort  = input('Ort: ')
        eingabe_kunplz  = input('PLZ: ')
        eingabe_kunstrasse = input('Straße: ')
        # Anlegen des neuen Kunden
        kunde = Kunde(eingabe_kunname, eingabe_kunort, eingabe_kunplz, eingabe_kunstrasse)
        try:
            session.add(kunde)  # Einfügen des Datensatzes in die DB
            session.commit()  # Commit - ist bei Datenänderungen zwingend erforderlich
            eingabe_kunnr = kunde.KunNr  # merken der Kundennummer, um damit weiter zu arbeiten
            print(f'Kunde {eingabe_kunnr} - {kunde.Name} angelegt.')
        except exc.SQLAlchemyError():
            print('Fehler beim einfügen des Kunden')
            session.close()
            return

    eingabe_aufdat = handleInputDatum('Auftragsdatum')
    auftrag = Auftrag(eingabe_kunnr, eingabe_aufdat)
    try:
        session.add(auftrag)
        session.commit()
        # Abfrage des neuen Auftrags aus der DB und Anzeige der Daten zur Überprüfung
        angelegter_auftrag = session.query(Auftrag).get(auftrag.AufNr)
        print()
        print(f'Neuer Auftrag: {angelegter_auftrag.AufNr} - {angelegter_auftrag.KunNr} {angelegter_auftrag.Auftragsdatum}')
        print()
    except exc.SQLAlchemyError():
        print('Fehler - Auftrag einfügen')
    session.close()


def planenAuftrag():
    """ Definition der Funktion planenAuftrag
    Bei der Planung wird dem Auftrag ein Mitarbeiter und ein Erledigungsdatum zugewiesen.
    """
    session = sessionLoader()
    # ungeplante Aufträge der letzten 20 Tage abfragen und ausgeben
    heute = datetime.datetime.now()
    abdatum = heute - datetime.timedelta(days=20)
    menge_auftrag = session.query(Auftrag) \
        .filter(Auftrag.Erledigungsdatum == None, Auftrag.Auftragsdatum > abdatum, Auftrag.Auftragsdatum <= heute) \
        .order_by(Auftrag.Auftragsdatum).all()
    if len(menge_auftrag) > 0:
        liste_aufnr = [0]  # Liste der angezeigten Auftragsnummern initialisieren
        for auf in menge_auftrag:
            print(f' {auf.AufNr} - {auf.Auftragsdatum}; {auf.Kunde.Ort}')
            liste_aufnr.append(auf.AufNr)  # Auftragsnummer zur Liste hinzufügen
        
        # Auftragsnummer eingeben lassen - muss in der erstellten Liste sein
        eingabe_aufnr = -1
        while eingabe_aufnr not in liste_aufnr:
            eingabe_aufnr = handleInputInteger('Auftragsnummer')
        if eingabe_aufnr != 0:           
            #Eingabe Erledigungsdatum
            eingabe_erldat = handleInputDatum('Erledigungsdatum')
            print("")
            
            # Absichern, dass nur Mitarbeiternummern von Monteuren oder Meistern eingegeben werden können
            menge_mitarbeiter = session.query(Mitarbeiter)\
                .filter(or_(Mitarbeiter.Job == 'Monteur', Mitarbeiter.Job == 'Meister')).all()
            liste_mit = []
            for mit in menge_mitarbeiter:
                print(f' {mit.MitId} - {mit.Name} {mit.Vorname}')
                liste_mit.append(int(mit.MitId))
            eingabe_mitid = -1
            while eingabe_mitid not in liste_mit:
                eingabe_mitid = handleInputInteger('Mitarbeiternummer')
            # Ende Absicherung
            
            # Auftragsobjekt-Objekt aus der Datenbank laden
            auftrag = session.query(Auftrag).get(eingabe_aufnr)
            # Abbruch, wenn der Auftrag nicht existiert
            if isinstance(auftrag, type(None)): 
               print(f'Auftrag {eingabe_aufnr} existiert nicht in der Datenbank.')  
               session.close()
               return
            try:
                # Update des Datensatzes mit der eingegebenen Auftragsnummer
                auftrag.Erledigungsdatum = eingabe_erldat
                auftrag.MitId = eingabe_mitid
                session.commit()
                # Abruf und Ausgabe des gerade geänderten Auftrages
                auftragUpdated = session.query(Auftrag).get(eingabe_aufnr)
                print(f' {auftragUpdated.AufNr} - Mitarbeiter: {auftragUpdated.Mitarbeiter.Name}, \
                Kunde: {auftragUpdated.Kunde.Name}, {auftragUpdated.Auftragsdatum}, {auftragUpdated.Erledigungsdatum}')
            except exc.SQLAlchemyError():
                print('Datenänderung nicht möglich.')
        else:
            print('Keine Auftragsnummer ausgewählt')
            session.close()
            return
    else:
        print('Keine neuen Aufträge vorhanden\n')
    session.close()

def erledigenAuftrag():
    """
    Task 7.3 + 7.4 – Auftrag erledigen inkl. Eingabe von Ersatzteilen

    7.3:
    - Anzeige aller geplanten Aufträge der letzten 20 Tage bis einschließlich heute
    - Auswahl einer gültigen Auftragsnummer
    - Eingabe von Dauer und Anfahrt (int) und speichern

    7.4:
    - Danach können mehrere Ersatzteile (EtID + Anzahl) erfasst werden
    - Lagerbestand prüfen (EtAnzLager muss ausreichen)
    - Wenn irgendein Teil nicht ausreicht: KEIN Speichern (Rollback von Auftrag + Montage + Lagerbestand)
    """
    session = sessionLoader()

    heute = datetime.date.today()
    abdatum = heute - datetime.timedelta(days=20)

    # "geplant" = MitId und Erledigungsdatum sind gesetzt
    menge_auftrag = (
        session.query(Auftrag)
        .filter(
            Auftrag.Auftragsdatum >= abdatum,
            Auftrag.Auftragsdatum <= heute,
            Auftrag.MitId != None,
            Auftrag.Erledigungsdatum != None
        )
        .order_by(Auftrag.Auftragsdatum)
        .all()
    )

    if len(menge_auftrag) == 0:
        print("Keine geplanten Aufträge der letzten 20 Tage vorhanden.\n")
        session.close()
        return

    print("Geplante Aufträge der letzten 20 Tage:")
    liste_aufnr = [0]
    for auf in menge_auftrag:
        mit_name = auf.Mitarbeiter.Name if auf.Mitarbeiter else "-"
        kun_name = auf.Kunde.Name if auf.Kunde else "-"
        print(f" {auf.AufNr} - AufDat: {auf.Auftragsdatum} | ErlDat: {auf.Erledigungsdatum} | MA: {mit_name} | Kunde: {kun_name}")
        liste_aufnr.append(int(auf.AufNr))

    print()
    eingabe_aufnr = -1
    while eingabe_aufnr not in liste_aufnr:
        eingabe_aufnr = handleInputInteger("Auftragsnummer eingeben (0 = zurück)")

    if eingabe_aufnr == 0:
        session.close()
        return

    # Auftrag laden
    auftrag = session.query(Auftrag).get(eingabe_aufnr)
    if auftrag is None:
        print(f"Auftrag {eingabe_aufnr} existiert nicht in der Datenbank.")
        session.close()
        return

    # Task 7.3: Dauer + Anfahrt
    dauer = handleInputInteger("Dauer eingeben")
    anfahrt = handleInputInteger("Anfahrt eingeben")

    # Task 7.4: Ersatzteile erfassen (mehrere möglich)
    # Wir sammeln erst alles, prüfen Lagerbestand, und speichern dann in EINER Transaktion.
    teile_wunsch = {}  # EtID -> Gesamtanzahl

    while True:
        etid = input("Ersatzteil EtID eingeben (Enter = fertig): ").strip()
        if etid == "":
            break

        anz = handleInputInteger("Anzahl eingeben")
        if anz <= 0:
            print("Anzahl muss > 0 sein.")
            continue

        # gleiche EtID mehrfach eingeben -> aufsummieren
        teile_wunsch[etid] = teile_wunsch.get(etid, 0) + anz

    # Wenn keine Ersatzteile eingegeben wurden, wird nur Dauer/Anfahrt gespeichert (ist erlaubt)
    try:
        # ---- WICHTIG: Alles oder Nichts ----
        # Wir verwenden commit/rollback auf einer Session:
        # Wenn Lager nicht reicht: rollback -> Auftrag bleibt unverändert und keine Montage wird gespeichert.

        # 1) Lagerbestand prüfen (nur wenn Ersatzteile eingegeben wurden)
        fehlermeldungen = []
        ersatzteile_objekte = {}  # EtID -> Ersatzteil-Objekt

        if len(teile_wunsch) > 0:
            for etid, anz_benoetigt in teile_wunsch.items():
                et = session.query(Ersatzteil).get(etid)
                if et is None:
                    fehlermeldungen.append(f"Ersatzteil {etid} existiert nicht.")
                    continue

                ersatzteile_objekte[etid] = et

                lager = et.EtAnzLager
                if lager is None:
                    lager = 0

                if lager < anz_benoetigt:
                    fehlermeldungen.append(
                        f"Nicht genug Lagerbestand für {etid} ({et.EtBezeichnung}): "
                        f"benötigt {anz_benoetigt}, verfügbar {lager}"
                    )

        # Wenn Fehler: NICHTS speichern
        if len(fehlermeldungen) > 0:
            print("\nFEHLER: Auftrag wurde NICHT gespeichert, da Lagerbestand nicht ausreicht / Daten ungültig sind:")
            for msg in fehlermeldungen:
                print(" -", msg)
            session.rollback()
            session.close()
            return

        # 2) Auftrag "erledigen" (Dauer/Anfahrt setzen)
        auftrag.Dauer = dauer
        auftrag.Anfahrt = anfahrt

        # 3) Montage speichern + Lagerbestand reduzieren
        if len(teile_wunsch) > 0:
            for etid, anz_benoetigt in teile_wunsch.items():
                et = ersatzteile_objekte[etid]

                # Lager reduzieren
                et.EtAnzLager = int(et.EtAnzLager) - int(anz_benoetigt)

                # Montage: existiert evtl. schon (PK ist EtID+AufNr)
                montage = session.query(Montage).get((etid, eingabe_aufnr))
                if montage is None:
                    montage = Montage()
                    montage.EtId = etid
                    montage.AufNr = eingabe_aufnr
                    montage.Anzahl = anz_benoetigt
                    session.add(montage)
                else:
                    montage.Anzahl = int(montage.Anzahl) + int(anz_benoetigt)

        # 4) Commit -> alles wird gespeichert
        session.commit()

        print(f"\nAuftrag {eingabe_aufnr} gespeichert: Dauer={dauer}, Anfahrt={anfahrt}")
        if len(teile_wunsch) > 0:
            print("Ersatzteile wurden gespeichert und Lagerbestand wurde angepasst.\n")
        else:
            print("Keine Ersatzteile eingegeben.\n")

    except exc.SQLAlchemyError as e:
        session.rollback()
        print("Fehler beim Speichern. Es wurde nichts übernommen (Rollback).")
        print("Fehlerdetails:", e)
    finally:
        session.close()
