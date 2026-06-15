# PROMPT MESTRE — Gerador de Welcome Book Digital (Mobile + PDF)
> Produto OFS Digital para hospedagens (Airbnb, pousadas, hotéis, hostels, flats)
> Stack: YAML (dados) + Jinja2 (templates) + Playwright (render PDF)
> Usar dentro do Antigravity / Claude Code com o briefing do cliente já preenchido

---

## PAPEL E OBJETIVO

Você é um engenheiro de pipeline de documentos. Sua tarefa é gerar um **Welcome Book trilíngue** (Português, Inglês, Espanhol) para uma hospedagem, em **duas saídas a partir da MESMA fonte de dados**:

1. **`welcome-book.html`** — versão mobile interativa, arquivo único, 100% offline (todos os assets embutidos), navegação por âncoras, botões de ação nativos (WhatsApp, telefone, e-mail, Maps).
2. **`welcome-book.pdf`** — versão PDF com links internos clicáveis, formato vertical mobile (540 × 1168,5 pt por página), para uso onde não há internet ou para impressão.

Nenhum texto pode ser digitado direto no template. **Todo conteúdo vem do `welcome-book.yaml`.** Se um dado obrigatório estiver ausente, PARE e liste o que falta — nunca invente e nunca deixe placeholder tipo `[Número de emergência local]` no produto final.

---

## ARQUITETURA DO PROJETO

```
welcome-book/
├── data/
│   └── welcome-book.yaml        # fonte única de verdade (3 idiomas)
├── assets/
│   ├── logo.png                 # logo do cliente (fundo transparente)
│   ├── cover.jpg                # foto de capa
│   ├── host.jpg                 # foto do anfitrião
│   ├── rooms/                   # fotos dos ambientes
│   ├── places/                  # fotos de restaurantes/atrações
│   └── icons/                   # ícones SVG line-art (gerar inline, não usar CDN)
├── templates/
│   ├── base.html.j2             # esqueleto compartilhado
│   ├── mobile.html.j2           # alvo 1: HTML interativo
│   └── pdf.html.j2              # alvo 2: HTML paginado p/ Playwright
├── build.py                     # orquestrador: lê YAML → renderiza → otimiza → gera PDF
└── dist/
    ├── welcome-book.html
    └── welcome-book.pdf
```

`build.py` deve: (1) validar o YAML contra o schema, (2) otimizar imagens (redimensionar para máx. 1080px de largura, JPEG qualidade 80, converter para base64 no HTML mobile), (3) renderizar os dois templates, (4) rodar Playwright para o PDF, (5) rodar o checklist de QA e imprimir relatório.

---

## SCHEMA DO YAML (obrigatório seguir)

```yaml
meta:
  version: "1.0"
  generated_by: "OFS Digital"
  languages: [pt, en, es]          # ordem define a ordem das seções no PDF

brand:
  name: ""                          # nome da hospedagem
  logo: "assets/logo.png"
  theme: "editorial"                # editorial | clean | dark_lux | custom (escolha do cliente)
  accent_override: ""               # opcional: substitui o acento padrão do tema pela cor da marca
  custom_theme:                     # OBRIGATÓRIO apenas quando theme: custom
    references: []                  # links/arquivos de referência enviados pelo cliente
    bg: ""                          # cor de fundo
    surface: ""                     # cor de superfícies/cards (se houver)
    ink: ""                         # cor do texto principal
    ink_soft: ""                    # cor do texto secundário
    accent: ""                      # cor de acento
    font_display: ""                # fonte de títulos (Google Fonts)
    font_body: ""                   # fonte de corpo (Google Fonts)
    photo_treatment: ""             # full_bleed | rounded | framed
    mood: ""                        # 1 frase descrevendo o clima desejado
  badge: ""                         # ex: "Superhost", "Anfitrião de Elite" — omitir se vazio

property:
  type: ""                          # airbnb | pousada | hotel | hostel | flat
  address:
    street: ""
    neighborhood: ""
    city: ""
    state: ""
    zip: ""
  maps_url: ""                      # link Google Maps
  airport:
    name: ""
    address: ""
    taxi_avg_price: ""              # ex: "R$ 80,00"

checkin:
  time: "15:00"
  checkout_time: "11:00"
  reception_hours: ""               # ex: "24/7" — omitir bloco se não houver recepção
  luggage_storage: true
  access_steps:                     # passo a passo de acesso, em PT (traduzir nos blocos i18n)
    pt: ""
    en: ""
    es: ""
  door_code_info: { pt: "", en: "", es: "" }
  vehicle_info: { pt: "", en: "", es: "" }

wifi:
  network: ""
  password: ""

amenities:                          # lista de chaves; ícone e rótulo i18n vêm do dicionário interno
  - single_bed
  - double_bed
  - sofa_bed
  - pool
  - tv
  - wifi
  - gym_24h
  - dining_table
  - washing_machine
  - fridge
  - stove_oven
  - gourmet_area
  - jacuzzi
  - microwave
  - coffee_maker
  - restaurant
amenities_note: { pt: "", en: "", es: "" }

rules:                              # exatamente 4 a 6 regras, cada uma com i18n
  - { pt: "", en: "", es: "" }

extras:
  parking: { pt: "", en: "", es: "" }
  garbage: { pt: "", en: "", es: "" }
  rentals: { pt: "", en: "", es: "" }          # omitir se vazio
  emergency_contact: ""                          # telefone do anfitrião p/ urgências — OBRIGATÓRIO
  emergency_numbers:                             # padrão Brasil; ajustar por país
    - { label: "SAMU", number: "192" }
    - { label: { pt: "Bombeiros", en: "Fire Dept.", es: "Bomberos" }, number: "193" }
    - { label: { pt: "Polícia", en: "Police", es: "Policía" }, number: "190" }

highlights:                         # 2 a 4 destaques do imóvel com foto
  - photo: "assets/rooms/lobby.jpg"
    title: { pt: "", en: "", es: "" }
    text:  { pt: "", en: "", es: "" }

eat:                                # 3 a 6 recomendações
  - name: ""
    photo: "assets/places/x.jpg"
    price: "$$"                     # $, $$ ou $$$
    cuisine: { pt: "", en: "", es: "" }
    address: ""
    tip: { pt: "", en: "", es: "" } # opcional: "dica do anfitrião"

visit:                              # 3 a 5 atrações
  - name: { pt: "", en: "", es: "" }
    photo: "assets/places/y.jpg"
    note: { pt: "", en: "", es: "" }
kids_note: { pt: "", en: "", es: "" }            # omitir se vazio

checkout_checklist:                 # lista i18n; usar padrão abaixo se cliente não alterar
  - { pt: "Confira seus pertences", en: "Pack your belongings", es: "Revise sus pertenencias" }
  - { pt: "Desligue luzes e aparelhos", en: "Turn off lights and appliances", es: "Apague luces y aparatos" }
  - { pt: "Esvazie o lixo", en: "Empty the trash", es: "Vacíe la basura" }
  - { pt: "Feche portas e janelas", en: "Close doors and windows", es: "Cierre puertas y ventanas" }
  - { pt: "Toalhas molhadas no varal", en: "Wet towels on the clothesline", es: "Toallas mojadas en el tendedero" }
  - { pt: "Notifique sua saída", en: "Notify us of your departure", es: "Avísenos de su salida" }

host:
  name: ""
  photo: "assets/host.jpg"
  message: { pt: "", en: "", es: "" }
  whatsapp: "+55..."                # formato E.164
  email: ""
  instagram: ""
  facebook: ""
  review_url: ""                    # link de avaliação (Airbnb/Booking/Google)
```

**Regra de omissão:** qualquer campo vazio/ausente NÃO renderiza bloco vazio — a seção se adapta (ex.: sem jacuzzi, o card não existe; sem `kids_note`, o bloco infantil some). Nunca renderize chave sem valor.

---

## SISTEMA VISUAL — 4 TEMAS (definido por `brand.theme`)

O design NÃO é livre: cada tema é um conjunto fechado de tokens. O template é um só; o tema troca apenas as variáveis CSS e o tratamento de foto. **Proibido em todos os temas:** gradientes decorativos, sombras difusas (drop-shadow), bordas grossas, fontes com contorno, ícones clipart, fotos em moldura circular, efeito gloss. A estética é flat, tipográfica e fotográfica.

### Princípios comuns a todos os temas
- **Fotografia protagonista:** aberturas de seção com foto em destaque (tratamento conforme o tema); texto sobre foto sempre com overlay de contraste (mín. WCAG AA).
- **Tipografia em escala generosa:** título de seção ≥ 28px; eyebrow/label em 11–12px com letter-spacing 0.14–0.22em; corpo 15–16px com line-height 1.6.
- **Divisores:** hairlines de 0.5–1px, nunca cards com sombra empilhados.
- **Navegação (HTML):** bottom nav fixa com 5 itens de ícone de traço fino — Início, Localização, Wi-Fi, Comer & Visitar, Contato. Item ativo na cor de acento. Demais seções são âncoras dentro desses cinco grupos.
- **Navegação (PDF):** a bottom nav vira um sumário tipográfico na 2ª página de cada idioma, com links internos; cada página traz um rodapé discreto com link "← Sumário".
- **Wi-Fi:** página tipográfica — rede em 17–20px, senha em ≥ 36px na fonte display, com botão "copiar" no HTML.
- **Ícones:** um único set de traço fino (stroke 1.5px), monocromático, SVG inline. Nunca misturar sets.
- **Contato:** foto do anfitrião, nome na fonte display em corpo grande (sem fonte script), botões de ação em pill, selo `brand.badge` discreto em label espaçado (sem estrelas clipart).
- `brand.accent_override`, se preenchido, substitui o acento padrão do tema.

### Tema 1 — `editorial` (default: pousadas, Airbnbs de charme, beach houses)
```css
--bg: #F7F1E6;        /* areia clara */
--surface: #FDFBF6;
--ink: #2C2C2A;
--ink-soft: #5F5E5A;
--accent: #B3502D;    /* terracota */
--hairline: #D8D2C4;
```
- Display: **Fraunces** (peso 400–500, alto contraste); Corpo: **Inter**.
- Fotos: **full-bleed** nas aberturas (sangram até a borda), sem border-radius.
- Eyebrows em caixa alta espaçada na cor de acento. Clima: revista de viagem, quente, artesanal.

### Tema 2 — `clean` (apartamentos urbanos, flats, studios, hostels)
```css
--bg: #FFFFFF;
--surface: #F6F7F8;
--ink: #1A1A1A;
--ink-soft: #6B7176;
--accent: #0E8A6B;    /* verde vibrante único */
--hairline: #E6E8EA;
```
- Display e corpo: **Inter** (display em peso 600, tracking levemente negativo).
- Fotos: cantos arredondados 16px, respiro lateral de 20px (estilo app).
- Botões pill cheios no acento. Clima: produto digital, prático, direto — sensação de app nativo.

### Tema 3 — `dark_lux` (hotéis premium, coberturas, alto padrão)
```css
--bg: #1D1C1A;        /* quase preto quente */
--surface: #262522;
--ink: #F1EFE8;       /* off-white */
--ink-soft: #B4B2A9;
--accent: #D6A256;    /* dourado/cobre */
--hairline: #3A3833;
```
- Display: **Fraunces** ou **Cormorant Garamond**; Corpo: **Inter**.
- Fotos com tratamento escuro (overlay 20% preto), composição centralizada e simétrica na capa, filetes de 1px no acento como ornamento único.
- Botões outline (borda fina dourada, sem preenchimento). Clima: hotel de luxo, silencioso, cerimonial.

### Tema 4 — `custom` (personalizado a partir de referências do cliente)
Quando `brand.theme: custom`:
1. Leia `brand.custom_theme.references` (links, prints, manual de marca, perfis que o cliente admira).
2. **Extraia e preencha os tokens** de `custom_theme` (bg, ink, accent, fontes, photo_treatment, mood) ANTES de codar — apresente os tokens extraídos para aprovação interna e registre-os no YAML.
3. As fontes devem existir no Google Fonts; se a referência usar fonte proprietária, escolha a equivalente livre mais próxima e anote a substituição.
4. Os **princípios comuns continuam valendo** (flat, hairlines, bottom nav, hierarquia tipográfica): o custom muda paleta, fontes, tratamento de foto e clima — não a arquitetura nem a qualidade.
5. Se as referências conflitarem entre si ou com legibilidade (ex.: texto claro sobre fundo claro), resolva a favor da legibilidade e documente a decisão.

---

## ESTRUTURA DE SEÇÕES (ordem fixa, por idioma)

1. **Capa** — foto de capa no tratamento do tema, logo, nome da hospedagem na fonte display, seletor de idiomas em pills tipográficas (PT · EN · ES, sem bandeiras clipart). Rodapé: "Criado por OFS Digital" + versão.
1b. **Sumário** (uma por idioma, no PDF) — índice tipográfico das seções com links internos.
2. **Check-in & Check-out** — horários em destaque, guarda-volumes, `access_steps`, `vehicle_info`.
3. **Boas-vindas** — mensagem, horários, `door_code_info`, destaques (`highlights`) com foto no tratamento do tema.
4. **Localização** — endereço completo, imagem estática do mapa + botão/link "Abrir no Google Maps" (`maps_url`), como chegar do aeroporto com preço médio de táxi/Uber.
5. **Wi-Fi** — rede + senha gigantes + frase "Sinta-se em casa!" (i18n).
6. **Comodidades** — grade 4 colunas de ícones com rótulo, vindos de `amenities`; nota de variação.
7. **Regras da casa** — cards numerados 01–06 (numerar só as que existem).
8. **Informações práticas** — estacionamento, lixo, aluguéis, emergências (números grandes + `emergency_contact` clicável no HTML).
9. **Onde comer** — cards alternando foto esquerda/direita, com nome, preço, cozinha, endereço, dica.
10. **Para visitar** — cards de atração + bloco infantil se houver.
11. **Antes de partir** — horário de check-out em destaque + checklist com ícones de check.
12. **Contato** — host completo + pedido de avaliação com link/QR.

No **PDF**, as seções 2–12 se repetem por idioma na ordem de `meta.languages` (estrutura idêntica ao original analisado: capa única + bloco PT + bloco EN + bloco ES).
No **HTML**, usar UMA estrutura com troca de idioma via JS (botões PT/EN/ES fixos no topo) — sem duplicar DOM por idioma; textos trocam via dicionário JS gerado do YAML.

---

## ALVO 1 — HTML MOBILE INTERATIVO

Requisitos técnicos:

- **Arquivo único e offline:** CSS e JS inline, imagens e fontes em base64. Zero requisições externas. Meta `viewport` correto. Deve abrir do WhatsApp/arquivos do celular sem internet.
- **Peso máximo: 8 MB.** Se estourar, reduzir qualidade das fotos (não remover conteúdo).
- Navegação: bottom nav fixa de 5 itens (conforme Sistema Visual); âncoras com scroll suave; botão "voltar ao topo" discreto.
- Troca de idioma instantânea (JS puro, sem framework), persistindo a escolha apenas em memória.
- Botões de ação nativos: `https://wa.me/<numero>` (WhatsApp), `tel:`, `mailto:`, link Maps, link de avaliação.
- Acessibilidade: contraste AA, alvos de toque mínimos de 44px, `alt` em todas as imagens, foco visível.
- Testar em viewport 390×844 (deve funcionar de 320px a 480px sem quebra).

## ALVO 2 — PDF OFFLINE

Requisitos técnicos:

- Renderizar `pdf.html.j2` com Playwright (Chromium), `page.pdf()` com:
  - `width: '540pt'`, `height: '1168.5pt'` (formato vertical mobile idêntico ao benchmark), `printBackground: true`, margens zero.
  - Cada seção = uma página exata. Usar `page-break-after: always` e containers com altura fixa de 1168.5pt + `overflow: hidden`.
- **Links internos clicáveis:** seletor de idiomas da capa → página de sumário de cada idioma; cada item do sumário → página da seção correspondente; rodapé "← Sumário" em cada página → sumário do idioma atual. Implementar com `<a href="#id">` — o Chromium converte âncoras em links internos no PDF automaticamente.
- Links externos (Maps, WhatsApp, avaliação) clicáveis também no PDF; e exibir o dado por extenso ao lado (telefone, endereço), porque no papel/offline o link não funciona.
- Peso máximo: 15 MB. Comprimir imagens antes do render.
- Validar com `pdfinfo` (nº de páginas = 1 capa + 12 × nº de idiomas, sendo 1 sumário + 11 seções por idioma) e abrir 3 páginas rasterizadas para conferência visual.

---

## QA OBRIGATÓRIO (relatório no final do build)

Erros reais encontrados no benchmark de mercado — o pipeline existe para eliminá-los:

1. **Zero placeholders:** grep por `[`, `XXX`, `TODO`, `Lorem` em todo texto renderizado → build falha se encontrar.
2. **Tradução completa:** nenhum bloco EN/ES pode conter texto do dicionário PT (verificar palavras-sentinela: "você", "horário", "acomodação" no bloco EN; idem para ES).
3. **Ortografia:** rodar revisão nos 3 idiomas; relatar termos suspeitos.
4. **Consistência estrutural:** os 3 idiomas têm exatamente as mesmas seções e o mesmo nº de itens em cada lista.
5. **Dados críticos presentes:** wifi.network, wifi.password, checkin.time, checkout_time, host.whatsapp, emergency_contact, address completo.
6. **Links testados:** todos os `wa.me`, `tel:`, `mailto:` e Maps com formato válido; âncoras internas resolvem.
7. **Peso e páginas:** HTML ≤ 8 MB; PDF ≤ 15 MB e contagem de páginas correta.

Saída final esperada: `dist/welcome-book.html`, `dist/welcome-book.pdf` e `dist/qa-report.txt`.

---

## COMO USAR ESTE PROMPT

1. Cole este prompt no Claude Code.
2. Anexe o `welcome-book.yaml` preenchido (gerado a partir do formulário de briefing OFS) e a pasta `assets/` com as fotos do cliente.
3. Peça: "Execute o pipeline completo e me entregue os dois arquivos + relatório de QA."
4. **Builds de variantes de tema** (demos/comparação): ao buildar o mesmo YAML com outro `brand.theme`, sufixe as saídas — `dist/welcome-book-clean.html`, `dist/welcome-book-darklux.html` (e PDFs equivalentes) — preservando o build principal. Para o site-modelo público, cada variante é publicada como `exemplos/<tema>/index.html`.
5. **Operação multi-cliente:** os caminhos `data/`, `assets/` e `dist/` da raiz pertencem ao exemplo de validação (Vento Leste) e nunca são sobrescritos. Cada cliente real vive em `clients/<slug>/` (slug em minúsculas, sem acento, com hífen) contendo `data.yaml`, `assets/` e `dist/` próprios. Quando o pedido indicar um cliente, leia e escreva EXCLUSIVAMENTE dentro da pasta dele — jamais altere arquivos de outros clientes ou da raiz.
