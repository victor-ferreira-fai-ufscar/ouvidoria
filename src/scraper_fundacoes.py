import os
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib3
import json
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

# Desativa avisos de SSL (comum em sites acadêmicos/fundações mais antigos)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
console = Console()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
CACHE_FILE_FUND = Path("output/cache_fundacoes.json")

def load_cache():
    if CACHE_FILE_FUND.exists():
        with open(CACHE_FILE_FUND, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except json.JSONDecodeError: return {}
    return {}

def save_cache(cache):
    CACHE_FILE_FUND.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE_FUND, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)

def buscar_fundacao_tavily(uni_nome, sigla):
    """ Busca o site oficial da Fundação de Apoio da Universidade usando IA (Tavily) """
    if not TAVILY_API_KEY:
        return "Desconhecido", "API_KEY Ausente"
        
    query = f'"Fundação de Apoio" universidade {uni_nome} {sigla} site oficial'
    try:
        url = "https://api.tavily.com/search"
        headers = {"Content-Type": "application/json"}
        data = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "basic",
            "max_results": 2,
            "include_answer": False
        }
        res = requests.post(url, json=data, headers=headers).json()
        if "results" in res and res["results"]:
            for r in res["results"]:
                link = r["url"]
                title = r["title"]
                # Filtros para evitar pegar portal da transparência ou diário oficial
                if 'jus.br' not in link and 'gov.br' not in link and 'wikipedia' not in link:
                    return title, link
            return res["results"][0]["title"], res["results"][0]["url"]
            
        return "Fundação não identificada na busca", "Não Encontrado"
    except Exception as e:
        return "Erro Tavily", str(e)

def varrer_site_fundacao(url_base):
    if "Não Encontrado" in url_base or not url_base.startswith("http"):
        return "Site Inválido", ""
        
    palavras_chave = [
        'ouvidoria', 'denuncia', 'denúncia', 'compliance', 'etica', 'ética', 
        'integridade', 'fala.br', 'falabr'
    ]
    
    links_encontrados = set()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # Pega a home page
        response = requests.get(url_base, headers=headers, timeout=12, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for a_tag in soup.find_all('a', href=True):
            texto_link = a_tag.get_text().strip().lower()
            href = a_tag['href'].lower()
            
            if any(p in texto_link for p in palavras_chave) or any(p in href for p in palavras_chave):
                if href.startswith('/'):
                    # Limpa a barra final do url base adequadamente
                    href_completo = url_base.rstrip('/') + href
                elif href.startswith('http'):
                    href_completo = href
                else:
                    continue 
                links_encontrados.add(href_completo)
                
        if links_encontrados:
            return "Canal Identificado", " | ".join(links_encontrados)
        return "Oculto na Home / Requer Busca Manual", "Nenhum link direto"
        
    except Exception as e:
        return "Erro de Conexão", f"Site offline ou bloqueou a varredura ({str(e).split(':', 1)[0]})"

def main():
    console.print("[bold cyan]Iniciando IA Scanner: Fundações de Apoio das Federais[/bold cyan]\n")
    
    lista_federais = "output/ouvidorias_lista.csv"
    if not os.path.exists(lista_federais):
        console.print("[bold red]Base de dados não encontrada![/] Execute o script de universidades primeiro.")
        return
        
    # Carrega base, filtra apenas as Federais
    df = pd.read_csv(lista_federais)
    federais = df[df['Tipo'] == 'Federal'].copy()
    
    console.print(f"Encontramos [yellow]{len(federais)}[/] Universidades Federais mapeadas.\n")
    
    resultados = []
    cache_fundacoes = load_cache()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Varrendo Fundações (Pesquisa IA + Scraping)...", total=len(federais))
        
        for _, row in federais.iterrows():
            nome_uni = row['Nome']
            sigla_uni = row['Sigla']
            cache_key = f"{sigla_uni}"
            
            # Etapa 1: Descobrir o site da fundação
            if cache_key in cache_fundacoes:
                nome_fundacao = cache_fundacoes[cache_key]['nome']
                url_fundacao = cache_fundacoes[cache_key]['url']
            else:
                nome_fundacao, url_fundacao = buscar_fundacao_tavily(nome_uni, sigla_uni)
                cache_fundacoes[cache_key] = {'nome': nome_fundacao, 'url': url_fundacao}
                save_cache(cache_fundacoes)
            
            # Etapa 2: Varrer a homepage da fundação em busca de ouvidoria
            status_site, links_compl = varrer_site_fundacao(url_fundacao)
            
            resultados.append({
                "Universidade Apoiada": f"{nome_uni} ({sigla_uni})",
                "Fundação Encontrada (Tavily/IA)": nome_fundacao,
                "Site da Fundação": url_fundacao,
                "Status Varredura": status_site,
                "Links de Integridade": links_compl
            })
            
            progress.update(task, advance=1, description=f"[cyan]Analisando: Fundação da {sigla_uni}")
            time.sleep(0.5)

    df_final = pd.DataFrame(resultados)
    df_final.to_csv("output/mapeamento_fundacoes_apoio.csv", index=False, encoding='utf-8')
    df_final.to_excel("output/mapeamento_fundacoes_apoio.xlsx", index=False)
    
    console.print("\n[bold green]🚀 Varredura concluída! Arquivos CSV e Excel das Fundações gerados em output/[/]")

if __name__ == '__main__':
    main()
