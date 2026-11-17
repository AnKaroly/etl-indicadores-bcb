"""Configurações do pipeline: séries do Banco Central e caminhos padrão."""

from dataclasses import dataclass
from pathlib import Path

# API pública do SGS (Sistema Gerenciador de Séries Temporais) do Banco Central
BCB_SGS_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"

DEFAULT_DB_PATH = Path("data/indicadores.db")


@dataclass(frozen=True)
class Serie:
    nome: str
    codigo: int
    descricao: str
    unidade: str
    periodicidade: str  # "diaria" ou "mensal"


SERIES: dict[str, Serie] = {
    "ipca": Serie("ipca", 433, "IPCA - variação mensal", "% a.m.", "mensal"),
    "selic": Serie("selic", 432, "Meta da taxa Selic", "% a.a.", "diaria"),
    "dolar": Serie("dolar", 1, "Dólar comercial (venda) - PTAX", "R$", "diaria"),
}
