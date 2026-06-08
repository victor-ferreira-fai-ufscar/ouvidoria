"""
Varredura automática de canais de ouvidoria das Fundações de Apoio (FAIs).

Diferente da versão antiga (que "adivinhava" a fundação a partir da
universidade via busca), esta parte da base curada `src/fais_data.py` — o
universo autoritativo de FAIs — e, para cada fundação com `site` cadastrado,
varre a home em busca de links de ouvidoria/ética/denúncias/compliance.

- Roda SEM nenhuma API key quando o `site` já está preenchido na base.
- Para fundações SEM site, tenta descobrir o site via Google Custom Search
  ou Tavily, mas SOMENTE se as chaves estiverem no `.env` (caso contrário,
  apenas marca como "site não cadastrado").
- Por padrão, só varre as linhas pendentes (status != "Verificado"); use
  `--all` para revarrer tudo (útil para reconfirmar as verificadas).

Resultado: output/fais_varredura.csv e .xlsx — revise e promova os achados
para `src/fais_data.py` (preenchendo site/ouvidoria/canal_url/status).

Por padrão varre apenas as FAIs de **universidades federais** (mesmo recorte da
planilha). Use `--todas` para incluir estaduais/IFs/ICTs.

Uso:
    uv run python -m src.scraper_fundacoes            # federais, só pendentes
    uv run python -m src.scraper_fundacoes --all      # federais, revarre todas
    uv run python -m src.scraper_fundacoes --todas    # inclui todas as esferas
"""

import os
import re
import sys
import json
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
import urllib3
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

try:
    from src.fais_data import FAIS
    from src.gerar_planilha import tipo_ies, ESCOPO_FEDERAL
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.fais_data import FAIS
    from src.gerar_planilha import tipo_ies, ESCOPO_FEDERAL

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()
console = Console()

CACHE_FILE = Path("output/cache_varredura.json")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# Palavras-chave por categoria de força (define a classificação).
KW_OUVIDORIA = ["ouvidoria", "denuncia", "denúncia", "linha etica", "linha ética", "canal-de-etica", "canal de etica"]
KW_COMPLIANCE = ["compliance", "integridade", "etica", "ética", "transparencia", "transparência", "fala.br", "falabr"]
TODAS_KW = KW_OUVIDORIA + KW_COMPLIANCE


def load_cache():
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_cache(cache):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def descobrir_site(nome, instituicao):
    """Tenta achar o site oficial da fundação. Só roda se houver chave de API."""
    google_key = os.getenv("GOOGLE_API_KEY")
    google_cx = os.getenv("GOOGLE_CX")
    tavily_key = os.getenv("TAVILY_API_KEY")

    query = f'"{nome}" fundação de apoio {instituicao} site oficial'

    if google_key and google_cx:
        try:
            from googleapiclient.discovery import build
            service = build("customsearch", "v1", developerKey=google_key)
            res = service.cse().list(q=query, cx=google_cx, num=1).execute()
            items = res.get("items", [])
            if items:
                return items[0]["link"]
        except Exception:
            pass

    if tavily_key:
        try:
            res = requests.post(
                "https://api.tavily.com/search",
                json={"api_key": tavily_key, "query": query, "search_depth": "basic", "max_results": 2},
                timeout=20,
            ).json()
            for r in res.get("results", []):
                link = r["url"]
                if not any(b in link for b in ("wikipedia", "gov.br", "jus.br", "facebook", "linkedin")):
                    return link
            if res.get("results"):
                return res["results"][0]["url"]
        except Exception:
            pass

    return ""


def varrer_site(url_base):
    """Varre a home e classifica. Retorna (classificacao, status, evidencias)."""
    if not url_base or not url_base.startswith("http"):
        return "Sem site cadastrado", "—", ""

    try:
        resp = requests.get(url_base, headers=HEADERS, timeout=15, verify=False)
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        return "Erro de conexão", str(e).split(":", 1)[0], ""

    achados_ouvidoria = set()
    achados_compliance = set()

    for a in soup.find_all("a", href=True):
        texto = a.get_text().strip().lower()
        href = a["href"].lower()
        alvo = f"{texto} {href}"
        link_abs = urljoin(url_base, a["href"])

        if any(k in alvo for k in KW_OUVIDORIA):
            achados_ouvidoria.add(link_abs)
        elif any(k in alvo for k in KW_COMPLIANCE):
            achados_compliance.add(link_abs)

    if achados_ouvidoria:
        evid = " | ".join(sorted(achados_ouvidoria)[:3])
        return "Sim (provável)", "Canal de ouvidoria/denúncia encontrado", evid
    if achados_compliance:
        evid = " | ".join(sorted(achados_compliance)[:3])
        return "Parcial (provável)", "Só compliance/transparência na home", evid
    return "Não encontrado", "Sem link de ouvidoria na home", ""


def main(revarrer_tudo=False, todas_esferas=False):
    console.print("[bold cyan]Varredura de Ouvidorias das Fundações de Apoio[/bold cyan]\n")

    base = FAIS if todas_esferas else [f for f in FAIS if tipo_ies(f["instituicao"]) in ESCOPO_FEDERAL]
    alvos = [f for f in base if revarrer_tudo or f["status"] != "Verificado"]
    escopo = "todas as esferas" if todas_esferas else "universidades federais"
    console.print(
        f"Recorte: [yellow]{escopo}[/] ({len(base)} fundações) · varrendo [yellow]{len(alvos)}[/] "
        f"({'todas' if revarrer_tudo else 'apenas pendentes'}).\n"
    )

    cache = load_cache()
    resultados = []

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
        BarColumn(), TaskProgressColumn(), console=console,
    ) as progress:
        task = progress.add_task("[cyan]Varrendo...", total=len(alvos))

        for f in alvos:
            sigla = f["sigla"]
            site = f["site"]

            if sigla in cache:
                dados = cache[sigla]
            else:
                if not site:
                    site = descobrir_site(f["nome"], f["instituicao"])
                classificacao, status_scan, evidencias = varrer_site(site)
                dados = {
                    "site_usado": site,
                    "scan_classificacao": classificacao,
                    "scan_status": status_scan,
                    "scan_evidencias": evidencias,
                }
                cache[sigla] = dados
                save_cache(cache)
                time.sleep(0.3)

            resultados.append({
                "Sigla": sigla,
                "Nome": f["nome"],
                "Instituição": f["instituicao"],
                "UF": f["uf"],
                "Ouvidoria (curada)": f["ouvidoria"],
                "Site usado": dados["site_usado"],
                "Classificação (scan)": dados["scan_classificacao"],
                "Detalhe (scan)": dados["scan_status"],
                "Evidências (links)": dados["scan_evidencias"],
            })
            progress.update(task, advance=1, description=f"[cyan]{sigla}")

    df = pd.DataFrame(resultados)
    Path("output").mkdir(exist_ok=True)
    df.to_csv("output/fais_varredura.csv", index=False, encoding="utf-8-sig")
    try:
        df.to_excel("output/fais_varredura.xlsx", index=False)
    except Exception as e:
        console.print(f"[yellow]Excel não gerado: {e}[/]")

    console.print("\n[bold green]✓ Varredura concluída.[/] Resultados em output/fais_varredura.csv / .xlsx")
    console.print(
        "[dim]Revise os achados 'Sim/Parcial (provável)' e promova-os para "
        "src/fais_data.py (preenchendo site/ouvidoria/canal_url/status='Verificado').[/]"
    )


if __name__ == "__main__":
    main(revarrer_tudo="--all" in sys.argv, todas_esferas="--todas" in sys.argv)
