-- OFRAA テーブル定義（開発用 SQLite）
-- ※ 再実行すると既存データは消えます
DROP TABLE IF EXISTS photo;
DROP TABLE IF EXISTS spot;
DROP TABLE IF EXISTS floor_map;
DROP TABLE IF EXISTS floor;
DROP TABLE IF EXISTS admin;
DROP TABLE IF EXISTS facility;

CREATE TABLE facility (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL,
    address TEXT
);

CREATE TABLE admin (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    login_id      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name          TEXT NOT NULL,
    facility_id   INTEGER NOT NULL REFERENCES facility(id)
);

CREATE TABLE floor (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    facility_id INTEGER NOT NULL REFERENCES facility(id),
    floor_no    INTEGER NOT NULL,
    name        TEXT NOT NULL
);

CREATE TABLE floor_map (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    floor_id   INTEGER NOT NULL UNIQUE REFERENCES floor(id),
    image_path TEXT NOT NULL
);

CREATE TABLE spot (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    floor_id   INTEGER NOT NULL REFERENCES floor(id),
    name       TEXT NOT NULL,
    type       TEXT NOT NULL,
    pos_x      INTEGER NOT NULL,
    pos_y      INTEGER NOT NULL,
    detail     TEXT,
    verified   INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE photo (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    target_type TEXT NOT NULL,          -- 'spot' または 'path'
    target_id   INTEGER NOT NULL,
    file_path   TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
