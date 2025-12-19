from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

# Tipo genérico para PageResponse
T = TypeVar("T")


class PageResponse(BaseModel, Generic[T]):
    """
    Schema genérico de resposta paginada.

    Attributes:
        items (List[T]): Lista de itens retornados.
        limit (int): Quantidade máxima de registros retornados.
        offset (int): Deslocamento usado na paginação.
        total (int): Total de registros disponíveis na query.
    """

    items: List[T] = Field(..., description="Lista de itens da página")
    limit: int = Field(
        ...,
        description="Quantidade máxima de registros retornados na página",
        example=10,
    )
    offset: int = Field(..., description="Deslocamento usado para paginação", example=0)
    total: int = Field(
        ..., description="Total de registros disponíveis na consulta", example=125
    )
