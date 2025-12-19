from typing import Optional, Any
from datetime import date

from pydantic import BaseModel, Field, ConfigDict
from shapely.geometry import mapping, Polygon, MultiPolygon, GeometryCollection
from geoalchemy2.shape import to_shape
from app.db.models import Fazenda


# -------------------- Input Schemas --------------------
class BuscaPontoIn(BaseModel):
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        example=-23.5505,
        description="Latitude em graus decimais (-90 a 90)",
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        example=-46.6333,
        description="Longitude em graus decimais (-180 a 180)",
    )


class BuscaRaioIn(BuscaPontoIn):
    raio_km: float = Field(
        ..., gt=0, le=500, example=50, description="Raio de busca em quilômetros"
    )


class BuscaAreaIn(BaseModel):
    area_min: Optional[float] = Field(
        None,
        ge=0,
        le=1000000,
        example=50,
        description="Área mínima da fazenda em hectares",
    )
    area_max: Optional[float] = Field(
        None,
        ge=0,
        le=1000000,
        example=500,
        description="Área máxima da fazenda em hectares",
    )


# -------------------- GeoJSON Schema --------------------
class GeoJSONGeometry(BaseModel):
    type: str = Field(..., example="MultiPolygon")
    coordinates: Any

    model_config = ConfigDict(from_attributes=True)


# -------------------- Output Schema --------------------
class FazendaOut(BaseModel):
    id: int = Field(..., description="ID da fazenda")
    cod_tema: Optional[str] = Field(None, description="Código do tema da fazenda")
    nom_tema: Optional[str] = Field(None, description="Nome do tema")
    cod_imovel: Optional[str] = Field(None, description="Código do imóvel")
    mod_fiscal: Optional[float] = Field(None, description="Módulo fiscal da fazenda")
    num_area: Optional[float] = Field(None, description="Área da fazenda em hectares")
    ind_status: Optional[str] = Field(None, description="Status da fazenda")
    ind_tipo: Optional[str] = Field(None, description="Tipo da fazenda")
    des_condic: Optional[str] = Field(None, description="Descrição das condições")
    municipio: Optional[str] = Field(None, description="Município da fazenda")
    cod_estado: Optional[str] = Field(None, description="Código do estado (UF)")
    dat_criaca: Optional[date] = Field(None, description="Data de criação da fazenda")
    dat_atuali: Optional[date] = Field(None, description="Data da última atualização")
    geom: Optional[GeoJSONGeometry] = Field(
        None, description="Geometria da fazenda em GeoJSON"
    )

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, fazenda: Fazenda) -> "FazendaOut":
        """Converte o model Fazenda (SQLAlchemy) para schema com GeoJSON."""

        geom_geojson: Optional[GeoJSONGeometry] = None

        if fazenda.geom is not None:
            shape_obj = to_shape(fazenda.geom)

            # Normaliza GeometryCollection para Polygon/MultiPolygon
            if isinstance(shape_obj, GeometryCollection):
                polygons = [
                    g for g in shape_obj.geoms if isinstance(g, (Polygon, MultiPolygon))
                ]
                if len(polygons) == 1:
                    shape_obj = polygons[0]
                elif len(polygons) > 1:
                    shape_obj = MultiPolygon(polygons)
                else:
                    shape_obj = None

            if shape_obj is not None:
                geojson = mapping(shape_obj)
                geom_geojson = GeoJSONGeometry(
                    type=geojson.get("type"),
                    coordinates=geojson.get("coordinates"),
                )

        return cls(
            id=fazenda.id,
            cod_tema=fazenda.cod_tema,
            nom_tema=fazenda.nom_tema,
            cod_imovel=fazenda.cod_imovel,
            mod_fiscal=fazenda.mod_fiscal,
            num_area=fazenda.num_area,
            ind_status=fazenda.ind_status,
            ind_tipo=fazenda.ind_tipo,
            des_condic=fazenda.des_condic,
            municipio=fazenda.municipio,
            cod_estado=fazenda.cod_estado,
            dat_criaca=fazenda.dat_criaca,
            dat_atuali=fazenda.dat_atuali,
            geom=geom_geojson,
        )
