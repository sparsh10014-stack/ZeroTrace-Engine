CREATE TABLE IF NOT EXISTS citizens (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    dob TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
);

INSERT OR IGNORE INTO citizens
(id, name, dob, active)
VALUES
('DEMO-001', 'DEMO USER ONE', '2000-01-15', 1);

INSERT OR IGNORE INTO citizens
(id, name, dob, active)
VALUES
('DEMO-002', 'DEMO USER TWO', '2012-05-20', 1);

INSERT OR IGNORE INTO citizens
(id, name, dob, active)
VALUES
('DEMO-003', 'DEMO REVOKED USER', '1998-03-10', 0);