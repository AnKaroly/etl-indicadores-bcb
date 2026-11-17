from datetime import date
from unittest.mock import MagicMock

import pytest

from etl_bcb.config import SERIES
from etl_bcb.extract import buscar_serie


def _session_falsa(payload):
    resposta = MagicMock()
    resposta.json.return_value = payload
    session = MagicMock()
    session.get.return_value = resposta
    return session


def test_buscar_serie_monta_requisicao_corretamente():
    session = _session_falsa([{"data": "01/01/2024", "valor": "0.42"}])

    dados = buscar_serie(SERIES["ipca"], date(2024, 1, 1), date(2024, 12, 31), session=session)

    assert dados == [{"data": "01/01/2024", "valor": "0.42"}]
    url = session.get.call_args.args[0]
    params = session.get.call_args.kwargs["params"]
    assert "bcdata.sgs.433" in url
    assert params["dataInicial"] == "01/01/2024"
    assert params["dataFinal"] == "31/12/2024"


def test_buscar_serie_resposta_inesperada():
    session = _session_falsa({"erro": "algo deu errado"})
    with pytest.raises(ValueError, match="Resposta inesperada"):
        buscar_serie(SERIES["ipca"], date(2024, 1, 1), date(2024, 1, 31), session=session)
