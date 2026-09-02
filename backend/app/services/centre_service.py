"""Procurement-centre listing business logic."""
from typing import List, Optional

from app.core.exceptions import NotFoundError
from app.repositories.base import CentreRepository
from app.schemas.centre import CentreOut


def list_centres(
    repo: CentreRepository, district: Optional[str] = None, state: Optional[str] = None
) -> List[CentreOut]:
    records = repo.list(district=district, state=state)
    records.sort(key=lambda r: r["name"])
    return [CentreOut.model_validate(r) for r in records]


def get_centre(repo: CentreRepository, centre_id: str) -> CentreOut:
    record = repo.get(centre_id)
    if record is None:
        raise NotFoundError("Procurement centre not found")
    return CentreOut.model_validate(record)
