"""DBManager：SQLite への接続と初期化"""
import os
import sqlite3

from flask import current_app, g
from werkzeug.security import generate_password_hash


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)


def init_db():
    """テーブルを作り直し、動作確認用の初期データを入れる"""
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))

    cur = db.execute("INSERT INTO facility (name, address) VALUES (?, ?)", ("サンプル商業施設", "（住所を入力）"))
    facility_id = cur.lastrowid
    password = os.environ.get("OFRAA_ADMIN_PASSWORD", "admin1234")
    db.execute(
        "INSERT INTO admin (login_id, password_hash, name, facility_id) VALUES (?, ?, ?, ?)",
        ("admin", generate_password_hash(password), "施設管理者", facility_id),
    )
    for floor_no, name in [(-1, "B1"), (1, "1F"), (2, "2F")]:
        fcur = db.execute(
            "INSERT INTO floor (facility_id, floor_no, name) VALUES (?, ?, ?)", (facility_id, floor_no, name)
        )
        # フロアマップ登録機能ができるまでは仮の地図画像を使う
        db.execute("INSERT INTO floor_map (floor_id, image_path) VALUES (?, ?)", (fcur.lastrowid, "img/no_map.svg"))
    db.commit()
