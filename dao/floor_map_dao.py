from db import get_db
from beans.floor_map_bean import FloorMapBean


class FloorMapDAO:
    @staticmethod
    def find_by_floor(floor_id):
        row = get_db().execute(
            "SELECT id, floor_id, image_path FROM floor_map WHERE floor_id = ?", (floor_id,)
        ).fetchone()
        return FloorMapBean.from_row(row) if row else None
