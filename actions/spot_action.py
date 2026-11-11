"""SpotListAction / SpotRegisterAction（FCSM001・FCSR001・FCSR002）"""
import os

from flask import Blueprint, abort, current_app, redirect, render_template, request, session, url_for

from beans.spot_bean import SPOT_TYPES, SpotBean
from dao.floor_dao import FloorDAO
from dao.floor_map_dao import FloorMapDAO
from dao.photo_dao import PhotoDAO
from dao.spot_dao import SpotDAO
from db import get_db
from utils.auth import login_required
from utils.photo_util import MAX_FILES, save_photo, validate_photo

spot_bp = Blueprint("spot", __name__, url_prefix="/spots")

NAME_MAX = 50
DETAIL_MAX = 200
DEFAULT_MAP = "img/no_map.svg"


@spot_bp.route("/")
@login_required
def spot_list():
    spots = SpotDAO.find_by_facility(session["facility_id"])
    return render_template("spot_list.html", spots=spots)


def _floors_for_form(facility_id):
    """画面に渡すフロア一覧（地図画像のURL付き）"""
    floors = FloorDAO.find_by_facility(facility_id)
    data = []
    for f in floors:
        fm = FloorMapDAO.find_by_floor(f.id)
        data.append({"id": f.id, "name": f.name, "mapUrl": url_for("static", filename=fm.image_path if fm else DEFAULT_MAP)})
    return floors, data


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@spot_bp.route("/register", methods=["GET", "POST"])
@login_required
def spot_register():
    facility_id = session["facility_id"]
    floors, floors_json = _floors_for_form(facility_id)
    form = {"spotName": "", "typeSelect": "", "floorSelect": "", "posX": "", "posY": "", "detail": ""}
    errors = {}

    if request.method == "POST":
        form = {k: request.form.get(k, "").strip() for k in form}
        floor_id = _to_int(form["floorSelect"])
        pos_x, pos_y = _to_int(form["posX"]), _to_int(form["posY"])
        files = [f for f in request.files.getlist("photoFile") if f and f.filename]

        # --- 入力チェック（代替フロー：必須未入力・不正値） ---
        if not form["spotName"]:
            errors["spotName"] = "スポット名を入力してください。"
        elif len(form["spotName"]) > NAME_MAX:
            errors["spotName"] = f"スポット名は{NAME_MAX}文字以内で入力してください。"
        if form["typeSelect"] not in SPOT_TYPES:
            errors["typeSelect"] = "種別を選択してください。"
        floor = FloorDAO.find_by_id(floor_id) if floor_id is not None else None
        if floor is None or floor.facility_id != facility_id:   # 他施設のフロアは指定できない
            errors["floorSelect"] = "フロアを選択してください。"
        if pos_x is None or pos_y is None or pos_x < 0 or pos_y < 0:
            errors["position"] = "マップ上で位置を指定してください。"
        if len(form["detail"]) > DETAIL_MAX:
            errors["detail"] = f"詳細・説明は{DETAIL_MAX}文字以内で入力してください。"
        if len(files) > MAX_FILES:
            errors["photoFile"] = f"写真は最大{MAX_FILES}枚までです。"
        else:
            for f in files:
                msg = validate_photo(f)
                if msg:
                    errors["photoFile"] = msg
                    break

        if not errors:
            saved = []
            db = get_db()
            try:
                spot_id = SpotDAO.insert(SpotBean(0, floor.id, form["spotName"], form["typeSelect"], pos_x, pos_y, form["detail"]))
                for f in files:
                    path = save_photo(f, current_app.config["UPLOAD_FOLDER"])
                    saved.append(path)
                    PhotoDAO.insert("spot", spot_id, path)
                db.commit()
            except Exception:
                db.rollback()
                for p in saved:  # 登録に失敗したら保存した写真も消す
                    try:
                        os.remove(os.path.join(current_app.static_folder, p))
                    except OSError:
                        pass
                current_app.logger.exception("スポット登録に失敗しました")
                abort(500)
            return redirect(url_for("spot.spot_register_done", spot_id=spot_id))

    return render_template(
        "spot_register.html", spot_types=SPOT_TYPES, floors=floors, floors_json=floors_json,
        form=form, errors=errors, max_files=MAX_FILES, name_max=NAME_MAX, detail_max=DETAIL_MAX,
    )


@spot_bp.route("/register/done/<int:spot_id>")
@login_required
def spot_register_done(spot_id):
    spot = SpotDAO.find_by_id_in_facility(spot_id, session["facility_id"])
    if spot is None:
        abort(404)
    return render_template("spot_register_done.html", spot=spot)
