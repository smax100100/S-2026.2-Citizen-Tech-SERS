import csv
import math
from pathlib import Path
from typing import Dict, Any


PASTA_MODULO = Path(__file__).resolve().parent

# Dias por mes usados na geracao solar (simplificacao documentada no README, secao 6.4).
DIAS_GERACAO_MES = 30.0

# Parametros obrigatorios no CSV. `perda_recarga` e opcional (se ausente, considera-se 0).
PARAMETROS_OBRIGATORIOS = (
    "km_por_dia", "dias_por_mes", "meses_periodo", "preco_gasolina", "consumo_combustao",
    "consumo_eletrico", "tarifa_energia", "fator_emissao_gasolina", "fator_emissao_rede",
    "irradiacao_solar", "performance_solar_pr", "potencia_modulo_wp", "preco_sistema_solar",
    "percentual_fio_b", "tarifa_fio_b_com_tributos",
)


def localizar_csv(caminho_csv: str | None = None) -> Path:
    """Acha o premissas.csv sem depender da pasta de onde o script foi executado.

    Ordem de busca (usa o primeiro que existir):
      1. caminho informado pelo chamador;
      2. <pasta do script>/dados/premissas.csv  (estrutura do README);
      3. <pasta do script>/premissas.csv        (CSV ao lado do script);
      4. <pasta atual>/SERS/dados/premissas.csv e <pasta atual>/dados/premissas.csv.
    """
    candidatos = []
    if caminho_csv:
        candidatos.append(Path(caminho_csv))
    candidatos += [
        PASTA_MODULO / "dados" / "premissas.csv",
        PASTA_MODULO / "premissas.csv",
        Path.cwd() / "SERS" / "dados" / "premissas.csv",
        Path.cwd() / "dados" / "premissas.csv",
    ]
    for candidato in candidatos:
        if candidato.is_file():
            return candidato
    procurados = "\n  - ".join(str(c) for c in candidatos)
    raise FileNotFoundError(f"premissas.csv nao encontrado. Locais procurados:\n  - {procurados}")


def carregar_premissas(caminho_csv: str | None = None) -> Dict[str, float]:
    """Le os parametros numericos do arquivo CSV de premissas."""
    premissas = {}
    # utf-8-sig tolera o BOM que o Excel adiciona ao salvar CSV em UTF-8.
    with open(localizar_csv(caminho_csv), mode="r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            nome = (linha.get("parametro") or "").strip()
            if not nome:
                continue
            valor = (linha.get("valor") or "").strip().replace(",", ".")
            try:
                premissas[nome] = float(valor)
            except ValueError:
                raise ValueError(f"Valor invalido para '{nome}' no premissas.csv: '{linha.get('valor')}'") from None
    faltando = [nome for nome in PARAMETROS_OBRIGATORIOS if nome not in premissas]
    if faltando:
        raise KeyError(f"Parametros ausentes no premissas.csv: {', '.join(faltando)}")
    return premissas


def simular_cenarios_energia(
    km_por_dia: float | None = None,
    dias_por_mes: float | None = None,
    caminho_csv: str | None = None,
) -> Dict[str, Any]:
    """Calcula e compara Combustao x Eletrico Rede x Eletrico + Solar em 12 meses."""
    p = carregar_premissas(caminho_csv)

    km_dia = km_por_dia if km_por_dia is not None else p["km_por_dia"]
    dias_mes = dias_por_mes if dias_por_mes is not None else p["dias_por_mes"]
    meses = p["meses_periodo"]

    if km_dia <= 0 or dias_mes <= 0 or meses <= 0:
        raise ValueError("km_por_dia, dias_por_mes e meses_periodo devem ser maiores que zero.")

    km_mes = km_dia * dias_mes
    km_ano = km_mes * meses

    # 1. Combustao (Gasolina C)
    litros_ano = km_ano / p["consumo_combustao"]
    custo_combustao_ano = litros_ano * p["preco_gasolina"]
    co2_combustao_ano = litros_ano * p["fator_emissao_gasolina"]

    # 2. Eletrico na Rede Convencional
    consumo_efetivo_kwh_km = p["consumo_eletrico"] * (1.0 + p.get("perda_recarga", 0.0))
    kwh_mes = km_mes * consumo_efetivo_kwh_km
    kwh_ano = km_ano * consumo_efetivo_kwh_km
    custo_rede_ano = kwh_ano * p["tarifa_energia"]
    co2_rede_ano = kwh_ano * p["fator_emissao_rede"]

    # 3. Eletrico + Solar Fotovoltaico (Lei 14.300/2022)
    geracao_mensal_por_kwp = p["irradiacao_solar"] * DIAS_GERACAO_MES * p["performance_solar_pr"]
    kwp_necessario = kwh_mes / geracao_mensal_por_kwp
    # Sistema comercial: arredonda para cima ao numero inteiro de modulos (ex.: 0,79 kWp -> 2 x 550 Wp = 1,10 kWp).
    wp_modulo = p["potencia_modulo_wp"]
    modulos = math.ceil(round(kwp_necessario * 1000.0 / wp_modulo, 9))
    kwp_instalado = modulos * wp_modulo / 1000.0
    capex_solar = (kwp_instalado * 1000.0) * p["preco_sistema_solar"]
    custo_fio_b_ano = kwh_ano * (p["percentual_fio_b"] * p["tarifa_fio_b_com_tributos"])
    economia_solar_vs_rede = custo_rede_ano - custo_fio_b_ano
    payback_anos = capex_solar / economia_solar_vs_rede if economia_solar_vs_rede > 0 else float("inf")

    return {
        "km_mes": round(km_mes, 1),
        "km_ano": round(km_ano, 1),
        "combustao": {
            "litros_ano": round(litros_ano, 2),
            "custo_ano": round(custo_combustao_ano, 2),
            "co2_kg_ano": round(co2_combustao_ano, 2),
        },
        "eletrico_rede": {
            "kwh_mes": round(kwh_mes, 2),
            "kwh_ano": round(kwh_ano, 2),
            "custo_ano": round(custo_rede_ano, 2),
            "economia_vs_combustao": round(custo_combustao_ano - custo_rede_ano, 2),
            "co2_kg_ano": round(co2_rede_ano, 2),
        },
        "eletrico_solar": {
            "kwp_necessario": round(kwp_necessario, 2),
            "modulos": modulos,
            "potencia_modulo_wp": round(wp_modulo, 1),
            "kwp_instalado": round(kwp_instalado, 2),
            "capex_estimado": round(capex_solar, 2),
            "custo_fio_b_ano": round(custo_fio_b_ano, 2),
            "economia_vs_combustao": round(custo_combustao_ano - custo_fio_b_ano, 2),
            "payback_vs_rede_anos": round(payback_anos, 2),
            "co2_kg_ano": 0.0,
        },
    }


def gerar_resposta_citizen_assist(km_por_dia: float | None = None) -> str:
    """Formata a orientacao energetica para resposta direta no Citizen Assist AI."""
    res = simular_cenarios_energia(km_por_dia=km_por_dia)
    payback = res["eletrico_solar"]["payback_vs_rede_anos"]
    payback_txt = f"{payback:.1f} anos" if math.isfinite(payback) else "sem retorno"
    return (
        f"[Citizen Assist AI - Orientacao de Energia e Mobilidade | {res['km_ano']:.0f} km/ano]\n"
        f"1. Combustao (Gasolina C): R$ {res['combustao']['custo_ano']:.2f}/ano | "
        f"{res['combustao']['co2_kg_ano']:.1f} kg CO2/ano\n"
        f"2. Eletrico na Rede (Enel SP): R$ {res['eletrico_rede']['custo_ano']:.2f}/ano "
        f"(economia de R$ {res['eletrico_rede']['economia_vs_combustao']:.2f}/ano) | "
        f"{res['eletrico_rede']['co2_kg_ano']:.1f} kg CO2/ano\n"
        f"3. Eletrico + Solar ({res['eletrico_solar']['kwp_instalado']:.2f} kWp = "
        f"{res['eletrico_solar']['modulos']} modulos de {res['eletrico_solar']['potencia_modulo_wp']:.0f} Wp): "
        f"R$ {res['eletrico_solar']['custo_fio_b_ano']:.2f}/ano de Fio B "
        f"(economia de R$ {res['eletrico_solar']['economia_vs_combustao']:.2f}/ano; "
        f"CAPEX solar ~R$ {res['eletrico_solar']['capex_estimado']:.2f}; "
        f"payback vs. rede: {payback_txt}) | "
        f"0.0 kg CO2 operacionais/ano.\n"
        "Fontes: ANP (nov/2026), Inmetro PBEV 2026, ANEEL REH 3.596/2026, MCTI/SIRENE, CRESESB SunData, Lei 14.300/2022.\n"
        "Limitacoes: Estimativa operacional (nao inclui diferenca de compra do veiculo ou manutencao; "
        "consumo real varia +-20% conforme conducao e relevo; cobranca do Fio B aumenta gradualmente ate 2029)."
    )


if __name__ == "__main__":
    print(gerar_resposta_citizen_assist())