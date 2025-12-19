import logging
from pathlib import Path
from datetime import datetime, date
from typing import Any, Optional, List
import sys

import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
from geoalchemy2 import WKTElement
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import Fazenda, SeedControl

# -------------------- Logging --------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# -------------------- Helpers --------------------
def parse_date(value: Any) -> Optional[date]:
    """Converte datas vindas do shapefile para date."""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
    logger.warning("Data inválida ignorada: %s", value)
    return None


def load_geodataframe(path: Path) -> gpd.GeoDataFrame:
    """Carrega shapefile e garante CRS 4326."""
    if not path.exists():
        raise FileNotFoundError(f"Shapefile não encontrado: {path}")
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        raise RuntimeError("Arquivo espacial sem CRS definido")
    if gdf.crs.to_epsg() != 4326:
        logger.info("Reprojetando shapefile para EPSG:4326")
        gdf = gdf.to_crs(epsg=4326)
    return gdf


def normalize_geometry(geom):
    """Garante que geometria seja MultiPolygon."""
    if geom is None:
        return None
    if isinstance(geom, Polygon):
        return MultiPolygon([geom])
    if isinstance(geom, MultiPolygon):
        return geom
    raise ValueError(f"Geometria inválida: {type(geom)}")


# -------------------- Seed --------------------
def run_seed(
    db: Session, shapefile_path: Path, seed_name: str = "seed_fazendas_default"
) -> None:
    """Executa seed de fazendas a partir de um shapefile.

    Args:
        db (Session): Sessão SQLAlchemy.
        shapefile_path (Path): Caminho do arquivo shapefile.
        seed_name (str): Nome único do seed.
    """
    # Idempotência
    if db.query(SeedControl).filter_by(name=seed_name).first():
        logger.info("Seed já executado. Pulando execução. seed_name=%s", seed_name)
        return

    logger.info("Iniciando seed de fazendas. seed_name=%s", seed_name)
    gdf = load_geodataframe(shapefile_path)
    logger.info("Shapefile carregado. total_registros=%d", len(gdf))

    fazendas: List[Fazenda] = []

    for idx, row in gdf.iterrows():
        try:
            geom = normalize_geometry(row.geometry)
            geom_wkt = WKTElement(geom.wkt, srid=4326)

            atributos = {
                "cod_tema": row.get("cod_tema"),
                "nom_tema": row.get("nom_tema"),
                "cod_imovel": row.get("cod_imovel"),
                "mod_fiscal": row.get("mod_fiscal"),
                "num_area": row.get("num_area"),
                "ind_status": row.get("ind_status"),
                "ind_tipo": row.get("ind_tipo"),
                "des_condic": row.get("des_condic"),
                "municipio": row.get("municipio"),
                "cod_estado": row.get("cod_estado"),
                "dat_criaca": parse_date(row.get("dat_criaca")),
                "dat_atuali": parse_date(row.get("dat_atuali")),
            }
            atributos = {k: v for k, v in atributos.items() if v is not None}

            fazendas.append(Fazenda(geom=geom_wkt, **atributos))

        except Exception as e:
            logger.warning("Registro ignorado no índice %d: %s", idx, str(e))

    logger.info("Inserindo fazendas no banco. total_validos=%d", len(fazendas))
    db.add_all(fazendas)
    db.add(SeedControl(name=seed_name))
    db.commit()
    logger.info(
        "Seed de fazendas executado com sucesso. total_inseridos=%d", len(fazendas)
    )


# -------------------- Entrypoint --------------------
def main(
    shapefile_path: Optional[str] = None, seed_name: str = "seed_fazendas_default"
):
    db = SessionLocal()
    try:
        path = (
            Path(shapefile_path)
            if shapefile_path
            else Path("seed/data/AREA_IMOVEL_1.shp")
        )
        run_seed(db, path, seed_name)
    except Exception:
        logger.exception("Erro ao executar seed")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
