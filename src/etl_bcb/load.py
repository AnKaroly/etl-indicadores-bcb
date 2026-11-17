"""Load: grava os dados em um banco SQLite de forma idempotente (upsert)."""

import logging
import sqlite3
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

DDL = """
CREATE TABLE IF NOT EXISTS indicadores (
    serie       TEXT NOT NULL,
    data        TEXT NOT NULL,      -- ISO 8601 (aaaa-mm-dd)
    valor       REAL NOT NULL,
    carregado_em TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (serie, data)
);
"""

UPSERT = """
INSERT INTO indicadores (serie, data, valor)
VALUES (?, ?, ?)
ON CONFLICT (serie, data) DO UPDATE SET
    valor = excluded.valor,
    carregado_em = datetime('now');
"""


def conectar(caminho: Path | str) -> sqlite3.Connection:
    if str(caminho) != ":memory:":
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(caminho)
    conn.execute(DDL)
    return conn


def carregar(conn: sqlite3.Connection, df: pd.DataFrame) -> int:
    """Insere/atualiza as linhas do DataFrame. Retorna a quantidade processada."""
    if df.empty:
        return 0
    linhas = [
        (row.serie, row.data.strftime("%Y-%m-%d"), float(row.valor))
        for row in df.itertuples(index=False)
    ]
    with conn:  # transação: commit se der certo, rollback se falhar
        conn.executemany(UPSERT, linhas)
    logger.info("%d linhas gravadas para a série %s", len(linhas), df["serie"].iloc[0])
    return len(linhas)


def ler(conn: sqlite3.Connection, serie: str) -> pd.DataFrame:
    """Lê uma série do banco de volta para um DataFrame."""
    df = pd.read_sql_query(
        "SELECT serie, data, valor FROM indicadores WHERE serie = ? ORDER BY data",
        conn,
        params=(serie,),
    )
    df["data"] = pd.to_datetime(df["data"])
    return df
