"""create_tables

Revision ID: 4d780f4e338f
Revises:
Create Date: 2025-12-18 15:57:38.696547
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

revision: str = "4d780f4e338f"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    op.create_table(
        "fazendas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cod_tema", sa.String(), nullable=True, comment="Código do tema"),
        sa.Column(
            "nom_tema", sa.String(), nullable=True, index=True, comment="Nome do tema"
        ),
        sa.Column("cod_imovel", sa.String(), nullable=True),
        sa.Column("mod_fiscal", sa.Float(), nullable=True),
        sa.Column("num_area", sa.Float(), nullable=True, comment="Área da fazenda"),
        sa.Column("ind_status", sa.String(), nullable=True),
        sa.Column("ind_tipo", sa.String(), nullable=True),
        sa.Column("des_condic", sa.String(), nullable=True),
        sa.Column("municipio", sa.String(), nullable=True, index=True),
        sa.Column("cod_estado", sa.String(length=2), nullable=True, index=True),
        sa.Column("dat_criaca", sa.Date(), nullable=True),
        sa.Column("dat_atuali", sa.Date(), nullable=True),
        sa.Column(
            "geom",
            Geometry("MULTIPOLYGON", srid=4326),
            nullable=False,
            comment="Geometria da fazenda",
        ),
        sa.CheckConstraint("num_area >= 0", name="ck_fazendas_num_area_positive"),
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_fazendas_geom
        ON fazendas USING gist (geom);
        """
    )

    op.create_table(
        "seed_control",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "executed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("name", name="uq_seed_control_name"),
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_seed_control_name
        ON seed_control (name);
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_fazendas_geom;")
    op.execute("DROP INDEX IF EXISTS idx_seed_control_name;")
    op.drop_table("seed_control")
    op.drop_table("fazendas")
