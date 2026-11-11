"""MenuAction（MMNU001）"""
from flask import Blueprint, render_template

from utils.auth import login_required

menu_bp = Blueprint("menu", __name__)


@menu_bp.route("/menu")
@login_required
def menu():
    return render_template("menu.html")
