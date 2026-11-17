"""Extract: busca dados brutos na API do Banco Central."""

import logging
from datetime import date

import requests

from etl_bcb.config import BCB_SGS_URL, Serie

logger = logging.getLogger(__name__)


def buscar_serie(
    serie: Serie,
    data_inicial: date,
    data_final: date,
    timeout: int = 30,
    session: requests.Session | None = None,
) -> list[dict]:
    """Retorna a lista de registros brutos ({"data": "dd/mm/aaaa", "valor": "x.xx"})."""
    http = session or requests.Session()
    params = {
        "formato": "json",
        "dataInicial": data_inicial.strftime("%d/%m/%Y"),
        "dataFinal": data_final.strftime("%d/%m/%Y"),
    }
    url = BCB_SGS_URL.format(codigo=serie.codigo)
    logger.info("Buscando série %s (%s) de %s a %s", serie.nome, serie.codigo, data_inicial, data_final)

    resposta = http.get(url, params=params, timeout=timeout)
    resposta.raise_for_status()
    dados = resposta.json()

    if not isinstance(dados, list):
        raise ValueError(f"Resposta inesperada da API para a série {serie.nome}: {dados!r}")

    logger.info("Série %s: %d registros recebidos", serie.nome, len(dados))
    return dados
