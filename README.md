# DierSignaal pilot v0.2 — lokaal testbaar

**Uitsluitend fictieve data. Niet gebruiken in productie of met echte dier-/persoonsgegevens.**

## Starten

Python 3.10+ (alleen standaardbibliotheek):

```bash
cd diersignaal-pilot
python3 run.py
```

Open http://127.0.0.1:8100

De publieke conceptpagina **Over DierSignaal** staat op http://127.0.0.1:8100/about. Deze beschrijft de initiatiefnemers, uitnodiging tot samenwerking en de grenzen van de demonstratie. Controleer biografieën, contactroute en status voordat materiaal extern wordt gedeeld.

Demo-dierenarts: `arts.west` / `PilotDemo!2026`. Demo-beheerder: `beheerder` / `PilotDemo!2026`. Inloggen vereist ook een code per e-mail.

Chipnummer `999000000000001`; consult `CONS-W-1001`.
Tweede account: `arts.noord`, goedgekeurde consultreferentie `CONS-N-3001`.
`reviewer` heeft geen toegang tot dierdossiers. Alle demo-accounts delen uitsluitend voor deze lokale pilot het wachtwoord; voor echte toegang is dit onacceptabel.

## Account- en beheerdemo

- Dierenartsen kunnen via **Account aanvragen** een account registreren. Het account krijgt alleen de dierenartsrol en blijft inactief tot `beheerder` het goedkeurt.
- Een actief account logt in met wachtwoord én een eenmalige code die via geconfigureerde SMTP-over-TLS wordt verzonden. Nieuwe of gewijzigde e-mailadressen moeten eerst met een code worden bevestigd; beheer verzendt die code nadat het account is aangemaakt. De verificatiecode verloopt na 15 minuten.
- De beheerder kan dierenartsaccounts goedkeuren/deactiveren, en een eenmalige herstelcode van 15 minuten laten genereren. De gebruiker vult die code in bij **Wachtwoord vergeten?**. Geef herstelcodes alleen rechtstreeks en gecontroleerd door.
- In **Beheer** kan de beheerder fictieve honden- en kattendossiers bekijken, toevoegen en aanpassen. Chipnummers en bestaande signalen zijn niet verwijderbaar via de demo.
- `DIERSIGNAAL_ADMIN_PASSWORD` wordt alleen bij het aanmaken van een nieuw beheerdersaccount toegepast; wijzig een bestaand wachtwoord via de herstelprocedure.

Voor de e-mailcodes zijn minimaal `DIERSIGNAAL_SMTP_HOST` en `DIERSIGNAAL_SMTP_FROM` nodig. De mailserver moet impliciet TLS op poort 465 ondersteunen; configureer optioneel `DIERSIGNAAL_SMTP_PORT`, `DIERSIGNAAL_SMTP_USER` en `DIERSIGNAAL_SMTP_PASSWORD`. TLS-certificaatcontrole staat aan; gebruik alleen `DIERSIGNAAL_SMTP_CA` voor een vertrouwde CA-bundel. Stel voor een eerste lokale beheerlogin ook `DIERSIGNAAL_ADMIN_EMAIL` in. Eventuele demo-e-mailadressen kunnen vooraf worden gezet met `DIERSIGNAAL_EMAIL_ARTS_WEST`, `DIERSIGNAAL_EMAIL_ARTS_NOORD` en `DIERSIGNAAL_EMAIL_REVIEWER`. Op een bestaande database wordt het beheeradres alleen automatisch ingevuld wanneer dat nog leeg is. Gebruik mailboxen die je beheert.

De codes worden niet door de applicatie gelogd of in API-antwoorden getoond; SMTP-fouten blokkeren de login (fail closed). Zonder mailconfiguratie kan geen login worden afgerond. De lokale demo genereert een interne sleutel bij iedere start; voor een beheerde omgeving moet `DIERSIGNAAL_MFA_SECRET` als stabiel geheim in veilige opslag worden ingesteld. Deze e-mail-MFA en accountflows zijn nog geen productiegeschikt identiteitsbeheer of phishingbestendige MFA. Beroepsidentiteit wordt niet geverifieerd. Stel deze demo niet bloot aan internet en voer geen echte gegevens in.

## Automatische tests

```bash
python3 -m unittest discover -s tests -v
```

De tests starten de drie services en een lokale TLS-mailtestserver op tijdelijke poorten, maken tijdelijk een testcertificaat met de `openssl`-CLI en gebruiken een aparte tijdelijke database. Geen externe Python-pakketten nodig.

## Architectuur

- `services/gateway.py`: publieke (alleen localhost) webserver, static frontend en API-router.
- `services/identity.py`: gebruikers, PBKDF2-wachtwoordhashes, 30-minuten sessies, autorisatiebeleid en tevoren gekoppelde consulten.
- `services/signals.py`: dieren, observaties, conceptregistraties en auditgebeurtenissen. Vraagt voor **elke** actie expliciete toestemming aan identity.
- `data/identity.sqlite3` en `data/signals.sqlite3`: strikt gescheiden SQLite-bestanden.
- `web/`: loginpagina en dashboard zonder afhankelijkheden.
- `web/about.html`: publieke informatiepagina voor het concept; nog geen operationeel meldpunt.

## Pilotvoorbereiding

- `docs/PILOT_PROTOCOL.md`: conceptprotocol voor een begeleide verkenning met maximaal drie dierenartsen; geen goedkeuring voor verwerking van echte gegevens.
- `docs/DPIA_PREPARATION.md`: inventarisatie en risico-/besluitenlijst ter voorbereiding van beoordeling door de verantwoordelijke organisatie en deskundigen; geen afgeronde DPIA.
- `docs/ACCEPTANCE.md`: openstaande criteria. Geen criterium is automatisch voldaan door deze documenten of de demo.

Alle drie services luisteren op `127.0.0.1`; interne API's eisen een tijdens het starten gegenereerd gedeeld geheim. Dit is een demonstratiegrens, **geen security boundary voor een publiek netwerk**. De sessie wordt uitsluitend in JavaScript-geheugen gehouden (verversen logt uit).

## Belangrijkste beperkingen

- Geen echte koppeling met chipregisters, dierenartsenregister of bronsystemen.
- Consulten zijn vooraf als fictieve toegangsrechten ingevoerd. Er is **geen** geverifieerde behandelrelatie of beroepsbevoegdheid in de werkelijkheid.
- E-mail-MFA vereist correct ingerichte SMTP/TLS en geverifieerde mailboxen; geen account-lockout of IP-rate limiting en geen centraal identiteitsbeheer. Niet internet-facing maken.
- Geen TLS omdat de demo uitsluitend op localhost draait. Voor een echte omgeving vereisten: OIDC + MFA, sterke service-authenticatie (bijv. mTLS), databaseversleuteling, isolatie, veilige sleutelopslag en centraal toezicht.
- Audit heeft een hashketen maar is nog niet append-only/extern verankerd; databasebeheerders kunnen logs wijzigen.
- Geen publicatieflow: nieuwe signalen blijven concept, niet zichtbaar bij lookup.
- Geen breed zoeken of eigenaarprofilering. Identificatie gebeurt uitsluitend via exact fictief chipnummer.
- Geen externe meldingen of automatische verdenking, risicoscore of eigenaar-blacklist.

## Juridische toetsing

Zie `docs/LEGAL_REVIEW.md`, `docs/THREAT_MODEL.md` en `docs/ARCHITECTURE.md`. De documenten uit v0.1 zijn uitgangspunten, niet reeds gevalideerde compliancedocumenten. Toets zeker rechtmatigheid, beroepsgeheim, verantwoordelijkheden, noodzaak van centrale signalering, bewaartermijnen, rechten van betrokkenen en DPIA.
