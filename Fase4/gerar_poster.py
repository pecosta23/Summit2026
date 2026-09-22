"""Fase 4 - Gera o Pôster Científico Digital (PDF, A1 paisagem: 841 x 594 mm).

Todos os números e gráficos vêm dos resultados da Fase 2 (Fase2/modelo_correcao.py), então o pôster
sempre acompanha o código. O layout é uma página HTML que o Google Chrome converte em PDF.

Como rodar:   python Fase4/gerar_poster.py
Requer:       pandas, numpy, scikit-learn, matplotlib e Google Chrome
Saídas:       Fase4/poster_cientifico.pdf (entrega) + poster.html e figuras/ (fontes editáveis)
"""
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA.parent / "Fase2"))
import modelo_correcao as mc  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PASTA_FIG = PASTA / "figuras"

TITULO = "Quando 2,4 milhões de respostas não bastam"
SUBTITULO = "O erro da Literary Digest em 1936: diagnóstico de viés e correção por regressão linear com âncora em 1932"
EQUIPE = "[Nome da equipe e integrantes: preencher]"
RODAPE = "Universidade de Mogi das Cruzes (UMC) · LaBiOmicS · Hackathon de Ciência de Dados · Summit UMC"

# Uma cor por entidade (paleta validada para daltonismo), igual à do notebook
COR_PESQUISA, COR_REAL, COR_MODELO, COR_NEUTRA = "#eb6834", "#2a78d6", "#1baf7a", "#8a8985"
TEXTO, TEXTO_2 = "#0b0b0b", "#52514e"


def pt(x, casas=1):
    """Número com vírgula decimal (padrão brasileiro)."""
    return f"{x:.{casas}f}".replace(".", ",")


def estilo_figuras():
    plt.rcParams.update({
        "font.family": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 21, "axes.labelsize": 21, "xtick.labelsize": 19, "ytick.labelsize": 19, "legend.fontsize": 19,
        "savefig.dpi": 170, "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#c9c8c4", "axes.labelcolor": TEXTO_2, "xtick.color": TEXTO_2, "ytick.color": TEXTO_2,
        "axes.grid": True, "grid.color": "#e8e7e3", "grid.linewidth": 1, "axes.axisbelow": True, "legend.frameon": False,
    })


def fig_comparacao(nac):
    """Pesquisa × real nos dois anos: 1932 acertou, 1936 não."""
    fig, ax = plt.subplots(figsize=(10.2, 3.6))
    x, larg = np.arange(2), 0.36
    b1 = ax.bar(x - larg / 2, [nac["ld32"] * 100, nac["ld36"] * 100], larg, color=COR_PESQUISA, edgecolor="white",
                linewidth=2, label="Pesquisa Literary Digest")
    b2 = ax.bar(x + larg / 2, [nac["real32"] * 100, nac["real36"] * 100], larg, color=COR_REAL, edgecolor="white",
                linewidth=2, label="Resultado real")
    ax.bar_label(b1, fmt="%.1f%%", padding=4, color=TEXTO, fontweight="bold")
    ax.bar_label(b2, fmt="%.1f%%", padding=4, color=TEXTO, fontweight="bold")
    ax.axhline(50, color=COR_NEUTRA, lw=1.5, ls="--")
    ax.text(1.68, 51.2, "maioria", color=COR_NEUTRA, ha="right", fontsize=17)
    ax.set_xticks(x, ["Eleição de 1932", "Eleição de 1936"])
    ax.set_ylabel("Voto republicano (%)")
    ax.set_ylim(0, 74)
    ax.legend(loc="upper left")
    ax.grid(axis="x", visible=False)
    fig.savefig(PASTA_FIG / "p1_comparacao.png")
    plt.close(fig)


def fig_vies(df):
    """Quanto mais republicana a amostra do estado em 1932, maior o erro de 1936."""
    x, y = df["vies_amostra32"] * 100, df["erro36"] * 100
    fig, ax = plt.subplots(figsize=(10.2, 4.15))
    ax.scatter(x, y, s=120, color=COR_PESQUISA, edgecolor="white", linewidth=1.5, zorder=3)
    b, a = np.polyfit(x, y, 1)
    xs = np.array([x.min(), x.max()])
    ax.plot(xs, b * xs + a, color=TEXTO_2, lw=2.5, zorder=2)
    desloc = {"MA": (-40, 6), "RI": (12, -26), "WI": (10, 8), "NC": (14, -6), "TN": (-6, 16), "KY": (10, 12)}
    for i in df.index[df["sigla"].isin(desloc)]:
        s = df.loc[i, "sigla"]
        ax.annotate(s, (x[i], y[i]), xytext=desloc[s], textcoords="offset points", fontsize=17, color=TEXTO_2)
    ax.set_xlim(x.min() - 2, x.max() + 4)
    ax.set_ylim(-1, y.max() + 4)
    ax.set_xlabel("Viés da amostra em 1932 (pp)")
    ax.set_ylabel("Erro em 1936 (pp)")
    fig.savefig(PASTA_FIG / "p2_vies.png")
    plt.close(fig)


def fig_antes_depois(previsoes, tabela):
    """Cada ponto é um estado: pesquisa bruta (laranja) e corrigida (verde-água) contra o resultado real."""
    real = previsoes["real36_rep"] * 100
    fig, ax = plt.subplots(figsize=(10.2, 5.1))
    lim = (5, 80)
    ax.plot(lim, lim, color=COR_NEUTRA, lw=2, ls="--", zorder=1)
    ax.text(72, 67.5, "previsão = real", color=COR_NEUTRA, rotation=33, fontsize=17, ha="center", va="center")
    ax.scatter(previsoes["ld36_rep"] * 100, real, s=120, color=COR_PESQUISA, edgecolor="white", linewidth=1.5, zorder=3,
               label=f"Pesquisa bruta (erro médio {pt(tabela.iloc[0]['MAE (pp)'])} pp)")
    ax.scatter(previsoes["prev_corrigida"] * 100, real, s=120, color=COR_MODELO, edgecolor="white", linewidth=1.5,
               zorder=4, label=f"Pesquisa corrigida (erro médio {pt(tabela.iloc[2]['MAE (pp)'])} pp)")
    ax.set_xlim(lim)
    ax.set_ylim(5, 62)
    ax.set_xlabel("Previsão de voto republicano (%)")
    ax.set_ylabel("Resultado real de 1936 (%)")
    ax.legend(loc="upper left", handletextpad=0.3, borderaxespad=0.2)
    fig.savefig(PASTA_FIG / "p3_antes_depois.png")
    plt.close(fig)


CSS = """
@page { size: 841mm 594mm; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { width: 841mm; height: 594mm; overflow: hidden; display: flex; flex-direction: column; background: #f5f7fa;
  color: #1b1b1b; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 25pt; line-height: 1.32; }
header { flex: none; background: #12294d; color: #fff; padding: 24pt 56pt 20pt; border-bottom: 11pt solid #2a78d6; }
h1 { font-size: 78pt; line-height: 1.02; margin: 0 0 8pt; }
.sub { font-size: 30pt; line-height: 1.2; color: #d3e0f6; margin: 0; max-width: 1900pt; }
.meta { margin-top: 10pt; font-size: 22pt; color: #b7c9e8; }
main { flex: 1; min-height: 0; display: grid; grid-template-columns: repeat(3, 1fr); gap: 34pt; padding: 24pt 56pt 0; }
.col { display: flex; flex-direction: column; gap: 18pt; min-height: 0; }
h2 { font-size: 39pt; line-height: 1.1; margin: 0; color: #12294d; padding-left: 15pt; border-left: 11pt solid #2a78d6; }
p { margin: 0; }
.card { background: #fff; border: 2pt solid #dfe3ea; border-radius: 16pt; padding: 18pt 22pt; }
.figura { background: #fff; border: 2pt solid #dfe3ea; border-radius: 16pt; padding: 14pt 18pt 12pt; }
.figura img { width: 100%; display: block; }
.legenda { font-size: 22pt; line-height: 1.25; color: #3b3a37; margin-top: 8pt; }
.kpis { display: flex; gap: 16pt; }
.tile { flex: 1; background: #fff; border: 2pt solid #dfe3ea; border-radius: 16pt; padding: 16pt 18pt 14pt; }
.num { font-size: 66pt; font-weight: 800; line-height: 1; }
.lbl { font-size: 21pt; line-height: 1.22; color: #52514e; margin-top: 6pt; }
.c-pesq { color: #d9531f; } .c-real { color: #2a78d6; } .c-erro { color: #12294d; } .c-mod { color: #0f8c60; }
.passos { display: flex; flex-direction: column; gap: 12pt; }
.passo { display: flex; gap: 16pt; align-items: flex-start; }
.n { flex: none; width: 46pt; height: 46pt; border-radius: 50%; background: #2a78d6; color: #fff; font-weight: 800;
  font-size: 27pt; display: flex; align-items: center; justify-content: center; margin-top: 2pt; }
.passo b { color: #12294d; }
table { width: 100%; border-collapse: collapse; font-size: 21pt; }
th { text-align: right; font-weight: 700; color: #52514e; padding: 7pt 8pt; border-bottom: 3pt solid #12294d; line-height: 1.15; }
th:first-child, td:first-child { text-align: left; }
td { text-align: right; padding: 8pt 8pt; border-bottom: 1.5pt solid #e3e6ec; line-height: 1.15; }
tr.destaque td { background: #e6f5ee; font-weight: 700; color: #0b0b0b; }
tr.ref td { color: #52514e; font-style: italic; border-bottom: 0; }
.licoes { flex: none; display: grid; grid-template-columns: repeat(4, 1fr); gap: 20pt; padding: 18pt 56pt 0; }
.licao { background: #12294d; color: #fff; border-radius: 16pt; padding: 13pt 22pt 15pt; }
.licao b { display: block; font-size: 26pt; line-height: 1.15; color: #fff; margin-bottom: 5pt; }
.licao span { font-size: 21pt; line-height: 1.25; color: #d3e0f6; }
.lim { flex: none; padding: 10pt 56pt 0; font-size: 20pt; color: #52514e; line-height: 1.28; }
footer { flex: none; padding: 8pt 56pt 14pt; font-size: 18.5pt; color: #6b6a66; border-top: 2pt solid #dfe3ea; margin-top: 8pt; }
"""


def montar_html(d):
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{TITULO}</title>
<style>{CSS}</style></head><body>
<header>
  <h1>{TITULO}</h1>
  <p class="sub">{SUBTITULO}</p>
  <p class="meta">{EQUIPE} · Universidade de Mogi das Cruzes (UMC) · Summit UMC</p>
</header>

<main>
  <!-- COLUNA 1: contexto e método -->
  <section class="col">
    <h2>1. O caso de 1936</h2>
    <div class="card">
      <p>A revista <i>The Literary Digest</i> enviou <b>10 milhões</b> de cartões e recebeu
      <b>{pt(d['respondentes'] / 1e6)} milhões</b> de respostas. Previu a vitória de Landon, mas
      <b>Roosevelt venceu com {pt((1 - d['nac']['real36']) * 100, 0)}%</b> dos votos e a revista faliu.
      Nosso papel: cientistas de dados forenses.</p>
    </div>
    <div class="kpis">
      <div class="tile"><div class="num c-pesq">{pt(d['nac']['ld36'] * 100)}%</div><div class="lbl">Landon segundo a pesquisa</div></div>
      <div class="tile"><div class="num c-real">{pt(d['nac']['real36'] * 100)}%</div><div class="lbl">Landon nas urnas</div></div>
      <div class="tile"><div class="num c-erro">+{pt(d['nac']['erro36'] * 100)}</div><div class="lbl">pontos percentuais de erro</div></div>
    </div>
    <div class="card">
      <p>A pesquisa deu <b>{d['ev_pesq']} votos eleitorais</b> a Landon; ele obteve <b>{d['ev_real']}</b>. Errou o vencedor em
      <b>{48 - d['certos_pesq']} de 48 estados</b> e superestimou Landon em <b>{d['n_super']} de 48</b>.</p>
    </div>

    <h2>2. Dados e método</h2>
    <div class="card passos">
      <div class="passo"><div class="n">1</div><p><b>Limpeza (Pandas).</b> 48 estados, 4 blocos unidos pelo nome do estado, traços tratados e totais conferidos.</p></div>
      <div class="passo"><div class="n">2</div><p><b>Exploração (NumPy).</b> Voto republicano entre os dois partidos; erro = pesquisa − real.</p></div>
      <div class="passo"><div class="n">3</div><p><b>Diagnóstico de viés.</b> O “voto em 1932” dos respondentes contra o resultado real de 1932.</p></div>
      <div class="passo"><div class="n">4</div><p><b>Modelo (Scikit-Learn).</b> Regressão linear simples: erro de 1936 = a + b · viés de 1932. Validação leave-one-out.</p></div>
    </div>
  </section>

  <!-- COLUNA 2: diagnóstico -->
  <section class="col">
    <h2>3. Diagnóstico de viés</h2>
    <div class="figura"><img src="figuras/p1_comparacao.png" alt="Pesquisa e resultado real em 1932 e 1936">
      <p class="legenda"><b>Em 1932 a pesquisa acertou</b> (erro de {pt(abs(d['nac']['ld32'] - d['nac']['real32']) * 100)} pp). <b>Em 1936, errou por {pt(d['nac']['erro36'] * 100)} pp.</b></p></div>
    <div class="kpis">
      <div class="tile"><div class="num c-pesq">{pt(d['nac']['recordado32'] * 100)}%</div><div class="lbl">dos respondentes diziam ter votado em Hoover em 1932…</div></div>
      <div class="tile"><div class="num c-real">{pt(d['nac']['real32'] * 100)}%</div><div class="lbl">…contra a votação real: <b>viés de amostragem de {pt(d['nac']['vies_amostra32'] * 100)} pp</b></div></div>
    </div>
    <div class="figura"><img src="figuras/p2_vies.png" alt="Viés da amostra e erro por estado">
      <p class="legenda">Cada ponto é um estado: <b>quanto mais republicana a amostra em 1932, maior o erro em 1936</b> (r = {pt(d['r_vies'], 2)}).</p></div>
    <div class="card">
      <p><b>Não-resposta:</b> só <b>{pt(d['taxa_resp'] * 100)}%</b> dos cartões voltaram; os outros {pt((1 - d['taxa_resp']) * 100, 0)}% teriam de ser
      <b>{pt(d['dif_nao_resp'] * 100)} pp menos republicanos</b> que quem respondeu (cenário hipotético).</p>
    </div>
  </section>

  <!-- COLUNA 3: correção -->
  <section class="col">
    <h2>4. Correção com âncora em 1932</h2>
    <div class="figura"><img src="figuras/p3_antes_depois.png" alt="Antes e depois da correção">
      <p class="legenda">Cada ponto é um estado. Modelo: <b>erro de 1936 = {pt(d['a'] * 100)} pp + {pt(d['b'], 2)} × viés de 1932</b>; previsão corrigida = pesquisa − erro previsto.</p></div>
    <div class="card">
      <table>
        <tr><th>Abordagem</th><th>Erro médio<br>(pp)</th><th>Estados<br>certos</th><th>Votos<br>Landon</th><th>Landon<br>no país</th></tr>
        {d['linhas_tabela']}
        <tr class="ref"><td>Resultado real</td><td>–</td><td>–</td><td>{d['ev_real']}</td><td>{pt(d['nac']['real36'] * 100)}%</td></tr>
      </table>
      <p class="legenda">Regressão e referência: previsões estado a estado por validação leave-one-out.</p>
    </div>
    <div class="tile"><div class="num c-mod">−{pt(d['reducao'], 0)}%</div>
      <div class="lbl">no erro médio por estado: de {pt(d['mae_bruta'])} para <b>{pt(d['mae_modelo'])} pp</b>, e o vencedor certo em {d['certos_modelo']} de 48 estados.</div></div>
  </section>
</main>

<div class="licoes">
  <div class="licao"><b>Volume não é representatividade</b><span>{pt(d['respondentes'] / 1e6)} milhões de respostas e {pt(d['nac']['erro36'] * 100, 0)} pontos de erro: mais dados do mesmo viés não o corrigem.</span></div>
  <div class="licao"><b>Quem falta nos dados é mal previsto</b><span>Crédito, saúde e reconhecimento facial treinados com populações pouco diversas correm o mesmo risco.</span></div>
  <div class="licao"><b>Use uma âncora externa</b><span>Comparar a amostra com um resultado conhecido (aqui, 1932) revelou o viés e permitiu corrigi-lo.</span></div>
  <div class="licao"><b>Documente e audite</b><span>Medir cobertura, auditar por grupo e reportar limitações são deveres éticos da engenharia de dados.</span></div>
</div>
<p class="lim"><b>Limitações:</b> 48 estados; voto de 1932 autodeclarado; validação entre estados (não é previsão ao vivo); só o real de 1932, sem pesquisa, já erra {pt(d['mae_sem_pesq'])} pp: o ganho de usar a pesquisa é real, porém moderado.</p>
<footer>{RODAPE} · Dados: LitDigestFull.xlsx · Código: Fase1/main.ipynb, Fase2/modelo_correcao.py</footer>
</body></html>"""


def coletar_numeros():
    """Reúne todos os números do pôster a partir da Fase 2."""
    df = mc.carregar_dados()
    tabela, previsoes, modelo = mc.avaliar_modelos(df)
    nac = mc.resumo_nacional(df)
    respondentes = 2_376_523                          # linha "Totals" da aba 1936 (conferida na Fase 1)
    taxa = respondentes / 10_000_000
    nao_resp = (nac["real36"] - taxa * nac["ld36"]) / (1 - taxa)

    linhas = ""
    rotulos = ["Pesquisa bruta", "Correção ingênua (1932)", "Regressão com âncora", "Só o real de 1932"]
    for i, (_, m) in enumerate(tabela.iterrows()):
        cls = ' class="destaque"' if i == 2 else ""
        linhas += (f"<tr{cls}><td>{rotulos[i]}</td><td>{pt(m['MAE (pp)'])}</td><td>{int(m['Estados certos (de 48)'])}/48</td>"
                   f"<td>{int(m['Votos eleit. Landon'])}</td><td>{pt(m['Voto rep. nacional (%)'])}%</td></tr>")

    bruta, regr = tabela.iloc[0], tabela.iloc[2]
    numeros = dict(
        nac=nac, respondentes=respondentes, taxa_resp=taxa, dif_nao_resp=nac["ld36"] - nao_resp,
        ev_pesq=int(bruta["Votos eleit. Landon"]), ev_real=nac["ev_real"], certos_pesq=int(bruta["Estados certos (de 48)"]),
        certos_modelo=int(regr["Estados certos (de 48)"]), n_super=int((df["erro36"] > 0).sum()),
        r_vies=df["vies_amostra32"].corr(df["erro36"]), a=modelo.intercept_, b=modelo.coef_[0],
        mae_bruta=bruta["MAE (pp)"], mae_modelo=regr["MAE (pp)"], mae_sem_pesq=tabela.iloc[3]["MAE (pp)"],
        reducao=100 * (1 - regr["MAE (pp)"] / bruta["MAE (pp)"]), linhas_tabela=linhas,
    )
    return df, previsoes, tabela, numeros


def main():
    PASTA_FIG.mkdir(exist_ok=True)
    df, previsoes, tabela, numeros = coletar_numeros()

    estilo_figuras()
    fig_comparacao(numeros["nac"])
    fig_vies(df)
    fig_antes_depois(previsoes, tabela)

    html = PASTA / "poster.html"
    html.write_text(montar_html(numeros), encoding="utf-8")
    saida = PASTA / "poster_cientifico.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={saida}", html.as_uri()], check=True, capture_output=True)
    print("Pôster gerado:", saida)


if __name__ == "__main__":
    main()
