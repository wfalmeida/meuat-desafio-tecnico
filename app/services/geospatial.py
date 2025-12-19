import logging
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.types import Geography

from app.db.models import Fazenda
from app.schemas.fazenda import FazendaOut

logger = logging.getLogger("geospatial")


# -------------------- Helpers --------------------
def paginate(query, limit: int, offset: int):
    """Aplica paginação com validação mínima."""
    offset = max(offset, 0)
    limit = max(min(limit, 100), 1)
    return query.limit(limit).offset(offset)


def count_scalar(query) -> int:
    """Conta total de registros de uma query SQLAlchemy."""
    return query.with_entities(func.count()).order_by(None).scalar() or 0


# -------------------- Obter por ID --------------------
def obter_fazenda_por_id(db: Session, fazenda_id: int) -> Optional[FazendaOut]:
    fazenda = db.query(Fazenda).filter(Fazenda.id == fazenda_id).first()
    if fazenda:
        logger.info("Fazenda encontrada por ID", extra={"id": fazenda_id})
        return FazendaOut.from_model(fazenda)
    logger.warning("Fazenda não encontrada", extra={"id": fazenda_id})
    return None


# -------------------- Busca por ponto --------------------
def buscar_fazendas_por_ponto(
    db: Session,
    latitude: float,
    longitude: float,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    ponto = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
    base_query = db.query(Fazenda).filter(func.ST_Contains(Fazenda.geom, ponto))

    total = count_scalar(base_query)
    items = paginate(base_query.order_by(Fazenda.id), limit, offset).all()

    logger.info(
        "Busca por ponto concluída",
        extra={"latitude": latitude, "longitude": longitude, "total": total},
    )

    return {
        "items": [FazendaOut.from_model(f) for f in items],
        "limit": limit,
        "offset": offset,
        "total": total,
    }


# -------------------- Busca por raio --------------------
def buscar_fazendas_por_raio(
    db: Session,
    latitude: float,
    longitude: float,
    raio_km: float,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    ponto = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
    base_query = db.query(Fazenda).filter(
        func.ST_DWithin(
            Fazenda.geom.cast(Geography), ponto.cast(Geography), raio_km * 1000
        )
    )

    total = count_scalar(base_query)
    items = paginate(base_query.order_by(Fazenda.id), limit, offset).all()

    logger.info(
        "Busca por raio concluída",
        extra={
            "latitude": latitude,
            "longitude": longitude,
            "raio_km": raio_km,
            "total": total,
        },
    )

    return {
        "items": [FazendaOut.from_model(f) for f in items],
        "limit": limit,
        "offset": offset,
        "total": total,
    }


# -------------------- Busca por área com filtros adicionais --------------------
def buscar_fazendas_por_area(
    db: Session,
    area_min: Optional[float] = None,
    area_max: Optional[float] = None,
    nom_tema: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    """
    Busca fazendas filtrando por área e nome do tema.
    """
    query = db.query(Fazenda)

    if area_min is not None:
        query = query.filter(Fazenda.num_area >= area_min)
    if area_max is not None:
        query = query.filter(Fazenda.num_area <= area_max)
    if nom_tema:
        query = query.filter(Fazenda.nom_tema.ilike(f"%{nom_tema}%"))

    total = count_scalar(query)
    items = paginate(query.order_by(Fazenda.id), limit, offset).all()

    logger.info(
        "Busca por área concluída",
        extra={
            "area_min": area_min,
            "area_max": area_max,
            "nom_tema": nom_tema,
            "total": total,
        },
    )

    return {
        "items": [FazendaOut.from_model(f) for f in items],
        "limit": limit,
        "offset": offset,
        "total": total,
    }
