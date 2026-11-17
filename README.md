# ETL de Indicadores do Banco Central 🇧🇷

![CI](../../actions/workflows/ci.yml/badge.svg)

Projeto de estudo em Python: um pipeline **ETL** que busca indicadores econômicos na
[API pública SGS do Banco Central](https://dadosabertos.bcb.gov.br/), trata os dados com **pandas**
e grava em um banco **SQLite**.

| Série   | Código SGS | Descrição                        |
|---------|-----------:|----------------------------------|
| `ipca`  | 433        | IPCA – variação mensal (%)       |
| `selic` | 432        | Meta da taxa Selic (% a.a.)      |
| `dolar` | 1          | Dólar comercial venda – PTAX (R$)|

## Arquitetura

```
API BCB (JSON) ──► extract.py ──► transform.py ──► load.py ──► SQLite
                   requests       pandas            upsert idempotente
                           ╰──────── pipeline.py (CLI) ────────╯
```

```
src/etl_bcb/
├── config.py      # séries e caminhos
├── extract.py     # chamada HTTP à API
├── transform.py   # limpeza, tipagem, agregação mensal, IPCA 12m
├── load.py        # SQLite com PRIMARY KEY + ON CONFLICT (upsert)
└── pipeline.py    # orquestração + linha de comando
tests/             # pytest (API mockada, sem acesso à internet)
sql/               # consultas de exemplo
```

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# todas as séries desde 2020
etl-bcb --inicio 2020-01-01

# só dólar e selic, agregando em média mensal
etl-bcb --series dolar selic --inicio 2023-01-01 --mensal
```

Depois explore o banco:

```bash
sqlite3 data/indicadores.db < sql/consultas_exemplo.sql
```

ou em Python:

```python
from etl_bcb.load import conectar, ler
from etl_bcb.transform import ipca_acumulado_12m

conn = conectar("data/indicadores.db")
ipca = ler(conn, "ipca")
print(ipca_acumulado_12m(ipca).tail())
```

## Testes e qualidade

```bash
pytest -v
ruff check .
```

O GitHub Actions roda os dois a cada push.

## Conceitos praticados

- Separação em camadas Extract / Transform / Load
- Consumo de API REST com `requests` e tratamento de erros
- Limpeza de dados com `pandas` (tipos, nulos, duplicados, agregações, janelas móveis)
- Carga **idempotente** (rodar 2x não duplica dados)
- Testes unitários com `pytest` e *mocks* (injeção de dependência)
- Empacotamento com `pyproject.toml` e CLI com `argparse`
- CI com GitHub Actions

## Ideias para evoluir

- [ ] Carga incremental: buscar só a partir da última data gravada
- [ ] Novas séries (ex.: IGP-M = 189, CDI = 12)
- [ ] Gráficos com matplotlib ou um dashboard em Streamlit
- [ ] Agendar a execução com GitHub Actions (`schedule`)
- [ ] Trocar SQLite por PostgreSQL com SQLAlchemy
