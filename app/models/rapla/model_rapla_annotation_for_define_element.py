from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, Index

from app.core.database import Base


class RaplaAnnotationForDefineElement(Base):
    __tablename__ = "rapla_annotation_for_define_element"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    annotation_id = Column(Integer, ForeignKey("rapla_annotation.id", ondelete="CASCADE"), index=True, nullable=False)
    define_element_id = Column(Integer, ForeignKey("rapla_define_element.id", ondelete="CASCADE"), index=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("annotation_id", "define_element_id", name="u_annot_define"),
        Index("ix_annot_define_define_element_id", "define_element_id"),
    )
