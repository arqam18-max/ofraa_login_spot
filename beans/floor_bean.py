from dataclasses import dataclass


@dataclass
class FloorBean:
    id: int
    facility_id: int
    floor_no: int
    name: str

    @classmethod
    def from_row(cls, r):
        return cls(r["id"], r["facility_id"], r["floor_no"], r["name"])
