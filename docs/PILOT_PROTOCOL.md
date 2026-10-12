# Pilotprotocol — werkdocument, nog niet goedgekeurd

**Status:** concept ter bespreking met dierenartsen, privacy-/juridisch adviseur en beoogde verantwoordelijke organisatie. Dit document is geen toestemming om persoonsgegevens, dierdossiers of echte meldingen te verwerken. De huidige software is alleen een lokale demonstratie met fictieve data.

## 1. Doel en onderzoeksvragen

Verken met maximaal drie dierenartsen of een zorgvuldig, beperkt ondersteunend proces bruikbaar is om welzijnssignalen bij honden en katten te documenteren en professioneel te bespreken. De pilot beoordeelt de workflow en technische bruikbaarheid; zij stelt geen mishandeling vast, doet geen voorspellingen en vervangt geen klinisch oordeel, meldcode of officiële meldroute.

Voor de start leggen de verantwoordelijke organisatie en deelnemers vast:

- welke onderzoeksvragen worden beantwoord en welke uitkomsten niet worden geclaimd;
- waarom drie deelnemers passend zijn en welke praktijken/rollen deelnemen;
- of de pilot uitsluitend met fictieve/synthetische casussen kan worden uitgevoerd;
- wanneer een eventuele fase met echte casussen noodzakelijk, rechtmatig en proportioneel is;
- wie de pilot kan pauzeren of beëindigen en op welke gronden.

## 2. Reikwijdte en uitsluitingen

**Beoogd:** kleinschalige, begeleide evaluatie van de invoerstructuur, autorisatieconcepten en collegiale beoordeling.

**Buiten scope, tenzij afzonderlijk goedgekeurd:**

- automatische risicoscores, verdenkingen, eigenaarprofielen of beslissingen;
- eigenaarcontactgegevens, bulkzoeken, openbare zoekfuncties of gegevens uit chipregisters;
- automatische publicatie, landelijke signalering of koppeling met politie, toezichthouders of andere meldpunten;
- gebruik als spoedvoorziening, diagnose-instrument of vervanging van bestaande professionele routes;
- productiegebruik van de huidige localhost-demo.

## 3. Rollen en verantwoordelijkheden — in te vullen

| Rol | Naam/organisatie | Verantwoordelijkheid | Nog te bevestigen |
|---|---|---|---|
| Verwerkingsverantwoordelijke | `[in te vullen]` | Doel, middelen, rechtmatigheid, transparantie en rechten | Ja |
| Pilotcoördinator | `[in te vullen]` | Protocol, deelnemers, incidenten en stopbesluiten | Ja |
| Veterinaire inhoudelijk verantwoordelijke | `[in te vullen]` | Klinische workflow, kwaliteitskaders en escalatie | Ja |
| Privacy-/juridisch adviseur of FG/DPO | `[in te vullen]` | Onafhankelijke toets en DPIA-advies | Ja |
| Technisch beheerder/verwerker(s) | `[in te vullen]` | Beveiliging, toegang, logging en afspraken | Ja |
| Deelnemende dierenartsen (maximaal 3) | `[in te vullen]` | Gebruik volgens instructie en melden van incidenten | Ja |

De rolverdeling en eventuele gezamenlijke verantwoordelijkheid moeten juridisch worden vastgesteld; deze tabel kent die rollen niet zelf toe.

## 4. Gegevens- en casusregels

Vóór iedere pilotfase is een goedgekeurde gegevensinventaris nodig. Neem alleen gegevens op die aantoonbaar noodzakelijk zijn. Scheid in de interface en werkinstructies:

1. waargenomen feiten en bron/methode;
2. verklaring van eigenaar/verzorger, duidelijk als verklaring gemarkeerd;
3. professionele duiding, onzekerheden en alternatieve verklaringen;
4. mogelijke vervolgstappen en menselijke beoordelingsbeslissing.

Gebruik voor de technische evaluatie bij voorkeur alleen volledig fictieve of onomkeerbaar geanonimiseerde casussen. Een chipnummer is een identificator en kan in combinatie met een register of andere gegevens herleidbaar worden. Gebruik daarom geen echte chipnummers, herleidbare casusdetails of eigenaargegevens zonder voorafgaande beoordeling en goedkeuring. Pseudonimisering alleen maakt gegevens niet anoniem.

Leg per gegevenscategorie vast: doel, bron, grondslag, toegangsgroep, ontvangers, bewaartermijn, verwijdermethode en procedure voor inzage, correctie, betwisting en verwijdering. De juridische adviseur bepaalt welke informatie aan betrokkenen moet worden verstrekt en welke uitzonderingen eventueel gelden.

## 5. Menselijke beoordeling en correcties

- Iedere relevante duiding blijft herkenbaar als mening van een benoemde bevoegde professional, niet als vastgesteld feit.
- Definieer vooraf wanneer een tweede beoordelaar nodig is; registreer diens eigen beoordeling en eventuele afwijkende visie.
- Ontwerp een correctie- en betwistingsproces dat de oorspronkelijke auditgeschiedenis niet stilzwijgend overschrijft.
- Bepaal wie besluit over delen of escaleren, op welke professionele grond, en hoe de meldcode en geheimhoudingsplichten worden gevolgd.
- Beperk inzage tot rol en taak; beoordeel autorisaties vooraf en periodiek.

## 6. Beveiliging, incidenten en beheer

De huidige demo heeft geen productiegeschikte identiteitsverificatie, MFA, rate limiting, TLS-inrichting, centrale onveranderbare logging of operationeel herstelproces. Deze punten zijn **no-go's** voor echte data. Voor een pilot met persoonsgegevens zijn minimaal nodig: goedgekeurde hosting en servicegrenzen, unieke geverifieerde accounts, sterke authenticatie, least privilege, beveiligde back-ups, geteste herstelprocedure, bewaartermijnen, monitoring, logging, incidentrespons, contact- en escalatieroutes en passende contractuele afspraken.

Leg vóór start vast wie incidenten ontvangt, hoe toegang onmiddellijk kan worden ingetrokken, wie beoordeelt of betrokkenen/toezichthouder moeten worden geïnformeerd en hoe bewijs wordt bewaard.

## 7. Evaluatie en stopcriteria

Evalueer met deelnemers: begrijpelijkheid, volledigheid, foutkansen, toegangsgedrag, werklast, correcties, ervaren veiligheid en ongewenste neveneffecten. Gebruik geen casusinhoud in evaluatierapporten tenzij daar afzonderlijk noodzaak en toestemming/rechtsgrond voor zijn vastgesteld.

Pauzeer de pilot direct bij onder meer onbevoegde toegang, verlies of verkeerde koppeling van gegevens, onduidelijkheid over wettelijke grondslag, onjuist gebruik als bewijs of besluit, ernstige professionele bezwaren, of onvermogen om rechtenverzoeken/incidenten af te handelen. Hervatting vereist gedocumenteerde beoordeling en akkoord van de verantwoordelijke organisatie.

## 8. Goedkeuring vóór start

- [ ] Doel, scope, uitkomsten en stopcriteria goedgekeurd.
- [ ] Verantwoordelijke organisatie en rolverdeling schriftelijk bevestigd.
- [ ] Juridische beoordeling en eventuele DPIA afgerond; restrisico geaccepteerd.
- [ ] Gegevensinventaris, rechtsgrond per doel, transparantie en rechtenproces vastgesteld.
- [ ] Beveiligingsontwerp, verwerkersafspraken, penetratietest en hersteltest afgerond.
- [ ] Deelnemers geverifieerd, geïnstrueerd en formeel akkoord.
- [ ] Klinische werkwijze en relatie tot meldcode door bevoegde deskundigen beoordeeld.
- [ ] Incident-, bezwaar-, correctie-, bewaartermijn- en verwijderprocessen getest.
- [ ] Schriftelijk besluit dat de gekozen pilotfase mag starten.

Geen enkel vakje is met het aanmaken van dit document afgevinkt.
