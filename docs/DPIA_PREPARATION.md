# DPIA-voorbereiding — inventarisatie, geen afgeronde DPIA

**Status:** voorbereidingsdocument voor de beoogde verwerkingsverantwoordelijke en privacy-/juridisch adviseur. Dit is geen juridisch advies of DPIA. Alleen de verantwoordelijke organisatie kan, met passende deskundigheid, de noodzaak van een DPIA bepalen, deze uitvoeren en resterende risico's formeel accepteren.

## 1. Beschrijving van het beoogde project

| Vraag | Huidige stand / te beantwoorden |
|---|---|
| Project en versie | DierSignaal; huidige repository bevat een localhost-demo |
| Doel(en) van verwerking | Nog vast te stellen; maak doelen specifiek per handeling |
| Beoogde verantwoordelijke(n) | Onbekend; expliciet aanwijzen en juridisch toetsen |
| Verwerkers en ontvangers | Nog onbekend; inventariseer hosting, beheer, adviseurs, deelnemers en eventuele ontvangers |
| Betrokkenen | Mogelijk dierenartsen, praktijkmedewerkers en identificeerbare eigenaren/verzorgers |
| Gegevens | Demo bevat fictieve accounts, chipnummers, dierkenmerken en veterinaire observaties; reële pilotset nog te bepalen |
| Bronnen/koppelingen | Geen echte chipregisters of beroepsregisters aangesloten |
| Doelgroep/toegang | In demo: lokale dierenartsaccounts en beheerder; geen werkelijkheidstoets van bevoegdheid |
| Bewaartermijn | Niet vastgesteld voor een echte pilot |
| Hosting/locatie/doorgifte | Demo draait lokaal; productie-/pilotarchitectuur is niet vastgesteld |

Een diermedisch gegeven is niet automatisch een persoonsgegeven, maar een chipnummer, casuscontext of combinatie met registers kan personen identificeerbaar maken. Informatie over vermoedens kan bijzondere juridische risico's geven. Laat deskundigen elke gegevenscategorie en koppeling beoordelen.

## 2. Noodzaak en proportionaliteit te beoordelen

Beantwoord en documenteer voor elke afzonderlijke verwerking:

- Welk concreet dierenwelzijnsdoel wordt nagestreefd en waarom is verwerking noodzakelijk?
- Kan hetzelfde doel met minder gegevens, lokale dossiers, collegiale bespreking of een federatieve verwijzing worden bereikt?
- Welke juridische grondslag geldt voor verzamelen, bewaren, raadplegen, delen, beheer en eventuele escalatie?
- Welke professionele geheimhouding, sectorspecifieke regels en beperkingen rond verdenkingsgegevens zijn van toepassing?
- Hoe worden juistheid, actualiteit, herkomst, context, onzekerheid en correcties gewaarborgd?
- Hoe wordt voorkomen dat een melding, koppeling of meerdere consulten als bewijs of automatische conclusie worden behandeld?
- Welke transparantie, inzage, rectificatie, bezwaar, beperking en verwijdering zijn vereist; welke beperkingen zijn mogelijk en wie toetst die?
- Welke bewaartermijnen gelden per categorie en hoe worden back-ups, auditgegevens en verwijdering behandeld?
- Welke alternatieven en belangen van betrokkenen zijn onderzocht en waarom is de gekozen oplossing evenredig?

Toestemming van deelnemers of gebruikers is op zichzelf geen antwoord op alle vragen over de verwerking van gegevens van andere betrokkenen.

## 3. Voorlopige gegevensstroom

```text
Deelnemende dierenarts
  → account-/rolcontrole
  → doel- en behandelrelatiecontrole
  → beperkt dossier op basis van chipnummer
  → feit, bron, verklaring en professionele duiding apart
  → menselijke review / eventuele vervolgroute (nog niet geïmplementeerd)
  → audit, correctie, bewaartermijn en verwijdering (operationeel ontwerp vereist)
```

Dit is een conceptueel beeld, geen goedgekeurde verwerking. De bestaande demo heeft aparte identity- en signal-services en databases, maar gebruikt fictieve vooraf gekoppelde consultreferenties. De publieke pagina is informatief; er is geen aanmeld- of casusformulier ingebouwd.

## 4. Voorlopige risicoanalyse om met deskundigen te valideren

| Risico | Mogelijk gevolg | Bestaande demo-beperking / benodigde maatregel |
|---|---|---|
| Verkeerde identiteit, praktijk of behandelrelatie | Onrechtmatige toegang of onjuiste koppeling | Demo-accounts zijn niet werkelijk geverifieerd; voor pilot onafhankelijke verificatie en intrekking nodig |
| Ongefundeerde of contextloze melding | Reputatie-/rechtsgevolgen, verkeerde professionele actie | Feit, verklaring en interpretatie scheiden; bron, onzekerheid, review, betwisting en correctieproces |
| Onbevoegde inzage, enumeratie of export | Datalek en profiling | Rate limits, detectie, minimale antwoorden, exportbeperking, logging en periodieke toegangscontrole |
| Herleidbaarheid via chipnummer of casusdetails | Identificatie van eigenaar of dier | Dataminimalisatie; registerkoppeling alleen na aantoonbare toestemming/grondslag en contractuele toegang |
| Insider- of beheerdersmisbruik | Ongeoorloofde inzage/manipulatie | Least privilege, onafhankelijke audit, scheiding van taken en tweede goedkeuring voor gevoelige acties |
| Verlies, ransomware of onbeschikbaarheid | Vertrouwelijkheid/integriteit/beschikbaarheid en verstoring zorg | Productiehosting, encryptie, herstel/back-up- en incidenttests ontbreken |
| Onvoldoende transparantie of rechtenafhandeling | Niet-naleving en verlies van vertrouwen | Verantwoordelijke, privacy-informatie, contactpunt en geteste rechtenprocedures ontbreken |
| Onterechte indruk van officiële status | Misbruik of verkeerd vertrouwen | Site noemt zich concept/demo; formele status, contactroute en disclaimer vóór extern gebruik vaststellen |

Beoordeel kans, ernst, betrokkenen, bestaande maatregelen, restrisico en eigenaar van elke maatregel met de betrokkenen en onafhankelijke deskundigen. Deze tabel is geen risicoacceptatie.

## 5. Verplichte besluiten vóór verwerking van echte gegevens

- Identificeer de verantwoordelijke organisatie, doeleinden en rollen; leg contracten en verantwoordelijkheden vast.
- Verkrijg onafhankelijk juridisch advies over grondslagen, geheimhouding, gegevens over verdenkingen, registertoegang en meldroutes.
- Laat de bevoegde organisatie bepalen of een DPIA vereist is; voer die uit vóór verwerking waar vereist en raadpleeg de toezichthouder indien wettelijk nodig.
- Beperk pilotgegevens en deelnemers; toets of synthetische casussen voldoende zijn.
- Ontwerp onafhankelijke verificatie van dierenarts/praktijk, sterke authenticatie, veilige hosting, TLS, sleutel- en databasebescherming, audit, monitoring en herstel.
- Definieer transparantie, inzage/rechtencasus, betwisting, correctie, retentie, verwijdering en incidentcommunicatie.
- Laat veterinair deskundigen het protocol, meldcode, kwaliteitscontrole en mogelijke schade toetsen.
- Leg acceptatie van restrisico en schriftelijk go/no-go-besluit vast.

**No-go:** gebruik de repository-demo niet met echte dieren-, chip-, casus- of persoonsgegevens en stel deze niet publiek op internet beschikbaar. Een privacy- of DPIA-document maakt onveilige software of een onbeoordeelde verwerking niet rechtmatig.

## 6. Bronnen om door de verantwoordelijke te verifiëren

- Autoriteit Persoonsgegevens: actuele DPIA-richtsnoeren, verplichting en voorafgaande raadpleging.
- EUR-Lex: toepasselijke AVG-tekst en relevante nationale wetgeving.
- KNMvD: actuele veterinaire meldcode en professionele richtlijnen.
- RVO en erkende databankhouders: actuele regels en contractuele voorwaarden voor chipregistraties.

Controleer versies, toepasselijkheid en actuele officiële links bij de juridische beoordeling; deze lijst vormt geen validatie van de inhoud of beschikbaarheid van diensten.
