# Benfeitorias em Campo — guia para o Claude Code

App web (PWA), em um único arquivo, para o perito Daniel Vasques Aleixo (Eng. Agrônomo, CREA-MS 12.577/D) conferir e medir benfeitorias rurais em vistoria. Ele usa no celular/tablet Android em campo, sem internet, e depois passa a perícia para o computador.

Toda a interface, os textos e os comentários do código ficam em **português do Brasil**.

## Fluxo de uso
1. No Google Earth, Daniel desenha as benfeitorias (polígonos, linhas e pontos, com nome) e exporta KML/KMZ.
2. No app: **Importar KML/KMZ** → o app classifica cada geometria pelo nome ou pasta e mede área, perímetro, retângulo mínimo e comprimento.
3. Em campo: digita as medidas da trena, o formato, os acabamentos, o padrão, a conservação e a idade aparente, tira fotos com legenda e marca o item como conferido.
4. Exporta: relatório (croqui + quadro + total + uma ficha "Planilha das construções" por benfeitoria), planilha .xlsx, KML/KMZ ajustado (KMZ com fotos) e backup .json (perícia + fotos, para passar ao computador).

## Estrutura
```
src/app.html          ← TODO o código (HTML+CSS+JS). Placeholders /*LEAFLET_CSS*/ e /*LEAFLET_JS*/
public/               ← manifest.json, sw.js (service worker, cache offline), ícones
scripts/build.py      ← injeta o Leaflet inline e gera dist/index.html (+ copia public/)
test/fixtures/        ← teste.kml / teste.kmz (gerados por gerar_kml_teste.py)
test/e2e.py           ← teste Playwright ponta a ponta (gera test/out/)
.github/workflows/pages.yml ← build + deploy no GitHub Pages a cada push na main
```
Comandos: `npm ci` → `npm run build` → `npm test` (precisa de `pip install playwright && playwright install chromium`). Para servir localmente: `npm run serve`. O service worker só registra em https; em http://localhost o app funciona sem ele.

**Restrição de projeto:** o app precisa funcionar **offline e sem dependências externas**. Nada de CDN em tempo de execução: as bibliotecas vão inline pelo build, e ZIP, XLSX e KMZ são escritos à mão no próprio arquivo. A única coisa online é a camada opcional de satélite (Esri World Imagery).

## Mapa do código (src/app.html, na ordem)
- **utilidades**: `$`, `esc`, `fmt` (pt-BR), `num` (aceita vírgula), `fmtArea` (m² ou ha ≥ 10.000).
- **TIPOS**: `[chave, nome, cor, regex]`. A ordem importa (o primeiro que casar vence; "casa de funcionário" vem antes de "casa"). `GRANDES` = tipos fora do total de benfeitorias (perímetro, pastagem, lavoura, RL, APP).
- **geodésia**: projeção plana topocêntrica local sobre WGS84 (`projetor`/`projDe`); `shoe` = área por shoelace; `retMin` = retângulo mínimo (rotating calipers sobre o casco convexo); `mede(it)` preenche `it.kml`.
- **curral**: `dentro` (ray casting), `candidatosCob`/`vincula` (polígono dentro do curral = parte coberta; prioridade para nomes com "cobert/telhad"), `candidatosInt`/`anexa`/`solta` (linhas, pontos e polígonos dentro do curral = divisões/componentes em `it.div`), `autoCob` roda na importação. `linCurral` = lances × distância; `linKmlCurral` = perímetro + divisões.
- **formatos**: `sugereFormato` (pela razão área/retângulo mínimo e proporção), `formatoDe`. `adotada(it)`: prioridade **área direta > diâmetro (circ./semicirc.) > lado² (quadrado) > C×L > KML**. `totais()` soma as áreas adotadas fora de `GRANDES`; a área coberta é informada à parte e não é somada de novo.
- **armazenamento**: `DB` = IndexedDB `benfeitorias-campo` (stores `proj` e `foto`), com fallback em memória. `salva()` faz debounce de 300 ms. Sugestões digitadas (tipologia, padrão, conservação, acabamentos) ficam em `localStorage` `sug_*`.
- **ZIP**: `zip()` (store, sem compressão, flag UTF-8) e `unzip()` (deflate via `DecompressionStream('deflate-raw')`).
- **KML**: `lerKml` (aceita Polygon com furos, LineString, LinearRing, Point, MultiGeometry; uma LineString fechada que não é cerca, estrada ou rede vira polígono).
- **telas**: `home`, `lista`, `abreItem` (ficha), `cobFicha`, `divFicha`, `fotosItem` (legenda ao tocar na foto), `mapa`/`desenha` (Leaflet; tracejado = pendente, linha cheia = conferido), `exportTela`.
- **ficha**: `ACAB`/`ACAB_OP` (paredes, revestimento, piso, teto/forro, telhado, janelas, portas, instalações, outros) → `descAcab`; `descCurral`/`diviCurral` geram textos do curral; `tipologiaPadrao`.
- **exportação**: `baixa()` usa `<a download>` no app instalado e a capacidade `downloads` quando roda como artifact do Claude (ali kml/kmz saem dentro de .zip). `geraKml`, `geraXlsx` (XLSX mínimo, 2 abas, linha de TOTAL), `croqui` (SVG com escala e norte), `geraRelatorio` (HTML A4; no app instalado abre e chama print → "Salvar como PDF").

## Modelo de dados (item)
```
{id, n, nome, tipo, pasta, desc, g:'Polygon'|'LineString'|'Point'|'None', c:[[lon,lat]...], holes,
 kml:{area, perim, comp, larg, ret, nv, len},
 campo:{formato, comp, larg, area, diam, alt, lances, nPal, espPal, reguas, madeira, compLin, port, divs,
        tronco, balanca, embarc, seringa, brete, fios, esp},
 cob:{nome, c, kml, campo:{comp,larg,area}, tipo, alt},     // parte coberta do curral
 div:[{id, nome, g, c, kml, tipo}],                          // divisões/componentes do curral
 tipologia, idade, padrao, conserv, descr, divisao, acab:{estr,revest,piso,forro,cob,jan,port,inst,outros},
 obs, fotos:[idFoto], leg:{idFoto: legenda}, ok}
```
Projeto: `{id, nome, processo, municipio, perito, crea, arquivo, criado, alterado, itens}`. **Ao mudar o modelo, mantenha compatível com backups .json antigos** (campos novos opcionais).

## Modelo da ficha (relatório)
Reproduz a "Planilha das construções" dos laudos do Daniel: faixa verde "PLANILHA DAS CONSTRUÇÕES"; "N - Nome"; blocos "Descrição suscinta" e "Divisão interna"; "Aspectos técnicos" com Tipologia | Padrão | Conservação / I. aparente | Área (para o curral: Lances | Réguas/lance | Madeira / Linear | Área coberta | Formato); fotos 2×2 com legenda embaixo (Vista externa, Vista interna, Vista aérea…). Padrão e conservação são texto livre por enquanto (ex.: "8 - Médio", "E - Regular").

## Pendências / próximos passos
- [ ] **Publicar no GitHub Pages** (repo público `benfeitorias`; o workflow já está pronto) e instalar no Android pelo Chrome → "Adicionar à tela inicial". No app do Claude para Android o seletor de arquivos não abre; por isso o app precisa rodar instalado.
- [ ] Trocar padrão/conservação por **listas fixas** quando Daniel mandar a tabela de enquadramento que ele usa (manter o texto já digitado).
- [ ] Ideia aprovada para avaliar: carregar o **ortomosaico do drone** (GeoTIFF/JPG georreferenciado) como fundo offline do mapa.
- [ ] Ao lançar uma versão, troque o nome do cache em `public/sw.js` (`benfeitorias-vN`).

## Convenções
- Testar sempre com `npm test` (sem erros JS; medidas do KML de teste: galpão 20×12 = 240,00 m²; cerca 700,00 m; total das benfeitorias = soma das adotadas).
- Contas que vão para laudo devem ser conferidas fora da IA (protocolo do Daniel).
- Números no formato brasileiro (vírgula decimal) na interface e no relatório; ponto na planilha (números de verdade).
- Não colocar número de processo ou nome das partes em textos de divulgação.
