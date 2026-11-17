"""Orquestra o ETL e expõe uma linha de comando.

Exemplo:
    python -m etl_bcb.pipeline --series ipca selic dolar --inicio 2020-01-01
"""

import argparse
import logging
from datetime import date
from pathlib import Path

from etl_bcb.config import DEFAULT_DB_PATH, SERIES
from etl_bcb.extract import buscar_serie
from etl_bcb.load import carregar, conectar
from etl_bcb.transform import para_mensal, transformar

logger = logging.getLogger("etl_bcb")


def executar(
    nomes_series: list[str],
    inicio: date,
    fim: date,
    db_path: Path | str = DEFAULT_DB_PATH,
    mensal: bool = False,
    extrair=buscar_serie,
) -> dict[str, int]:
    """Roda Extract -> Transform -> Load para cada série. Retorna linhas gravadas por série."""
    resultado: dict[str, int] = {}
    conn = conectar(db_path)
    try:
        for nome in nomes_series:
            serie = SERIES[nome]
            brutos = extrair(serie, inicio, fim)
            df = transformar(brutos, serie)
            if mensal and serie.periodicidade == "diaria":
                df = para_mensal(df)
            resultado[nome] = carregar(conn, df)
    finally:
        conn.close()
    return resultado


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="ETL de indicadores do Banco Central -> SQLite")
    p.add_argument("--series", nargs="+", choices=sorted(SERIES), default=sorted(SERIES))
    p.add_argument("--inicio", type=date.fromisoformat, default=date(date.today().year - 5, 1, 1))
    p.add_argument("--fim", type=date.fromisoformat, default=date.today())
    p.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    p.add_argument("--mensal", action="store_true", help="agrega séries diárias em média mensal")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    args = _parse_args(argv)
    resultado = executar(args.series, args.inicio, args.fim, args.db, args.mensal)
    for nome, qtd in resultado.items():
        print(f"{nome:<6} {qtd:>6} linhas")
    print(f"Banco: {args.db}")


if __name__ == "__main__":
    main()
