# DierSignaal pilot v0.2 — lokaal testbaar

**Uitsluitend fictieve data. Niet gebruiken in productie of met echte dier-/persoonsgegevens.**

## Starten

Python 3.10+ (alleen standaardbibliotheek):

```bash
cd diersignaal-pilot
python3 run.py
```

Open http://127.0.0.1:8100

Demo: `arts.west` / `PilotDemo!2026`

Chipnummer `999000000000001`; consult `CONS-W-1001`.
Tweede account: `arts.noord`, goedgekeurde consultreferentie `CONS-N-3001`.
`reviewer` heeft geen toegang tot dierdossiers. Alle demo-accounts delen uitsluitend voor deze lokale pilot het wachtwoord; voor echte toegang is dit onacceptabel.

## Automatische tests

```bash
python3 -m unittest discover -s tests -v
```

De tests starten de drie services op tijdelijke poorten en gebruiken een aparte tijdelijke database. Geen externe Python-pakketten nodig.

## Architectuur

- `services/gateway.py`: publieke (alleen localhost) webserver, static frontend en API-router.
- `services/identity.py`: gebruikers, PBKDF2-wachtwoordhashes, 30-minuten sessies, autorisatiebeleid en tevoren gekoppelde consulten.
- `services/signals.py`: dieren, observaties, conceptregistraties en auditgebeurtenissen. Vraagt voor **elke** actie expliciete toestemming aan identity.
- `data/identity.sqlite3` en `data/signals.sqlite3`: strikt gescheiden SQLite-bestanden.
- `web/`: loginpagina en dashboard zonder afhankelijkheden.

Alle drie services luisteren op `127.0.0.1`; interne API's eisen een tijdens het starten gegenereerd gedeeld geheim. Dit is een demonstratiegrens, **geen security boundary voor een publiek netwerk**. De sessie wordt uitsluitend in JavaScript-geheugen gehouden (verversen logt uit).

## Belangrijkste beperkingen

- Geen echte koppeling met chipregisters, dierenartsenregister of bronsystemen.
- Consulten zijn vooraf als fictieve toegangsrechten ingevoerd. Er is **geen** geverifieerde behandelrelatie of beroepsbevoegdheid in de werkelijkheid.
- Geen MFA, account-lockout, IP-rate limiting of centraal identiteitsbeheer. Niet internet-facing maken.
- Geen TLS omdat de demo uitsluitend op localhost draait. Voor een echte omgeving vereisten: OIDC + MFA, sterke service-authenticatie (bijv. mTLS), databaseversleuteling, isolatie, veilige sleutelopslag en centraal toezicht.
- Audit heeft een hashketen maar is nog niet append-only/extern verankerd; databasebeheerders kunnen logs wijzigen.
- Geen publicatieflow: nieuwe signalen blijven concept, niet zichtbaar bij lookup.
- Geen breed zoeken of eigenaarprofilering. Identificatie gebeurt uitsluitend via exact fictief chipnummer.
- Geen externe meldingen of automatische verdenking, risicoscore of eigenaar-blacklist.

## Juridische toetsing

Zie `docs/LEGAL_REVIEW.md`, `docs/THREAT_MODEL.md` en `docs/ARCHITECTURE.md`. De documenten uit v0.1 zijn uitgangspunten, niet reeds gevalideerde compliancedocumenten. Toets zeker rechtmatigheid, beroepsgeheim, verantwoordelijkheden, noodzaak van centrale signalering, bewaartermijnen, rechten van betrokkenen en DPIA.
