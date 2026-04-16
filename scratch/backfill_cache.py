import pandas as pd
import json
import os

def main():
    p = 'output/ouvidorias_lista.csv'
    c = 'output/cache_buscas.json'
    d = {}
    if os.path.exists(p):
        df = pd.read_csv(p)
        for i, row in df.iterrows():
            k = f"{row['Nome']} - {row['Sigla']}"
            link = row.get('Página da Ouvidoria Encontrada', '')
            title = row.get('Título da Página', '')
            if pd.notna(link) and 'Erro' not in str(link) and 'Não encontrado' not in str(link):
                d[k] = {'link': str(link), 'title': str(title) if pd.notna(title) else ''}
        
        if d:
            os.makedirs('output', exist_ok=True)
            with open(c, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=4)
            print(f"Cache preenchido com {len(d)} itens retroativos!")
        else:
            print("Nenhum item válido para cachear.")
    else:
        print("CSV não encontrado.")

if __name__ == '__main__':
    main()
