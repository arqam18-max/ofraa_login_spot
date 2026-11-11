from dataclasses import dataclass


@dataclass
class FloorMapBean:
    id: int
    floor_id: int
    image_path: str

    @classmethod
    def from_row(cls, r):
        return cls(r["id"], r["floor_id"], r["image_path"])
