"""Fase 3 - Gera o Resumo Acadêmico (Padrão Summit UMC) em Markdown, Word (.docx) e PDF.

Os números do texto vêm direto dos resultados da Fase 2 (Fase2/modelo_correcao.py), então o resumo
nunca fica desatualizado em relação ao código. Para mudar o texto, edite `montar_texto()`.

Como rodar:   python Fase3/gerar_resumo.py
Requer:       pandas, numpy, scikit-learn, pandoc (para o .docx) e Google Chrome (para o .pdf)
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA.parent / "Fase2"))
import modelo_correcao as mc  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
LIMITE_PALAVRAS = 500

TITULO = "O erro de 1936 da Literary Digest: viés de amostragem, não-resposta e lições éticas para a IA atual"
EQUIPE = "[Nome da equipe e integrantes: preencher]"
AFILIACAO = "Universidade de Mogi das Cruzes (UMC) · Summit UMC"
PALAVRAS_CHAVE = "viés de amostragem; não-resposta; regressão linear; ética em IA"


def pt(x, casas=1):
    """Formata número com vírgula decimal (padrão brasileiro)."""
    return f"{x:.{casas}f}".replace(".", ",")


def montar_texto():
    """Devolve as seções do resumo, com os números calculados a partir dos dados."""
    df = mc.carregar_dados()
    tabela, previsoes, modelo = mc.avaliar_modelos(df)
    nac = mc.resumo_nacional(df)
    bruta, aditiva, regr, sem_pesq = (tabela.iloc[i] for i in range(4))

    respondentes = 2_376_523                          # linha "Totals" da aba 1936 (conferida na Fase 1)
    taxa_resp = respondentes / 10_000_000
    nao_resp = (nac["real36"] - taxa_resp * nac["ld36"]) / (1 - taxa_resp)
    r_vies = df["vies_amostra32"].corr(df["erro36"])
    parte_amostra = modelo.coef_[0] * nac["vies_amostra32"] * 100
    n_super = int((df["erro36"] > 0).sum())

    intro = (
        "Em 1936, a revista *The Literary Digest* enviou 10 milhões de cartões e recebeu quase 2,4 milhões de respostas. "
        "Previu a vitória de Alf Landon (57% × 43%), mas Franklin Roosevelt venceu com 62% dos votos e a revista faliu. "
        "O caso mostra que grande volume de dados não garante boas previsões quando a amostra é seletiva. "
        "Investigamos as causas do erro com dados estaduais, testamos uma correção simples e discutimos por que "
        "a lição permanece atual para a inteligência artificial (IA)."
    )
    metodologia = (
        "Usamos as pesquisas de 1932 e 1936 e a votação real de 48 estados. "
        "Os dados foram limpos com Pandas (estados padronizados, valores ausentes tratados, consistência checada) e o voto "
        "republicano foi medido entre os dois grandes partidos. Como a pesquisa de 1936 perguntou em quem os respondentes "
        "votaram em 1932, comparamos essa lembrança com o resultado real daquele ano para medir o viés da amostra. "
        "Uma Regressão Linear simples (Scikit-Learn) relacionou esse viés ao erro de 1936 e o descontou da previsão. "
        "A avaliação usou validação cruzada leave-one-out."
    )
    resultados = (
        f"A pesquisa previu {pt(nac['ld36'] * 100)}% para o republicano contra {pt(nac['real36'] * 100)}% reais: erro de "
        f"{pt(nac['erro36'] * 100)} pontos percentuais (pp), com Landon superestimado em {n_super} dos 48 estados e "
        f"{int(bruta['Votos eleit. Landon'])} votos eleitorais previstos (real: {nac['ev_real']}). "
        f"Em 1932, porém, o erro nacional fora de apenas {pt(abs((nac['ld32'] - nac['real32']) * 100))} pp. "
        f"A amostra de 1936 já era enviesada: {pt(nac['recordado32'] * 100)}% dos respondentes diziam ter votado em Hoover em 1932, "
        f"contra {pt(nac['real32'] * 100)}% reais (viés de {pt(nac['vies_amostra32'] * 100)} pp), e o viés estadual "
        f"correlacionou-se com o erro de 1936 (r = {pt(r_vies, 2)}). Apenas {pt(taxa_resp * 100)}% dos cartões foram respondidos; "
        f"para fechar a conta, os demais precisariam ser {pt((nac['ld36'] - nao_resp) * 100)} pp menos republicanos que os respondentes. "
        f"A regressão reduziu o erro médio por estado de {pt(bruta['MAE (pp)'])} para {pt(regr['MAE (pp)'])} pp e apontou o vencedor "
        f"em {int(regr['Estados certos (de 48)'])} de 48 estados (pesquisa bruta: {int(bruta['Estados certos (de 48)'])}), "
        f"estimando {pt(regr['Voto rep. nacional (%)'])}% republicano no país. "
        f"Descontar só o erro de 1932 quase não ajudou ({pt(aditiva['MAE (pp)'])} pp). "
        f"Cerca de {pt(parte_amostra)} pp do erro nacional acompanham o viés de amostragem; o restante, compatível com "
        "não-resposta diferencial, não pode ser separado com estes dados. "
        f"Limitações: 48 observações, voto lembrado autodeclarado e um referencial sem pesquisa (só o real de 1932) "
        f"com erro de {pt(sem_pesq['MAE (pp)'])} pp; o ganho de usar a pesquisa é real, porém moderado."
    )
    conclusao = (
        "O erro de 1936 era previsível: veio de amostra e resposta seletivas, não de falta de dados. A mesma armadilha ameaça a IA atual, "
        "treinada com bases coletadas de quem está conectado, empregado ou solvente; os grupos ausentes são previstos pior, "
        "com impacto em crédito, saúde e justiça. Auditar a representatividade dos dados, compará-los a uma âncora externa, "
        "medir cobertura e reportar limitações são deveres éticos da engenharia de dados."
    )
    return {"Introdução": intro, "Metodologia": metodologia, "Resultados e Discussão": resultados, "Conclusão": conclusao}


def contar_palavras(texto):
    """Conta palavras do texto puro (sem símbolos de Markdown)."""
    return len(re.sub(r"[#*_\[\]]", "", texto).split())


def montar_markdown(secoes):
    corpo = "\n\n".join(f"## {nome}\n\n{texto}" for nome, texto in secoes.items())
    return (f'---\ntitle: "{TITULO}"\nauthor: "{EQUIPE}"\n---\n\n{AFILIACAO}\n\n{corpo}\n\n'
            f"**Palavras-chave:** {PALAVRAS_CHAVE}.\n")


def montar_html(secoes):
    """HTML de uma página A4 com aparência de resumo acadêmico (usado só para gerar o PDF)."""
    inline = lambda t: re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
    blocos = "".join(f"<h2>{n}</h2><p>{inline(t)}</p>" for n, t in secoes.items())
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{TITULO}</title><style>
@page {{ size: A4; margin: 22mm 22mm 20mm 22mm; }}
body {{ font-family: Georgia, "Times New Roman", serif; font-size: 10.6pt; line-height: 1.42; color: #1b1b1b; }}
header {{ text-align: center; border-bottom: 1.5px solid #1c3d6e; padding-bottom: 10px; margin-bottom: 6px; }}
h1 {{ font-size: 15.5pt; line-height: 1.25; margin: 0 0 8px; color: #12294d; }}
.equipe {{ font-size: 10.5pt; margin: 0; }} .afil {{ font-size: 9.5pt; color: #555; margin: 2px 0 0; font-style: italic; }}
h2 {{ font-family: Helvetica, Arial, sans-serif; font-size: 9.5pt; letter-spacing: .08em; text-transform: uppercase;
     color: #1c3d6e; margin: 13px 0 3px; }}
p {{ margin: 0; text-align: justify; hyphens: auto; }}
header p {{ text-align: center; }}
.kw {{ margin-top: 12px; font-size: 10pt; }}
</style></head><body>
<header><h1>{TITULO}</h1><p class="equipe">{EQUIPE}</p><p class="afil">{AFILIACAO}</p></header>
{blocos}
<p class="kw"><strong>Palavras-chave:</strong> {PALAVRAS_CHAVE}.</p>
</body></html>"""


def main():
    secoes = montar_texto()
    md = montar_markdown(secoes)

    palavras = contar_palavras(md.replace("---", ""))
    print(f"Palavras no documento (título, equipe, seções e palavras-chave): {palavras} (limite {LIMITE_PALAVRAS})")
    if palavras > LIMITE_PALAVRAS:
        raise SystemExit("O resumo passou de 500 palavras: encurte o texto em montar_texto().")

    (PASTA / "resumo_academico.md").write_text(md, encoding="utf-8")
    subprocess.run(["pandoc", str(PASTA / "resumo_academico.md"), "-o", str(PASTA / "resumo_academico.docx")], check=True)

    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / "resumo.html"
        html.write_text(montar_html(secoes), encoding="utf-8")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={PASTA / 'resumo_academico.pdf'}", html.as_uri()],
                       check=True, capture_output=True)
    print("Gerados: resumo_academico.md, .docx e .pdf em", PASTA)


if __name__ == "__main__":
    main()
