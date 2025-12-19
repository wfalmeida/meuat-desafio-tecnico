from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.sql import func

from app.db.models import Base


class SeedControl(Base):
    """
    Model de controle de execução de seeds.

    Attributes:
        id (int): ID do registro.
        name (str): Nome único do seed executado.
        executed_at (datetime): Data e hora de execução do seed.
    """

    __tablename__ = "seed_control"

    id = Column(Integer, primary_key=True, comment="ID do registro do seed")

    name = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="Identificador único do seed executado",
    )

    executed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Data/hora em que o seed foi executado",
    )

    __table_args__ = (Index("idx_seed_control_name", "name"),)
