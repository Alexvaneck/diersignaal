# Doelarchitectuur — voorstel ter beoordeling

## Trust boundaries
1. **Frontend (onvertrouwd):** nooit zelfstandig besluiten nemen over toegang. Browser toont uitsluitend door backend vrijgegeven, minimaal noodzakelijke informatie.
2. **Identity provider:** OIDC met MFA en verificatie van dierenarts, praktijk en actuele bevoegdheid. Expliciete rol, praktijkbinding en levenscyclus bij personeelswisselingen.
3. **API gateway:** TLS, aanvraag-ID, rate limiting, anti-enumeratie, strikte schema-validatie en monitoring.
4. **Policy decision point:** deny-by-default op actor, rol, praktijk, specifiek dier, doel, behandelrelatie, noodzaak, eventuele toestemming/uitzonderingsgrond en datacategorie. Her-evalueer bij iedere read/write.
5. **Dossier- en signaleringsservice:** encryptie at rest, gescheiden medische feiten, anamnese, professionele duiding en status. Geen automatische beschuldigingen.
6. **Auditservice:** append-only gebeurtenissen, afzonderlijke bevoegdheden en retentie; geen onnodige medische inhoud in auditlogs.
7. **Integraties:** alleen contractueel, juridisch en technisch goedgekeurde veterinaire bronnen; mutual authentication, doelbinding, mapping van datakwaliteit.

## Illustratieve API (niet geïmplementeerd)
- `POST /v1/access-decisions` — input: chipToken, purpose, treatmentReference; output: scoped one-time access capability or denial.
- `GET /v1/animals/{animalRef}/signals` — uitsluitend minimale gegevens voor toegestane scope; gepagineerd.
- `POST /v1/animals/{animalRef}/observations` — feit, bron, anamnese, interpretatie, onzekerheden, auteur, tijd.
- `POST /v1/reviews/{reviewId}/decision` — deskundige beoordeling van vervolgstap; vier-ogen bij escalatie waar passend.
- `GET /v1/audit/self` — bevoegde inzage in eigen raadplegingen.

## Belangrijk
- Gebruik **nooit** een client-side checkbox als bewijs voor behandelrelatie.
- Evalueer of een centrale kopie van dossiers überhaupt noodzakelijk en proportioneel is. Een federatieve discovery-service die alleen geverifieerde verwijzingen of minimale signalen levert, kan minder ingrijpend zijn.
- Voorkom koppeling van ongefundeerde vermoedens aan eigenaarsidentiteiten. Eigenaargegevens alleen wanneer aantoonbaar noodzakelijk en rechtmatig.
- Geautomatiseerde risicoclassificatie of profiling vereist zelfstandige juridische en ethische analyse en is geen uitgangspunt.
- Definieer idempotency keys, concurrency controls, herleidbaarheid van mutaties, correctiemechanismen en bezwaar/rectificatieprocessen.
