from db import get_db
from beans.floor_bean import FloorBean


class FloorDAO:
    @staticmethod
    def find_by_facility(facility_id):
        rows = get_db().execute(
            "SELECT id, facility_id, floor_no, name FROM floor WHERE facility_id = ? ORDER BY floor_no DESC",
            (facility_id,),
        ).fetchall()
        return [FloorBean.from_row(r) for r in rows]

    @staticmethod
    def find_by_id(floor_id):
        row = get_db().execute(
            "SELECT id, facility_id, floor_no, name FROM floor WHERE id = ?", (floor_id,)
        ).fetchone()
        return FloorBean.from_row(row) if row else None
