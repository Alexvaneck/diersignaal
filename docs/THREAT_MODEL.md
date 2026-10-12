# Dreigingsmodel — eerste inventarisatie

| Dreiging | Risico | Vereiste maatregel |
|---|---|---|
| Dierenarts zoekt chip van buurman | Onrechtmatige inzage | Verifieer behandelrelatie, logging, audits, signalen bij afwijkend zoekgedrag |
| Massaal enumereren van chips | Opbouw ongeautoriseerde dier-/eigenaarprofielen | Rate limiting, detectie, minimal response, geen onderscheidende foutinformatie |
| Gecompromitteerde praktijkaccount | Brede datalekken | Phishingbestendige MFA, apparaat-/sessiebeleid, reauth voor gevoelige operaties |
| Manipulatie van observaties | Onterechte verdenking | Bronverwijzing, auteur, timestamp, correctiehistorie, review en tegengeluid |
| Foutieve samenvoeging van dieren | Verkeerd dossier | Chipverificatie, identiteitsconflicten expliciet maken, bevestiging via kliniek |
| Onbedoelde uitlek via logging | Privacyinbreuk | Chipmasking, geen medische details in technische logs, gescheiden toegang |
| Insider exporteert signalen | Privacy- en reputatieschade | Scope-limieten, DLP, exportbeleid, second approval, monitoring |
| Centralisatie creëert kwetsbaar doelwit | Grootschalig incident | Federatieve opties onderzoeken, segmentatie, encryptie, sleutelbeheer |
| XSS/injectie | Sessiediefstal, manipulatie | Context-encoding, CSP, inputvalidatie, veilige templating, pentest |
| Beschikbaarheid faalt | Zorgproces gehinderd | Fail-safe, incidentplan, uitwijk, expliciet systeem is ondersteunend |

Bij bouw: STRIDE-sessies per gegevensstroom, concrete abuse cases en periodieke herijking.
