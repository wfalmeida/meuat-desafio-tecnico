from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import logging

from app.db.session import SessionLocal
from app.schemas.fazenda import BuscaAreaIn, FazendaOut, BuscaPontoIn, BuscaRaioIn
from app.schemas.pagination import PageResponse
from app.services.geospatial import (
    buscar_fazendas_por_area,
    obter_fazenda_por_id,
    buscar_fazendas_por_ponto,
    buscar_fazendas_por_raio,
)

# -------------------- Logger --------------------
logger = logging.getLogger("routes")

# -------------------- Router --------------------
router = APIRouter(
    prefix="/fazendas",
    tags=["Fazendas"],
    responses={404: {"description": "Fazenda não encontrada"}},
)


# -------------------- Dependency --------------------
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------- Endpoints --------------------


@router.get(
    "/{id}",
    response_model=FazendaOut,
    status_code=status.HTTP_200_OK,
    summary="Buscar fazenda por ID",
)
def obter_fazenda(id: int, db: Session = Depends(get_db)):
    try:
        fazenda = obter_fazenda_por_id(db, id)
        if not fazenda:
            logger.warning(
                "fazenda_nao_encontrada",
                extra={"method": "GET", "path": f"/fazendas/{id}", "status_code": 404},
            )
            raise HTTPException(status_code=404, detail="Fazenda não encontrada")

        logger.info(
            "fazenda_obtida",
            extra={
                "method": "GET",
                "path": f"/fazendas/{id}",
                "status_code": 200,
                "id": id,
            },
        )
        return fazenda
    except Exception as exc:
        logger.exception(
            "erro_ao_buscar_fazenda", extra={"method": "GET", "path": f"/fazendas/{id}"}
        )
        raise


@router.post(
    "/busca-ponto",
    response_model=PageResponse[FazendaOut],
    status_code=status.HTTP_200_OK,
    summary="Buscar fazendas por ponto geográfico",
)
def busca_por_ponto(
    payload: BuscaPontoIn,
    limit: int = Query(10, ge=1, le=100, description="Quantidade máxima de registros"),
    offset: int = Query(0, ge=0, description="Deslocamento para paginação"),
    db: Session = Depends(get_db),
):
    result = buscar_fazendas_por_ponto(
        db=db,
        latitude=payload.latitude,
        longitude=payload.longitude,
        limit=limit,
        offset=offset,
    )

    logger.info(
        "busca_por_ponto_executada",
        extra={
            "method": "POST",
            "path": "/fazendas/busca-ponto",
            "status_code": 200,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "limit": limit,
            "offset": offset,
            "total": result["total"],
        },
    )
    return result


@router.post(
    "/busca-raio",
    response_model=PageResponse[FazendaOut],
    status_code=status.HTTP_200_OK,
    summary="Buscar fazendas por raio",
)
def busca_por_raio(
    payload: BuscaRaioIn,
    limit: int = Query(10, ge=1, le=100, description="Quantidade máxima de registros"),
    offset: int = Query(0, ge=0, description="Deslocamento para paginação"),
    db: Session = Depends(get_db),
):
    result = buscar_fazendas_por_raio(
        db=db,
        latitude=payload.latitude,
        longitude=payload.longitude,
        raio_km=payload.raio_km,
        limit=limit,
        offset=offset,
    )

    logger.info(
        "busca_por_raio_executada",
        extra={
            "method": "POST",
            "path": "/fazendas/busca-raio",
            "status_code": 200,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "raio_km": payload.raio_km,
            "limit": limit,
            "offset": offset,
            "total": result["total"],
        },
    )
    return result


@router.post(
    "/busca-area",
    response_model=PageResponse[FazendaOut],
    status_code=status.HTTP_200_OK,
    summary="Buscar fazendas por área",
)
def busca_area(
    payload: BuscaAreaIn,
    limit: int = Query(10, ge=1, le=100, description="Quantidade máxima de registros"),
    offset: int = Query(0, ge=0, description="Deslocamento para paginação"),
    db: Session = Depends(get_db),
):
    result = buscar_fazendas_por_area(
        db=db,
        area_min=payload.area_min,
        area_max=payload.area_max,
        limit=limit,
        offset=offset,
    )

    logger.info(
        "busca_por_area_executada",
        extra={
            "method": "POST",
            "path": "/fazendas/busca-area",
            "status_code": 200,
            "area_min": payload.area_min,
            "area_max": payload.area_max,
            "limit": limit,
            "offset": offset,
            "total": result["total"],
        },
    )
    return result
