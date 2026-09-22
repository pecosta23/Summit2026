---
title: "O erro de 1936 da Literary Digest: viés de amostragem, não-resposta e lições éticas para a IA atual"
author: "[Nome da equipe e integrantes: preencher]"
---

Universidade de Mogi das Cruzes (UMC) · Summit UMC

## Introdução

Em 1936, a revista *The Literary Digest* enviou 10 milhões de cartões e recebeu quase 2,4 milhões de respostas. Previu a vitória de Alf Landon (57% × 43%), mas Franklin Roosevelt venceu com 62% dos votos e a revista faliu. O caso mostra que grande volume de dados não garante boas previsões quando a amostra é seletiva. Investigamos as causas do erro com dados estaduais, testamos uma correção simples e discutimos por que a lição permanece atual para a inteligência artificial (IA).

## Metodologia

Usamos as pesquisas de 1932 e 1936 e a votação real de 48 estados. Os dados foram limpos com Pandas (estados padronizados, valores ausentes tratados, consistência checada) e o voto republicano foi medido entre os dois grandes partidos. Como a pesquisa de 1936 perguntou em quem os respondentes votaram em 1932, comparamos essa lembrança com o resultado real daquele ano para medir o viés da amostra. Uma Regressão Linear simples (Scikit-Learn) relacionou esse viés ao erro de 1936 e o descontou da previsão. A avaliação usou validação cruzada leave-one-out.

## Resultados e Discussão

A pesquisa previu 57,1% para o republicano contra 37,5% reais: erro de 19,6 pontos percentuais (pp), com Landon superestimado em 48 dos 48 estados e 370 votos eleitorais previstos (real: 8). Em 1932, porém, o erro nacional fora de apenas 0,7 pp. A amostra de 1936 já era enviesada: 51,4% dos respondentes diziam ter votado em Hoover em 1932, contra 40,9% reais (viés de 10,6 pp), e o viés estadual correlacionou-se com o erro de 1936 (r = 0,91). Apenas 23,8% dos cartões foram respondidos; para fechar a conta, os demais precisariam ser 25,7 pp menos republicanos que os respondentes. A regressão reduziu o erro médio por estado de 18,6 para 2,6 pp e apontou o vencedor em 48 de 48 estados (pesquisa bruta: 18), estimando 38,4% republicano no país. Descontar só o erro de 1932 quase não ajudou (17,1 pp). Cerca de 10,4 pp do erro nacional acompanham o viés de amostragem; o restante, compatível com não-resposta diferencial, não pode ser separado com estes dados. Limitações: 48 observações, voto lembrado autodeclarado e um referencial sem pesquisa (só o real de 1932) com erro de 3,5 pp; o ganho de usar a pesquisa é real, porém moderado.

## Conclusão

O erro de 1936 era previsível: veio de amostra e resposta seletivas, não de falta de dados. A mesma armadilha ameaça a IA atual, treinada com bases coletadas de quem está conectado, empregado ou solvente; os grupos ausentes são previstos pior, com impacto em crédito, saúde e justiça. Auditar a representatividade dos dados, compará-los a uma âncora externa, medir cobertura e reportar limitações são deveres éticos da engenharia de dados.

**Palavras-chave:** viés de amostragem; não-resposta; regressão linear; ética em IA.
