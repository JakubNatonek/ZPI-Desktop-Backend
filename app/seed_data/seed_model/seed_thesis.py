from sqlalchemy.orm import Session

from app.seed_data.seed_model.seed_thesis_proposals import seed_thesis_proposals


def seed_thesis(db: Session) -> None:
    """Backward-compatible alias for seeding thesis proposals."""
    seed_thesis_proposals(db)
