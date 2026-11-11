"""LoginAction / LogoutAction（LOGI001・LOGO001）"""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from dao.admin_dao import AdminDAO
from utils.auth import login_required

login_bp = Blueprint("login", __name__)

# ID が存在しない場合も同じ時間をかけて照合し、ID の有無を推測されにくくする
_DUMMY_HASH = generate_password_hash("dummy-password")


@login_bp.route("/")
def index():
    return redirect(url_for("menu.menu" if "admin_id" in session else "login.login"))


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if "admin_id" in session:
            return redirect(url_for("menu.menu"))
        return render_template("login.html")

    login_id = request.form.get("loginId", "").strip()
    password = request.form.get("password", "")

    # 代替フロー 3a：IDまたはパスワードが未入力
    if not login_id or not password:
        return render_template("login.html", error="IDとパスワードを入力してください。", login_id=login_id)

    admin = AdminDAO.find_by_login_id(login_id)
    if admin is None:
        check_password_hash(_DUMMY_HASH, password)
        ok = False
    else:
        ok = admin.verify_password(password)

    # 代替フロー 3b：IDまたはパスワードの誤り
    if not ok:
        return render_template("login.html", error="IDまたはパスワードが正しくありません。", login_id=login_id)

    session.clear()  # ログイン前のセッションを引き継がない
    session["admin_id"] = admin.id
    session["admin_name"] = admin.name
    session["facility_id"] = admin.facility_id
    return redirect(url_for("menu.menu"))


@login_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    if request.method == "POST":
        session.clear()
        flash("ログアウトしました。")
        return redirect(url_for("login.login"))
    # GET：確認画面を表示（戻る → 元の画面、確認 → ログアウト）
    return render_template("logout.html")
