from db import get_db
from beans.spot_bean import SpotBean


class SpotDAO:
    @staticmethod
    def insert(spot: SpotBean) -> int:
        """登録して新しいIDを返す（commit は呼び出し側）"""
        cur = get_db().execute(
            "INSERT INTO spot (floor_id, name, type, pos_x, pos_y, detail, verified) VALUES (?, ?, ?, ?, ?, ?, 0)",
            (spot.floor_id, spot.name, spot.type, spot.pos_x, spot.pos_y, spot.detail),
        )
        return cur.lastrowid

    @staticmethod
    def find_by_facility(facility_id):
        rows = get_db().execute(
            """
            SELECT s.*, f.name AS floor_name,
                   (SELECT COUNT(*) FROM photo p WHERE p.target_type = 'spot' AND p.target_id = s.id) AS photo_count
            FROM spot s JOIN floor f ON f.id = s.floor_id
            WHERE f.facility_id = ?
            ORDER BY f.floor_no DESC, s.id
            """,
            (facility_id,),
        ).fetchall()
        return [SpotBean.from_row(r) for r in rows]

    @staticmethod
    def find_by_id_in_facility(spot_id, facility_id):
        row = get_db().execute(
            """
            SELECT s.*, f.name AS floor_name, 0 AS photo_count
            FROM spot s JOIN floor f ON f.id = s.floor_id
            WHERE s.id = ? AND f.facility_id = ?
            """,
            (spot_id, facility_id),
        ).fetchone()
        return SpotBean.from_row(row) if row else None
