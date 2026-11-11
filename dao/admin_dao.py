from db import get_db
from beans.admin_bean import AdminBean


class AdminDAO:
    @staticmethod
    def find_by_login_id(login_id):
        row = get_db().execute(
            "SELECT id, login_id, password_hash, name, facility_id FROM admin WHERE login_id = ?", (login_id,)
        ).fetchone()
        return AdminBean.from_row(row) if row else None
