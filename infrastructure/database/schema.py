from .connection import DatabaseConnection


_SCHEMA = """
CREATE TABLE IF NOT EXISTS taxpayers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Active',
    taxpayer_type TEXT NOT NULL DEFAULT 'Individual',
    registration_date TEXT NOT NULL,
    address TEXT DEFAULT '',
    notes TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS declarations (
    number TEXT PRIMARY KEY,
    taxpayer TEXT NOT NULL,
    amount REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'Draft',
    date TEXT NOT NULL,
    declaration_type TEXT NOT NULL DEFAULT 'VAT',
    notes TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    user TEXT NOT NULL,
    action TEXT NOT NULL,
    entity TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'info'
);
"""

_SEED_TAXPAYERS = """
INSERT OR IGNORE INTO taxpayers VALUES
('TP-10241','Société Médina SARL','contact@medina.tn','+216 71 234 567','Active','Company','2023-02-14','Tunis',''),
('TP-10242','Amel Ben Salah','amel.bensalah@mail.tn','+216 98 112 233','Active','Individual','2023-03-02','Sfax',''),
('TP-10243','Atelier Carthage','hello@carthage.tn','+216 71 998 100','Suspended','Self-employed','2022-11-21','Tunis',''),
('TP-10244','Nour Trabelsi','nour.trabelsi@mail.tn','+216 22 445 667','Active','Individual','2024-01-09','Bizerte',''),
('TP-10245','TechNova Tunisie','finance@technova.tn','+216 70 600 700','Active','Company','2021-06-30','Tunis',''),
('TP-10246','Olivia Khelifi','olivia.k@mail.tn','+216 55 778 990','Deregistered','Individual','2020-09-18','Sousse',''),
('TP-10247','Sahara Logistics','ops@saharalog.tn','+216 75 332 110','Active','Company','2023-08-12','Gabès',''),
('TP-10248','Yassine Gharbi','yassine.gharbi@mail.tn','+216 24 009 887','Suspended','Self-employed','2022-04-05','Nabeul',''),
('TP-10249','Med Pharma Group','billing@medpharma.tn','+216 71 010 220','Active','Company','2024-05-27','Tunis',''),
('TP-10250','Ines Bouazizi','ines.b@mail.tn','+216 99 543 210','Active','Individual','2023-12-01','Monastir',''),
('TP-10251','Délices de Sfax','contact@delices-sfax.tn','+216 74 221 334','Active','Self-employed','2024-02-19','Sfax',''),
('TP-10252','Karim Jelassi','karim.jelassi@mail.tn','+216 23 667 889','Deregistered','Individual','2019-10-10','Kairouan','');
"""

_SEED_DECLARATIONS = """
INSERT OR IGNORE INTO declarations VALUES
('DCL-2026-0481','TechNova Tunisie',18420.50,'Validated','2026-06-22','VAT',''),
('DCL-2026-0480','Société Médina SARL',7350.00,'Submitted','2026-06-21','Corporate',''),
('DCL-2026-0479','Amel Ben Salah',1240.75,'Draft','2026-06-20','Income Tax',''),
('DCL-2026-0478','Sahara Logistics',9810.00,'Rejected','2026-06-19','VAT','Missing invoice'),
('DCL-2026-0477','Med Pharma Group',24500.00,'Validated','2026-06-18','Corporate',''),
('DCL-2026-0476','Nour Trabelsi',980.00,'Submitted','2026-06-17','Withholding',''),
('DCL-2026-0475','Délices de Sfax',3120.40,'Draft','2026-06-16','VAT',''),
('DCL-2026-0474','Ines Bouazizi',2210.00,'Validated','2026-06-15','Income Tax',''),
('DCL-2026-0473','Atelier Carthage',1540.90,'Rejected','2026-06-14','Withholding',''),
('DCL-2026-0472','TechNova Tunisie',15600.00,'Submitted','2026-06-13','VAT',''),
('DCL-2026-0471','Yassine Gharbi',760.25,'Draft','2026-06-12','Income Tax',''),
('DCL-2026-0470','Sahara Logistics',8420.00,'Validated','2026-06-11','Corporate','');
"""

_SEED_AUDIT = """
INSERT OR IGNORE INTO audit_logs VALUES
('LOG-9912','2026-06-27 09:42','admin@taxadmin.tn','Create','Taxpayer','New taxpayer Med Pharma Group added','success'),
('LOG-9911','2026-06-27 09:15','amel.officer','Validate','Declaration','Declaration DCL-2026-0481 validated','success'),
('LOG-9910','2026-06-27 08:51','amel.officer','Reject','Declaration','Declaration DCL-2026-0478 rejected — missing invoice','danger'),
('LOG-9909','2026-06-27 08:30','admin@taxadmin.tn','Login','Session','User signed in from 41.226.x.x','info'),
('LOG-9908','2026-06-26 17:12','karim.audit','Export','Report','Exported monthly report to PDF','info'),
('LOG-9907','2026-06-26 16:40','admin@taxadmin.tn','Update','Taxpayer','Taxpayer TP-10243 set to Suspended','warning'),
('LOG-9906','2026-06-26 15:05','nour.officer','Create','Declaration','Draft declaration DCL-2026-0475 created','info'),
('LOG-9905','2026-06-26 11:22','karim.audit','Export','Declarations','Exported declarations to Excel','info'),
('LOG-9904','2026-06-25 10:18','admin@taxadmin.tn','Delete','Taxpayer','Taxpayer TP-10252 deregistered','warning');
"""


def initialize_database() -> None:
    """Create tables and seed demo data."""
    conn = DatabaseConnection.get_instance().connect()
    conn.executescript(_SCHEMA)
    conn.executescript(_SEED_TAXPAYERS)
    conn.executescript(_SEED_DECLARATIONS)
    conn.executescript(_SEED_AUDIT)
    conn.commit()