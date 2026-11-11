from dataclasses import dataclass

# 画面の「種別」に表示する値
SPOT_TYPES = ["店舗", "トイレ", "エレベーター", "休憩スペース", "階段", "駐車場", "その他"]


@dataclass
class SpotBean:
    id: int
    floor_id: int
    name: str
    type: str
    pos_x: int
    pos_y: int
    detail: str = ""
    verified: bool = False
    floor_name: str = ""     # 一覧表示用
    photo_count: int = 0     # 一覧表示用

    @classmethod
    def from_row(cls, r):
        keys = r.keys()
        return cls(
            r["id"], r["floor_id"], r["name"], r["type"], r["pos_x"], r["pos_y"],
            r["detail"] or "", bool(r["verified"]),
            r["floor_name"] if "floor_name" in keys else "",
            r["photo_count"] if "photo_count" in keys else 0,
        )
