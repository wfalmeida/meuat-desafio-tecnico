from sqlalchemy.orm import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    CheckConstraint,
    Index,
)
from sqlalchemy.sql import func
from geoalchemy2 import Geometry

Base = declarative_base()


class Fazenda(Base):
    __tablename__ = "fazendas"

    id = Column(
        Integer,
        primary_key=True,
        comment="Identificador único",
    )

    cod_tema = Column(String, nullable=True, comment="Código do tema")
    nom_tema = Column(String, nullable=True, index=True, comment="Nome do tema")
    cod_imovel = Column(String, nullable=True, comment="Código do imóvel")

    mod_fiscal = Column(
        Float,
        nullable=True,
        comment="Modificador fiscal",
    )
    num_area = Column(
        Float,
        nullable=True,
        comment="Área da fazenda",
    )

    ind_status = Column(
        String,
        nullable=True,
        comment="Indicador de status",
    )
    ind_tipo = Column(
        String,
        nullable=True,
        comment="Indicador de tipo",
    )
    des_condic = Column(
        String,
        nullable=True,
        comment="Descrição da condição",
    )

    municipio = Column(
        String,
        nullable=True,
        index=True,
        comment="Município",
    )
    cod_estado = Column(
        String(2),
        nullable=True,
        index=True,
        comment="Código do estado",
    )

    dat_criaca = Column(
        Date,
        nullable=True,
        comment="Data de criação",
    )
    dat_atuali = Column(
        Date,
        nullable=True,
        comment="Data de atualização",
    )

    geom = Column(
        Geometry("MULTIPOLYGON", srid=4326),
        nullable=False,
        comment="Geometria da fazenda (SRID 4326)",
    )

    __table_args__ = (
        CheckConstraint("num_area >= 0", name="ck_fazendas_num_area_positive"),
        Index("idx_fazendas_geom", "geom", postgresql_using="gist"),
    )


class SeedControl(Base):
    __tablename__ = "seed_control"

    id = Column(
        Integer,
        primary_key=True,
        comment="Identificador único",
    )
    name = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="Nome da execução",
    )
    executed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Data/hora de execução do seed",
    )
