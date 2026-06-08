# Ouvidorias das Fundações de Apoio — Universidades Federais

Mapeamento das **fundações de apoio institucional (FAIs) de universidades
federais**, verificando se cada uma possui **sistema de ouvidoria próprio** ou
se utiliza o **sistema unificado do governo federal (Fala.BR)** / a ouvidoria
da universidade.

📊 **Planilha (Excel):** `output/ouvidorias_fais_federais.xlsx`
📄 **Versão legível (GitHub):** [`docs/ouvidorias_fais.md`](docs/ouvidorias_fais.md)
📁 **CSV:** `output/ouvidorias_fais_federais.csv`

## Abordagem

Em vez de partir de "todas as universidades" e tentar adivinhar a fundação de
cada uma (o que gera resultados inconsistentes), partimos do **universo
autoritativo de FAIs**: a relação de afiliadas da
[CONFIES](https://confies.org.br), complementada por pesquisa manual. São FAIs
credenciadas MEC/MCTI (Lei 8.958/1994).

O **foco** é nas fundações de **universidades federais**. As fundações de
universidades estaduais, institutos federais (IFs/CEFETs) e ICTs não
universitárias (INPE, Fiocruz, Embrapa etc.) permanecem na base
[`src/fais_data.py`](src/fais_data.py), mas ficam **fora** do recorte do
entregável (gere com `--todas` para incluí-las).

O trabalho é feito em **duas camadas**:

1. **Curadoria manual** (alta confiança) — base [`src/fais_data.py`](src/fais_data.py).
   Cada fundação verificada à mão recebe `status="Verificado"`.
2. **Varredura automática** (cobre o restante) — [`src/scraper_fundacoes.py`](src/scraper_fundacoes.py)
   visita o site de cada fundação e classifica o que encontra, apontando
   candidatos e divergências para revisão humana.

### Classificação ("Sistema de Ouvidoria")

| Valor | Significado |
|---|---|
| ✅ **Própria** | Tem canal de ouvidoria/denúncia próprio (nominal). |
| 🟡 **Própria parcial** | Tem transparência/compliance/código de ética próprios, mas a ouvidoria formal é via universidade / Fala.BR. |
| ❌ **Fala.BR / universidade** | Sem estrutura própria; usa o sistema unificado federal / a ouvidoria da universidade. |
| 🔍 **A verificar** | Pendente de varredura/curadoria. |

> **Contexto legal:** quando a FAI não tem canal próprio, a Ouvidoria da
> universidade federal vinculada tem competência para tratar de manifestações
> sobre contratos e convênios da fundação — e opera pela plataforma unificada
> **Fala.BR** (CGU).

## Como rodar

Pré-requisitos: [uv](https://docs.astral.sh/uv/).

```bash
uv sync                                   # instala dependências

# 1) Gera a planilha (Excel + CSV + Markdown) — só universidades federais
uv run python -m src.gerar_planilha
uv run python -m src.gerar_planilha --todas   # inclui estaduais/IFs/ICTs

# 2) Varredura automática dos canais de ouvidoria das fundações
uv run python -m src.scraper_fundacoes          # federais, só pendentes
uv run python -m src.scraper_fundacoes --all    # federais, revarre todas
uv run python -m src.scraper_fundacoes --todas  # inclui todas as esferas
```

A varredura roda **sem nenhuma API key** para as fundações que já têm `site`
preenchido em `src/fais_data.py`. Para descobrir automaticamente o site das que
ainda não têm, configure um `.env` (opcional):

```ini
# .env (opcional — só para descoberta de site das fundações sem URL)
GOOGLE_API_KEY=...
GOOGLE_CX=...
TAVILY_API_KEY=...
```

## Fluxo de trabalho recomendado

1. Rode a varredura: `uv run python -m src.scraper_fundacoes`.
2. Abra `output/fais_varredura.csv` e revise os achados `Sim/Parcial (provável)`.
3. Para cada achado confirmado, edite [`src/fais_data.py`](src/fais_data.py)
   preenchendo `site`, `ouvidoria`, `canal_url` e `status="Verificado"`.
4. Regenere a planilha: `uv run python -m src.gerar_planilha`.

Assim a planilha vai ficando cada vez mais completa e confiável.

## Estrutura

```text
src/
  fais_data.py          # base curada (FONTE ÚNICA DE VERDADE) — todas as FAIs
  gerar_planilha.py     # gera a planilha (Excel/CSV/Markdown), recorte federal
  scraper_fundacoes.py  # varredura dos canais de ouvidoria das fundações
  scraper.py            # (complementar) mapeia ouvidorias das universidades
output/                 # planilhas e caches gerados (fora do git)
docs/                   # pesquisa de origem + planilha em Markdown
```

## Fontes

- Relação de fundações de apoio: [CONFIES — afiliadas](https://confies.org.br/institucional/category/afiliadas/)
- Marco legal: [Lei nº 8.958/1994](https://www.planalto.gov.br/ccivil_03/leis/l8958.htm) e [Decreto nº 7.423/2010](https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2010/decreto/d7423.htm)
- Plataforma federal de ouvidoria: [Fala.BR / CGU](https://falabr.cgu.gov.br)
