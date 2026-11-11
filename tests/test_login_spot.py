import io
import re
import pytest

from app import create_app
import db


@pytest.fixture()
def app(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE": str(tmp_path / "test.sqlite3"),
        "UPLOAD_FOLDER": str(tmp_path / "uploads"),
    })
    with app.app_context():
        db.init_db()
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def token(client, url="/login"):
    html = client.get(url).get_data(as_text=True)
    return re.search(r'name="_csrf" value="([0-9a-f]+)"', html).group(1)


def do_login(client, login_id="admin", password="admin1234"):
    return client.post("/login", data={"_csrf": token(client), "loginId": login_id, "password": password})


PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 100


def spot_data(client, **over):
    data = {"_csrf": token(client, "/spots/register"), "spotName": "多目的トイレ", "typeSelect": "トイレ",
            "floorSelect": "2", "posX": "120", "posY": "85", "detail": "車いす対応"}
    data.update(over)
    return data


# ---------------- ログイン ----------------
def test_login_page_shows(client):
    assert client.get("/login").status_code == 200


def test_login_ok_goes_to_menu(client):
    r = do_login(client)
    assert r.status_code == 302 and r.headers["Location"].endswith("/menu")
    assert "メインメニュー" in client.get("/menu").get_data(as_text=True)


def test_login_empty_shows_message(client):
    r = do_login(client, "", "")
    assert "IDとパスワードを入力してください" in r.get_data(as_text=True)


def test_login_wrong_password_and_unknown_id_same_message(client):
    a = do_login(client, "admin", "wrong").get_data(as_text=True)
    b = do_login(client, "nobody", "wrong").get_data(as_text=True)
    assert "IDまたはパスワードが正しくありません" in a and "IDまたはパスワードが正しくありません" in b


def test_menu_requires_login(client):
    r = client.get("/menu")
    assert r.status_code == 302 and "/login" in r.headers["Location"]


def test_post_without_csrf_is_rejected(client):
    assert client.post("/login", data={"loginId": "admin", "password": "admin1234"}).status_code == 400


# ---------------- ログアウト ----------------
def test_logout_flow(client):
    do_login(client)
    assert "ログアウトしますか" in client.get("/logout").get_data(as_text=True)
    r = client.post("/logout", data={"_csrf": token(client, "/logout")})
    assert r.status_code == 302 and "/login" in r.headers["Location"]
    assert "ログアウトしました" in client.get("/login").get_data(as_text=True)
    assert client.get("/menu").status_code == 302   # もうログインしていない


def test_logout_requires_login(client):
    assert client.get("/logout").status_code == 302


# ---------------- スポット登録 ----------------
def test_spot_pages_require_login(client):
    assert client.get("/spots/").status_code == 302
    assert client.get("/spots/register").status_code == 302


def test_register_spot_ok_with_photo(client, app):
    do_login(client)
    data = spot_data(client)
    data["photoFile"] = (io.BytesIO(PNG), "t.png")
    r = client.post("/spots/register", data=data, content_type="multipart/form-data")
    assert r.status_code == 302 and "/register/done/" in r.headers["Location"]
    assert "スポット情報を登録しました" in client.get(r.headers["Location"]).get_data(as_text=True)
    with app.app_context():
        d = db.get_db()
        assert d.execute("SELECT COUNT(*) FROM spot").fetchone()[0] == 1
        assert d.execute("SELECT COUNT(*) FROM photo").fetchone()[0] == 1
    assert "多目的トイレ" in client.get("/spots/").get_data(as_text=True)


@pytest.mark.parametrize("field,msg", [
    ("spotName", "スポット名を入力してください"),
    ("typeSelect", "種別を選択してください"),
    ("floorSelect", "フロアを選択してください"),
    ("posX", "位置を指定してください"),
])
def test_register_required_fields(client, field, msg):
    do_login(client)
    r = client.post("/spots/register", data=spot_data(client, **{field: ""}), content_type="multipart/form-data")
    assert r.status_code == 200 and msg in r.get_data(as_text=True)


def test_register_name_too_long(client):
    do_login(client)
    r = client.post("/spots/register", data=spot_data(client, spotName="あ" * 51), content_type="multipart/form-data")
    assert "50文字以内" in r.get_data(as_text=True)


def test_register_invalid_type_rejected(client):
    do_login(client)
    r = client.post("/spots/register", data=spot_data(client, typeSelect="不正な種別"), content_type="multipart/form-data")
    assert "種別を選択してください" in r.get_data(as_text=True)


def test_register_too_many_photos(client):
    do_login(client)
    data = spot_data(client)
    data["photoFile"] = [(io.BytesIO(PNG), f"{i}.png") for i in range(4)]
    r = client.post("/spots/register", data=data, content_type="multipart/form-data")
    assert "最大3枚" in r.get_data(as_text=True)


def test_register_fake_image_rejected(client):
    do_login(client)
    data = spot_data(client)
    data["photoFile"] = (io.BytesIO(b"<?php evil ?>"), "evil.png")   # 拡張子だけ png
    r = client.post("/spots/register", data=data, content_type="multipart/form-data")
    assert "ファイル形式が正しくありません" in r.get_data(as_text=True)


def test_register_wrong_extension_rejected(client):
    do_login(client)
    data = spot_data(client)
    data["photoFile"] = (io.BytesIO(PNG), "a.gif")
    r = client.post("/spots/register", data=data, content_type="multipart/form-data")
    assert "jpg / png のみ" in r.get_data(as_text=True)


def test_register_other_facility_floor_rejected(client, app):
    with app.app_context():
        d = db.get_db()
        fid = d.execute("INSERT INTO facility (name) VALUES ('別施設')").lastrowid
        other = d.execute("INSERT INTO floor (facility_id, floor_no, name) VALUES (?, 1, '1F')", (fid,)).lastrowid
        d.commit()
    do_login(client)
    r = client.post("/spots/register", data=spot_data(client, floorSelect=str(other)), content_type="multipart/form-data")
    assert r.status_code == 200 and "フロアを選択してください" in r.get_data(as_text=True)
    with app.app_context():
        assert db.get_db().execute("SELECT COUNT(*) FROM spot").fetchone()[0] == 0


def test_done_page_unknown_spot_404(client):
    do_login(client)
    assert client.get("/spots/register/done/999").status_code == 404
