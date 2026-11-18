# Citizen Assist AI - Modulo de Energia (SERS)

> Ciencia da Computacao, turmas 1CC (FIAP) | Global Solution: Citizen Assist AI | Disciplina: Solucoes em Energias Renovaveis e Sustentaveis (SERS)

Esta e a nossa parte do Citizen Assist AI na disciplina de SERS. A ideia foi simples: pegar uma duvida real de quem dirige na cidade ("vale a pena trocar meu carro a gasolina por um eletrico? E se eu colocar painel solar?") e fazer o assistente responder com numeros, fontes e avisos honestos sobre o que a conta nao cobre.

Tudo que o modulo usa esta nesta pasta: o codigo, os dados com a origem de cada numero, as contas e o registro dos testes.

---

## 1. Integrantes do Grupo

Andrei Henrique Santos - RM 569440
Heitor Maxímus Mucha - RM 571407

---

## 2. Contexto, Publico-Alvo e Problema Energetico

* **Para quem fizemos:** motoristas urbanos da Regiao Metropolitana de Sao Paulo (area da Enel Distribuicao Sao Paulo) que usam o Citizen Assist AI para planejar a rotina e decidir com mais seguranca onde gastar dinheiro.
* **Problema que atacamos:** o custo de rodar todo dia com carro a gasolina e as emissoes de CO2 que vem junto. Para ter um caso concreto, usamos um perfil padrao de 30 km por dia, 22 dias por mes, o que da 660 km/mes ou 7.920 km/ano.
* **Como o assistente ajuda:** ele traduz tarifa, emissao, consumo do veiculo e irradiacao solar em uma resposta que qualquer pessoa entende. Compara tres opcoes na mesma base de 12 meses e mostra custo, tempo para o investimento se pagar (payback), impacto ambiental e o que a estimativa nao cobre.

---

## 3. Estrutura da Pasta e Funcionalidades

```text
GS-SERS/
|-- README.md             # este arquivo: metodologia, contas, testes e referencias
|-- energia_advisor.py    # modulo Python que o Citizen Assist AI chama
`-- dados/
    `-- premissas.csv     # todos os numeros usados, com fonte e tipo (UTF-8)
```

### O que o `energia_advisor.py` faz

1. **Le as premissas do CSV** (`carregar_premissas`). Cada numero vem de `dados/premissas.csv`, com a fonte, a data da consulta e a marcacao de `real` ou `estimado`. O arquivo e encontrado sozinho (`localizar_csv`), de qualquer pasta onde o script for executado.
2. **Simula tres cenarios** (`simular_cenarios_energia`) para 12 meses, com a quilometragem que o usuario informar (padrao: 30 km/dia):
   * **Alternativa 1 - gasolina:** carro compacto a combustao, abastecido com gasolina C.
   * **Alternativa 2 - eletrico na rede:** carro eletrico recarregado em casa, com a tarifa residencial da Enel SP (com tributos) e as perdas de recarga.
   * **Alternativa 3 - eletrico + energia solar:** o mesmo eletrico, abastecido por um sistema fotovoltaico dimensionado em modulos inteiros, seguindo a Lei no 14.300/2022 (em 2026 se paga 60% do Fio B).
3. **Monta a resposta para o cidadao** (`gerar_resposta_citizen_assist`). O texto sai pronto para o chat, com os valores comparados, as fontes e o aviso de limitacoes no final.

---

## 4. Como Executar e Testar

### Pre-requisitos
* Python 3.10 ou superior.
* Nenhuma biblioteca externa: so usamos a biblioteca padrao (`csv`, `math`, `pathlib` e `typing`).

### Rodando pelo terminal

1. Clone o repositorio e entre na pasta:
   ```bash
   git clone https://github.com/smax100100/GS-2026.2-Citizen-Tech.git
   cd GS-2026.2-Citizen-Tech/SERS
   ```
2. Rode o modulo para ver a simulacao padrao (30 km/dia):
   ```bash
   python energia_advisor.py
   ```

### Chamando de dentro do Citizen Assist AI

Para gerar a resposta com a quilometragem que o usuario informar:

```python
from energia_advisor import gerar_resposta_citizen_assist, simular_cenarios_energia

# Texto pronto para o chat (exemplo com 45 km/dia)
resposta_chat = gerar_resposta_citizen_assist(km_por_dia=45.0)
print(resposta_chat)

# Dicionario com todos os numeros, para usar em cards ou graficos
dados_estruturados = simular_cenarios_energia(km_por_dia=45.0, dias_por_mes=22)
```

### Exemplo de saida

```text
[Citizen Assist AI - Orientacao de Energia e Mobilidade | 7920 km/ano]
1. Combustao (Gasolina C): R$ 3692.12/ano | 875.9 kg CO2/ano
2. Eletrico na Rede (Enel SP): R$ 1007.37/ano (economia de R$ 2684.75/ano) | 37.9 kg CO2/ano
3. Eletrico + Solar (1.10 kWp = 2 modulos de 550 Wp): R$ 212.47/ano de Fio B (economia de R$ 3479.65/ano; CAPEX solar ~R$ 2695.00; payback vs. rede: 3.4 anos) | 0.0 kg CO2 operacionais/ano.
Fontes: ANP (nov/2026), Inmetro PBEV 2026, ANEEL REH 3.596/2026, MCTI/SIRENE, CRESESB SunData, Lei 14.300/2022.
Limitacoes: Estimativa operacional (nao inclui diferenca de compra do veiculo ou manutencao; consumo real varia +-20% conforme conducao e relevo; cobranca do Fio B aumenta gradualmente ate 2029).
```

---

## 5. Dados Utilizados, Origem e Premissas (`dados/premissas.csv`)

Separamos os dados em dois tipos: **real** (vem de uma base publica oficial) e **estimado** (uma premissa nossa, com a justificativa ao lado). Assim fica claro o que e medido e o que e suposicao.

| Parametro | Valor | Unidade | Fonte / Justificativa | Consulta | Tipo |
| :--- | :---: | :---: | :--- | :---: | :---: |
| `km_por_dia` | 30 | km | Premissa do grupo (perfil de deslocamento urbano na RMSP) | 17/11/2026 | **estimado** |
| `dias_por_mes` | 22 | dias | Premissa do grupo (dias uteis no mes) | 17/11/2026 | **estimado** |
| `meses_periodo` | 12 | meses | Premissa do grupo (periodo comum de comparacao) | 17/11/2026 | **estimado** |
| `preco_gasolina` | 6,34 | R$/L | ANP, Levantamento Semanal de Precos (Sao Paulo/SP, 08/11 a 14/11/2026) | 17/11/2026 | **real** |
| `preco_etanol` | 4,09 | R$/L | ANP, Levantamento Semanal de Precos (Sao Paulo/SP, 08/11 a 14/11/2026) | 17/11/2026 | **real** |
| `consumo_combustao` | 13,6 | km/L | Inmetro, PBE Veicular 2026 (Fiat Argo 1.0 manual, gasolina, ciclo urbano) | 17/11/2026 | **real** |
| `consumo_eletrico` | 0,108 | kWh/km | Inmetro, PBE Veicular 2026 (BYD Dolphin Mini GL: 0,39 MJ/km / 3,6) | 17/11/2026 | **real** |
| `perda_recarga` | 0,15 | fracao | Premissa tecnica (perda media de 15% em carregador AC residencial) | 17/11/2026 | **estimado** |
| `tarifa_energia` | 1,0241 | R$/kWh | ANEEL, REH no 3.596/2026 Enel SP: tarifa base de R$ 0,78938 dividida por (1 - 0,18) x (1 - 0,06), ou seja, ICMS de 18% e PIS/COFINS de 6% calculados "por dentro" | 17/11/2026 | **real** |
| `taxa_minima_kwh` | 50 | kWh/mes | ANEEL, REN no 1.000/2021 (custo de disponibilidade, ligacao bifasica) | 17/11/2026 | **real** |
| `fator_emissao_gasolina` | 1,504 | kg CO2/L | Programa Brasileiro GHG Protocol. Gasolina C com mistura E32, vigente desde 01/08/2026: 68% de gasolina A x 2,212 kg CO2/L | 17/11/2026 | **real** |
| `fator_emissao_rede` | 0,0385 | kg CO2/kWh | MCTI/SIRENE, fator medio do SIN, media anual de 2023 (0,0385 tCO2/MWh) | 17/11/2026 | **real** |
| `irradiacao_solar` | 4,45 | kWh/m2.dia | CRESESB/CEPEL, SunData v3.0 (Sao Paulo/SP, plano horizontal) | 17/11/2026 | **real** |
| `performance_solar_pr` | 0,78 | adimensional | Premissa tecnica (Performance Ratio usual entre 0,75 e 0,80, INPE/CRESESB) | 17/11/2026 | **estimado** |
| `potencia_modulo_wp` | 550 | Wp | Premissa tecnica (modulo fotovoltaico comercial usual de 550 Wp) | 17/11/2026 | **estimado** |
| `preco_sistema_solar` | 2,45 | R$/Wp | Relatorios de mercado fotovoltaico Brasil 2026 (Greener / Solfacil), aplicado sobre a potencia instalada | 17/11/2026 | **estimado** |
| `percentual_fio_b` | 0,60 | fracao | Lei no 14.300/2022 e ANEEL (transicao: 60% do Fio B em 2026) | 17/11/2026 | **real** |
| `tarifa_fio_b_com_tributos` | 0,36 | R$/kWh | ANEEL, REH no 3.596/2026 Enel SP (parcela TUSD Fio B, estimada com tributos) | 17/11/2026 | **estimado** |

---

## 6. Memoria de Calculo e Comparacao das Alternativas

Todas as contas abaixo sao exatamente as que o `energia_advisor.py` faz, usando os valores da tabela acima.

### 6.1. Quanto a pessoa roda

```text
30 km/dia x 22 dias/mes = 660 km/mes
660 km/mes x 12 meses   = 7.920 km/ano
```

### 6.2. Alternativa 1 - carro a gasolina

```text
Combustivel:  7.920 km / 13,6 km/L        = 582,35 L/ano (48,53 L/mes)
Custo:        582,35 L x R$ 6,34/L        = R$ 3.692,12/ano (R$ 307,68/mes, R$ 0,466/km)
Emissoes:     582,35 L x 1,504 kg CO2/L   = 875,86 kg CO2/ano
```

### 6.3. Alternativa 2 - eletrico recarregado na rede (Enel SP, B1)

```text
Consumo na tomada:  0,108 kWh/km x (1 + 0,15)        = 0,1242 kWh/km
Energia por ano:    7.920 km x 0,1242 kWh/km         = 983,66 kWh/ano (81,97 kWh/mes)
Custo (bandeira verde):  983,66 kWh x R$ 1,0241/kWh  = R$ 1.007,37/ano (R$ 83,95/mes, R$ 0,127/km)
Emissoes:           983,66 kWh x 0,0385 kg CO2/kWh   = 37,87 kg CO2/ano
```

Sobre a perda de recarga: os 15% sao um acrescimo sobre a energia que chega na bateria, o que equivale a uma eficiencia de carga de cerca de 87%. Se a perda fosse tratada como eficiencia de 85% (0,108 / 0,85 = 0,1271 kWh/km), o consumo ficaria uns 2,3% maior.

### 6.4. Alternativa 3 - eletrico + energia solar

**Quanto um painel gera.** Cada 1 kWp instalado em Sao Paulo gera:

```text
4,45 kWh/m2.dia x 30 dias x 0,78 = 104,13 kWh/mes por kWp
```

**Quanto de painel precisamos.**

```text
81,97 kWh/mes / 104,13 kWh/mes por kWp = 0,787 kWp
```

**O que se instala de verdade.** Painel vem em modulos inteiros de 550 Wp, entao arredondamos para cima:

```text
modulos = arredonda_para_cima(787,2 Wp / 550 Wp) = 2
potencia instalada = 2 x 550 Wp = 1,10 kWp
```

Esse sistema gera 1,10 x 104,13 = 114,54 kWh/mes, cerca de 32,6 kWh/mes a mais do que o carro consome. Essa folga cobre a variacao entre as estacoes do ano, e nao contamos esse excedente como ganho, o que deixa a conta conservadora.

**Investimento inicial (CAPEX).**

```text
1.100 Wp x R$ 2,45/Wp = R$ 2.695,00
```

**Custo anual com solar.** Mesmo gerando a propria energia, em 2026 ainda se paga 60% do Fio B sobre a energia compensada (Lei no 14.300/2022). Consideramos uma casa com consumo acima do minimo de 50 kWh/mes:

```text
983,66 kWh/ano x (0,60 x R$ 0,36/kWh) = R$ 212,47/ano (R$ 17,71/mes)
```

**Em quanto tempo o painel se paga**, comparando com recarregar na rede:

```text
Economia por ano = R$ 1.007,37 - R$ 212,47 = R$ 794,90
Payback          = R$ 2.695,00 / R$ 794,90 = 3,39 anos (cerca de 41 meses)
```

**Emissoes operacionais:** praticamente zero.

### 6.5. Quadro comparativo (12 meses, 7.920 km)

| Criterio | 1. Gasolina | 2. Eletrico na rede (Enel SP) | 3. Eletrico + solar |
| :--- | :---: | :---: | :---: |
| **Energia consumida por ano** | 582,35 L | 983,66 kWh | 983,66 kWh (geracao propria) |
| **Custo operacional por ano** | **R$ 3.692,12** | **R$ 1.007,37** | **R$ 212,47** (60% do Fio B) |
| **Economia vs. gasolina** | linha de base | **R$ 2.684,75 (-72,7%)** | **R$ 3.479,65 (-94,2%)** |
| **Investimento em energia** | R$ 0,00 | R$ 0,00 (tomada) ou cerca de R$ 3.500 (wallbox) | **R$ 2.695,00** (sistema de 1,10 kWp) |
| **Emissoes operacionais de CO2** | **875,86 kg** | **37,87 kg (-95,7%)** | **0,00 kg (-100%)** |
| **Pontos de atencao** | Postos por todo lado, mas custo por km alto e emissao fossil. | Precisa de ponto de recarga em casa; sujeito a reajuste de tarifa e bandeiras da ANEEL. | Menor custo e emissao zero, mas exige telhado sem sombra e investimento inicial. |

---

## 7. Nossas Recomendacoes e Limitacoes

### O que recomendamos

* **Eletrico na rede (cenario 2):** bom primeiro passo para quem mora em apartamento ou nao tem telhado, desde que tenha uma vaga com ponto de energia. Mesmo sem painel solar, o motor eletrico e eficiente e a matriz eletrica brasileira e majoritariamente renovavel, entao o custo operacional cai 72,7% e as emissoes, 95,7%.
* **Eletrico + solar (cenario 3):** faz mais sentido para quem tem casa com telhado livre e pretende ficar nela por mais de 3,4 anos, que e o tempo do payback do sistema de 1,10 kWp (3,39 anos). Nesse caso a economia de custo chega a 94,2% e a emissao operacional vai a zero.

### O que a estimativa NAO garante

As contas sao estimativas, nao promessas de economia. Os limites principais:

1. **Escopo so de energia.** Comparamos o custo de abastecer ou recarregar e o investimento no sistema solar. Ficam de fora a diferenca de preco entre comprar um carro a combustao e um eletrico, seguro, IPVA e manutencao.
2. **Consumo real muda.** Segundo o proprio Inmetro, o consumo no dia a dia pode variar cerca de 20% para mais ou para menos, por causa de relevo, transito, ar-condicionado, pneus e estilo de direcao.
3. **Tarifa e regras mudam.** Usamos bandeira verde e a regra de 2026 da Lei no 14.300/2022 (60% do Fio B). Nos proximos anos essa cobranca sobe (75% em 2027 e 90% em 2028), o que reduz um pouco a economia do solar.
4. **Preco do sistema solar e estimado.** Usamos R$ 2,45 por Wp, que e um valor medio de mercado. Sistemas pequenos como o de 1,10 kWp costumam custar mais por Wp, entao o payback real pode ser maior.
5. **Valor do Fio B e estimado.** A parcela de R$ 0,36/kWh e uma estimativa com tributos, e ela pesa bastante no custo do cenario 3.

---

## 8. Registro de Testes com Usuarios e Ajustes Realizados

Testamos se as orientacoes eram compreensiveis e uteis com tres perfis diferentes de usuario. Nao coletamos nenhum dado pessoal, so o perfil geral.

| ID | Perfil testado | Situacao no assistente | O que a pessoa disse | O que ajustamos |
| :--- | :--- | :--- | :--- | :--- |
| **U01** | Motorista urbano (30 km/dia, casa propria) | Comparacao entre carro 1.0 a gasolina e eletrico, com e sem painel solar. | Achou os numeros claros, mas perguntou se a perda na tomada e os impostos da conta de luz estavam incluidos. | Deixamos explicitas a `perda_recarga` (15%) e a tarifa da Enel SP com tributos (ICMS + PIS/COFINS) na documentacao e nas contas. |
| **U02** | Morador de apartamento (25 km/dia, sem telhado) | Viabilidade de um eletrico carregado so na rede eletrica. | Ficou em duvida se o painel solar era obrigatorio e qual o impacto ambiental da eletricidade da rede. | Separamos bem o cenario 2 (rede) do cenario 3 (solar) e destacamos a reducao de cerca de 95,7% de CO2 ja no cenario 2, via SIN. |
| **U03** | Motorista de aplicativo (80 km/dia, uso intenso) | Simulacao com 80 km/dia e 22 dias por mes. | Sugeriu deixar claro que o calculo nao inclui o preco de compra do veiculo e que a regra do Fio B muda todo ano. | O bloco `Limitacoes` agora aparece sempre no final das respostas geradas por `gerar_resposta_citizen_assist()`. |

---

## 9. Referencias

1. **ANP - Agencia Nacional do Petroleo, Gas Natural e Biocombustiveis.** *Sistema de Levantamento de Precos (SLP), sintese semanal do municipio de Sao Paulo/SP (08/11/2026 a 14/11/2026).* https://www.gov.br/anp/
2. **INMETRO - Instituto Nacional de Metrologia, Qualidade e Tecnologia.** *Programa Brasileiro de Etiquetagem Veicular (PBE Veicular), tabela 2026.* https://www.gov.br/inmetro/
3. **ANEEL - Agencia Nacional de Energia Eletrica.** *Resolucao Homologatoria no 3.596/2026 (reajuste tarifario anual da Enel Distribuicao Sao Paulo) e Resolucao Normativa no 1.000/2021.* https://www.gov.br/aneel/
4. **BRASIL.** *Lei no 14.300, de 6 de janeiro de 2022 (Marco Legal da Microgeracao e Minigeracao Distribuida).* https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2022/lei/l14300.htm
5. **CRESESB / CEPEL - Centro de Referencia para Energia Solar e Eolica Sergio Brito.** *Potencial Solar, SunData v3.0 / Atlas Brasileiro de Energia Solar (INPE), municipio de Sao Paulo/SP.* https://cresesb.cepel.br/index.php?section=sundata
6. **MCTI - Ministerio da Ciencia, Tecnologia e Inovacao.** *SIRENE, fatores de emissao de CO2 pela geracao de energia eletrica no Sistema Interligado Nacional (SIN).* https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao
7. **FGVces / WRI Brasil.** *Ferramenta de Calculo do Programa Brasileiro GHG Protocol, fatores de emissao de combustiveis moveis (gasolina A e gasolina C).* https://registropublicodeemissoes.fgv.br/
