"""Fase 2 - Modelo de correção da pesquisa da Literary Digest (1936) e métricas de erro.

Ideia: a pesquisa de 1936 errou por ~20 pontos percentuais (pp). Usamos o comportamento eleitoral de
1932 como âncora: a própria pesquisa perguntou "em quem você votou em 1932?", e como sabemos o resultado
real de 1932 dá para medir o quanto a amostra era enviesada. Uma Regressão Linear simples aprende a
relação "viés da amostra em 1932 -> erro da pesquisa em 1936" e desconta esse erro da previsão.

Como rodar (a partir de qualquer pasta):
    python Fase2/modelo_correcao.py

Entrada : Fase1/dados_limpos.csv (gerado pelo notebook da Fase 1)
Saídas  : Fase2/resultados/metricas_modelos.csv
          Fase2/resultados/previsoes_por_estado.csv
Requer  : pandas, numpy, scikit-learn
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import LeaveOneOut, cross_val_predict

PASTA = Path(__file__).resolve().parent
CSV_LIMPO = PASTA.parent / "Fase1" / "dados_limpos.csv"
PASTA_SAIDA = PASTA / "resultados"


def prop_rep(rep, dem):
    """Proporção do candidato republicano entre os votos republicano + democrata (dois partidos)."""
    return rep / (rep + dem)


def carregar_dados(caminho=CSV_LIMPO):
    """Lê a base limpa da Fase 1 e calcula proporções, erros e o viés da amostra em 1932."""
    if not Path(caminho).exists():
        raise SystemExit(f"Não encontrei {caminho}. Rode antes o notebook da Fase 1 (Fase1/main.ipynb).")
    df = pd.read_csv(caminho)

    df["ld36_rep"] = prop_rep(df["ld36_landon"], df["ld36_roosevelt"])          # pesquisa 1936
    df["real36_rep"] = prop_rep(df["real36_landon"], df["real36_roosevelt"])    # resultado real 1936
    df["ld32_rep"] = prop_rep(df["ld32_hoover"], df["ld32_roosevelt"])          # pesquisa 1932
    df["real32_rep"] = prop_rep(df["real32_hoover"], df["real32_roosevelt"])    # resultado real 1932
    df["erro36"] = df["ld36_rep"] - df["real36_rep"]                            # erro da pesquisa em 1936
    df["erro32"] = df["ld32_rep"] - df["real32_rep"]                            # erro da pesquisa em 1932

    # Âncora: como os respondentes de 1936 diziam ter votado em 1932 (Hoover = republicano, Roosevelt = democrata)
    rep32 = df["landon_v32_rep"] + df["roosevelt_v32_rep"] + df["lemke_v32_rep"]
    dem32 = df["landon_v32_dem"] + df["roosevelt_v32_dem"] + df["lemke_v32_dem"]
    df["recordado32_rep"] = prop_rep(rep32, dem32)
    df["vies_amostra32"] = df["recordado32_rep"] - df["real32_rep"]             # amostra mais republicana que o país
    return df


def metricas(df, nome, previsto):
    """Métricas de erro de uma previsão da proporção republicana de 1936 (um valor por estado)."""
    real = df["real36_rep"].to_numpy()
    previsto = np.asarray(previsto)
    votos_reais = (df["real36_landon"] + df["real36_roosevelt"]).to_numpy()
    return {
        "Abordagem": nome,
        "MAE (pp)": mean_absolute_error(real, previsto) * 100,             # erro absoluto médio
        "RMSE (pp)": np.sqrt(mean_squared_error(real, previsto)) * 100,    # penaliza erros grandes
        "R2": r2_score(real, previsto),
        "Estados certos (de 48)": int(((previsto > 0.5) == (real > 0.5)).sum()),
        "Votos eleit. Landon": int(df.loc[previsto > 0.5, "votos_eleitorais"].sum()),
        "Voto rep. nacional (%)": np.average(previsto, weights=votos_reais) * 100,
    }


def avaliar_modelos(df):
    """Compara as 4 abordagens (validação leave-one-out nos modelos com regressão).

    Retorna: tabela de métricas, previsões por estado e o modelo ajustado com todos os estados.
    """
    loo = LeaveOneOut()   # cada estado é previsto por um modelo treinado nos outros 47

    prev_bruta = df["ld36_rep"].to_numpy()                                       # 1) pesquisa bruta
    prev_aditiva = (df["ld36_rep"] - df["erro32"]).to_numpy()                    # 2) desconta o erro de 1932

    X, y_erro = df[["vies_amostra32"]], df["erro36"]                             # 3) regressão simples com âncora
    erro_previsto = cross_val_predict(LinearRegression(), X, y_erro, cv=loo)
    prev_modelo = df["ld36_rep"].to_numpy() - erro_previsto

    prev_sem_pesquisa = cross_val_predict(                                       # 4) referência: ignora a pesquisa
        LinearRegression(), df[["real32_rep"]], df["real36_rep"], cv=loo)

    tabela = pd.DataFrame([
        metricas(df, "1. Pesquisa bruta (Literary Digest)", prev_bruta),
        metricas(df, "2. Correção aditiva ingênua (erro de 1932)", prev_aditiva),
        metricas(df, "3. Regressão simples, âncora em 1932", prev_modelo),
        metricas(df, "4. Referência: só o resultado real de 1932", prev_sem_pesquisa),
    ]).set_index("Abordagem")

    previsoes = df[["estado", "sigla", "votos_eleitorais", "real36_rep", "ld36_rep", "vies_amostra32"]].copy()
    previsoes["prev_aditiva"], previsoes["prev_corrigida"] = prev_aditiva, prev_modelo
    previsoes["prev_sem_pesquisa"] = prev_sem_pesquisa
    previsoes["erro_bruto_pp"] = (previsoes["ld36_rep"] - previsoes["real36_rep"]) * 100
    previsoes["erro_corrigido_pp"] = (previsoes["prev_corrigida"] - previsoes["real36_rep"]) * 100

    modelo = LinearRegression().fit(X, y_erro)   # ajuste final, só para descrever/interpretar o modelo
    return tabela, previsoes, modelo


def resumo_nacional(df):
    """Números nacionais (soma dos 48 estados) usados na interpretação."""
    nac = {
        "ld32": prop_rep(df["ld32_hoover"].sum(), df["ld32_roosevelt"].sum()),
        "real32": prop_rep(df["real32_hoover"].sum(), df["real32_roosevelt"].sum()),
        "ld36": prop_rep(df["ld36_landon"].sum(), df["ld36_roosevelt"].sum()),
        "real36": prop_rep(df["real36_landon"].sum(), df["real36_roosevelt"].sum()),
    }
    rep32 = df["landon_v32_rep"] + df["roosevelt_v32_rep"] + df["lemke_v32_rep"]
    dem32 = df["landon_v32_dem"] + df["roosevelt_v32_dem"] + df["lemke_v32_dem"]
    nac["recordado32"] = prop_rep(rep32.sum(), dem32.sum())
    nac["erro36"] = nac["ld36"] - nac["real36"]
    nac["vies_amostra32"] = nac["recordado32"] - nac["real32"]
    nac["ev_real"] = int(df.loc[df["real36_rep"] > 0.5, "votos_eleitorais"].sum())
    return nac


def main():
    df = carregar_dados()
    tabela, previsoes, modelo = avaliar_modelos(df)
    nac = resumo_nacional(df)
    a, b = modelo.intercept_, modelo.coef_[0]

    PASTA_SAIDA.mkdir(exist_ok=True)
    tabela.round(4).to_csv(PASTA_SAIDA / "metricas_modelos.csv")
    previsoes.round(5).to_csv(PASTA_SAIDA / "previsoes_por_estado.csv", index=False)

    pd.options.display.width = 200
    pd.options.display.max_columns = 20
    print("=" * 78)
    print("MODELO DE CORREÇÃO - PESQUISA LITERARY DIGEST 1936")
    print("=" * 78)
    print(f"Estados: {len(df)} | Resultado real: {100 * nac['real36']:.1f}% republicano no país, "
          f"Landon com {nac['ev_real']} votos eleitorais")
    print(f"Pesquisa bruta: {100 * nac['ld36']:.1f}% republicano (erro de {100 * nac['erro36']:.1f} pp)")
    print(f"Amostra de 1936 dizia ter votado em Hoover em 1932: {100 * nac['recordado32']:.1f}% "
          f"(real: {100 * nac['real32']:.1f}%)  -> viés de {100 * nac['vies_amostra32']:.1f} pp")

    print("\nModelo (ajustado nos 48 estados):")
    print(f"  erro36 = {100 * a:.2f} pp + {b:.3f} x vies_amostra32   (R2 no ajuste = {modelo.score(df[['vies_amostra32']], df['erro36']):.3f})")
    print("  previsão corrigida = pesquisa 1936 - erro previsto")

    print("\nMÉTRICAS DE ERRO (previsões leave-one-out: cada estado previsto sem ter sido usado no treino)")
    print(tabela.round(2).to_string())

    print("\nEstados em que o modelo mais errou (previsão corrigida - real, em pp):")
    piores = previsoes.reindex(previsoes["erro_corrigido_pp"].abs().sort_values(ascending=False).index).head(5)
    print(piores[["estado", "real36_rep", "ld36_rep", "prev_corrigida", "erro_bruto_pp", "erro_corrigido_pp"]]
          .round(3).to_string(index=False))

    print(f"\nArquivos gravados em {PASTA_SAIDA}")


if __name__ == "__main__":
    main()
