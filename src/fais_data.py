"""
Base curada das Fundações de Apoio (FAIs) credenciadas às IFES/ICTs.

Fonte da relação (universo autoritativo): CONFIES — Conselho Nacional das
Fundações de Apoio às Instituições de Ensino Superior e de Pesquisa Científica
e Tecnológica (lista de afiliadas), complementada pela pesquisa manual em
docs/problema.md.

Esta é a ÚNICA fonte de verdade do projeto. Os scripts
`src/gerar_planilha.py` (gera Markdown/CSV/Excel) e `src/scraper_fundacoes.py`
(varredura automática de canais de ouvidoria) leem desta base.

Campos por fundação:
    sigla       : sigla da fundação
    nome        : nome (completo quando conhecido)
    instituicao : IES/ICT apoiada (pode ser mais de uma)
    uf          : unidade federativa
    esfera      : "Federal" | "Estadual" | "ICT Federal"
    site        : site oficial (quando conhecido; usado pela varredura)
    ouvidoria   : "Sim" | "Não" | "Parcial" | "A verificar"
                  - Sim     => canal de ouvidoria/ética/denúncias PRÓPRIO
                  - Parcial => tem transparência/compliance, mas ouvidoria
                               formal é direcionada à universidade/Fala.BR
                  - Não     => sem canal próprio; usa a ouvidoria da
                               universidade e/ou Fala.BR
    canal_url   : URL do canal de ouvidoria/denúncias (quando conhecido)
    status      : "Verificado" (checado manualmente) | "Pendente"
    obs         : observações / fonte
"""

# Linhas com status "Verificado" foram conferidas manualmente (jun/2026).
# Linhas "Pendente" entram na fila da varredura automática do scraper.
FAIS = [
    # ----------------------- VERIFICADAS MANUALMENTE -----------------------
    {
        "sigla": "FUNDEP", "nome": "Fundação de Desenvolvimento da Pesquisa",
        "instituicao": "UFMG, UFABC, ITA", "uf": "MG", "esfera": "Federal",
        "site": "https://www.fundep.br", "ouvidoria": "Sim",
        "canal_url": "https://www.fundep.br/canal-de-denuncias/",
        "status": "Verificado",
        "obs": "Canal de Denúncias gerido por empresa externa (anonimato); programa de compliance/Código de Conduta.",
    },
    {
        "sigla": "FUNCAMP", "nome": "Fundação de Desenvolvimento da Unicamp",
        "instituicao": "UNICAMP", "uf": "SP", "esfera": "Estadual",
        "site": "https://www.funcamp.unicamp.br", "ouvidoria": "Sim",
        "canal_url": "https://www.funcamp.unicamp.br",
        "status": "Verificado",
        "obs": "Canal de Denúncias e Remediação (programa de compliance); formulário web e WhatsApp dedicado.",
    },
    {
        "sigla": "FINATEC", "nome": "Fundação de Empreendimentos Científicos e Tecnológicos",
        "instituicao": "UnB", "uf": "DF", "esfera": "Federal",
        "site": "https://www.finatec.org.br", "ouvidoria": "Sim",
        "canal_url": "https://www.finatec.org.br",
        "status": "Verificado",
        "obs": "Possui Ouvidoria e Linha Ética; atuação ativa em auditoria e transparência ativa.",
    },
    {
        "sigla": "FADE", "nome": "Fundação de Apoio ao Desenvolvimento da UFPE",
        "instituicao": "UFPE", "uf": "PE", "esfera": "Federal",
        "site": "https://www.fade.org.br", "ouvidoria": "Sim",
        "canal_url": "https://www.fade.org.br",
        "status": "Verificado",
        "obs": "Seção de Ouvidoria no portal de transparência; manifestações da sociedade e de pesquisadores.",
    },
    {
        "sigla": "FUNPEC", "nome": "Fundação Norte-Rio-Grandense de Pesquisa e Cultura",
        "instituicao": "UFRN", "uf": "RN", "esfera": "Federal",
        "site": "https://www.funpec.br", "ouvidoria": "Sim",
        "canal_url": "https://www.funpec.br",
        "status": "Verificado",
        "obs": "Disponibiliza canal de Ouvidoria e Serviço de Informação ao Cidadão (SIC).",
    },
    {
        "sigla": "FAP UNIFESP", "nome": "Fundação de Apoio à UNIFESP",
        "instituicao": "UNIFESP, UFABC", "uf": "SP", "esfera": "Federal",
        "site": "https://www.fapunifesp.edu.br", "ouvidoria": "Sim",
        "canal_url": "https://www.fapunifesp.edu.br",
        "status": "Verificado",
        "obs": "Canal de comunicação direta para transparência/compliance; LGPD e Portal da Transparência.",
    },
    {
        "sigla": "FUNARBE", "nome": "Fundação de Apoio à Universidade Federal de Viçosa",
        "instituicao": "UFV", "uf": "MG", "esfera": "Federal",
        "site": "https://funarbe.org.br", "ouvidoria": "Sim",
        "canal_url": "https://funarbe.org.br/a-funarbe/compliance/",
        "status": "Verificado",
        "obs": "Canal de Ouvidoria gerido por escritório externo; ISO 37301/37001; selo CGU 'Pacto Brasil pela Integridade'.",
    },
    {
        "sigla": "FUNAPE", "nome": "Fundação de Apoio à Pesquisa",
        "instituicao": "UFG", "uf": "GO", "esfera": "Federal",
        "site": "https://site.funape.org.br", "ouvidoria": "Sim",
        "canal_url": "https://site.funape.org.br/ouvidoria.php",
        "status": "Verificado",
        "obs": "Página de Ouvidoria própria + Política de Compliance (Lei 13.460/2017).",
    },
    {
        "sigla": "FAPEC", "nome": "Fundação de Apoio à Pesquisa, ao Ensino e à Cultura",
        "instituicao": "UFMS", "uf": "MS", "esfera": "Federal",
        "site": "https://fundacaofapec.org.br", "ouvidoria": "Sim",
        "canal_url": "https://fundacaofapec.org.br",
        "status": "Verificado",
        "obs": "Ouvidoria por e-mail; única fundação credenciada MEC/MCTI de apoio à UFMS.",
    },
    {
        "sigla": "FCPC", "nome": "Fundação Cearense de Pesquisa e Cultura",
        "instituicao": "UFC", "uf": "CE", "esfera": "Federal",
        "site": "https://fcpc.ufc.br", "ouvidoria": "Sim",
        "canal_url": "https://fcpc.ufc.br/ouvidoria/",
        "status": "Verificado",
        "obs": "Ouvidoria própria criada pela Portaria 007/2016; ouvidoria@fcpc.ufc.br.",
    },
    {
        "sigla": "COPPETEC", "nome": "Fundação Coordenação de Projetos, Pesquisas e Estudos Tecnológicos",
        "instituicao": "UFRJ", "uf": "RJ", "esfera": "Federal",
        "site": "https://www.coppetec.coppe.ufrj.br", "ouvidoria": "Sim",
        "canal_url": "https://ouvidoria.coppetec.coppe.ufrj.br/",
        "status": "Verificado",
        "obs": "Ouvidoria própria (ouvidoria.coppetec.coppe.ufrj.br) + Política de Integridade/Transparência; auditada pelo MP (Curadoria de Fundações).",
    },
    {
        "sigla": "FADESP", "nome": "Fundação de Amparo e Desenvolvimento da Pesquisa",
        "instituicao": "UFPA", "uf": "PA", "esfera": "Federal",
        "site": "https://portalfadesp.org.br", "ouvidoria": "Parcial",
        "canal_url": "https://transparencia.fadesp.org.br/",
        "status": "Verificado",
        "obs": "Portal de Transparência próprio; ouvidoria/denúncias direcionadas à Ouvidoria da UFPA (Fala.BR).",
    },
    {
        "sigla": "FUNDUNESP", "nome": "Fundação para o Desenvolvimento da UNESP",
        "instituicao": "UNESP", "uf": "SP", "esfera": "Estadual",
        "site": "https://www.fundunesp.org.br", "ouvidoria": "Parcial",
        "canal_url": "https://www.fundunesp.org.br/governanca/compliance",
        "status": "Verificado",
        "obs": "Possui área de Compliance/Governança; ouvidoria formal integrada às Ouvidorias Locais da UNESP.",
    },
    {
        "sigla": "FAI.UFSCAR", "nome": "Fundação de Apoio Institucional ao Desenvolvimento Científico e Tecnológico",
        "instituicao": "UFSCar", "uf": "SP", "esfera": "Federal",
        "site": "https://www.fai.ufscar.br", "ouvidoria": "Parcial",
        "canal_url": "https://www.fai.ufscar.br/transparencia/home/index/1",
        "status": "Verificado",
        "obs": "Tem Portal da Transparência próprio, mas NÃO possui ouvidoria/canal de denúncias nominal. Ouvidoria via UFSCar (ouvidoria.ufscar.br) e CPE-UFSCar / Fala.BR.",
    },
    {
        "sigla": "FUSP", "nome": "Fundação de Apoio à Universidade de São Paulo",
        "instituicao": "USP", "uf": "SP", "esfera": "Estadual",
        "site": "https://www.fusp.org.br", "ouvidoria": "Parcial",
        "canal_url": "https://www.fusp.org.br/codigo-de-etica",
        "status": "Verificado",
        "obs": "Tem Código de Ética e Portal da Transparência próprios, mas sem ouvidoria nominal; 'Fale Conosco' por áreas. Demandas críticas vão à Ouvidoria Geral da USP.",
    },

    # ------------------- PENDENTES (FILA DA VARREDURA) ---------------------
    # Relação CONFIES (afiliadas). ouvidoria="A verificar" => varredura automática.
    {"sigla": "FEPBA", "nome": "Fundação Escola Politécnica da Bahia", "instituicao": "UFBA, IFBA, UFSB", "uf": "BA", "esfera": "Federal", "site": "https://www.fepba.org.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Tem 'Fale Conosco'; sem ouvidoria/canal de denúncias nominal. Transparência via Portal Federal."},
    {"sigla": "FUPEF", "nome": "Fundação de Pesquisas Florestais do Paraná", "instituicao": "UFPR", "uf": "PR", "esfera": "Federal", "site": "https://fupef.org.br", "ouvidoria": "Sim", "canal_url": "https://fupef.org.br/ouvidoria/", "status": "Verificado", "obs": "Página de Ouvidoria própria + Portal da Transparência."},
    {"sigla": "RTVE", "nome": "Fundação RTVE", "instituicao": "UFG", "uf": "GO", "esfera": "Federal", "site": "https://rtve.org.br", "ouvidoria": "Sim", "canal_url": "https://rtve.org.br/ouvidoria/", "status": "Verificado", "obs": "Ouvidoria própria (ouvidoria@rtve.org.br, 10 dias úteis) + Canal de Denúncias/Compliance + Transparência."},
    {"sigla": "FUNETEC-PB", "nome": "Fundação de Educação Tecnológica e Cultural da Paraíba", "instituicao": "IFPB", "uf": "PB", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNJAB", "nome": "Fundação José Arthur Boiteux", "instituicao": "UFSC", "uf": "SC", "esfera": "Federal", "site": "https://www.funjab.com.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Tem normas/compliance, mas manifestações são direcionadas à Ouvidoria da UFSC."},
    {"sigla": "FUNPAR", "nome": "Fundação da Universidade Federal do Paraná", "instituicao": "UFPR", "uf": "PR", "esfera": "Federal", "site": "https://www.funpar.ufpr.br", "ouvidoria": "Sim", "canal_url": "https://www.funpar.ufpr.br/paginas.php?page=39", "status": "Verificado", "obs": "Ouvidoria própria (canal de reclamações, sugestões, denúncias e elogios) + Portal da Transparência."},
    {"sigla": "FUNPEA", "nome": "Fundação de Apoio ao Ensino, Pesquisa e Extensão", "instituicao": "UFPA", "uf": "PA", "esfera": "Federal", "site": "", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Sem canal próprio identificado; manifestações via Ouvidoria da UFPA (Fala.BR)."},
    {"sigla": "FUNRIO", "nome": "Fundação de Apoio à Pesquisa, Ensino e Assistência (Gaffrée e Guinle)", "instituicao": "UNIRIO", "uf": "RJ", "esfera": "Federal", "site": "https://www.funrio.org", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Vínculo corrigido: apoia a UNIRIO e o HU Gaffrée e Guinle (não a UFRJ). Sem canal próprio identificado; via UNIRIO/Fala.BR."},
    {"sigla": "FUNTEF-PR", "nome": "Fundação de Apoio à Educação, Pesquisa e Desenvolvimento Científico", "instituicao": "UTFPR", "uf": "PR", "esfera": "Federal", "site": "https://funtefpr.org.br", "ouvidoria": "Sim", "canal_url": "https://funtefpr.org.br/fale-conosco/", "status": "Verificado", "obs": "Ouvidoria/Fale Conosco (formulário + superintendencia@funtefpr.org.br) + Portal da Transparência."},
    {"sigla": "FUPAI", "nome": "Fundação de Pesquisa e Assessoramento à Indústria", "instituicao": "UNIFEI", "uf": "MG", "esfera": "Federal", "site": "https://fupai.org.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Busca não localizou canal próprio de ouvidoria; manifestações via UNIFEI/Fala.BR."},
    {"sigla": "FURJ", "nome": "Fundação Universitária José Bonifácio", "instituicao": "UFRJ", "uf": "RJ", "esfera": "Federal", "site": "", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Sem canal próprio identificado; manifestações via Ouvidoria da UFRJ (Fala.BR)."},
    {"sigla": "GORCEIX", "nome": "Fundação Gorceix", "instituicao": "UFOP", "uf": "MG", "esfera": "Federal", "site": "https://site.gorceix.org.br", "ouvidoria": "Parcial", "canal_url": "https://site.gorceix.org.br/transparencia", "status": "Verificado", "obs": "Portal da Transparência próprio; manifestações de ouvidoria via UFOP (Fala.BR)."},
    {"sigla": "IMEPEN", "nome": "Fundação IMEPEN", "instituicao": "UFJF", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Sem canal próprio identificado; manifestações via Ouvidoria da UFJF (Fala.BR)."},
    {"sigla": "IPEAD", "nome": "Fundação Instituto de Pesquisas Econômicas, Administrativas e Contábeis", "instituicao": "UFMG", "uf": "MG", "esfera": "Federal", "site": "https://site.ipead.face.ufmg.br", "ouvidoria": "Sim", "canal_url": "https://site.ipead.face.ufmg.br/contato/", "status": "Verificado", "obs": "Ouvidoria própria (0800 000 7110, WhatsApp, ipead@ipead.face.ufmg.br) + Portal da Transparência."},
    {"sigla": "MURAKI", "nome": "Fundação Muraki", "instituicao": "UEA", "uf": "AM", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "TROMPOWSKY", "nome": "Fundação Trompowsky", "instituicao": "DECEx (Exército)", "uf": "RJ", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "UNISELVA", "nome": "Fundação de Apoio e Desenvolvimento da UFMT", "instituicao": "UFMT", "uf": "MT", "esfera": "Federal", "site": "https://www1.fundacaouniselva.org.br", "ouvidoria": "Parcial", "canal_url": "https://webunisig.fundacaouniselva.org.br/transparencia/", "status": "Verificado", "obs": "Portal da Transparência próprio; ouvidoria via UFMT (ouvidoria@ufmt.br / Fala.BR)."},
    {"sigla": "UNISOL", "nome": "Fundação de Apoio Institucional Rio Solimões", "instituicao": "UFAM", "uf": "AM", "esfera": "Federal", "site": "", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Sem canal próprio identificado; manifestações via Ouvidoria da UFAM (Fala.BR)."},
    {"sigla": "FUNCATE", "nome": "Fundação de Ciência, Aplicações e Tecnologia Espaciais", "instituicao": "INPE", "uf": "SP", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNCERN", "nome": "Fundação de Apoio à Educação e ao Desenvolvimento Tecnológico do RN", "instituicao": "IFRN", "uf": "RN", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "ADM", "nome": "Fundação ADM (Escola de Administração)", "instituicao": "UFBA", "uf": "BA", "esfera": "Federal", "site": "http://www.fundacaoadm.org.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Ligada à Escola de Administração da UFBA; sem canal próprio identificado. Obs.: a UFBA não a lista entre suas fundações de apoio credenciadas (FEPBA e FAPEX); vínculo formal a confirmar."},
    {"sigla": "ASTEF", "nome": "Fundação ASTEF / FASTEF (Apoio a Serviços Técnicos, Ensino e Fomento a Pesquisas)", "instituicao": "UFC", "uf": "CE", "esfera": "Federal", "site": "https://fastef.ufc.br", "ouvidoria": "Parcial", "canal_url": "https://fastef.ufc.br/informacao-institucional/", "status": "Verificado", "obs": "A ASTEF instituiu a FASTEF (fundação de apoio à UFC). Tem Acesso à Informação institucional; canal de ouvidoria/denúncias nominal não localizado; via UFC/Fala.BR."},
    {"sigla": "CEFETMINAS", "nome": "Fundação CEFET Minas Gerais", "instituicao": "CEFET-MG", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNDMED", "nome": "Fundação Médica do Rio Grande do Sul", "instituicao": "UFRGS / HCPA", "uf": "RS", "esfera": "Federal", "site": "https://fundmed.org.br", "ouvidoria": "Sim", "canal_url": "https://fundmed.org.br/en/compliance-program/", "status": "Verificado", "obs": "Canal de Ética e Conduta gerido por empresa externa (Ouvidor Digital) + Programa de Compliance e Política Anticorrupção."},
    {"sigla": "PaqTcPB", "nome": "Fundação Parque Tecnológico da Paraíba", "instituicao": "UFCG", "uf": "PB", "esfera": "Federal", "site": "https://www.paqtc.org.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Busca não localizou canal próprio de ouvidoria; manifestações via UFCG/Fala.BR."},
    {"sigla": "FUNDACTE", "nome": "Fundação de Apoio à Ciência, Tecnologia e Educação", "instituicao": "UNESP", "uf": "SP", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNDAEPE", "nome": "Fundação de Apoio ao Ensino, Pesquisa e Extensão", "instituicao": "UFVJM", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Sem canal próprio identificado; manifestações via Ouvidoria da UFVJM (Fala.BR)."},
    {"sigla": "FUNDAHC", "nome": "Fundação de Apoio ao Hospital das Clínicas da UFG", "instituicao": "UFG", "uf": "GO", "esfera": "Federal", "site": "https://fundahc.org.br", "ouvidoria": "Sim", "canal_url": "https://fundahc.org.br/p/487-ouvidoria", "status": "Verificado", "obs": "Ouvidoria própria com plataforma SieOuv (Lei 13.460), Canal de Denúncias e SIC; ouvidoria@fundahc.com.br."},
    {"sigla": "FUNDAPE", "nome": "Fundação de Apoio ao Desenvolvimento da Pesquisa e Extensão Universitária no Acre", "instituicao": "UFAC", "uf": "AC", "esfera": "Federal", "site": "https://fundape.com.br", "ouvidoria": "Sim", "canal_url": "https://fundape.com.br/ouvidoria", "status": "Verificado", "obs": "Canal de Ouvidoria próprio + Portal da Transparência (emendas parlamentares)."},
    {"sigla": "FUNDECC", "nome": "Fundação de Desenvolvimento Científico e Cultural", "instituicao": "UFLA", "uf": "MG", "esfera": "Federal", "site": "https://fundecc.org.br", "ouvidoria": "Sim", "canal_url": "https://www.fundecc.org.br/denuncias/", "status": "Verificado", "obs": "Canal próprio de denúncias (/denuncias/). UFLA também mantém ouvidoria autônoma."},
    {"sigla": "FUNDEPES", "nome": "Fundação Universitária de Desenvolvimento de Extensão e Pesquisa", "instituicao": "UFAL", "uf": "AL", "esfera": "Federal", "site": "https://www.fundepes.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Busca não localizou canal próprio; manifestações via Ouvidoria da UFAL (Fala.BR)."},
    {"sigla": "FUNDETEC", "nome": "Fundação de Apoio ao Desenvolvimento Tecnológico", "instituicao": "CEFET-MT", "uf": "MT", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FEESC", "nome": "Fundação de Ensino e Engenharia de Santa Catarina (Stemmer)", "instituicao": "UFSC", "uf": "SC", "esfera": "Federal", "site": "https://www.feesc.org.br", "ouvidoria": "Parcial", "canal_url": "https://www.feesc.org.br", "status": "Verificado", "obs": "Portal de Transparência próprio + referência a Canal de Denúncias; ouvidoria nominal a confirmar."},
    {"sigla": "FEOP", "nome": "Fundação Educativa de Rádio e TV Ouro Preto", "instituicao": "UFOP", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Fundação educativa de rádio/TV da UFOP; sem canal próprio. Manifestações via Ouvidoria da UFOP (Fala.BR)."},
    {"sigla": "FEPESE", "nome": "Fundação de Estudos e Pesquisas Socioeconômicos", "instituicao": "UFSC", "uf": "SC", "esfera": "Federal", "site": "https://fepese.org.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Canais de contato (reclamações/sugestões), sem ouvidoria nominal identificada; via UFSC/Fala.BR."},
    {"sigla": "FEST", "nome": "Fundação Espírito-Santense de Tecnologia", "instituicao": "UFES", "uf": "ES", "esfera": "Federal", "site": "https://fest.org.br", "ouvidoria": "Sim", "canal_url": "https://fest.org.br/ouvidoria/", "status": "Verificado", "obs": "Ouvidoria própria (superintendencia@fest.org.br) + Código de Ética e Normas de Conduta + Portal da Transparência."},
    {"sigla": "FGD", "nome": "Fundação Guimarães Duque", "instituicao": "UFERSA", "uf": "RN", "esfera": "Federal", "site": "https://www.fgduque.org.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Busca não localizou canal próprio; manifestações via Ouvidoria da UFERSA (Fala.BR)."},
    {"sigla": "FHU", "nome": "Fundação do Hospital Universitário da UFJF", "instituicao": "UFJF", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Ligada ao HU-UFJF (EBSERH); manifestações via Ouvidoria do HU-UFJF / UFJF (Fala.BR)."},
    {"sigla": "FIOTEC", "nome": "Fundação para o Desenvolvimento Científico e Tecnológico em Saúde", "instituicao": "Fiocruz", "uf": "RJ", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FIPT", "nome": "Fundação de Apoio ao Instituto de Pesquisas Tecnológicas", "instituicao": "IPT", "uf": "SP", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FJM", "nome": "Fundação Josué Montello", "instituicao": "UFMA", "uf": "MA", "esfera": "Federal", "site": "https://www.fjmontello.org", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Apoia o HU-UFMA; busca não localizou canal próprio. Manifestações via UFMA/Fala.BR."},
    {"sigla": "FLE", "nome": "Fundação Luiz Englert", "instituicao": "UFRGS", "uf": "RS", "esfera": "Federal", "site": "https://fle.org.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Canais de contato, sem ouvidoria nominal; manifestações via Ouvidoria da UFRGS (Fala.BR)."},
    {"sigla": "FRF", "nome": "Fundação Ricardo Franco", "instituicao": "IME", "uf": "RJ", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FSADU", "nome": "Fundação Sousândrade de Apoio ao Desenvolvimento da UFMA", "instituicao": "UFMA", "uf": "MA", "esfera": "Federal", "site": "https://fsadu.org.br", "ouvidoria": "Sim", "canal_url": "https://fsadu.org.br/sugestoes-e-criticas/", "status": "Verificado", "obs": "Canal de denúncias/sugestões/críticas próprio (anonimato + antirretaliação)."},
    {"sigla": "FSB", "nome": "Fundação Simon Bolívar", "instituicao": "UFPel", "uf": "RS", "esfera": "Federal", "site": "", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Sem canal próprio identificado; manifestações via Ouvidoria da UFPel (Fala.BR)."},
    {"sigla": "FUJB", "nome": "Fundação Universitária José Bonifácio", "instituicao": "UFRJ", "uf": "RJ", "esfera": "Federal", "site": "https://www.fujb.ufrj.br", "ouvidoria": "Sim", "canal_url": "https://www.fujb.ufrj.br", "status": "Verificado", "obs": "Site traz seções de Ouvidoria e Transparência próprias."},
    {"sigla": "FEEng", "nome": "Fundação Empresa Escola de Engenharia da UFRGS", "instituicao": "UFRGS", "uf": "RS", "esfera": "Federal", "site": "https://www.feeng.com.br", "ouvidoria": "Sim", "canal_url": "https://www.ufrgs.br/feeng/?page_id=81", "status": "Verificado", "obs": "Ouvidoria própria (ouvidoria@feeng.com.br)."},
    {"sigla": "FEC", "nome": "Fundação Euclides da Cunha", "instituicao": "UFF", "uf": "RJ", "esfera": "Federal", "site": "https://somosfec.org.br", "ouvidoria": "Sim", "canal_url": "https://somosfec.org.br/compliance-denuncias/", "status": "Verificado", "obs": "Canal de Ética/Denúncias próprio (confidencial, anônimo, antirretaliação) + Compliance + Transparência."},
    {"sigla": "FDTE", "nome": "Fundação para o Desenvolvimento Tecnológico da Engenharia", "instituicao": "USP", "uf": "SP", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FCT/JF", "nome": "Fundação para Pesquisa Científica e Tecnológica", "instituicao": "UFJF", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Sem canal próprio identificado; manifestações via Ouvidoria da UFJF (Fala.BR)."},
    {"sigla": "FCO", "nome": "Fundação Christiano Ottoni", "instituicao": "UFMG", "uf": "MG", "esfera": "Federal", "site": "https://fco.org.br", "ouvidoria": "Parcial", "canal_url": "https://fco.org.br", "status": "Verificado", "obs": "Comitê de Ética e Transparência + Código de Integridade e Transparência; ouvidoria/canal de denúncias nominal não localizado."},
    {"sigla": "FCMF", "nome": "Fundação Casimiro Montenegro Filho", "instituicao": "ITA", "uf": "SP", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAURGS", "nome": "Fundação de Apoio da Universidade Federal do Rio Grande do Sul", "instituicao": "UFRGS", "uf": "RS", "esfera": "Federal", "site": "https://portalfaurgs.com.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Busca não localizou canal próprio; manifestações via Ouvidoria da UFRGS (Fala.BR)."},
    {"sigla": "FUCAM", "nome": "Fundação de Apoio Cassiano Antônio Moraes", "instituicao": "UFES", "uf": "ES", "esfera": "Federal", "site": "http://fucam.org.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Ligada ao HUCAM/UFES (EBSERH); sem canal próprio identificado, manifestações via HUCAM/UFES (Fala.BR). (A antiga Fundação Ceciliano Abel de Almeida está em liquidação judicial.)"},
    {"sigla": "FAURG", "nome": "Fundação de Apoio à Universidade Federal do Rio Grande", "instituicao": "FURG", "uf": "RS", "esfera": "Federal", "site": "https://faurg.org.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Sem canal próprio identificado; manifestações via Ouvidoria da FURG (Fala.BR)."},
    {"sigla": "FAUF", "nome": "Fundação de Apoio à Universidade Federal de São João del-Rei", "instituicao": "UFSJ", "uf": "MG", "esfera": "Federal", "site": "https://fauf.org.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Sem canal próprio identificado; manifestações via Ouvidoria da UFSJ (Fala.BR)."},
    {"sigla": "FAU-UNICENTRO", "nome": "Fundação de Apoio ao Desenvolvimento da UNICENTRO", "instituicao": "UNICENTRO", "uf": "PR", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FATEC-UFSM", "nome": "Fundação de Apoio à Tecnologia e Ciência", "instituicao": "UFSM", "uf": "RS", "esfera": "Federal", "site": "https://www.fatecsm.org.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Tem controles internos, mas sem ouvidoria pública identificada; manifestações via UFSM/Fala.BR."},
    {"sigla": "FAPTO", "nome": "Fundação de Apoio Científico e Tecnológico do Tocantins", "instituicao": "UFT", "uf": "TO", "esfera": "Federal", "site": "https://fapto.org.br", "ouvidoria": "Parcial", "canal_url": "https://fapto.org.br", "status": "Verificado", "obs": "Menciona canal de denúncias confidencial + Portal de Transparência (com falhas apontadas pela CGU). Ouvidoria nominal a confirmar."},
    {"sigla": "FAPEU", "nome": "Fundação de Amparo à Pesquisa e Extensão Universitária", "instituicao": "UFSC, IFSC, UFFS", "uf": "SC", "esfera": "Federal", "site": "https://fapeu.org.br", "ouvidoria": "Sim", "canal_url": "https://www.contatoseguro.com.br/fapeu", "status": "Verificado", "obs": "Canal de Denúncias próprio via Contato Seguro (0800 900 9099, anônimo) + Portal da Transparência."},
    {"sigla": "FAPESE", "nome": "Fundação de Apoio à Pesquisa e Extensão de Sergipe", "instituicao": "UFS", "uf": "SE", "esfera": "Federal", "site": "https://www.fapese.org.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Sem canal próprio identificado; manifestações via Ouvidoria da UFS (Fala.BR)."},
    {"sigla": "FAIFSUL", "nome": "Fundação de Apoio do IFSul", "instituicao": "IFSul", "uf": "RS", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAHERG", "nome": "Fundação de Apoio ao Hospital de Ensino do Rio Grande", "instituicao": "HU-FURG", "uf": "RS", "esfera": "Federal", "site": "", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Ligada ao HU-FURG (EBSERH); manifestações via Ouvidoria do HU-FURG (ouv.hu-furg@ebserh.gov.br / Fala.BR)."},
    {"sigla": "FADURPE", "nome": "Fundação Apolônio Salles de Desenvolvimento Educacional", "instituicao": "UFRPE", "uf": "PE", "esfera": "Federal", "site": "https://fadurpe.com.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Sem canal próprio identificado; manifestações via Ouvidoria da UFRPE (Fala.BR)."},
    {"sigla": "FADUC", "nome": "Fundação de Apoio ao Desenvolvimento da Computação Científica", "instituicao": "CEFET-MG", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FADEX", "nome": "Fundação Cultural e de Fomento à Pesquisa, Ensino, Extensão e Inovação", "instituicao": "UFPI", "uf": "PI", "esfera": "Federal", "site": "https://www.fadex.org.br", "ouvidoria": "Sim", "canal_url": "https://www.fadex.org.br/dados_contatos", "status": "Verificado", "obs": "Ouvidoria própria (ouvidoria@fadex.org.br, monitorada pela superintendência)."},
    {"sigla": "FACTI", "nome": "Fundação de Apoio à Capacitação em Tecnologia da Informação", "instituicao": "CTI Renato Archer", "uf": "SP", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FACC", "nome": "Fundação de Apoio à Computação Científica", "instituicao": "LNCC", "uf": "RJ", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "BIORIO", "nome": "Fundação Bio-Rio", "instituicao": "UFRJ", "uf": "RJ", "esfera": "Federal", "site": "http://www.biorio.org.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Sem canal próprio identificado; manifestações via Ouvidoria da UFRJ (Fala.BR)."},
    {"sigla": "FEMAR", "nome": "Fundação de Estudos do Mar", "instituicao": "Marinha (NIT)", "uf": "RJ", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FDMS", "nome": "Fundação Delfim Mendes Silveira", "instituicao": "UFPel", "uf": "RS", "esfera": "Federal", "site": "https://fundacoesufpel.com.br/fdms/", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Sem canal próprio identificado; manifestações via Ouvidoria da UFPel (Fala.BR)."},
    {"sigla": "FAUEL", "nome": "Fundação de Apoio ao Desenvolvimento da UEL", "instituicao": "UEL", "uf": "PR", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAESPE", "nome": "Fundação de Apoio ao Ensino Superior Público Estadual", "instituicao": "UNEMAT", "uf": "MT", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FACEV", "nome": "Fundação Artística, Cultural e de Educação para a Cidadania de Viçosa", "instituicao": "UFV", "uf": "MG", "esfera": "Federal", "site": "https://www.facev.org", "ouvidoria": "Sim", "canal_url": "https://www.facev.org/ouvidoria", "status": "Verificado", "obs": "Canal de Denúncias próprio (Lei 14.457/22, sigilo, antirretaliação) + Código de Conduta."},
    {"sigla": "FUNCEPE", "nome": "Fundação Cearense de Pesquisa e Desenvolvimento", "instituicao": "IFCE", "uf": "CE", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAEPI", "nome": "Fundação de Apoio ao Ensino, Pesquisa e Inovação", "instituicao": "IFAM", "uf": "AM", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNEP", "nome": "Fundação de Apoio à Pesquisa, Ensino e Extensão", "instituicao": "UNESP/FCAV", "uf": "SP", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAPEB", "nome": "Fundação de Apoio à Pesquisa e ao Ensino do Brasil", "instituicao": "DCT (Exército)", "uf": "RJ", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNAEPE", "nome": "Fundação de Apoio ao Ensino, Pesquisa e Extensão", "instituicao": "UFGD", "uf": "MS", "esfera": "Federal", "site": "https://funaepe.org.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Sem canal próprio identificado; manifestações via Ouvidoria da UFGD (Fala.BR)."},
    {"sigla": "FADECIT", "nome": "Fundação de Apoio ao Desenvolvimento Científico e Tecnológico", "instituicao": "UEMG", "uf": "MG", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FEPE", "nome": "Fundação de Apoio ao Ensino, Pesquisa e Extensão", "instituicao": "UFMG", "uf": "MG", "esfera": "Federal", "site": "https://www.fepe.com.br", "ouvidoria": "Sim", "canal_url": "https://www.fepe.com.br/contatos/", "status": "Verificado", "obs": "Canal de Ouvidoria/Denúncias próprio (ouvidoria@fepe.com.br, anônimo)."},
    {"sigla": "FAHUB", "nome": "Fundação de Apoio ao Desenvolvimento Científico e Tecnológico do HUB", "instituicao": "HUB (UnB)", "uf": "DF", "esfera": "Federal", "site": "https://fahub.org.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Ligada ao HUB/UnB (EBSERH); manifestações via Ouvidoria da UnB/HUB (Fala.BR)."},
    {"sigla": "FAPED", "nome": "Fundação de Apoio à Pesquisa e ao Desenvolvimento", "instituicao": "EMBRAPA", "uf": "MG", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FADEPE/JF", "nome": "Fundação de Apoio e Desenvolvimento ao Ensino, Pesquisa e Extensão", "instituicao": "UFJF", "uf": "MG", "esfera": "Federal", "site": "https://fadepe.org.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Tem 'Fale Conosco'; sem ouvidoria nominal. Manifestações via Ouvidoria da UFJF (Fala.BR)."},
    {"sigla": "FAU-UFU", "nome": "Fundação de Apoio Universitário", "instituicao": "UFU", "uf": "MG", "esfera": "Federal", "site": "https://fau.org.br", "ouvidoria": "Sim", "canal_url": "https://fau.org.br/etica-e-compliance/", "status": "Verificado", "obs": "Programa de Integridade + Canal de Denúncias seguro e confidencial."},
    {"sigla": "FAPEPE", "nome": "Fundação de Apoio ao Ensino, Pesquisa e Extensão de Itajubá", "instituicao": "UNIFEI", "uf": "MG", "esfera": "Federal", "site": "https://fapepe.org.br", "ouvidoria": "Parcial", "canal_url": "http://fapepe.conveniar.com.br/portaltransparencia/", "status": "Verificado", "obs": "Portal de Transparência próprio + Fale Conosco; ouvidoria via UNIFEI (Fala.BR)."},
    {"sigla": "FAEPE", "nome": "Fundação de Apoio ao Ensino, Pesquisa e Extensão", "instituicao": "UFLA", "uf": "MG", "esfera": "Federal", "site": "https://www.faepe.org.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Canal de contato (Fale Conosco) para reclamações/denúncias; sem ouvidoria nominal. Via UFLA/Fala.BR."},
    {"sigla": "FACEPE-UNIFAL", "nome": "Fundação de Apoio à Cultura, Ensino, Pesquisa e Extensão de Alfenas", "instituicao": "UNIFAL", "uf": "MG", "esfera": "Federal", "site": "https://facepevirtual.org.br", "ouvidoria": "Não", "canal_url": "", "status": "Verificado", "obs": "Sem canal próprio identificado; manifestações via Ouvidoria da UNIFAL-MG (Fala.BR)."},
    {"sigla": "FAPEX", "nome": "Fundação de Apoio à Pesquisa e Extensão", "instituicao": "UFBA, UFRB, UFOB, UNILAB, IFBA", "uf": "BA", "esfera": "Federal", "site": "https://www.fapex.org.br", "ouvidoria": "Sim", "canal_url": "https://www.fapex.org.br/Fapex/Site/Principal/Home/ouvidoria", "status": "Verificado", "obs": "Ouvidoria própria (confidencial e imparcial) + Portal da Transparência."},
    {"sigla": "FAPES", "nome": "Fundação de Apoio à Pesquisa e Extensão", "instituicao": "UNEB", "uf": "BA", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAEPU", "nome": "Fundação de Assistência, Estudo e Pesquisa de Uberlândia", "instituicao": "UFU", "uf": "MG", "esfera": "Federal", "site": "http://www.faepu.org.br", "ouvidoria": "Sim", "canal_url": "http://www.faepu.org.br/pagina/canal-denuncias-faepu", "status": "Verificado", "obs": "Canal de Denúncias próprio (confidencial)."},
    {"sigla": "FACTO", "nome": "Fundação de Apoio à Ciência, Tecnologia e Inovação", "instituicao": "IFES", "uf": "ES", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
]


def colunas():
    """Ordem canônica das colunas para exportação."""
    return [
        "sigla", "nome", "instituicao", "uf", "esfera",
        "site", "ouvidoria", "canal_url", "status", "obs",
    ]


# Rótulos amigáveis (cabeçalhos das planilhas)
ROTULOS = {
    "sigla": "Sigla",
    "nome": "Nome da Fundação",
    "instituicao": "Instituição(ões) Apoiada(s)",
    "uf": "UF",
    "esfera": "Esfera",
    "site": "Site Oficial",
    "ouvidoria": "Ouvidoria Própria?",
    "canal_url": "Canal / URL",
    "status": "Verificação",
    "obs": "Observações",
}
