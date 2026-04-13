from datetime import datetime

from sqlalchemy import Column, DateTime, Integer

from app.core.database import Base
from app.core.thesis_datetime import utc_now_minute


def _utcnow() -> datetime:
    return utc_now_minute()


class ThesisScheduleSettings(Base):
    __tablename__ = "thesis_schedule_settings"

    id = Column(Integer, primary_key=True, default=1) # NOTE: Shouldn't this be this: id = Column(Integer, primary_key=True, index=True, autoincrement=True)
                                                                            #_
    tab_visible_from = Column(DateTime(timezone=True), nullable=True)       # |
    tab_visible_to = Column(DateTime(timezone=True), nullable=True)         # |
    topic_submission_from = Column(DateTime(timezone=True), nullable=True)  # | -> NOTE: What is the goal here?
    topic_submission_to = Column(DateTime(timezone=True), nullable=True)    # |
    proposal_selection_from = Column(DateTime(timezone=True), nullable=True)#_|

    proposal_selection_deadline = Column(DateTime(timezone=True), nullable=True)
    max_approved_proposals = Column(Integer, nullable=False, default=3)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)