import pandas as pd
import pytest

from etl_bcb.config import SERIES
from etl_bcb.transform import ipca_acumulado_12m, para_mensal, transformar


def test_transformar_converte_tipos_e_ordena():
    brutos = [
        {"data": "02/01/2024", "valor": "4.90"},
        {"data": "01/01/2024", "valor": "4.85"},
    ]
    df = transformar(brutos, SERIES["dolar"])

    assert list(df.columns) == ["serie", "data", "valor"]
    assert df["data"].tolist() == [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")]
    assert df["valor"].tolist() == [4.85, 4.90]
    assert (df["serie"] == "dolar").all()


def test_transformar_remove_invalidos_e_duplicados():
    brutos = [
        {"data": "01/01/2024", "valor": "1.0"},
        {"data": "01/01/2024", "valor": "2.0"},  # duplicado -> mantém o último
        {"data": "data ruim", "valor": "3.0"},
        {"data": "03/01/2024", "valor": ""},
    ]
    df = transformar(brutos, SERIES["selic"])
    assert len(df) == 1
    assert df["valor"].iloc[0] == 2.0


def test_transformar_vazio():
    assert transformar([], SERIES["ipca"]).empty


def test_transformar_sem_colunas_obrigatorias():
    with pytest.raises(ValueError, match="Colunas ausentes"):
        transformar([{"x": 1}], SERIES["ipca"])


def test_para_mensal_calcula_media():
    df = transformar(
        [
            {"data": "01/01/2024", "valor": "4.0"},
            {"data": "15/01/2024", "valor": "6.0"},
            {"data": "01/02/2024", "valor": "5.0"},
        ],
        SERIES["dolar"],
    )
    mensal = para_mensal(df)
    assert mensal["data"].tolist() == [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-02-01")]
    assert mensal["valor"].tolist() == [5.0, 5.0]


def test_ipca_acumulado_12m():
    brutos = [{"data": f"01/{m:02d}/2024", "valor": "1.0"} for m in range(1, 13)]
    acumulado = ipca_acumulado_12m(transformar(brutos, SERIES["ipca"]))
    assert acumulado.iloc[:11].isna().all()
    assert acumulado.iloc[-1] == pytest.approx(12.68, abs=0.01)  # 1.01**12 - 1
