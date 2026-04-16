import os
import time
import time
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

# Carrega variáveis de ambiente
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")

CACHE_FILE = Path("output/cache_buscas.json")

def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_cache(cache):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)

# Limpa o GOOGLE_CX caso o usuário tenha colado a URL inteira por engano
if GOOGLE_CX and "cx=" in GOOGLE_CX:
    import re
    match = re.search(r'cx=([\w]+)', GOOGLE_CX)
    if match:
        GOOGLE_CX = match.group(1)

console = Console()

def extract_universities_from_table(page, tipo):
    js_code = r'''(tipo) => {
        const results = [];
        const tables = document.querySelectorAll('table.wikitable');
        tables.forEach(table => {
            const headers = Array.from(table.querySelectorAll('th')).map(th => th.innerText.trim().toLowerCase());
            
            // Busca pelos índices das colunas de Nome e Sigla dinamicamente
            let nomeIdx = headers.findIndex(h => h.includes('nome') || h.includes('universidade') || h.includes('instituição'));
            let siglaIdx = headers.findIndex(h => h.includes('sigla'));
            let estIdx = headers.findIndex(h => h.includes('estado') || h.includes('uf') || h.includes('unidade federativa') || h.includes('sede'));
            
            if (nomeIdx !== -1 && siglaIdx !== -1) {
                table.querySelectorAll('tr').forEach(tr => {
                    // Pode haver ths misturados nas linhas, pegamos todos os text contents
                    const cells = tr.querySelectorAll('td, th');
                    // Ignora as linhas de cabeçalho
                    if (cells.length > Math.max(nomeIdx, siglaIdx) && tr.querySelector('td')) {
                        const nome = cells[nomeIdx].innerText.trim().replace(/\n/g, ' ');
                        const sigla = cells[siglaIdx].innerText.trim().replace(/\n/g, ' ');
                        const estado = estIdx !== -1 && cells.length > estIdx ? cells[estIdx].innerText.trim().replace(/\n/g, ' ') : 'Brasil';
                        
                        // Limpeza básica
                        if (nome && sigla && nome.length > 5 && sigla.length >= 2 && !results.some(r => r.nome === nome)) {
                            results.push({nome: nome, sigla: sigla, tipo: tipo, estado: estado});
                        }
                    }
                });
            }
        });'
        
        // Fallback para estaduais que não estão em formato tabela
        if (results.length === 0 && tipo === 'Estadual') {
            let currentState = 'Desconhecido';
            document.querySelectorAll('.mw-parser-output h2, .mw-parser-output h3, .mw-parser-output ul').forEach(el => {
                if (el.tagName === 'H2' || el.tagName === 'H3') {
                    const headline = el.querySelector('.mw-headline');
                    if (headline) currentState = headline.innerText.trim();
                }
                if (el.tagName === 'UL') {
                    el.querySelectorAll('li').forEach(li => {
                        const text = li.innerText.trim();
                        const match = text.match(/([^\(]+)\s*\(([A-Za-z]+)\)/);
                        if (match) {
                            let nome = match[1].trim();
                            let sigla = match[2].trim();
                            
                            // Tratamento para limpar " [1]", " [2]" etc e outros lixos visuais do texto
                            nome = nome.replace(/\[\d+\]|–.*|-.*| Dissolvida/g, '').trim();
                            
                            if (nome.includes('Universidade') || nome.includes('Centro')) {
                                 if (nome.length > 5 && sigla.length >= 2 && !results.some(r => r.nome === nome)) {
                                     results.push({nome: nome, sigla: sigla, tipo: tipo, estado: currentState});
                                 }
                            }
                        }
                    });
                }
            });
        }
        return results;
    }'''
    return page.evaluate(js_code, tipo)


def get_wikipedia_universities(playwright):
    universities = []
    
    with console.status("[bold cyan]Coletando listas de universidades da Wikipedia via Playwright...") as status:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        # --- Federais ---
        status.update("[bold cyan]Acessando Wikipédia: Universidades Federais...")
        page.goto("https://pt.wikipedia.org/wiki/Lista_de_universidades_federais_do_Brasil")
        fed_rows = extract_universities_from_table(page, 'Federal')
        universities.extend(fed_rows)

        # --- Estaduais ---
        status.update("[bold cyan]Acessando Wikipédia: Universidades Estaduais...")
        page.goto("https://pt.wikipedia.org/wiki/Lista_de_universidades_estaduais_do_Brasil")
        est_rows = extract_universities_from_table(page, 'Estadual')
        universities.extend(est_rows)
        
        browser.close()
        
    console.print(f"[bold green]Coleta concluída![/] {len(fed_rows)} Federais e {len(est_rows)} Estaduais encontradas.")
    return universities

def search_ouvidoria_tavily(nome, sigla):
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    if not TAVILY_API_KEY:
         return "Erro: Google falhou e Chave Tavily indisponível", ""
         
    query = f'site oficial ouvidoria ou fala.br universidade {nome} {sigla}'
    try:
        import requests
        url = "https://api.tavily.com/search"
        headers = {"Content-Type": "application/json"}
        data = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "basic",
            "max_results": 1,
            "include_answer": False
        }
        res = requests.post(url, json=data, headers=headers).json()
        if "results" in res and res["results"]:
            return res["results"][0]["url"], res["results"][0]["title"]
        return "Não encontrado na Tavily", "Não encontrado"
    except Exception as e:
        return f"Erro Tavily: {str(e)}", ""

def search_ouvidoria(service, nome, sigla):
    # A query procura rigorosamente pelo nome da universidade e indícios de canais de denúncia/ouvidoria
    query = f'"{nome}" (ouvidoria OR "Fala.BR" OR compliance OR denúncia)'
    try:
        res = service.cse().list(q=query, cx=GOOGLE_CX, num=1).execute()
        items = res.get('items', [])
        if items:
            return items[0]['link'], items[0]['title']
        return "Não encontrado", "Não encontrado"
    except HttpError as e:
        # Qualquer erro de API do Google (403 Forbidden, 400 Bad Request, 429 Quota) vai para o Fallback Tavily
        return search_ouvidoria_tavily(nome, sigla)
    except Exception as e:
        return search_ouvidoria_tavily(nome, sigla)

def main():
    console.print("[bold cyan]Iniciando o Mapeamento de Ouvidorias[/bold cyan]\n")
    
    if (not GOOGLE_API_KEY or not GOOGLE_CX) and not os.getenv("TAVILY_API_KEY"):
        console.print("[bold red]ATENÇÃO:[/] Nenhuma API Key configurada.")
        console.print("Por favor, preencha GOOGLE_API_KEY e GOOGLE_CX, ou informe uma TAVILY_API_KEY no arquivo [bold].env[/]")
        return

    # Extrai Universidade usando Playwright
    with sync_playwright() as p:
        universities = get_wikipedia_universities(p)
        
    if not universities:
        console.print("[bold red]Nenhuma universidade encontrada. Falha no scraping da Wikipédia.[/]")
        return

    # Configura serviço do Google Search
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    
    resultados = []
    
    # Carrega cache
    cache = load_cache()
    
    # Executa a busca processando a UI interativa com rich
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Buscando Ouvidorias no Google...", total=len(universities))
        
        for uni in universities:
            # Respeitar limites para não sobrecarregar e evitar Timeouts rápidos
            time.sleep(0.5) 
            
            nome = uni['nome']
            sigla = uni['sigla']
            cache_key = f"{nome} - {sigla}"
            
            if cache_key in cache:
                link = cache[cache_key]['link']
                title = cache[cache_key]['title']
            else:
                link, title = search_ouvidoria(service, nome, sigla)
                cache[cache_key] = {'link': link, 'title': title}
                save_cache(cache) # Salva a cada descoberta para não perder
            
            resultados.append({
                "Nome": nome,
                "Sigla": sigla,
                "Estado": uni.get('estado', 'Desconhecido'),
                "Tipo": uni['tipo'],
                "Página da Ouvidoria Encontrada": link,
                "Título da Página": title
            })
            
            progress.update(task, advance=1, description=f"[cyan]Verificando: {sigla}")

    console.print("\n[bold green]Busca finalizada! Exportando relatórios...[/]")
    df = pd.DataFrame(resultados)
    
    # Limpa caracteres zumbis eventuais
    df['Nome'] = df['Nome'].str.replace(r'\[.*?\]', '', regex=True) # remove referências tipo [1]
    
    # Remove duplicatas pela Sigla (ex: a Wikipédia às vezes lista a UNILAB duas vezes)
    df = df.drop_duplicates(subset=['Sigla'], keep='first')
    
    df.to_csv("output/ouvidorias_lista.csv", index=False, encoding='utf-8')
    df.to_excel("output/ouvidorias_lista.xlsx", index=False)
    
    console.print("[bold blue]✓ Arquivos `ouvidorias_lista.csv` e `.xlsx` gerados com sucesso na pasta output/![/]")

if __name__ == "__main__":
    main()
