"""Transform: limpa, tipa e padroniza os dados com pandas."""

import pandas as pd

from etl_bcb.config import Serie

COLUNAS = ["serie", "data", "valor"]


def transformar(registros: list[dict], serie: Serie) -> pd.DataFrame:
    """Converte os registros brutos em um DataFrame limpo.

    - converte "dd/mm/aaaa" em data
    - converte o valor (texto) em número
    - remove linhas inválidas e datas duplicadas
    - ordena por data
    """
    if not registros:
        return pd.DataFrame(columns=COLUNAS)

    df = pd.DataFrame(registros)
    faltando = {"data", "valor"} - set(df.columns)
    if faltando:
        raise ValueError(f"Colunas ausentes nos dados: {sorted(faltando)}")

    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y", errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df = df.dropna(subset=["data", "valor"])
    df = df.drop_duplicates(subset="data", keep="last").sort_values("data")

    df["serie"] = serie.nome
    return df[COLUNAS].reset_index(drop=True)


def para_mensal(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega uma série diária em média mensal (data = 1º dia do mês)."""
    if df.empty:
        return df.copy()
    mensal = (
        df.assign(data=df["data"].dt.to_period("M").dt.to_timestamp())
        .groupby(["serie", "data"], as_index=False)["valor"]
        .mean()
    )
    mensal["valor"] = mensal["valor"].round(4)
    return mensal[COLUNAS]


def ipca_acumulado_12m(df_ipca: pd.DataFrame) -> pd.Series:
    """IPCA acumulado em 12 meses (%), a partir das variações mensais."""
    fatores = 1 + df_ipca.set_index("data")["valor"] / 100
    return ((fatores.rolling(12).apply(lambda x: x.prod(), raw=True) - 1) * 100).round(2)
