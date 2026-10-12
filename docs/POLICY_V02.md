# Autorisatiemodel v0.2 (prototype)

Alle autorisatie vindt server-side plaats. Frontend-invoer is nooit bewijs van een behandelrelatie.

| Actie | Rol | Doel | Vooraf goedgekeurde consultrelatie | Uitkomst |
| --- | --- | --- | --- | --- |
| read_signals | veterinarian | clinical_care of welfare_assessment | ja, zelfde gebruiker én exact chip | allow |
| create_signal | veterinarian | welfare_assessment | ja, zelfde gebruiker én exact chip | allow (draft only) |
| read_signals | auditor | alle | n.v.t. | deny |
| iedere actie | veterinarian | onjuist doel / verkeerde consultref / andere gebruiker of chip / ingetrokken consult | ontbreekt | deny |

## Beperkingen van de pilot

In de identiteitendatabase aangemaakte consultrelaties zijn demo-fixtures en geen bewijs uit een bronregistratie. Voor productie moeten beroepsidentiteit, bevoegdheid, relatie, doel en eventueel noodtoegang aantoonbaar uit een onafhankelijk beheerd proces komen. Logging moet tegen beheerdersmanipulatie worden beschermd; opvraaggedrag moet worden gemonitord op misbruik en enumeratie. De autorisatie moet onafhankelijk worden getest en versioned/formeel goedgekeurd worden.
