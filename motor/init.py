#!/usr/bin/env python3
"""Cria um documento vivo inicial, sem perguntas (convenção em vez de configuração):

    python3 motor/init.py

cria documentos/documento-vivo/ ao lado da pasta motor/ (ou documento-vivo-2, -3…
se já existir) com um documento.xml e gera as duas páginas:

    <pasta>/
    ├── motor/        build.py · template.html · documento.xsd · README.md · init.py
    └── documentos/
        └── documento-vivo/   documento.xml · documento-vivo.html · documento-vivo-admin.html

O documento é um tutorial: as raias, os blocos, os anéis, a tabela de referências,
os cartões e as notas explicam como inserir conteúdo e como usar o documento vivo —
inclusive como trocar título, ícone, telas e tudo o mais. Eles mesmos são o que se
troca pelo conteúdo do documento.
"""
import datetime
import importlib.util
import os
import subprocess
import sys

sys.dont_write_bytecode = True
AQUI = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- build
def carregar_build(caminho):
    spec = importlib.util.spec_from_file_location("motor_build", caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def gerar_paginas(motor, doc):
    """Roda o build (público e administração). Devolve as linhas de saída ou o erro."""
    saidas = []
    for extra in ([], ["--admin"]):
        r = subprocess.run([sys.executable, "-I", os.path.join(motor, "build.py"), "--doc", doc, *extra],
                           capture_output=True, text=True)
        if r.returncode != 0:
            return False, (r.stdout + r.stderr).strip()
        saidas.append(r.stdout.strip())
    return True, "\n".join(saidas)


# ---------------------------------------------------------------- o tutorial
def tutorial(r):
    """O documento inicial: um tutorial sobre o próprio documento vivo, nos
    elementos do desenho (raias, blocos, anéis, referências, cartões, notas)."""
    refs, mapa = r["telaRefs"], r["telaMapa"]
    doc = f"documentos/{r['slug']}/documento.xml"
    build = f"python3 build.py --doc ../{doc}"

    def bloco(id_, grupo, nome, resumo, itens, sistemas, dica=None):
        secoes = [{"titulo": "Como fazer", "itens": itens}]
        if dica:
            secoes.append({"titulo": "Dica", "itens": [dica], "margem": True})
        return {"id": id_, "grupo": grupo, "nome": nome, "resumo": resumo, "secoes": secoes, "sistemas": sistemas}

    blocos = [
        # --- raia numerada: usar o documento, em ordem
        bloco("u1", "uso", "Navegar", "Por enquanto este documento vivo é um tutorial: cada bloco ensina uma coisa e, depois, vira conteúdo seu.",
              ["Clique num bloco das raias para abrir este painel; ✕ ou Esc fecham.",
               f"O menu à esquerda troca de tela: {mapa}, {refs}, Arquivos e Para começar.",
               "Clique num anel do ecossistema (acima das raias) para ver os blocos ligados a ele.",
               "Passe o mouse — ou toque — numa sigla sublinhada, como XML, para ver o que ela significa."],
              ["pagina"], "Os blocos desta raia são numerados porque a raia é sequencial: a ordem importa."),
        bloco("u2", "uso", "Editar textos", "Qualquer texto da página pode ser editado ali mesmo, sem abrir arquivo nenhum.",
              ["Clique em \"Editar conteúdo\", no rodapé do menu.",
               "Clique num texto contornado e digite; Enter ou clicar fora confirma.",
               "O que se cola entra sempre como texto puro.",
               "\"Concluir edição\" desliga o modo de edição."],
              ["pagina"], "As mudanças ficam salvas neste navegador automaticamente — mas só nele. Para levar adiante, exporte (bloco 5)."),
        bloco("u3", "uso", "Itens e seções", "Listas como a de \"Como fazer\" crescem e encolhem no modo de edição.",
              ["\"+ adicionar\" cria um item novo no fim da lista.",
               "O × ao lado de um item o remove.",
               "Seções marcadas como dica (como a de baixo) aparecem destacadas."],
              ["pagina"]),
        bloco("u4", "uso", f"A tela {refs}", f"A tela {refs} é uma tabela de referências — normas, fontes, documentos — ligadas aos blocos.",
              ["Busque por texto e filtre pelas pílulas de âmbito.",
               "No modo de edição, \"+ adicionar referência\" cria uma linha.",
               "Na coluna Blocos, escreva os números dos blocos a que a referência se liga (ex.: 1, 4).",
               "Marque \"a conferir\" no que ainda falta verificar."],
              ["pagina"], "O botão no rodapé deste painel leva às referências ligadas a este bloco."),
        bloco("u5", "uso", "Salvar e exportar", "O conteúdo publicado é o do arquivo documento.xml; o que se edita na página fica no navegador até ser exportado.",
              ["\"Exportar dados (JSON)\" baixa tudo o que está na página.",
               "\"Restaurar conteúdo original\" volta ao publicado (com Desfazer).",
               "Quando a página é publicada de novo com conteúdo diferente, a cópia local antiga é substituída — exporte antes."],
              ["pagina", "xml"]),
        # --- raia livre: a estrutura (build de administração)
        bloco("s1", "estrutura", "Build de administração", "Mudar a estrutura (telas, raias, sistemas, elos) é tarefa da página de administração.",
              [f"Na pasta motor/: {build} --admin",
               f"Isso gera {r['slug']}-admin.html, com Importar, Comparar proposta e Estrutura do documento.",
               "No modo de edição dela, \"+ bloco\", \"×\" e \"+ anel\" aparecem no próprio diagrama, para incluir e remover blocos e anéis.",
               "Não publique a página de administração: publique só a normal."],
              ["build", "admin"]),
        bloco("s2", "estrutura", "Painel Estrutura do documento", "No modo de edição da página de administração, \"Estrutura do documento\" abre um painel com tudo o que define o documento.",
              ["Identidade: título, ícone e descrição.",
               "Vistas: as telas do menu — ordem, rótulos, títulos e introduções.",
               "Grupos: as raias — nome, cor, numeração; \"+ adicionar bloco neste grupo\".",
               "Sistemas de contexto, elos e o vocabulário da tela de referências."],
              ["admin"], "Uma mudança que deixaria o documento inválido é recusada, e a barra de status diz por quê."),
        bloco("s3", "estrutura", "Estrutura do bloco", "Na página de administração, o painel de cada bloco ganha mais controles.",
              ["↑ ↓ mudam a ordem do bloco dentro da raia.",
               "× remove o bloco (com confirmação).",
               "Grupo e sistemas de contexto do bloco se escolhem ali mesmo."],
              ["admin"]),
        # --- raia livre: colaborar e publicar
        bloco("c1", "colaborar", "Propor mudanças", "Quem colabora não precisa de nada além da página publicada.",
              ["Edite na página normal (blocos 2 a 4).",
               "Exporte (bloco 5) e envie o arquivo para quem administra o documento."],
              ["pagina"]),
        bloco("c2", "colaborar", "Comparar e adotar", "Na página de administração, uma proposta é comparada com o documento atual, item a item.",
              ["\"Comparar proposta (JSON)\" lista as diferenças: + novo, − removido, ~ alterado.",
               "Marque o que deve entrar e clique em \"Adotar selecionadas\".",
               "Se a combinação não formar um documento válido, nada muda; \"↺ Desfazer\" volta atrás."],
              ["admin"]),
        bloco("c3", "colaborar", "Gravar e publicar", "O que foi feito na página só fica permanente quando volta ao documento.xml.",
              [f"Exporte e rode, na pasta motor/: {build} --de-json arquivo.json",
               "Ou, na administração, \"Exportar documento.xml\" baixa o arquivo pronto (e \"Exportar template\", só a estrutura, para outro documento do mesmo tipo).",
               "Ou edite o documento.xml num editor de texto — o build confere tudo.",
               f"{build} gera {r['slug']}.html, a página para publicar."],
              ["xml", "build"], "O documento.xml só é substituído se o resultado passar em todas as checagens."),
        # --- cartões (sem raia): os arquivos
        bloco("a1", "arquivos", "documento.xml", f"Todo o conteúdo deste documento, em documentos/{r['slug']}/.",
              ["<meta>: identidade.", "<modelo>: raias, sistemas, elos e telas.",
               "<blocos>, <normas> (as referências), <notas> e <siglas>: o conteúdo."], ["xml"]),
        bloco("a2", "arquivos", "documento.xsd", "A gramática de todo documento.xml, no motor.",
              ["Tipos, campos obrigatórios e valores permitidos.", "Ids únicos e referências entre seções.",
               "Comentado: é o melhor guia para editar o XML à mão."], ["xml", "build"]),
        bloco("a3", "arquivos", "build.py", "Gera a página a partir do documento.xml e confere tudo antes.",
              [f"{build}  (página publicada)", f"{build} --admin  (administração)",
               "--de-json arquivo.json  (grava um export no documento.xml)"], ["build"]),
        bloco("a4", "arquivos", "init.py", "Cria um documento novo — foi ele que criou este.",
              ["python3 motor/init.py", "Cria outro documento como este (documento-vivo-2, -3…) em documentos/."], ["build"]),
    ]

    normas = [
        {"esfera": "Uso", "titulo": "Como ler esta tabela", "resumo": "Cada linha é uma referência: âmbito, título (um link, quando há fonte), resumo e os blocos a que se liga.", "fonte": "", "elos": ["u4"], "status": "ok"},
        {"esfera": "Uso", "titulo": "Referência com link para a fonte", "resumo": "Quando a referência tem um endereço (http/https), o título vira link — como este, para a especificação do XML Schema.", "fonte": "https://www.w3.org/XML/Schema", "elos": ["u4"], "status": "ok"},
        {"esfera": "Edição", "titulo": "Adicionar uma referência", "resumo": "No modo de edição, \"+ adicionar referência\" (no fim da tabela) cria uma linha para preencher.", "fonte": "", "elos": ["u3", "u4"], "status": "ok"},
        {"esfera": "Edição", "titulo": "Marcar o que falta conferir", "resumo": "A caixa \"a conferir\" de cada linha põe o selo que se vê aqui; serve para o que ainda precisa de verificação.", "fonte": "", "elos": ["u4"], "status": "conferir"},
        {"esfera": "Edição", "titulo": "Ligar a vários blocos ou ao documento todo", "resumo": "Na coluna Blocos, separe os números por vírgula; \"ger\" liga a referência ao documento todo.", "fonte": "", "elos": ["geral"], "status": "ok"},
        {"esfera": "Administração", "titulo": "Mudar colunas, âmbitos e rótulos desta tela", "resumo": "No painel Estrutura do documento (administração), a vista desta tela tem os nomes das colunas, a ordem dos âmbitos e os textos dos botões.", "fonte": "", "elos": ["geral"], "status": "ok"},
    ]

    notas = [
        "Troque título, ícone e descrição (painel Estrutura do documento, ou <meta> no documento.xml).",
        "Renomeie as raias e os sistemas de contexto para o seu tema.",
        "Substitua os blocos do tutorial pelo seu conteúdo — ou apague-os e crie os seus.",
        f"Apague as referências de exemplo da tela {refs} e acrescente as suas.",
        "Grave tudo no documento.xml (bloco \"Gravar e publicar\") e gere a página.",
        "Depois, use esta lista para as pendências reais do documento.",
    ]

    modelo = {
        "grupos": [
            {"id": "uso", "nome": "Usar o documento", "icone": "🧭", "subtitulo": "ler, navegar, editar e exportar — em ordem",
             "etiqueta": "Usar", "sequencial": True, "raia": True, "cor": "principal"},
            {"id": "estrutura", "nome": "Mudar a estrutura", "icone": "🧱", "subtitulo": "na página de administração: telas, raias, sistemas, elos",
             "etiqueta": "Estrutura", "sequencial": False, "raia": True, "cor": "sup", "filtroElo": "geral"},
            {"id": "colaborar", "nome": "Colaborar e publicar", "icone": "🤝", "subtitulo": "propor, comparar, adotar, gravar e publicar",
             "etiqueta": "Colaborar", "sequencial": False, "raia": True, "cor": "aux", "filtroElo": "geral"},
            {"id": "arquivos", "nome": "Arquivos", "etiqueta": "Arquivo", "sequencial": False, "raia": False, "cor": "neutro", "filtroElo": "geral"},
        ],
        "sistemas": [
            {"id": "pagina", "nome": "Edição na página", "desc": "O que se faz direto na página publicada, no modo de edição."},
            {"id": "admin", "nome": "Administração", "desc": "O que só a página de administração oferece: estrutura, importar, comparar propostas."},
            {"id": "xml", "nome": "Arquivo documento.xml", "desc": "Onde o conteúdo fica de verdade; editável num editor de texto."},
            {"id": "build", "nome": "Build", "desc": "O build.py, que confere o documento.xml e gera as páginas."},
        ],
        "elos": [{"id": f"u{i}", "tipo": "bloco", "abrev": str(i)} for i in range(1, 6)]
                + [{"id": "geral", "tipo": "agregado", "abrev": "ger", "rotulo": "documento todo", "apelidos": []}],
        "ecossistema": {
            "nucleo": r["titulo"],
            "nota": "Os anéis são os sistemas de contexto em que os blocos se inserem. Clique num anel para ver os blocos ligados a ele.",
            "semItem": "Nenhum bloco está ligado a este sistema ainda.",
            "dicaChip": "Ver os blocos deste sistema",
        },
        "vistas": [
            {"id": "mapa", "tipo": "diagrama", "rotulo": mapa, "icone": "🗺️", "titulo": r["titulo"],
             "intro": f"Um documento vivo. Por enquanto, um tutorial: clique no bloco 1 para começar — e, quando quiser, troque cada parte pelo seu conteúdo.",
             "componentes": ["ecossistema", "raias"]},
            {"id": "referencias", "tipo": "normas", "rotulo": refs, "icone": "📚", "titulo": refs,
             "intro": "Referências ligadas aos blocos, com busca e filtros. {aConferir} marca o que ainda falta verificar.",
             "colunas": {"esfera": "Âmbito", "norma": "Referência", "resumo": "Resumo", "elos": "Blocos"},
             "ordemEsferas": ["Uso", "Edição", "Administração"],
             "rotulos": {"busca": "Buscar nas referências…", "buscaAria": "Buscar nas referências",
                         "contagem": "{total} referências · mostrando {visiveis}", "adicionar": "+ adicionar referência",
                         "filtroElo": "bloco", "aConferir": "a conferir",
                         "verElo": "Ver referências deste bloco →", "verAplicavel": "Ver referências aplicáveis →"}},
            {"id": "arquivos", "tipo": "cartoes", "rotulo": "Arquivos", "icone": "🗂️", "titulo": "Os arquivos do documento",
             "intro": "O que há em cada arquivo — clique num cartão.", "grupo": "arquivos"},
            {"id": "comecar", "tipo": "lista", "rotulo": "Para começar", "icone": "✅", "titulo": "Para começar",
             "intro": "O caminho para transformar este tutorial no seu documento.", "fonte": "notas"},
        ],
    }

    siglas = {
        "XML": {"expansao": "Extensible Markup Language — o formato do documento.xml", "url": "https://www.w3.org/XML/", "status": "ok"},
        "XSD": {"expansao": "XML Schema Definition — a gramática do documento.xsd", "url": "https://www.w3.org/XML/Schema", "status": "ok"},
        "JSON": {"expansao": "JavaScript Object Notation — o formato dos arquivos exportados pela página", "url": "https://www.json.org/json-pt.html", "status": "ok"},
        "HTML": {"expansao": "HyperText Markup Language — o formato da página gerada", "status": "ok"},
    }

    meta = {"slug": r["slug"], "titulo": r["titulo"], "icone": r["icone"], "subtitulo": r["descricao"],
            "margem": [], "atualizado": datetime.date.today().isoformat(),
            "apresentacao": {
                "titulo": "Bem-vindo ao seu documento vivo",
                "paragrafos": [
                    "Este documento é um tutorial: cada raia, bloco, anel e referência ensina como usá-lo e, depois, vira conteúdo seu.",
                    "Comece pelo bloco 1, na raia \"Usar o documento\". Esta apresentação aparece só na primeira visita; para revê-la, use \"Sobre este documento\", no menu.",
                    "Para trocar este texto, edite <apresentacao>, dentro de <meta>, no documento.xml — ou apague-o, e a apresentação deixa de existir.",
                ],
                "links": [{"rotulo": "Repositório do framework Documento Vivo", "url": "https://github.com/FilipeFT/documento-vivo"}],
                "botao": "Começar",
            }}
    return {"meta": meta, "modelo": modelo, "blocos": blocos, "normas": normas, "notas": notas, "siglas": siglas}


README_RAIZ = """# Documentos vivos

```
motor/          build.py · template.html · documento.xsd · README.md · init.py
documentos/     uma pasta por documento, cada uma com seu documento.xml
```

- Gerar a página de um documento: `cd motor && python3 build.py --doc ../documentos/<slug>/documento.xml` (`--admin` para a de administração).
- Criar mais um documento: `cd motor && python3 init.py`.
- Tudo sobre o método: [motor/README.md](motor/README.md).
"""


# ---------------------------------------------------------------- principal
PADRAO = {"slug": "documento-vivo", "titulo": "Documento vivo", "icone": "📘",
          "descricao": "Documento vivo: diagrama interativo e editável.", "telaMapa": "Mapa", "telaRefs": "Referências"}


def main():
    raiz = os.path.dirname(AQUI)  # a pasta que contém motor/
    docs = os.path.join(raiz, "documentos")
    r = dict(PADRAO)
    n = 1
    while os.path.exists(os.path.join(docs, r["slug"])):  # nunca sobrescreve: documento-vivo-2, -3…
        n += 1
        r["slug"] = f"{PADRAO['slug']}-{n}"
        r["titulo"] = f"{PADRAO['titulo']} {n}"

    B = carregar_build(os.path.join(AQUI, "build.py"))
    seed = tutorial(r)
    B.validate(seed)  # as regras do motor, antes de gravar qualquer coisa
    pasta = os.path.join(docs, r["slug"])
    os.makedirs(pasta)
    doc = os.path.join(pasta, "documento.xml")
    with open(doc, "w", encoding="utf-8") as f:
        f.write(B.json_para_xml(seed))
    if not os.path.exists(os.path.join(raiz, "README.md")):
        with open(os.path.join(raiz, "README.md"), "w", encoding="utf-8") as f:
            f.write(README_RAIZ)

    ok, msg = gerar_paginas(AQUI, doc)
    print(msg if ok else f"documento criado em {doc}, mas o build falhou:\n{msg}")
    rel = os.path.relpath(pasta, os.getcwd())
    print(f"\nPronto: abra {os.path.join(rel, r['slug'] + '.html')} no navegador e clique no bloco 1.")


if __name__ == "__main__":
    main()
