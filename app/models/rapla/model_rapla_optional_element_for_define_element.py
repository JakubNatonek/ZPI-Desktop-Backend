from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, Index

from app.core.database import Base


class RaplaOptionalElementForDefineElement(Base):
    __tablename__ = "rapla_optional_element_for_define_element"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    optional_element_id = Column(
        Integer, ForeignKey("rapla_optional_element.id", ondelete="CASCADE"), index=True, nullable=False
    )
    define_element_id = Column(
        Integer, ForeignKey("rapla_define_element.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("optional_element_id", "define_element_id", name="u_optional_define"),
        Index("ix_optional_define_define_element_id", "define_element_id"),
    )
