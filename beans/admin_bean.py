from dataclasses import dataclass
from werkzeug.security import check_password_hash


@dataclass
class AdminBean:
    id: int
    login_id: str
    password_hash: str
    name: str
    facility_id: int

    @classmethod
    def from_row(cls, r):
        return cls(r["id"], r["login_id"], r["password_hash"], r["name"], r["facility_id"])

    def verify_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
