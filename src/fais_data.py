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
    {"sigla": "FEPBA", "nome": "Fundação Escola Politécnica da Bahia", "instituicao": "UFBA, IFBA, UFSB", "uf": "BA", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUPEF", "nome": "Fundação de Pesquisas Florestais do Paraná", "instituicao": "UFPR", "uf": "PR", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "RTVE", "nome": "Fundação RTVE", "instituicao": "UFG", "uf": "GO", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNETEC-PB", "nome": "Fundação de Educação Tecnológica e Cultural da Paraíba", "instituicao": "IFPB", "uf": "PB", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNJAB", "nome": "Fundação José Arthur Boiteux", "instituicao": "UFSC", "uf": "SC", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNPAR", "nome": "Fundação da Universidade Federal do Paraná", "instituicao": "UFPR", "uf": "PR", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNPEA", "nome": "Fundação de Apoio ao Ensino, Pesquisa e Extensão", "instituicao": "UFPA", "uf": "PA", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNRIO", "nome": "Fundação de Apoio à Pesquisa e Extensão", "instituicao": "UFRJ", "uf": "RJ", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNTEF-PR", "nome": "Fundação de Apoio à Educação, Pesquisa e Desenvolvimento Científico", "instituicao": "UTFPR", "uf": "PR", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUPAI", "nome": "Fundação de Pesquisa e Assessoramento à Indústria", "instituicao": "UNIFEI", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FURJ", "nome": "Fundação Universitária José Bonifácio", "instituicao": "UFRJ", "uf": "RJ", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "GORCEIX", "nome": "Fundação Gorceix", "instituicao": "UFOP", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "IMEPEN", "nome": "Fundação IMEPEN", "instituicao": "UFJF", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "IPEAD", "nome": "Fundação Instituto de Pesquisas Econômicas, Administrativas e Contábeis", "instituicao": "UFMG", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "MURAKI", "nome": "Fundação Muraki", "instituicao": "UEA", "uf": "AM", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "TROMPOWSKY", "nome": "Fundação Trompowsky", "instituicao": "DECEx (Exército)", "uf": "RJ", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "UNISELVA", "nome": "Fundação de Apoio e Desenvolvimento da UFMT", "instituicao": "UFMT", "uf": "MT", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "UNISOL", "nome": "Fundação Universidade Solidária", "instituicao": "UFAM", "uf": "AM", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNCATE", "nome": "Fundação de Ciência, Aplicações e Tecnologia Espaciais", "instituicao": "INPE", "uf": "SP", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNCERN", "nome": "Fundação de Apoio à Educação e ao Desenvolvimento Tecnológico do RN", "instituicao": "IFRN", "uf": "RN", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "ADM", "nome": "Fundação Escola de Administração", "instituicao": "UFBA", "uf": "BA", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "ASTEF", "nome": "Fundação Cearense de Apoio ao Desenvolvimento Científico e Tecnológico", "instituicao": "UFC", "uf": "CE", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "CEFETMINAS", "nome": "Fundação CEFET Minas Gerais", "instituicao": "CEFET-MG", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNDMED", "nome": "Fundação Médica do Rio Grande do Sul", "instituicao": "UFRGS / HCPA", "uf": "RS", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "PaqTcPB", "nome": "Fundação Parque Tecnológico da Paraíba", "instituicao": "UFCG", "uf": "PB", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNDACTE", "nome": "Fundação de Apoio à Ciência, Tecnologia e Educação", "instituicao": "UNESP", "uf": "SP", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNDAEPE", "nome": "Fundação de Apoio ao Ensino, Pesquisa e Extensão", "instituicao": "UFVJM", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNDAHC", "nome": "Fundação de Apoio ao Hospital das Clínicas da UFG", "instituicao": "UFG", "uf": "GO", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNDAPE", "nome": "Fundação de Apoio ao Desenvolvimento da Pesquisa e Extensão", "instituicao": "UFAC", "uf": "AC", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNDECC", "nome": "Fundação de Desenvolvimento Científico e Cultural", "instituicao": "UFLA", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNDEPES", "nome": "Fundação Universitária de Desenvolvimento de Extensão e Pesquisa", "instituicao": "UFAL", "uf": "AL", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNDETEC", "nome": "Fundação de Apoio ao Desenvolvimento Tecnológico", "instituicao": "CEFET-MT", "uf": "MT", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FEESC", "nome": "Fundação de Ensino e Engenharia de Santa Catarina (Stemmer)", "instituicao": "UFSC", "uf": "SC", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FEOP", "nome": "Fundação Educativa de Ouro Preto", "instituicao": "UFOP", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FEPESE", "nome": "Fundação de Estudos e Pesquisas Socioeconômicos", "instituicao": "UFSC", "uf": "SC", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FEST", "nome": "Fundação Espírito-Santense de Tecnologia", "instituicao": "UFES", "uf": "ES", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FGD", "nome": "Fundação Guimarães Duque", "instituicao": "UFERSA", "uf": "RN", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FHU", "nome": "Fundação do Hospital Universitário da UFJF", "instituicao": "UFJF", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FIOTEC", "nome": "Fundação para o Desenvolvimento Científico e Tecnológico em Saúde", "instituicao": "Fiocruz", "uf": "RJ", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FIPT", "nome": "Fundação de Apoio ao Instituto de Pesquisas Tecnológicas", "instituicao": "IPT", "uf": "SP", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FJM", "nome": "Fundação Josué Montello", "instituicao": "UFMA", "uf": "MA", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FLE", "nome": "Fundação Luiz Englert", "instituicao": "UFRGS", "uf": "RS", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FRF", "nome": "Fundação Ricardo Franco", "instituicao": "IME", "uf": "RJ", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FSADU", "nome": "Fundação Sousândrade de Apoio ao Desenvolvimento da UFMA", "instituicao": "UFMA", "uf": "MA", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FSB", "nome": "Fundação Simon Bolívar", "instituicao": "UFPel", "uf": "RS", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUJB", "nome": "Fundação Universidade-Empresa de Tecnologia e Ciências (José Bonifácio)", "instituicao": "UFRJ", "uf": "RJ", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FEEng", "nome": "Fundação Empresa Escola de Engenharia da UFRGS", "instituicao": "UFRGS", "uf": "RS", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FEC", "nome": "Fundação Euclides da Cunha", "instituicao": "UFF", "uf": "RJ", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FDTE", "nome": "Fundação para o Desenvolvimento Tecnológico da Engenharia", "instituicao": "USP", "uf": "SP", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FCT/JF", "nome": "Fundação para Pesquisa Científica e Tecnológica", "instituicao": "UFJF", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FCO", "nome": "Fundação Christiano Ottoni", "instituicao": "UFMG", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FCMF", "nome": "Fundação Casimiro Montenegro Filho", "instituicao": "ITA", "uf": "SP", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAURGS", "nome": "Fundação de Apoio da Universidade Federal do Rio Grande do Sul", "instituicao": "UFRGS", "uf": "RS", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUCAM", "nome": "Fundação Ceciliano Abel de Almeida", "instituicao": "UFES", "uf": "ES", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAURG", "nome": "Fundação de Apoio à Universidade Federal do Rio Grande", "instituicao": "FURG", "uf": "RS", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAUF", "nome": "Fundação de Apoio à Universidade Federal de São João del-Rei", "instituicao": "UFSJ", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAU-UNICENTRO", "nome": "Fundação de Apoio ao Desenvolvimento da UNICENTRO", "instituicao": "UNICENTRO", "uf": "PR", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FATEC-UFSM", "nome": "Fundação de Apoio à Tecnologia e Ciência", "instituicao": "UFSM", "uf": "RS", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAPTO", "nome": "Fundação de Apoio Científico e Tecnológico do Tocantins", "instituicao": "UFT", "uf": "TO", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAPEU", "nome": "Fundação de Amparo à Pesquisa e Extensão Universitária", "instituicao": "UFSC, IFSC, UFFS", "uf": "SC", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAPESE", "nome": "Fundação de Apoio à Pesquisa e Extensão de Sergipe", "instituicao": "UFS", "uf": "SE", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAIFSUL", "nome": "Fundação de Apoio do IFSul", "instituicao": "IFSul", "uf": "RS", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAHERG", "nome": "Fundação de Apoio ao Hospital Universitário (Dr. Riet Corrêa Jr.)", "instituicao": "HU-FURG", "uf": "RS", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FADURPE", "nome": "Fundação Apolônio Salles de Desenvolvimento Educacional", "instituicao": "UFRPE", "uf": "PE", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FADUC", "nome": "Fundação de Apoio ao Desenvolvimento da Computação Científica", "instituicao": "CEFET-MG", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FADEX", "nome": "Fundação Cultural e de Fomento à Pesquisa, Ensino e Extensão", "instituicao": "UFPI", "uf": "PI", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FACTI", "nome": "Fundação de Apoio à Capacitação em Tecnologia da Informação", "instituicao": "CTI Renato Archer", "uf": "SP", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FACC", "nome": "Fundação de Apoio à Computação Científica", "instituicao": "LNCC", "uf": "RJ", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "BIORIO", "nome": "Fundação Bio-Rio", "instituicao": "UFRJ", "uf": "RJ", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FEMAR", "nome": "Fundação de Estudos do Mar", "instituicao": "Marinha (NIT)", "uf": "RJ", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FDMS", "nome": "Fundação Delfim Mendes Silveira", "instituicao": "UFPel", "uf": "RS", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAUEL", "nome": "Fundação de Apoio ao Desenvolvimento da UEL", "instituicao": "UEL", "uf": "PR", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAESPE", "nome": "Fundação de Apoio ao Ensino Superior Público Estadual", "instituicao": "UNEMAT", "uf": "MT", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FACEV", "nome": "Fundação de Apoio e Desenvolvimento Científico", "instituicao": "UFV", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNCEPE", "nome": "Fundação Cearense de Pesquisa e Desenvolvimento", "instituicao": "IFCE", "uf": "CE", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAEPI", "nome": "Fundação de Apoio ao Ensino, Pesquisa e Inovação", "instituicao": "IFAM", "uf": "AM", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNEP", "nome": "Fundação de Apoio à Pesquisa, Ensino e Extensão", "instituicao": "UNESP/FCAV", "uf": "SP", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAPEB", "nome": "Fundação de Apoio à Pesquisa e ao Ensino do Brasil", "instituicao": "DCT (Exército)", "uf": "RJ", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FUNAEPE", "nome": "Fundação de Apoio ao Ensino, Pesquisa e Extensão", "instituicao": "UFGD", "uf": "MS", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FADECIT", "nome": "Fundação de Apoio ao Desenvolvimento Científico e Tecnológico", "instituicao": "UEMG", "uf": "MG", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FEPE", "nome": "Fundação de Ensino e Pesquisa", "instituicao": "UFMG", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAHUB", "nome": "Fundação de Apoio ao Hospital Universitário de Brasília", "instituicao": "HUB (UnB)", "uf": "DF", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAPED", "nome": "Fundação de Apoio à Pesquisa e ao Desenvolvimento", "instituicao": "EMBRAPA", "uf": "MG", "esfera": "ICT Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FADEPE/JF", "nome": "Fundação de Apoio e Desenvolvimento ao Ensino, Pesquisa e Extensão", "instituicao": "UFJF", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAU-UFU", "nome": "Fundação de Apoio Universitário", "instituicao": "UFU", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAPEPE", "nome": "Fundação de Apoio à Pesquisa, Ensino e Extensão", "instituicao": "UNIFEI", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAEPE", "nome": "Fundação de Apoio ao Ensino, Pesquisa e Extensão", "instituicao": "UFLA", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FACEPE-UNIFAL", "nome": "Fundação de Apoio à Cultura, Ensino, Pesquisa e Extensão", "instituicao": "UNIFAL", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAPEX", "nome": "Fundação de Apoio à Pesquisa e Extensão", "instituicao": "UFBA, UFRB, UFOB, UNILAB, IFBA", "uf": "BA", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAPES", "nome": "Fundação de Apoio à Pesquisa e Extensão", "instituicao": "UNEB", "uf": "BA", "esfera": "Estadual", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
    {"sigla": "FAEPU", "nome": "Fundação de Assistência, Estudo e Pesquisa de Uberlândia", "instituicao": "UFU", "uf": "MG", "esfera": "Federal", "site": "", "ouvidoria": "A verificar", "canal_url": "", "status": "Pendente", "obs": ""},
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
