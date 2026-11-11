import os
import secrets

from flask import Flask, abort, render_template, request, session

import db
from actions.login_action import login_bp
from actions.menu_action import menu_bp
from actions.spot_action import spot_bp


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("OFRAA_SECRET_KEY", "dev-only-change-me"),
        DATABASE=os.path.join(app.instance_path, "ofraa.sqlite3"),
        UPLOAD_FOLDER=os.path.join(app.root_path, "static", "uploads"),
        MAX_CONTENT_LENGTH=20 * 1024 * 1024,   # 1回の送信は合計20MBまで
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    app.register_blueprint(login_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(spot_bp)

    @app.before_request
    def csrf_protect():
        """POST には CSRF トークンが必要"""
        if request.method == "POST":
            token = session.get("_csrf")
            if not token or token != request.form.get("_csrf"):
                abort(400)

    @app.context_processor
    def inject_common():
        if "_csrf" not in session:
            session["_csrf"] = secrets.token_hex(16)
        return {"csrf_token": session["_csrf"], "admin_name": session.get("admin_name")}

    # ERR001：エラー画面
    def _error(message, code):
        return render_template("error.html", message=message, code=code), code

    @app.errorhandler(400)
    def bad_request(e):
        return _error("不正なリクエストです。もう一度お試しください。", 400)

    @app.errorhandler(404)
    def not_found(e):
        return _error("ページが見つかりません。", 404)

    @app.errorhandler(413)
    def too_large(e):
        return _error("送信するファイルが大きすぎます。", 413)

    @app.errorhandler(500)
    def server_error(e):
        return _error("エラーが発生しました。時間をおいてもう一度お試しください。", 500)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
