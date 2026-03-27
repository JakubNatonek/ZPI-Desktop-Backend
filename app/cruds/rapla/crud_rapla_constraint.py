from typing import List, Optional, cast

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_constraint import RaplaConstraint

from app.schemas.rapla.schema_rapla_constraint import RaplaConstraint as SchemaRaplaConstraint


def get_constraint_by_id(db: Session, constraint_id: int) -> Optional[RaplaConstraint]:
    return db.query(RaplaConstraint).filter(RaplaConstraint.id == constraint_id).first()


def get_constraint_by_name(db: Session, name: str) -> Optional[RaplaConstraint]:
    return db.query(RaplaConstraint).filter(RaplaConstraint.name == name).first()


def list_constraints(db: Session, skip: Optional[int] = None, limit: Optional[int] = None) -> List[RaplaConstraint]:
    q = db.query(RaplaConstraint).order_by(RaplaConstraint.id.asc())
    if skip is not None:
        q = q.offset(skip)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


def create_constraint(db: Session, name: str, value: Optional[str] = None) -> RaplaConstraint:
    existing = get_constraint_by_name(db, name)
    if existing is not None:
        return existing

    c = RaplaConstraint(name=name, value=value)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def update_constraint(db: Session, constraint: RaplaConstraint, **fields) -> RaplaConstraint:
    for k, v in fields.items():
        if hasattr(constraint, k):
            setattr(constraint, k, v)
    db.add(constraint)
    db.commit()
    db.refresh(constraint)
    return constraint


def delete_constraint(db: Session, constraint: RaplaConstraint) -> None:
    db.delete(constraint)
    db.commit()


def delete_constraint_by_id(db: Session, constraint_id: int) -> bool:
    c = get_constraint_by_id(db, constraint_id)
    if c is None:
        return False
    db.delete(c)
    db.commit()
    return True


def get_constraint_schema_by_id(db: Session, constraint_id: int) -> Optional[SchemaRaplaConstraint]:
    """Return a RaplaConstraint schema object for the DB row with `constraint_id`, or None."""
    c = get_constraint_by_id(db, constraint_id)
    if c is None:
        return None
    return SchemaRaplaConstraint(name= cast(str, c.name) , value= cast( str, c.value ) or "")
