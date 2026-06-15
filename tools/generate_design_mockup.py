from __future__ import annotations

import base64
import html
from pathlib import Path

import yaml
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "welcome-book.yaml"
DIST = ROOT / "dist"
OUT = DIST / "design-mockup.html"


def data_uri(path: str) -> str:
    file_path = ROOT / path
    mime = "image/png" if file_path.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(file_path.read_bytes()).decode('ascii')}"


def img_size(path: str) -> tuple[int, int]:
    with Image.open(ROOT / path) as image:
        return image.size


def e(value: object) -> str:
    return html.escape(str(value), quote=True)


def icon(name: str) -> str:
    icons = {
        "home": '<svg viewBox="0 0 24 24"><path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10.5V20h13v-9.5"/><path d="M9.5 20v-5h5v5"/></svg>',
        "key": '<svg viewBox="0 0 24 24"><circle cx="8" cy="12" r="4"/><path d="M12 12h9"/><path d="M17 12v3"/><path d="M20 12v2"/></svg>',
        "wifi": '<svg viewBox="0 0 24 24"><path d="M5 9.5a11 11 0 0 1 14 0"/><path d="M8 13a6.5 6.5 0 0 1 8 0"/><path d="M11 16.5a2 2 0 0 1 2 0"/><path d="M12 20h.01"/></svg>',
        "pin": '<svg viewBox="0 0 24 24"><path d="M12 21s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12Z"/><circle cx="12" cy="9" r="2.4"/></svg>',
        "phone": '<svg viewBox="0 0 24 24"><path d="M7 4h3l1.5 4-2 1.2a12 12 0 0 0 5.3 5.3l1.2-2 4 1.5v3a2 2 0 0 1-2.2 2A16 16 0 0 1 5 6.2 2 2 0 0 1 7 4Z"/></svg>',
        "copy": '<svg viewBox="0 0 24 24"><rect x="8" y="8" width="11" height="11" rx="2"/><path d="M5 15V6a1 1 0 0 1 1-1h9"/></svg>',
    }
    return icons[name]


def place_card(item: dict, label: str) -> str:
    image = data_uri(item["photo"])
    title = item.get("name")
    if isinstance(title, dict):
        title = title["pt"]
    subtitle = item.get("cuisine", {}).get("pt") or item.get("note", {}).get("pt") or ""
    meta = item.get("price") or "Passeio"
    return f"""
      <article class="place-card">
        <div class="photo-wrap"><img src="{image}" alt="{e(title)}"></div>
        <div class="place-copy">
          <span>{e(label)}</span>
          <h3>{e(title)}</h3>
          <p>{e(meta)} · {e(subtitle)}</p>
        </div>
      </article>
    """


def main() -> None:
    DIST.mkdir(exist_ok=True)
    data = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    brand = data["brand"]
    checkin = data["checkin"]
    wifi = data["wifi"]
    host = data["host"]
    property_data = data["property"]
    cover = data["highlights"][0]["photo"]
    cover_w, cover_h = img_size(cover)
    place_items = data["eat"][:2] + data["visit"][:2]
    address = property_data["address"]
    address_text = f"{address['street']}, {address['neighborhood']} · {address['city']} - {address['state']}"
    whatsapp_digits = "".join(ch for ch in host["whatsapp"] if ch.isdigit())

    html_out = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Design Mockup · {e(brand['name'])}</title>
  <style>
    :root {{
      --sand: #f5ead8;
      --paper: #fffaf1;
      --ink: #201f1b;
      --muted: #736b60;
      --terracotta: #b6502d;
      --petrol: #0f4f5f;
      --sage: #667b5b;
      --line: rgba(54, 45, 34, .16);
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background:
        linear-gradient(90deg, rgba(15,79,95,.05) 0 1px, transparent 1px 100%),
        var(--sand);
      background-size: 28px 28px;
      color: var(--ink);
      font-family: Inter, "Segoe UI", Arial, sans-serif;
      line-height: 1.5;
    }}
    a {{ color: inherit; }}
    img {{ display: block; max-width: 100%; }}
    .phone {{
      width: min(100%, 430px);
      min-height: 100svh;
      margin: 0 auto;
      background: var(--sand);
      padding-bottom: 96px;
      position: relative;
    }}
    .topbar {{
      position: sticky;
      top: 0;
      z-index: 10;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      padding: 14px 18px;
      background: rgba(245,234,216,.82);
      border-bottom: 1px solid var(--line);
      backdrop-filter: blur(18px);
    }}
    .brand {{
      min-width: 0;
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 800;
    }}
    .brand img {{
      width: 38px;
      height: 38px;
      object-fit: contain;
      border-radius: 12px;
      background: var(--terracotta);
    }}
    .brand span {{
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }}
    .lang {{
      display: flex;
      gap: 6px;
    }}
    .lang button {{
      width: 38px;
      height: 38px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: rgba(255,250,241,.7);
      color: var(--ink);
      font-weight: 900;
      letter-spacing: .08em;
    }}
    .lang button:first-child {{
      background: var(--petrol);
      border-color: var(--petrol);
      color: #fff;
    }}
    .hero {{
      min-height: calc(100svh - 68px);
      display: grid;
      align-content: end;
      padding: 0 22px 118px;
      background: var(--petrol);
      color: #fff;
    }}
    .hero-visual {{
      height: min(30svh, 260px);
      display: grid;
      place-items: center;
      margin: 0 -22px 28px;
      background: #0b4351;
      border-bottom: 1px solid rgba(255,255,255,.14);
      overflow: hidden;
    }}
    .hero-visual img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      opacity: .86;
    }}
    .eyebrow {{
      display: block;
      margin-bottom: 10px;
      color: var(--terracotta);
      font-size: 11px;
      font-weight: 900;
      letter-spacing: .2em;
      text-transform: uppercase;
    }}
    .hero .eyebrow {{ color: #ffd7bd; }}
    h1, h2, h3 {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      font-weight: 500;
      letter-spacing: 0;
      line-height: 1.02;
    }}
    h1 {{
      max-width: 7.8ch;
      font-size: clamp(46px, 14vw, 64px);
    }}
    h2 {{
      margin-bottom: 18px;
      font-size: 36px;
    }}
    h3 {{ font-size: 24px; }}
    p {{ margin: 0; }}
    .hero p {{
      max-width: 31ch;
      margin-top: 14px;
      font-size: 16px;
    }}
    .hero-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 9px;
      margin-top: 16px;
    }}
    .chip {{
      min-height: 36px;
      display: inline-flex;
      align-items: center;
      border: 1px solid rgba(255,255,255,.38);
      border-radius: 999px;
      padding: 8px 12px;
      background: rgba(255,255,255,.1);
      backdrop-filter: blur(12px);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: .05em;
      text-transform: uppercase;
    }}
    section {{
      padding: 34px 20px;
      scroll-margin-top: 76px;
    }}
    .panel {{
      border: 1px solid var(--line);
      border-radius: 24px;
      background: rgba(255,250,241,.82);
      overflow: hidden;
    }}
    .check-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 14px;
    }}
    .time {{
      min-height: 118px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 22px;
      background: var(--paper);
    }}
    .time small {{
      display: block;
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      letter-spacing: .14em;
      text-transform: uppercase;
    }}
    .time strong {{
      display: block;
      margin-top: 10px;
      color: var(--petrol);
      font-family: Georgia, "Times New Roman", serif;
      font-size: 38px;
      line-height: 1;
    }}
    .note {{
      padding: 17px;
      color: var(--muted);
      border-top: 1px solid var(--line);
      background: rgba(255,255,255,.32);
    }}
    .wifi-card {{
      padding: 24px 18px;
      border-radius: 28px;
      background: var(--petrol);
      color: #fff;
      text-align: center;
      overflow: hidden;
      position: relative;
    }}
    .wifi-card::before {{
      content: "";
      position: absolute;
      inset: auto -80px -110px auto;
      width: 230px;
      height: 230px;
      border: 1px solid rgba(255,255,255,.22);
      border-radius: 50%;
    }}
    .wifi-card small {{
      color: #b9d7d7;
      font-weight: 900;
      letter-spacing: .16em;
      text-transform: uppercase;
    }}
    .wifi-card .network {{
      margin-top: 8px;
      font-size: 18px;
      font-weight: 800;
    }}
    .wifi-card .password {{
      margin: 16px 0 18px;
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(40px, 12vw, 52px);
      line-height: .96;
      overflow-wrap: anywhere;
    }}
    .copy-btn, .contact-btn {{
      min-height: 48px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      border: 0;
      border-radius: 999px;
      padding: 12px 18px;
      background: #fff;
      color: var(--petrol);
      font-weight: 900;
      text-decoration: none;
    }}
    .copy-btn svg, .contact-btn svg {{
      width: 20px;
      height: 20px;
      fill: none;
      stroke: currentColor;
      stroke-width: 1.6;
      stroke-linecap: round;
      stroke-linejoin: round;
    }}
    .rail {{
      display: flex;
      gap: 14px;
      margin: 0 -20px;
      padding: 2px 20px 4px;
      overflow-x: auto;
      scroll-snap-type: x mandatory;
    }}
    .place-card {{
      flex: 0 0 78%;
      scroll-snap-align: center;
      border: 1px solid var(--line);
      border-radius: 24px;
      background: var(--paper);
      overflow: hidden;
    }}
    .photo-wrap {{
      height: 176px;
      display: grid;
      place-items: center;
      background: #efe4d2;
      border-bottom: 1px solid var(--line);
    }}
    .photo-wrap img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
    }}
    .place-copy {{
      padding: 16px;
    }}
    .place-copy span {{
      color: var(--terracotta);
      font-size: 11px;
      font-weight: 900;
      letter-spacing: .16em;
      text-transform: uppercase;
    }}
    .place-copy p {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 14px;
    }}
    .host-card {{
      display: grid;
      grid-template-columns: 92px 1fr;
      gap: 16px;
      align-items: center;
      padding: 16px;
      border-radius: 28px;
      background: var(--paper);
      border: 1px solid var(--line);
    }}
    .host-card img {{
      width: 92px;
      height: 92px;
      object-fit: contain;
      border-radius: 22px;
      background: #eadcc7;
      border: 1px solid var(--line);
    }}
    .host-card p {{
      margin-top: 7px;
      color: var(--muted);
      font-size: 14px;
    }}
    .contact-actions {{
      display: flex;
      gap: 9px;
      margin-top: 16px;
      overflow-x: auto;
      padding-bottom: 3px;
    }}
    .contact-btn {{
      flex: 0 0 auto;
      background: var(--terracotta);
      color: #fff;
    }}
    .bottom-nav {{
      position: fixed;
      left: 50%;
      bottom: 12px;
      z-index: 20;
      width: min(calc(100% - 24px), 406px);
      transform: translateX(-50%);
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 2px;
      padding: 9px;
      border: 1px solid rgba(255,255,255,.58);
      border-radius: 28px;
      background: rgba(255,250,241,.78);
      backdrop-filter: blur(22px);
    }}
    .bottom-nav a {{
      min-height: 54px;
      display: grid;
      place-items: center;
      align-content: center;
      gap: 3px;
      color: var(--muted);
      font-size: 10px;
      text-decoration: none;
    }}
    .bottom-nav a:first-child {{
      color: var(--petrol);
      background: rgba(15,79,95,.08);
      border-radius: 20px;
    }}
    svg {{
      width: 22px;
      height: 22px;
      fill: none;
      stroke: currentColor;
      stroke-width: 1.5;
      stroke-linecap: round;
      stroke-linejoin: round;
    }}
    @media (max-width: 360px) {{
      .check-grid {{ grid-template-columns: 1fr; }}
      .place-card {{ flex-basis: 86%; }}
      .hero {{ min-height: calc(100svh - 68px); }}
      .host-card {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="phone">
    <header class="topbar">
      <div class="brand">
        <img src="{data_uri(brand['logo'])}" alt="{e(brand['name'])}">
        <span>{e(brand['name'])}</span>
      </div>
      <div class="lang" aria-label="Idiomas"><button>PT</button><button>EN</button><button>ES</button></div>
    </header>

    <main>
      <section class="hero" id="inicio" aria-label="Capa">
        <div>
          <div class="hero-visual"><img src="{data_uri(cover)}" alt="{e(data['highlights'][0]['title']['pt'])}"></div>
          <span class="eyebrow">Welcome Book</span>
          <h1>{e(brand['name'])}</h1>
          <p>Um guia mobile para chegar, conectar, explorar Jeri e falar com a pousada sem fricção.</p>
          <div class="hero-meta">
            <span class="chip">{e(brand.get('badge', ''))}</span>
            <span class="chip">{e(address['city'])}, {e(address['state'])}</span>
          </div>
        </div>
      </section>

      <section id="checkin">
        <span class="eyebrow">Chegada</span>
        <h2>Check-in sem ansiedade</h2>
        <div class="check-grid">
          <div class="time"><small>Entrada</small><strong>{e(checkin['time'])}</strong></div>
          <div class="time"><small>Saída</small><strong>{e(checkin['checkout_time'])}</strong></div>
        </div>
        <article class="panel">
          <p class="note">{e(checkin['access_steps']['pt'])}</p>
          <p class="note">{e(address_text)}</p>
        </article>
      </section>

      <section id="wifi">
        <span class="eyebrow">Conexão rápida</span>
        <h2>Wi-Fi em destaque</h2>
        <article class="wifi-card">
          <small>Rede</small>
          <p class="network">{e(wifi['network'])}</p>
          <p class="password">{e(wifi['password'])}</p>
          <button class="copy-btn" type="button" onclick="navigator.clipboard && navigator.clipboard.writeText('{e(wifi['password'])}'); this.textContent='Senha copiada'">{icon('copy')} Copiar senha</button>
        </article>
      </section>

      <section id="guia">
        <span class="eyebrow">Guia local</span>
        <h2>Dicas para aproveitar</h2>
        <div class="rail">
          {''.join(place_card(item, 'Comer' if index < 2 else 'Visitar') for index, item in enumerate(place_items))}
        </div>
      </section>

      <section id="contato">
        <span class="eyebrow">Contato</span>
        <h2>Fale com a gente</h2>
        <article class="host-card">
          <img src="{data_uri(host['photo'])}" alt="{e(host['name'])}">
          <div>
            <h3>{e(host['name'])}</h3>
            <p>{e(host['message']['pt'])}</p>
          </div>
        </article>
        <div class="contact-actions">
          <a class="contact-btn" href="https://wa.me/{whatsapp_digits}">{icon('phone')} WhatsApp</a>
          <a class="contact-btn" href="mailto:{e(host['email'])}">Email</a>
          <a class="contact-btn" href="{e(property_data['maps_url'])}">{icon('pin')} Maps</a>
        </div>
      </section>
    </main>

    <nav class="bottom-nav" aria-label="Navegação">
      <a href="#inicio">{icon('home')}<span>Início</span></a>
      <a href="#checkin">{icon('key')}<span>Check-in</span></a>
      <a href="#wifi">{icon('wifi')}<span>Wi-Fi</span></a>
      <a href="#guia">{icon('pin')}<span>Guia</span></a>
      <a href="#contato">{icon('phone')}<span>Contato</span></a>
    </nav>
  </div>
</body>
</html>
"""
    OUT.write_text(html_out, encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
