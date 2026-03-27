from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, Index

from app.core.database import Base


class RaplaAnnotationForOptionalElement(Base):
    __tablename__ = "rapla_annotation_for_optional_element"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    annotation_id = Column(Integer, ForeignKey("rapla_annotation.id", ondelete="CASCADE"), nullable=False)
    optional_element_id = Column(Integer, ForeignKey("rapla_optional_element.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("annotation_id", "optional_element_id", name="u_annot_optional"),
        Index("ix_annot_optional_optional_element_id", "optional_element_id"),
    )
