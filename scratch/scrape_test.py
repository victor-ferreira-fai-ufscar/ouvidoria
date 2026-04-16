from playwright.sync_api import sync_playwright
import bs4

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://pt.wikipedia.org/wiki/Lista_de_universidades_estaduais_do_Brasil')
        html = page.content()
        soup = bs4.BeautifulSoup(html, 'html.parser')
        
        # Onde a lista das estaduais está?
        # Normalmente sob h2 ou h3 por regiões ou estados
        # Vamos olhar as listas
        items = soup.select('.mw-parser-output ul li')
        results = set()
        for item in items:
            text = item.get_text()
            if 'Universidade Estadual' in text or 'Universidade do Estado' in text or 'Faculdade Estadual' in text \
               or 'Centro Universitário Estadual' in text or 'Universidade' in text:
                if ' – ' in text or ' - ' in text or '(' in text:
                    results.add(text)
                    
        with open('scratch/estaduais_dump.txt', 'w', encoding='utf-8') as f:
            for r in results:
                f.write(r + '\n')
                
        browser.close()

if __name__ == '__main__':
    main()
