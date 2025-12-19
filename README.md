# MeuAT – API Geoespacial de Fazendas (Desafio Técnico)

API REST para consulta de fazendas do estado de São Paulo, utilizando dados geoespaciais.  
Desenvolvida com **Python 3.11, FastAPI, PostgreSQL + PostGIS e Docker**.

A API permite consultar fazendas por **ID**, **ponto geográfico**, **raio** ou **área**, com suporte a **paginação, filtros adicionais e logs estruturados**.

---

## 🚀 Funcionalidades Principais

- Consulta de fazendas por **ID**
- Busca de fazendas que **contêm um ponto geográfico**
- Busca de fazendas **dentro de um raio** em km
- Busca de fazendas por **área mínima/máxima**
- Paginação (`limit` e `offset`) nos endpoints de busca
- **Health check** da API e conexão com o banco
- Documentação Swagger interativa (`/docs`)
- Logs estruturados em JSON para monitoramento e debug
- Seed automático carregando shapefile ou GeoJSON de fazendas
- Índices espaciais GiST para otimização de consultas geoespaciais

---

## 🛠 Tecnologias Utilizadas

- **Backend:** FastAPI, Python 3.11
- **Banco de Dados:** PostgreSQL + PostGIS
- **ORM:** SQLAlchemy + GeoAlchemy2
- **Geoprocessamento:** Shapely, GeoPandas
- **Containerização:** Docker, Docker Compose

---

## ✅ Checklist de Implementação

### Infraestrutura

- ✅ Docker Compose configurado (API + PostgreSQL/PostGIS)
- ✅ Dockerfile com todas as dependências
- ✅ Volume persistente para o banco

### Banco de Dados

- ✅ PostgreSQL com **PostGIS** habilitado
- ✅ Modelo `Fazenda` com polígonos geoespaciais
- ✅ Índice GiST para otimização de queries espaciais
- ✅ Seed automático carregando shapefile/GeoJSON

### Endpoints da API

| Método | Endpoint              | Descrição                                       | Status |
| ------ | --------------------- | ----------------------------------------------- | ------ |
| GET    | /fazendas/{id}        | Consulta fazenda por ID                         | ✅     |
| POST   | /fazendas/busca-ponto | Fazendas que contêm um ponto                    | ✅     |
| POST   | /fazendas/busca-raio  | Fazendas dentro de um raio (km)                 | ✅     |
| POST   | /fazendas/busca-area  | Fazendas filtradas por área                     | ✅     |
| GET    | /health               | Verifica se a API está rodando e conexão com DB | ✅     |
| GET    | /docs                 | Swagger UI com exemplos interativos             | ✅     |

### Funcionalidades Adicionais / Bônus

- ✅ Paginação em endpoints de busca (`limit` e `offset`)
- ✅ Filtros adicionais: busca por nome da fazenda, área mínima/máxima
- [ ] Testes automatizados (pytest) cobrindo endpoints principais
- ✅ Documentação Swagger com exemplos e descrições
- ✅ Logs estruturados para requisições e erros (JSON)
- [ ] CI/CD no GitHub Actions rodando **lint** + **testes**
- ✅ Uso correto de índices GiST para queries espaciais

### Tratamento de Erros

- ✅ Fazenda não encontrada → retorna 404
- ✅ Validação de coordenadas e parâmetros de busca

---

## ⚡ Como Rodar o Projeto

Clone o repositório, extraia os dados do link na pasta seed/data e suba os containers:

- [Dados de São Paulo](https://drive.google.com/file/d/15ghpnwzdDhFqelouqvQwXlbzovtPhlFe/view?usp=sharing)

```bash
git clone https://github.com/wfalmeida/MeuAT-Desafio.git
cd MeuAT-Desafio
docker-compose up --build
```
