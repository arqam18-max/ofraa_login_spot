from db import get_db
from beans.photo_bean import PhotoBean


class PhotoDAO:
    @staticmethod
    def insert(target_type, target_id, file_path):
        get_db().execute(
            "INSERT INTO photo (target_type, target_id, file_path) VALUES (?, ?, ?)",
            (target_type, target_id, file_path),
        )

    @staticmethod
    def find_by_target(target_type, target_id):
        rows = get_db().execute(
            "SELECT id, target_type, target_id, file_path FROM photo WHERE target_type = ? AND target_id = ?",
            (target_type, target_id),
        ).fetchall()
        return [PhotoBean.from_row(r) for r in rows]
