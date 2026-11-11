from dataclasses import dataclass


@dataclass
class PhotoBean:
    id: int
    target_type: str
    target_id: int
    file_path: str

    @classmethod
    def from_row(cls, r):
        return cls(r["id"], r["target_type"], r["target_id"], r["file_path"])
