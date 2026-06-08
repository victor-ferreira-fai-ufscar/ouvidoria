"""
Gera a planilha de Ouvidorias das Fundações de Apoio (FAIs).

FOCO: Fundações de Apoio de **universidades federais** — verificando se têm
sistema de ouvidoria PRÓPRIO ou se usam o sistema unificado do governo federal
(Fala.BR / ouvidoria da universidade).

Saídas:
    - output/ouvidorias_fais_federais.xlsx  (Excel — entregável principal)
    - output/ouvidorias_fais_federais.csv   (CSV)
    - docs/ouvidorias_fais.md               (Markdown, visível no GitHub)

Fonte única de verdade: src/fais_data.py (contém TODAS as FAIs; estaduais,
institutos federais e ICTs ficam na base, mas fora deste recorte federal).

Uso:
    uv run python -m src.gerar_planilha            # só universidades federais
    uv run python -m src.gerar_planilha --todas    # inclui estaduais/IFs/ICTs
"""

import re
import sys
from pathlib import Path
from collections import Counter

import pandas as pd

try:
    from src.fais_data import FAIS
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.fais_data import FAIS

OUTPUT_DIR = Path("output")   # CSV/Excel (regeneráveis, fora do git)
DOCS_DIR = Path("docs")       # Markdown legível (versionado, visível no GitHub)

# --------------------------------------------------------------------------
# Classificação do tipo de instituição apoiada (a partir do campo instituicao)
# --------------------------------------------------------------------------
_UNI_FED_EXPLICITAS = {"UNB", "UNIFESP", "UNIFEI", "UNIFAL", "UNILAB", "UTFPR", "FURG"}
_ESTADUAIS = {"USP", "UNESP", "UNICAMP", "UEA", "UEL", "UNEMAT", "UEMG", "UNEB", "UNICENTRO", "IPT", "FCAV"}
_ICT_FEDERAL = {"INPE", "FIOCRUZ", "EMBRAPA", "LNCC", "CTI", "IME", "ITA", "MARINHA", "NIT", "DCT", "DECEX", "EXÉRCITO", "EXERCITO"}

TIPO_UNI_FEDERAL = "Universidade Federal"
TIPO_HU_FEDERAL = "Hospital Universitário Federal"
TIPO_INSTITUTO = "Instituto/CEFET Federal"
TIPO_ESTADUAL = "Estadual"
TIPO_ICT = "ICT Federal (não-universidade)"

# Recorte do entregável federal: universidades federais (e seus hospitais).
ESCOPO_FEDERAL = {TIPO_UNI_FEDERAL, TIPO_HU_FEDERAL}


def _tokens(instituicao: str):
    return [t.strip().upper() for t in re.split(r"[,/()\-\s]+", instituicao) if t.strip()]


def tipo_ies(instituicao: str) -> str:
    toks = _tokens(instituicao)
    if any(t in _UNI_FED_EXPLICITAS or t.startswith("UF") for t in toks):
        return TIPO_UNI_FEDERAL
    if any(t.startswith("HU") or t.startswith("HC") for t in toks):
        return TIPO_HU_FEDERAL
    if any(t.startswith("IF") or "CEFET" in t for t in toks):
        return TIPO_INSTITUTO
    if any(t in _ESTADUAIS for t in toks):
        return TIPO_ESTADUAL
    if any(t in _ICT_FEDERAL for t in toks):
        return TIPO_ICT
    return "Outro"


# Sistema de ouvidoria, na ótica da pergunta: própria x unificado federal.
SISTEMA = {
    "Sim": "Própria",
    "Parcial": "Própria (parcial) + Fala.BR / universidade",
    "Não": "Fala.BR / ouvidoria da universidade",
    "A verificar": "A verificar",
}

COLUNAS_SAIDA = ["sigla", "nome", "instituicao", "uf", "tipo_ies", "sistema",
                 "ouvidoria", "canal_url", "status", "obs"]

ROTULOS = {
    "sigla": "Sigla",
    "nome": "Nome da Fundação",
    "instituicao": "Instituição(ões) Apoiada(s)",
    "uf": "UF",
    "tipo_ies": "Tipo de Instituição",
    "sistema": "Sistema de Ouvidoria",
    "ouvidoria": "Ouvidoria Própria?",
    "canal_url": "Canal / URL",
    "status": "Verificação",
    "obs": "Observações",
}


def montar_dataframe(somente_federais: bool = True) -> pd.DataFrame:
    df = pd.DataFrame(FAIS)
    df["tipo_ies"] = df["instituicao"].map(tipo_ies)
    df["sistema"] = df["ouvidoria"].map(SISTEMA).fillna(df["ouvidoria"])

    if somente_federais:
        df = df[df["tipo_ies"].isin(ESCOPO_FEDERAL)].copy()

    df = df[COLUNAS_SAIDA]
    # Verificadas primeiro; depois por UF e sigla.
    df["_ord"] = df["status"].map({"Verificado": 0}).fillna(1)
    df = df.sort_values(["_ord", "uf", "sigla"]).drop(columns="_ord").reset_index(drop=True)
    return df


def resumo_estatistico(df: pd.DataFrame) -> pd.DataFrame:
    c = Counter(df["ouvidoria"])
    linhas = [
        {"Indicador": "Total de fundações (universidades federais)", "Valor": len(df)},
        {"Indicador": "Sistema de ouvidoria PRÓPRIO (Sim)", "Valor": c.get("Sim", 0)},
        {"Indicador": "Próprio parcial (transparência/compliance + Fala.BR)", "Valor": c.get("Parcial", 0)},
        {"Indicador": "Usa Fala.BR / ouvidoria da universidade (Não)", "Valor": c.get("Não", 0)},
        {"Indicador": "Pendentes de verificação (varredura)", "Valor": c.get("A verificar", 0)},
        {"Indicador": "Verificadas manualmente", "Valor": int((df["status"] == "Verificado").sum())},
    ]
    return pd.DataFrame(linhas)


def _ajustar_larguras(writer, sheet_name: str, df: pd.DataFrame) -> None:
    ws = writer.sheets[sheet_name]
    for i, col in enumerate(df.columns, start=1):
        largura = max(len(str(col)), *(df[col].astype(str).map(len).tolist() or [0]))
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = min(largura + 2, 60)


def exportar_csv(df: pd.DataFrame) -> Path:
    destino = OUTPUT_DIR / "ouvidorias_fais_federais.csv"
    df.rename(columns=ROTULOS).to_csv(destino, index=False, encoding="utf-8-sig")
    return destino


def exportar_excel(df: pd.DataFrame) -> Path:
    destino = OUTPUT_DIR / "ouvidorias_fais_federais.xlsx"
    resumo = resumo_estatistico(df)
    df_lbl = df.rename(columns=ROTULOS)
    with pd.ExcelWriter(destino, engine="openpyxl") as writer:
        df_lbl.to_excel(writer, sheet_name="Fundações Federais", index=False)
        resumo.to_excel(writer, sheet_name="Resumo", index=False)
        _ajustar_larguras(writer, "Fundações Federais", df_lbl)
        _ajustar_larguras(writer, "Resumo", resumo)
    return destino


def exportar_markdown(df: pd.DataFrame) -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    destino = DOCS_DIR / "ouvidorias_fais.md"
    resumo = resumo_estatistico(df)
    emoji = {"Sim": "✅ Sim", "Parcial": "🟡 Parcial", "Não": "❌ Não", "A verificar": "🔍 A verificar"}

    L = []
    L.append("# Ouvidorias das Fundações de Apoio — Universidades Federais\n")
    L.append(
        "Mapeamento das **fundações de apoio (FAIs) de universidades federais**, "
        "indicando se possuem **sistema de ouvidoria próprio** ou se utilizam o "
        "**sistema unificado do governo federal (Fala.BR)** / a ouvidoria da universidade.\n"
    )
    L.append("> Fonte da relação: CONFIES (afiliadas) + pesquisa manual. "
             "Gerado por `src/gerar_planilha.py`. Estaduais, institutos federais e "
             "ICTs não-universitárias ficam na base, mas fora deste recorte.\n")

    L.append("## Resumo\n")
    L.append("| Indicador | Valor |")
    L.append("|---|---|")
    for _, r in resumo.iterrows():
        L.append(f"| {r['Indicador']} | {r['Valor']} |")
    L.append("")
    L.append("**Legenda:** ✅ Sim = sistema próprio · 🟡 Parcial = tem transparência/compliance "
             "própria, mas ouvidoria via Fala.BR/universidade · ❌ Não = usa Fala.BR / ouvidoria "
             "da universidade · 🔍 A verificar = pendente de varredura.\n")

    L.append("## Fundações\n")
    cab = ["Sigla", "Fundação", "Instituição", "UF", "Sistema de Ouvidoria", "Própria?", "Canal / URL", "Verificação"]
    L.append("| " + " | ".join(cab) + " |")
    L.append("|" + "|".join(["---"] * len(cab)) + "|")
    for _, r in df.iterrows():
        canal = r["canal_url"] or "—"
        if canal.startswith("http"):
            canal = f"[link]({canal})"
        L.append("| " + " | ".join([
            f"**{r['sigla']}**", r["nome"], r["instituicao"], r["uf"],
            r["sistema"], emoji.get(r["ouvidoria"], r["ouvidoria"]), canal, r["status"],
        ]) + " |")
    L.append("")
    destino.write_text("\n".join(L), encoding="utf-8")
    return destino


def main(somente_federais: bool = True):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = montar_dataframe(somente_federais=somente_federais)

    csv_path = exportar_csv(df)
    md_path = exportar_markdown(df)
    try:
        xlsx_path = exportar_excel(df)
    except Exception as e:
        xlsx_path = None
        print(f"[aviso] Excel não gerado: {e}")

    escopo = "universidades federais" if somente_federais else "todas as esferas"
    print(f"✓ {len(df)} fundações exportadas ({escopo}):")
    if xlsx_path:
        print(f"  - {xlsx_path}   ← planilha principal (Excel)")
    print(f"  - {csv_path}")
    print(f"  - {md_path}")
    print("\nResumo:")
    for _, r in resumo_estatistico(df).iterrows():
        print(f"  {r['Indicador']}: {r['Valor']}")


if __name__ == "__main__":
    main(somente_federais="--todas" not in sys.argv)
