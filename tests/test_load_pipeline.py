from datetime import date

from etl_bcb.config import SERIES
from etl_bcb.load import carregar, conectar, ler
from etl_bcb.pipeline import executar
from etl_bcb.transform import transformar


def test_carregar_e_idempotente():
    conn = conectar(":memory:")
    df = transformar([{"data": "01/01/2024", "valor": "10.0"}], SERIES["selic"])
    carregar(conn, df)

    df_atualizado = transformar([{"data": "01/01/2024", "valor": "11.0"}], SERIES["selic"])
    carregar(conn, df_atualizado)

    resultado = ler(conn, "selic")
    assert len(resultado) == 1
    assert resultado["valor"].iloc[0] == 11.0


def test_pipeline_ponta_a_ponta(tmp_path):
    def extrair_falso(serie, inicio, fim):
        return [
            {"data": "02/01/2024", "valor": "4.90"},
            {"data": "03/01/2024", "valor": "4.95"},
            {"data": "01/02/2024", "valor": "5.00"},
        ]

    db = tmp_path / "teste.db"
    resultado = executar(
        ["dolar"], date(2024, 1, 1), date(2024, 2, 28), db, mensal=True, extrair=extrair_falso
    )

    assert resultado == {"dolar": 2}  # 2 meses após agregação
    conn = conectar(db)
    assert ler(conn, "dolar")["valor"].tolist() == [4.925, 5.0]
    conn.close()
