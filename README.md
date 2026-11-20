# Motor de documentos vivos

Monta, a partir de um `documento.xml`, uma página HTML autocontida e editável: um diagrama de grupos (raias) e blocos dentro de um ecossistema de sistemas de contexto, uma tabela de referências ligadas a elos, cartões, listas de notas e um dicionário de siglas. Nasceu do [Observatório do Açaí](../documentos/observatorio-acai/README.md), o primeiro documento feito com ele.

## Começar: `init.py`

Ponha a pasta `motor/` (estes cinco arquivos) onde os documentos devem ficar e rode `python3 motor/init.py`. Sem perguntas: ele cria `documentos/documento-vivo/` ao lado de `motor/` (ou `documento-vivo-2`, `-3`… se já existir) e gera as páginas:

```
<pasta>/
├── README.md
├── motor/
│   ├── build.py          # confere um documento.xml (regras em Python + xmllint/XSD) e gera as páginas
│   ├── template.html     # a página (HTML/CSS/JS), com placeholders preenchidos pelo build
│   ├── documento.xsd     # a gramática de todo documento.xml: tipos, enumerações, ids e referências
│   ├── init.py           # cria um documento novo (rode de novo para outro)
│   └── README.md         # este arquivo
└── documentos/
    └── documento-vivo/
        ├── documento.xml              # o documento novo
        ├── documento-vivo.html        # a página para publicar
        └── documento-vivo-admin.html  # a página de administração (não publicar)
```

O documento novo é um **tutorial sobre o próprio documento vivo**, escrito nos elementos do desenho: a raia numerada "Usar o documento" ensina a navegar, editar, mexer em listas, usar a tela de referências e exportar; "Mudar a estrutura" e "Colaborar e publicar" explicam a página de administração, as propostas e o caminho de volta ao XML; os anéis são os contextos (página, administração, XML, build); a tela de referências traz exemplos de como usá-la; os cartões descrevem cada arquivo; e a lista "Para começar" é o roteiro para trocar o tutorial pelo conteúdo do tema. Abra `<slug>.html` e clique no bloco 1.

Título, ícone, identificador (o `slug`, que dá nome à pasta e às páginas), telas, raias e todo o resto se trocam depois — pela página de administração ou no `documento.xml` — e o próprio tutorial ensina como. Rodar `init.py` de novo cria mais um documento, sem tocar nos existentes nem no motor.

Nada no motor é específico de um documento: identidade, vocabulário, telas e conteúdo estão todos no `documento.xml` (há um teste que confere que o código do motor não menciona o açaí). Dois documentos com o mesmo slug no mesmo navegador dividiriam o que foi salvo localmente — por isso o `init` não aceita um slug que já exista em `documentos/`.

Também dá para editar o `documento.xml` direto num editor de texto: a gramática comentada está em `documento.xsd` e as regras em "Modelo de dados" abaixo; o build para com uma mensagem que diz onde (linha, campo, id) se algo não bater.

## Como gerar a página

```bash
cd motor
python3 build.py --doc ../documentos/<slug>/documento.xml            # escreve documentos/<slug>/<slug>.html (o publicado)
python3 build.py --doc ../documentos/<slug>/documento.xml --admin    # escreve …/<slug>-admin.html (administração)
python3 build.py --doc DOC [--admin] /caminho/saida.html           # ou escolha outro destino
python3 build.py --doc DOC --de-json exportado.json                # grava no DOC um JSON exportado pela página
```

O nome do arquivo gerado é o `slug` do documento (`<slug>.html` e `<slug>-admin.html`), na pasta do documento. Sem `--doc`, o build usa o `documento.xml` ao lado de `build.py` (útil para copiar motor e documento juntos para uma pasta só) e, se não houver, pede `--doc`.

**Dados em XML com schema (Fase 7).** A fonte do conteúdo é o `documento.xml` de cada documento, validado contra `motor/documento.xsd` pelo `xmllint` (libxml2; já vem no macOS e na maioria dos Linux, ou `apt install libxml2-utils`). O build converte o XML no mesmo objeto que antes vinha dos seis JSON — por isso, onde este README fala de `meta.json`, `modelo.json`, `blocos.json`, `normas.json`, `notas.json` ou `siglas.json`, leia a seção `<meta>`, `<modelo>`… de `documento.xml`. A conversão é sem perdas e na mesma ordem: o site gerado é byte a byte o da Fase 6, com a mesma `SEED_VERSION` (ninguém perde edição local). Três camadas de checagem, nesta ordem, e qualquer erro para o build: (1) a conversão — estrutura do XML, booleanos (`true`/`false`) e listas, declarados em `XML_LISTAS`/`XML_BOOLS`/`XML_MAPAS` no `build.py`; (2) as regras em Python (`validate()`, mensagens em português); (3) o XSD — tipos, enumerações (slots de cor, tipos de vista e de elo, `ok`/`conferir`), ids únicos e **referências** entre seções (`xs:key`/`xs:keyref`: bloco → grupo e sistemas, norma → elos, grupo → elo, vista → grupo), com número da linha do erro. O XSD não é mais estrito que a página no conteúdo (textos de blocos, normas e notas podem ficar vazios; campos opcionais lá são opcionais aqui), para que tudo o que a página publicada exporta caiba no XML; identidade e modelo são estritos como o portão da página. No navegador nada muda: exportar, importar e propostas continuam em JSON. Para levar ao `documento.xml` o que foi feito na página (por exemplo, depois de adotar propostas no build de administração), exporte e rode `python3 build.py --de-json arquivo.json`: o arquivo só é substituído se o resultado passar nas regras e no XSD.

**Dois builds, um documento (Fase 5).** O publicado oferece, no modo de edição, editar textos e conteúdo, desfazer/restaurar e **exportar** (o arquivo exportado é a forma de propor mudanças). O de administração (`--admin`) oferece a mais **Importar** e a **edição estrutural** (painel "Estrutura do documento" e "Estrutura do bloco"), e mostra o marcador "Administração". A única diferença entre os dois arquivos é a constante `ADMIN` (placeholder `__ADMIN__`); dados, `SEED_VERSION` e chave de armazenamento são os mesmos. É uma divisão de interface, não de segurança: tudo roda no navegador de quem abre a página, e o build de administração simplesmente não deve ser publicado.

**No diagrama da administração.** Com o modo de edição ligado, a página de administração mostra os controles de estrutura no próprio diagrama: "+ bloco" no fim de cada raia (cria o bloco ali e o abre para edição), "×" em cada cartão (remove o bloco, com confirmação; um bloco que é elo ligado a referências é recusado), "×" em cada anel do ecossistema (remove o sistema de contexto, com confirmação, desmarcando-o dos blocos que o usavam) e "+ anel" abaixo dos anéis (cria um sistema e abre o painel Estrutura no nome dele). Ela também exporta em XML: **"Exportar documento.xml"** baixa o documento inteiro, idêntico ao que o `build.py` escreveria (as regras de conversão vêm do próprio build, injetadas na página), pronto para substituir o `documento.xml` da pasta — sem passar por JSON e `--de-json`; **"Exportar template (estrutura)"** baixa `documento-modelo.xml`, só com a estrutura (identidade com slug `<slug>-modelo`, raias, anéis, telas, vocabulário e siglas; um bloco vazio por grupo; sem referências nem notas), para começar outro documento do mesmo tipo: crie `documentos/<novo>/`, ponha o arquivo lá como `documento.xml`, troque o `slug` e rode o build.

**Propor e adotar mudanças (Fase 6).** Quem colabora edita no build público e clica em "Exportar dados (JSON)"; o arquivo exportado é a **proposta** (enviada por qualquer meio). No build de administração, "Comparar proposta (JSON)" lê o arquivo (com as mesmas checagens de Importar) e lista as diferenças em relação ao documento atual, agrupadas por seção: `+` novo, `−` removido, `~` alterado — por item e por campo de primeiro nível (um bloco com o nome alterado aparece como `~ bloco "…": nome`, sem sobrescrever o resto do bloco). Normas, que não têm id, são casadas pelo título (uma norma renomeada aparece como `−` antiga e `+` nova); notas, pelo texto; siglas, pela sigla. Nada vem marcado: a administração escolhe e clica em "Adotar selecionadas". As escolhidas são aplicadas juntas pelo mesmo portão da edição estrutural — se a combinação não formar um documento válido (por exemplo, um bloco que usa um grupo novo sem adotar o grupo), nada muda e a barra de status avisa. Depois de adotar, "↺ Desfazer" volta ao estado anterior. A **ordem** das listas não é proposta (reordena-se no painel Estrutura).

O script injeta as seis seções de `documento.xml` (meta, modelo, blocos, normas, notas, siglas), já convertidas, no placeholder `__SEED_JSON__` de `template.html`. Antes de montar, `validate()` confere (1) o próprio `<modelo>` — campos obrigatórios e tipos, ids únicos, cor num slot de paleta válido, elos coerentes — e (2) a integridade referencial dos dados contra esse modelo: todo `bloco.grupo`, `bloco.sistemas[]` e `norma.elos[]` precisa apontar para um id que o modelo defina, e toda sigla precisa ter uma expansão não vazia. Recusa o build com uma mensagem clara se algo não bater, em vez de deixar o site publicar um card, um anel ou uma dica vazia por engano. Nenhum conjunto de ids está mais fixo no código: o que `build.py` ainda conhece é só `COR_SLOTS` (os slots de paleta que o CSS sabe pintar), `TIPOS_ELO` e, desde a Fase 3, os tipos de vista (`TIPOS_VISTA`, `COMPONENTES_DIAGRAMA`, `FONTES_LISTA`) — cada um corresponde a um renderizador do template. `validate()` também confere `meta` (slug, título, ícone e descrição) e as regras de `modelo.vistas`. Três placeholders do `<head>` (`__TITULO__`, `__DESCRICAO__`, `__FAVICON__`) são preenchidos com os textos de `<meta>`, escapados; o favicon é um SVG com o emoji de `meta.icone`, embutido como data-URI. O build é a única fonte do `<head>`; em tempo de execução o título da aba segue `state.meta.titulo`.

## Modelo de dados

**`bloco`** (um elo da cadeia):

| campo | tipo | observação |
|---|---|---|
| `id` | string | `e1`…`e10` (elos numerados — `e1`…`e4` no grupo `suprimentos`, `e5`…`e10` no grupo `principal`) ou id livre (demais grupos). O id não muda quando o bloco troca de grupo: é ele que `norma.elos[]` referencia e que o botão "Ver legislação" filtra |
| `grupo` | id | um dos `grupos[].id` de `<modelo>` (hoje `principal`, `suprimentos`, `auxiliar`, `circular`, `institucional`) |
| `nome`, `resumo` | string | — |
| `secoes` | lista | `{titulo, itens, margem?}` — o conteúdo expandido do card |
| `sistemas` | lista de ids \| ausente | quais dos `sistemas[].id` do modelo (hoje 7) esse bloco toca (relação N:N) |

**`norma`** (uma fonte legal/normativa):

| campo | tipo | observação |
|---|---|---|
| `esfera` | string | Federal, Amapá, Pará, Amazonas, Macapá, Belém, Manaus, Outros estados, Técnicas |
| `titulo`, `resumo`, `fonte` | string | — |
| `elos` | lista de ids | quais etiquetas de `modelo.elos` essa norma recebe (hoje `e1`…`e10`, `auxiliar`, `apoio`) |
| `status` | enum | `ok` (conferida) \| `conferir` (pendente de verificação) |

**`siglas`** (dicionário de acrônimos e abreviações; chave = a sigla, exatamente como ela aparece no texto — a correspondência é sensível a maiúsculas/minúsculas):

| campo | tipo | observação |
|---|---|---|
| `expansao` | string | obrigatório; o que a sigla significa |
| `url` | string \| ausente | link institucional opcional (nem toda sigla tem uma só instituição-dona, ex.: `IN`, `LC`, `PL`) |
| `status` | enum | `ok` \| `conferir` — mesma convenção de `norma.status` |

**`modelo`** (seção `<modelo>` do `documento.xml` — o *vocabulário* do documento; é dado, não código, e viaja junto com o conteúdo no estado, no export e no import). Chama-se `modelo` e não `schema` de propósito: no futuro, a *gramática* dos dados será um XSD, e este arquivo continua sendo o vocabulário que ela valida.

| campo | tipo | observação |
|---|---|---|
| `grupos[]` | lista (a ordem é a ordem das raias) | `{id, etiqueta, sequencial, raia, cor, filtroElo?, nome*, icone*, subtitulo*}` (\* obrigatórios quando `raia` é `true`). `etiqueta` = rótulo na tag do painel; `sequencial` = cartões numerados com setas; `raia` = se o grupo ganha uma raia na vista Cadeia; `cor` = slot de paleta (`principal`, `sup`, `aux`, `apoio`, `neutro`) — nunca um valor CSS livre, para o modo escuro continuar funcionando; `filtroElo` = elo agregado que o botão "Ver legislação aplicável" usa para os blocos do grupo que não são elo |
| `sistemas[]` | lista (do anel externo ao interno) | `{id, nome, desc}` — os sistemas de contexto do diagrama de ecossistema |
| `elos[]` | lista | etiquetas de legislação: `{id, tipo, abrev, rotulo?, apelidos?}`. `tipo: "bloco"` = a etiqueta é o id de um bloco (e1…e10) e o rótulo vem do nome dele; `tipo: "agregado"` = reúne vários (`auxiliar`, `apoio`) e traz `rotulo`. O campo "elos" da tabela de normas reconhece, sem diferenciar maiúsculas, exatamente o `id`, a `abrev` ou um dos `apelidos` (mais `todos`/`t`); o que não casa é descartado |
| `ecossistema` | objeto | `{nucleo, nota, semItem, dicaChip}` — textos do diagrama de anéis (`dicaChip` = a dica ao passar o mouse num anel) |
| `vistas[]` | lista (a ordem é a do menu; a primeira é a vista inicial) | as telas do documento, ver abaixo |

**`vistas[]`** — cada vista tem `{id, tipo, rotulo, icone, titulo, intro}` (`rotulo`/`icone` = botão do menu e título da barra mobile; `titulo` = o `<h1>`; `intro` = texto simples, com siglas expandidas) mais campos do seu `tipo`. O `id` (`^[a-z][a-z0-9-]*$`) vira o id da seção no DOM (`view-<id>`), então ids de vista não podem repetir.

| `tipo` | campos próprios | observação |
|---|---|---|
| `diagrama` | `componentes[]` — `"ecossistema"` e/ou `"raias"`, na ordem em que aparecem, sem repetir | no máximo **uma** vista (id de DOM único `#diagram`) |
| `normas` | `colunas{esfera,norma,resumo,elos}`, `ordemEsferas[]`, `rotulos{busca, buscaAria, contagem, adicionar, filtroElo, aConferir, verElo, verAplicavel}` | no máximo **uma** vista. `contagem` usa `{total}` e `{visiveis}`. Na `intro`, o token `{aConferir}` vira o selo (texto = `rotulos.aConferir`). Os botões "Ver legislação…" do painel lateral só existem se houver uma vista `normas`: é ela que os nomeia e para onde saltam. As `colunas` também nomeiam os campos da norma para leitores de tela no modo de edição |
| `cartoes` | `grupo` — id de um `grupos[]` | lista os blocos desse grupo; pode haver quantas vistas quiser |
| `lista` | `fonte` — hoje só `"notas"` | lista editável; quantas quiser |

**`meta`** (seção `<meta>` do `documento.xml` — a *identidade* do documento): `slug` (`^[a-z0-9][a-z0-9-]*$`; define a chave de armazenamento local `<slug>:content/main` e o nome do arquivo exportado `<slug>.json`; é lido **sempre da semente do build**, nunca do estado nem de um arquivo importado, para um arquivo de fora não poder redirecionar o armazenamento), `titulo` (marca no menu, título da aba), `icone` (emoji do favicon), `subtitulo` (a `<meta description>`), `atualizado`. `margem` é um dado sem uso hoje (nenhum código o lê), mantido intocado. O antigo `meta.intro` passou a ser a `intro` da vista Cadeia.

**`meta.apresentacao`** (opcional) — o texto mostrado num aviso na **primeira visita** de cada navegador ao documento, e depois pelo link "Sobre este documento" no menu: `titulo`, `paragrafos` (lista de textos), `links` (lista de `{rotulo, url}`, só `http(s)`; abrem numa aba nova) e `botao` (o texto do botão que fecha). A marca de visita fica no navegador (`<slug>:visitado`); sem `apresentacao`, não há aviso nem link. O documento gerado pelo `init.py` traz uma, que explica o tutorial e aponta para o repositório do framework.

Para montar um documento de **outro domínio**, escreva outro `documento.xml` (ver acima); `build.py`, `template.html` e `documento.xsd` não mudam (o `init` faz exatamente isso; há também um teste — com identidade, menu, vocabulário da vista de normas, duas vistas de cartões e sem vista de notas próprios). Ainda fixos no código e a tratar nas próximas fases: os nomes das entidades (blocos, normas, notas, siglas), o texto genérico do editor ("Editar conteúdo", "Desfazer", confirmações de importação, o sufixo "(ids separados por vírgula)") e a paleta (cinco slots, em CSS). No navegador, um modelo importado é conferido com as mesmas regras do build — com uma diferença deliberada: um elo `tipo: "bloco"` sem o bloco correspondente é tolerado, para não recusar arquivos parciais. Exports de antes da Fase 3 (modelo sem `vistas`/`dicaChip`, `meta` sem título/ícone, com `intro`) continuam entrando: o que falta é completado com os dados do build, campo a campo; se as vistas do build não combinarem com o modelo importado (por exemplo, apontam para um grupo que ele não tem), o arquivo é recusado. Como o modelo (e, com ele, as vistas) viaja no export, a definição das telas já é compartilhável por arquivo.

**Edição estrutural na página (Fase 4a).** No modo de edição, "Estrutura do documento" abre um painel (no drawer) com os **textos** de `meta` (título, ícone, descrição), de cada vista (rótulo do menu, ícone, título e introdução), de cada grupo (etiqueta, nome e subtítulo da raia), de cada sistema de contexto e do ecossistema. Toda edição desses campos passa por um único portão, `tentarEstado()`: a mudança é aplicada num **clone** do estado e só vale se `validShape()` — as mesmas regras de um arquivo importado — aceitar o resultado; senão o campo volta ao texto anterior e a barra de status avisa ("Alteração recusada…"). **Fase 4b:** cada vista, grupo e sistema tem ↑ ↓ (mover: muda a ordem do menu, das raias, dos anéis; a primeira vista é a inicial) e × (remover); vistas e sistemas têm também "+ adicionar" (uma vista nova mostra os cartões do primeiro grupo ainda não exibido por outra vista; ids novos são gerados, `vista-1`, `sistema-1`…). Remover é recusado, com mensagem específica, quando algo usa o item: grupo ou sistema com blocos ("em uso por N blocos"), grupo mostrado por uma vista de cartões, a última vista. Como os blocos ainda não têm interface para trocar de sistema, só sistemas sem blocos saem por enquanto. **Fase 4c.1:** cada grupo tem também cor (um dos slots da paleta), "raia no diagrama", "numerado em sequência" e "legislação aplicável" (o elo agregado de `filtroElo`, ou nenhum); ligar a raia de um grupo completa nome, ícone e subtítulo que faltarem. Grupos agora também podem ser adicionados (`grupo-1`…, raia vazia em cor neutra). **Fase 4c.2:** no modo de edição, o painel de cada bloco ganha "Estrutura do bloco": ↑ ↓ (ordem dentro do grupo, que é também a numeração das raias sequenciais), × (remover, com confirmação; recusado se o bloco é um elo do modelo), o grupo do bloco e os sistemas de contexto a que ele pertence. "+ adicionar bloco neste grupo", no painel Estrutura, cria um bloco (`bloco-1`…) e o abre para edição. Com isso, um sistema passa a poder ser removido depois de desmarcado dos blocos que o usavam. **Fase 4d:** a vista de normas mostra no painel o seu vocabulário — nomes das colunas, os oito rótulos (a contagem precisa conter `{total}` e `{visiveis}`) e a ordem das esferas (texto separado por vírgulas). Uma seção "Elos" edita abreviação, rótulo e apelidos (separados por vírgulas; apelido ambíguo ou reservado é recusado) e permite adicionar elos agregados (`elo-1`…), que passam a aparecer como opção de "legislação aplicável" dos grupos. Remover um elo é recusado se alguma norma o usa ou se ele é a legislação aplicável de um grupo; remover um bloco que é elo tira o elo junto, nas mesmas condições. Ids e tipos continuam não editáveis — trocar um id exigiria reescrever todas as referências e não é necessário para nada até aqui. Sem mudança nos arquivos de dados, então `SEED_VERSION` não muda e edições locais não são descartadas.


## Siglas e abreviações

Qualquer sigla cadastrada em `<siglas>` ganha, no site, um sublinhado pontilhado: passar o mouse, navegar até ela com Tab, ou tocar nela num celular/tablet mostra a expansão e, quando houver, um link para o site institucional. A correspondência roda inteiramente no `template.html` (função `wrapSiglas`, ao lado de `el()`/`editableSpan()`): o texto livre é varrido com uma expressão regular montada a partir das chaves de `<siglas>`, e cada ocorrência vira um `<span tabindex="0">` focável (nunca `innerHTML`, e nunca um `<button>` — ver "Segurança e robustez" abaixo). Três regras foram necessárias para não quebrar o resto do site:

- **Fica fora do modo de edição.** Em edição, o campo volta a ser texto puro — zero risco de a marcação da dica atrapalhar o cursor ou ser salva junto do conteúdo.
- **Nunca aninha dentro do link da fonte.** No título de uma norma (que já é um link para `fonte`), a sigla principal vira seu próprio span ao lado do link, em vez de ficar dentro dele — um link não pode conter outro link.
- **Em touch, um toque alterna a dica.** Tocar a sigla abre; tocar de novo na mesma, tocar em outra sigla, tocar fora, rolar a página ou apertar Esc fecha (só uma dica fica aberta por vez). Como não existe hover de verdade em touch, um `touchstart` liga uma flag (`touchActive`) que faz o `mouseover`/`mouseout` "fantasma" que o navegador dispara logo antes do `click` ser ignorado — sem essa flag, o toque abriria a dica duas vezes (uma por engano via hover, outra pelo toque de fato) e o `click` seguinte a fecharia na hora, dando a impressão de que nada aconteceu. Tocar no link institucional dentro da dica continua navegando normalmente (nada de `preventDefault`); a dica fechar junto é só um efeito colateral inofensivo.


## Segurança e robustez

Uma revisão de código (2026-10-16) encontrou e corrigiu um XSS real, além de vários pontos de robustez e acessibilidade, no `template.html`:

- **Links vindos de dados importados passam por um allowlist.** `norma.fonte` e `sigla.url` só viram `<a href>` se forem `http://`/`https://` (função `safeHref()`); um JSON importado com `fonte: "javascript:..."` agora renderiza como texto puro, nunca como link clicável.
- **Importar/restaurar ficou mais defensivo.** `validShape()` confere o tipo de cada campo que o render de fato usa (não só a presença de `meta`/`blocos`/`normas`/`notas`); o novo estado é montado campo a campo em vez de `Object.assign({}, seed, parsed)` (uma chave `"__proto__"` no arquivo importado não tem mais como alterar o protótipo do estado); um erro ao desenhar a tela depois de importar volta para a seed original sem salvar nada quebrado; e há um "↺ Desfazer" de um nível depois de importar ou restaurar o conteúdo original. Desde a Fase 2, `validShape()` também confere o `modelo` (o do arquivo, ou o do build se o arquivo — um export antigo — não trouxer um) com as mesmas regras do build e recusa blocos/normas que apontem para grupo, sistema ou elo que esse modelo não define; a cor de um grupo é sempre um slot de paleta, nunca um valor CSS vindo do arquivo. Desde a Fase 3, também confere `modelo.vistas` e `meta`: título, ícone e descrição do arquivo viram texto (nunca HTML) na página, o `slug` do arquivo é ignorado, e `meta`, `modelo` e `ecossistema` são montados campo a campo (uma chave `"__proto__"` em qualquer deles não contamina nada).
- **O gatilho de uma sigla é um `<span>` focável, não mais um `<button>`.** Um `<button>` com um `<a>` dentro (o link institucional da dica) é HTML inválido — conteúdo interativo não pode aninhar em conteúdo interativo. O span mantém o mesmo comportamento de Tab/hover/foco de antes, com `aria-describedby` + `role="tooltip"` para leitores de tela.
- **O painel lateral (drawer) tem semântica de diálogo.** `role="dialog"` + `aria-modal`, Tab fica preso dentro dele enquanto está aberto, e o foco volta para o elemento que o abriu ao fechar (✕, Escape, ou o fundo escurecido).
- **Colar e arrastar-e-soltar em campos editáveis só aceitam texto puro.** Antes, só colar era filtrado; uma `<img onerror="...">` arrastada para dentro de um campo não executa mais. O texto puro passou a ser inserido via `Selection`/`Range` em vez de `document.execCommand` (descontinuado).
- Uma `<meta http-equiv="Content-Security-Policy">` com `object-src`/`base-uri`/`form-action` todos `'none'` fecha mais uma camada, sem tocar em `script-src`/`style-src` (a página é de propósito um único arquivo com `<script>`/`<style>` inline, sem build step).
- **Conteúdo publicado agora vence uma cópia local desatualizada (2026-10-22).** Antes, qualquer edição salva no navegador (mesmo uma acidental, feita só testando o modo "Editar") passava a vencer a semente embutida pra sempre — inclusive num hard refresh — porque `init()` fazia `Object.assign({}, cloneSeed(), snap.data())`, e esse merge raso substitui cada array (`blocos`/`normas`/`notas`/`siglas`) inteiro pelo que estava salvo, por mais antigo que fosse. Um link corrigido em `normas.json`, por exemplo, nunca chegava a quem já tivesse qualquer coisa salva localmente. Agora `build.py` calcula um hash do conteúdo (`SEED_VERSION`, não um timestamp — o mesmo conteúdo gera sempre a mesma versão) e `doSave()` grava esse hash junto do estado; no carregamento, `init()` só reaproveita o que está salvo se a versão bater com a deste build — caso contrário (incluindo salvamentos de antes desta correção existir, que não têm hash nenhum) descarta a cópia local em favor do conteúdo publicado, avisando na barra de status ("Conteúdo atualizado nesta página…"). Uma edição feita ao vivo no navegador continua funcionando normalmente entre um salvamento e outro, enquanto o build não mudar.
- **Aviso de versão diferente (2026-11-20).** Quando a cópia salva neste navegador é de outra versão do conteúdo publicado, a página não a descarta mais em silêncio: mostra a versão publicada e um aviso (que não se fecha com Esc) com duas escolhas — **"Exportar minhas alterações e sincronizar"**, que baixa a cópia local como `<slug>-alteracoes-locais.json` (o mesmo formato de uma proposta, para enviar à equipe responsável) e então passa para a versão publicada, ou **"Sincronizar sem exportar"**. Até a escolha, a cópia antiga continua guardada: fechar a aba não perde nada. Só quem editou tem cópia salva; quem só leu nunca vê esse aviso.


## Princípios de design

- **Tufte**: clareza antes de ornamento, notas de margem, poucos elementos de chrome, dados em primeiro plano.
- **SaaS comercial**: sidenav fixo com as telas definidas em `modelo.vistas`, cards, tema claro/escuro.
- **YAGNI / KISS / DRY**: um único arquivo HTML autocontido publicado; conteúdo editável in-place com persistência em nuvem (artifact DB) e fallback automático em `localStorage` quando o arquivo é aberto fora do claude.ai.

## Roteiro

**Generalização do framework** (de PoC para método reaproveitável, uma fase por vez): ✅ 1 elos 1-4 movidos para Suprimentos · ✅ 2 grupos/sistemas/elos viram dados (`modelo.json`) · ✅ 3 identidade e vistas do documento dirigidas por dados (`meta.json`, `modelo.vistas`) · 4 edição estrutural (editar o próprio modelo): ✅ 4a textos pelo painel "Estrutura" · ✅ 4b mover/remover/adicionar vistas, grupos e sistemas · ✅ 4c campos de grupo (cor, raia…) e blocos · ✅ 4d elos e vocabulário da vista de normas · ✅ 5 build administrativo separado (`--admin`: importação e edição estrutural fora do build publicado) · ✅ 6 fluxo colaborativo (equipes propõem exportando, a administração compara e adota seletivamente) · ✅ 7 dados em XML com schema (`documento.xml`/`documento.xsd`, validados pelo xmllint; o navegador segue trocando JSON) · ✅ 8 empacotamento: `motor/` (build, template, gramática) separado de `documentos/` (cada um com seu `documento.xml`), `--doc`, saída pelo `slug` e um documento de exemplo — depois substituído pelo `init.py`, que gera um documento-tutorial, sem perguntas (convenção em vez de configuração). Cada fase ganha seu próprio plano antes de ser implementada.

- Componente em **Elixir** para validar/interagir com a estrutura do documento — escopo ainda em aberto.
