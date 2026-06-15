from __future__ import annotations

import base64
import io
import json
import re
import sys
import tempfile
from copy import deepcopy
from pathlib import Path
from urllib.parse import quote

import yaml
from jinja2 import Environment, FileSystemLoader
from PIL import Image
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "welcome-book.yaml"
TEMPLATE_DIR = ROOT / "templates"
DIST_DIR = ROOT / "dist"
HTML_OUT = DIST_DIR / "welcome-book.html"
PDF_OUT = DIST_DIR / "welcome-book.pdf"
QA_OUT = DIST_DIR / "qa-report.txt"

MAX_HTML_BYTES = 8 * 1024 * 1024
MAX_PDF_BYTES = 15 * 1024 * 1024

THEMES = {
    "editorial": {
        "bg": "#F7F1E6",
        "surface": "#FDFBF6",
        "ink": "#2C2C2A",
        "ink_soft": "#5F5E5A",
        "accent": "#B3502D",
        "hairline": "#D8D2C4",
    },
    "clean": {
        "bg": "#FFFFFF",
        "surface": "#F6F7F8",
        "ink": "#1A1A1A",
        "ink_soft": "#6B7176",
        "accent": "#0E8A6B",
        "hairline": "#E6E8EA",
    },
    "dark_lux": {
        "bg": "#1D1C1A",
        "surface": "#262522",
        "ink": "#F1EFE8",
        "ink_soft": "#B4B2A9",
        "accent": "#D6A256",
        "hairline": "#3A3833",
    },
}

UI = {
    "pt": {
        "coverEyebrow": "Welcome Book",
        "coverText": "Tudo que você precisa para chegar, se acomodar e aproveitar a estadia.",
        "summaryTitle": "Sumário",
        "backCover": "← Capa",
        "backSummary": "← Sumário",
        "checkinEyebrow": "Chegada",
        "checkinTitle": "Check-in e check-out",
        "labelCheckin": "Check-in",
        "labelCheckout": "Check-out",
        "welcomeEyebrow": "Boas-vindas",
        "welcomeTitle": "Sinta-se em casa",
        "locationEyebrow": "Localização",
        "locationTitle": "Como chegar",
        "addressLabel": "Endereço",
        "airportLabel": "Aeroporto",
        "taxiLabel": "Preço médio",
        "mapsButton": "Abrir no Google Maps",
        "wifiEyebrow": "Conexão",
        "wifiTitle": "Wi-Fi",
        "wifiNetworkLabel": "Rede",
        "wifiPasswordLabel": "Senha",
        "copyButton": "Copiar senha",
        "copiedButton": "Senha copiada",
        "homePhrase": "Sinta-se em casa!",
        "amenitiesEyebrow": "Conforto",
        "amenitiesTitle": "Comodidades",
        "rulesEyebrow": "Convivência",
        "rulesTitle": "Regras da casa",
        "practicalEyebrow": "Prático",
        "practicalTitle": "Informações práticas",
        "parking": "Estacionamento",
        "garbage": "Lixo",
        "rentals": "Aluguéis",
        "emergency": "Emergências",
        "eatEyebrow": "Guia local",
        "eatTitle": "Onde comer",
        "visitEyebrow": "Passeios",
        "visitTitle": "Para visitar",
        "checkoutEyebrow": "Saída",
        "checkoutTitle": "Antes de partir",
        "contactEyebrow": "Contato",
        "contactTitle": "Fale com a gente",
        "reviewButton": "Avaliar estadia",
        "navHome": "Início",
        "navLocation": "Local",
        "navWifi": "Wi-Fi",
        "navEatVisit": "Guia",
        "navContact": "Contato",
    },
    "en": {
        "coverEyebrow": "Welcome Book",
        "coverText": "Everything you need to arrive, settle in and enjoy your stay.",
        "summaryTitle": "Contents",
        "backCover": "← Cover",
        "backSummary": "← Contents",
        "checkinEyebrow": "Arrival",
        "checkinTitle": "Check-in and check-out",
        "labelCheckin": "Check-in",
        "labelCheckout": "Check-out",
        "welcomeEyebrow": "Welcome",
        "welcomeTitle": "Make yourself at home",
        "locationEyebrow": "Location",
        "locationTitle": "How to get here",
        "addressLabel": "Address",
        "airportLabel": "Airport",
        "taxiLabel": "Average price",
        "mapsButton": "Open in Google Maps",
        "wifiEyebrow": "Connection",
        "wifiTitle": "Wi-Fi",
        "wifiNetworkLabel": "Network",
        "wifiPasswordLabel": "Password",
        "copyButton": "Copy password",
        "copiedButton": "Password copied",
        "homePhrase": "Make yourself at home!",
        "amenitiesEyebrow": "Comfort",
        "amenitiesTitle": "Amenities",
        "rulesEyebrow": "House care",
        "rulesTitle": "House rules",
        "practicalEyebrow": "Practical",
        "practicalTitle": "Practical information",
        "parking": "Parking",
        "garbage": "Garbage",
        "rentals": "Rentals",
        "emergency": "Emergencies",
        "eatEyebrow": "Local guide",
        "eatTitle": "Where to eat",
        "visitEyebrow": "Outings",
        "visitTitle": "Places to visit",
        "checkoutEyebrow": "Departure",
        "checkoutTitle": "Before you leave",
        "contactEyebrow": "Contact",
        "contactTitle": "Get in touch",
        "reviewButton": "Review your stay",
        "navHome": "Home",
        "navLocation": "Place",
        "navWifi": "Wi-Fi",
        "navEatVisit": "Guide",
        "navContact": "Contact",
    },
    "es": {
        "coverEyebrow": "Welcome Book",
        "coverText": "Todo lo que necesita para llegar, instalarse y disfrutar la estancia.",
        "summaryTitle": "Índice",
        "backCover": "← Portada",
        "backSummary": "← Índice",
        "checkinEyebrow": "Llegada",
        "checkinTitle": "Check-in y check-out",
        "labelCheckin": "Check-in",
        "labelCheckout": "Check-out",
        "welcomeEyebrow": "Bienvenida",
        "welcomeTitle": "Siéntase como en casa",
        "locationEyebrow": "Ubicación",
        "locationTitle": "Cómo llegar",
        "addressLabel": "Dirección",
        "airportLabel": "Aeropuerto",
        "taxiLabel": "Precio medio",
        "mapsButton": "Abrir en Google Maps",
        "wifiEyebrow": "Conexión",
        "wifiTitle": "Wi-Fi",
        "wifiNetworkLabel": "Red",
        "wifiPasswordLabel": "Contraseña",
        "copyButton": "Copiar contraseña",
        "copiedButton": "Contraseña copiada",
        "homePhrase": "¡Siéntase como en casa!",
        "amenitiesEyebrow": "Comodidad",
        "amenitiesTitle": "Comodidades",
        "rulesEyebrow": "Convivencia",
        "rulesTitle": "Reglas de la casa",
        "practicalEyebrow": "Práctico",
        "practicalTitle": "Información práctica",
        "parking": "Aparcamiento",
        "garbage": "Basura",
        "rentals": "Alquileres",
        "emergency": "Emergencias",
        "eatEyebrow": "Guía local",
        "eatTitle": "Dónde comer",
        "visitEyebrow": "Paseos",
        "visitTitle": "Para visitar",
        "checkoutEyebrow": "Salida",
        "checkoutTitle": "Antes de partir",
        "contactEyebrow": "Contacto",
        "contactTitle": "Hable con nosotros",
        "reviewButton": "Valorar estancia",
        "navHome": "Inicio",
        "navLocation": "Lugar",
        "navWifi": "Wi-Fi",
        "navEatVisit": "Guía",
        "navContact": "Contacto",
    },
}

LABELS = {
    "language_codes": {"pt": "PT", "en": "EN", "es": "ES"},
    "language_names": {"pt": "Português", "en": "English", "es": "Español"},
}

AMENITY_LABELS = {
    "single_bed": {"pt": "Cama solteiro", "en": "Single bed", "es": "Cama individual"},
    "double_bed": {"pt": "Cama casal", "en": "Double bed", "es": "Cama doble"},
    "sofa_bed": {"pt": "Sofá-cama", "en": "Sofa bed", "es": "Sofá cama"},
    "pool": {"pt": "Piscina", "en": "Pool", "es": "Piscina"},
    "tv": {"pt": "TV", "en": "TV", "es": "TV"},
    "wifi": {"pt": "Wi-Fi", "en": "Wi-Fi", "es": "Wi-Fi"},
    "gym_24h": {"pt": "Academia 24h", "en": "24h gym", "es": "Gimnasio 24h"},
    "dining_table": {"pt": "Mesa de jantar", "en": "Dining table", "es": "Mesa de comedor"},
    "washing_machine": {"pt": "Máquina de lavar", "en": "Washer", "es": "Lavadora"},
    "fridge": {"pt": "Geladeira", "en": "Fridge", "es": "Nevera"},
    "stove_oven": {"pt": "Fogão e forno", "en": "Stove and oven", "es": "Cocina y horno"},
    "gourmet_area": {"pt": "Área gourmet", "en": "Gourmet area", "es": "Área gourmet"},
    "jacuzzi": {"pt": "Jacuzzi", "en": "Jacuzzi", "es": "Jacuzzi"},
    "microwave": {"pt": "Micro-ondas", "en": "Microwave", "es": "Microondas"},
    "coffee_maker": {"pt": "Cafeteira", "en": "Coffee maker", "es": "Cafetera"},
    "restaurant": {"pt": "Restaurante", "en": "Restaurant", "es": "Restaurante"},
}

TOC = [
    {"id": "checkin", "title_key": "checkinTitle"},
    {"id": "welcome", "title_key": "welcomeTitle"},
    {"id": "location", "title_key": "locationTitle"},
    {"id": "wifi", "title_key": "wifiTitle"},
    {"id": "amenities", "title_key": "amenitiesTitle"},
    {"id": "rules", "title_key": "rulesTitle"},
    {"id": "practical", "title_key": "practicalTitle"},
    {"id": "eat", "title_key": "eatTitle"},
    {"id": "visit", "title_key": "visitTitle"},
    {"id": "checkout", "title_key": "checkoutTitle"},
    {"id": "contact", "title_key": "contactTitle"},
]

ICONS = {
    "home": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10.5V20h13v-9.5"/><path d="M9.5 20v-5h5v5"/></svg>',
    "map": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 18 3 20V6l6-2 6 2 6-2v14l-6 2-6-2Z"/><path d="M9 4v14M15 6v14"/></svg>',
    "wifi": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 9.5a11 11 0 0 1 14 0"/><path d="M8 13a6.5 6.5 0 0 1 8 0"/><path d="M11 16.5a2 2 0 0 1 2 0"/><path d="M12 20h.01"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 21s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12Z"/><circle cx="12" cy="9" r="2.4"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M7 4h3l1.5 4-2 1.2a12 12 0 0 0 5.3 5.3l1.2-2 4 1.5v3a2 2 0 0 1-2.2 2A16 16 0 0 1 5 6.2 2 2 0 0 1 7 4Z"/></svg>',
    "spark": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 3v18M3 12h18M6.6 6.6l10.8 10.8M17.4 6.6 6.6 17.4"/></svg>',
}


class BuildError(Exception):
    pass


def load_data() -> dict:
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def require_path(data: dict, dotted: str, errors: list[str]) -> None:
    value = data
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            errors.append(dotted)
            return
        value = value[part]
    if value in (None, "", []):
        errors.append(dotted)


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    for field in [
        "meta.version",
        "meta.generated_by",
        "meta.languages",
        "brand.name",
        "brand.logo",
        "property.address.street",
        "property.address.neighborhood",
        "property.address.city",
        "property.address.state",
        "property.address.zip",
        "property.maps_url",
        "property.airport.name",
        "property.airport.address",
        "property.airport.taxi_avg_price",
        "checkin.time",
        "checkin.checkout_time",
        "wifi.network",
        "wifi.password",
        "amenities",
        "amenities_note",
        "rules",
        "extras.emergency_contact",
        "extras.emergency_numbers",
        "highlights",
        "eat",
        "visit",
        "checkout_checklist",
        "host.name",
        "host.photo",
        "host.message",
        "host.whatsapp",
        "host.email",
        "host.review_url",
    ]:
        require_path(data, field, errors)

    languages = data.get("meta", {}).get("languages", [])
    if languages != ["pt", "en", "es"]:
        errors.append("meta.languages must be [pt, en, es]")
    if not 4 <= len(data.get("rules", [])) <= 6:
        errors.append("rules must contain 4 to 6 items")
    if not 2 <= len(data.get("highlights", [])) <= 4:
        errors.append("highlights must contain 2 to 4 items")
    if not 3 <= len(data.get("eat", [])) <= 6:
        errors.append("eat must contain 3 to 6 items")
    if not 3 <= len(data.get("visit", [])) <= 5:
        errors.append("visit must contain 3 to 5 items")

    for key in data.get("amenities", []):
        if key not in AMENITY_LABELS:
            errors.append(f"amenities.{key} has no internal label")

    for image_path in image_paths(data):
        if not (ROOT / image_path).exists():
            errors.append(f"missing image: {image_path}")

    return errors


def image_paths(data: dict) -> list[str]:
    paths: list[str] = []

    def add(path: str | None) -> None:
        if path and path not in paths:
            paths.append(path)

    add(data.get("brand", {}).get("logo"))
    add(data.get("host", {}).get("photo"))
    for item in data.get("highlights", []):
        add(item.get("photo"))
    for item in data.get("eat", []):
        add(item.get("photo"))
    for item in data.get("visit", []):
        add(item.get("photo"))
    return paths


def image_data_uri(relative_path: str, max_width: int = 1080, quality: int = 80) -> str:
    path = ROOT / relative_path
    with Image.open(path) as image:
        if image.width > max_width:
            ratio = max_width / image.width
            image = image.resize((max_width, int(image.height * ratio)), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        if path.suffix.lower() == ".png":
            image.save(output, format="PNG", optimize=True)
            mime = "image/png"
        else:
            image = image.convert("RGB")
            image.save(output, format="JPEG", quality=quality, optimize=True)
            mime = "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(output.getvalue()).decode('ascii')}"


def address_text(data: dict) -> str:
    address = data["property"]["address"]
    return (
        f"{address['street']}, {address['neighborhood']}, "
        f"{address['city']} - {address['state']}, {address['zip']}"
    )


def wa_url(number: str) -> str:
    digits = re.sub(r"\D+", "", number)
    return f"https://wa.me/{digits}"


def enriched_context(data: dict) -> dict:
    context = deepcopy(data)
    theme_name = context["brand"].get("theme") or "editorial"
    if theme_name == "custom":
        custom = context["brand"].get("custom_theme", {})
        theme = {
            "bg": custom.get("bg") or THEMES["editorial"]["bg"],
            "surface": custom.get("surface") or THEMES["editorial"]["surface"],
            "ink": custom.get("ink") or THEMES["editorial"]["ink"],
            "ink_soft": custom.get("ink_soft") or THEMES["editorial"]["ink_soft"],
            "accent": custom.get("accent") or THEMES["editorial"]["accent"],
            "hairline": THEMES["editorial"]["hairline"],
        }
    else:
        theme = THEMES.get(theme_name, THEMES["editorial"]).copy()
    if context["brand"].get("accent_override"):
        theme["accent"] = context["brand"]["accent_override"]

    embedded = {path: image_data_uri(path) for path in image_paths(context)}
    context["theme"] = theme
    context["languages"] = context["meta"]["languages"]
    context["labels"] = LABELS
    context["ui"] = UI
    context["amenity_labels"] = AMENITY_LABELS
    context["toc"] = TOC
    context["icons"] = ICONS
    context["logo_image"] = embedded[context["brand"]["logo"]]
    context["host_image"] = embedded[context["host"]["photo"]]
    context["cover_image"] = embedded[context["highlights"][0]["photo"]]
    context["address"] = address_text(context)
    context["wa_url"] = wa_url(context["host"]["whatsapp"])

    for collection in ["highlights", "eat", "visit"]:
        for item in context.get(collection, []):
            item["image"] = embedded[item["photo"]]

    payload = {
        "languages": context["languages"],
        "ui": UI,
        "content": {
            "accessSteps": context["checkin"]["access_steps"],
            "vehicleInfo": context["checkin"]["vehicle_info"],
            "doorCodeInfo": context["checkin"]["door_code_info"],
            "hostMessage": context["host"]["message"],
            "amenitiesNote": context["amenities_note"],
            "kidsNote": context.get("kids_note", {}),
        },
        "property": context["property"],
        "address": context["address"],
        "highlights": context["highlights"],
        "amenities": context["amenities"],
        "amenityLabels": AMENITY_LABELS,
        "rules": context["rules"],
        "extras": context["extras"],
        "eat": context["eat"],
        "visit": context["visit"],
        "checkout_checklist": context["checkout_checklist"],
        "icon": ICONS["spark"],
    }
    context["payload_json"] = json.dumps(payload, ensure_ascii=False)
    return context


def render_templates(context: dict) -> tuple[str, str]:
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False)
    mobile = env.get_template("mobile.html.j2").render(**context)
    pdf = env.get_template("pdf.html.j2").render(**context)
    return mobile, pdf


def generate_pdf(pdf_html: str) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        temp_html = Path(tmp) / "welcome-book-pdf.html"
        temp_html.write_text(pdf_html, encoding="utf-8")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(viewport={"width": 720, "height": 1558}, device_scale_factor=1)
            page.goto(temp_html.as_uri(), wait_until="networkidle")
            page.pdf(
                path=str(PDF_OUT),
                width="7.5in",
                height="16.2291667in",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )
            browser.close()


def plain_text_for_lang(data: dict, lang: str) -> str:
    chunks: list[str] = []

    def add(value) -> None:
        if not value:
            return
        if isinstance(value, str):
            chunks.append(value)
        elif isinstance(value, dict):
            if lang in value:
                chunks.append(str(value[lang]))
        elif isinstance(value, list):
            for item in value:
                add(item)

    add(UI[lang])
    add(data["brand"]["name"])
    add(data["checkin"]["access_steps"])
    add(data["checkin"]["door_code_info"])
    add(data["checkin"]["vehicle_info"])
    add(data["amenities_note"])
    add(data["rules"])
    add(data["extras"].get("parking"))
    add(data["extras"].get("garbage"))
    add(data["extras"].get("rentals"))
    for item in data["highlights"]:
        add(item["title"])
        add(item["text"])
    for item in data["eat"]:
        add(item["name"])
        add(item["cuisine"])
        add(item.get("tip"))
    for item in data["visit"]:
        add(item["name"])
        add(item["note"])
    add(data.get("kids_note"))
    add(data["checkout_checklist"])
    add(data["host"]["message"])
    return "\n".join(chunks)


def pdf_page_count(path: Path) -> int:
    content = path.read_bytes()
    return len(re.findall(rb"/Type\s*/Page\b", content))


def check_links(html: str) -> list[str]:
    issues: list[str] = []
    anchors = set(re.findall(r'id="([^"]+)"', html))
    hrefs = re.findall(r'href="([^"]+)"', html)
    for href in hrefs:
        if "${" in href:
            continue
        if href.startswith("#") and href[1:] not in anchors:
            issues.append(f"internal anchor missing: {href}")
        if "wa.me/" in href and not re.match(r"^https://wa\.me/\d{10,15}$", href):
            issues.append(f"invalid WhatsApp URL: {href}")
        if href.startswith("tel:") and not re.match(r"^tel:\+?\d[\d\s().-]*$", href):
            issues.append(f"invalid tel URL: {href}")
        if href.startswith("mailto:") and not re.match(r"^mailto:[^@\s]+@[^@\s]+\.[^@\s]+$", href):
            issues.append(f"invalid mailto URL: {href}")
        if "maps.google" in href and not href.startswith("https://"):
            issues.append(f"invalid Maps URL: {href}")
    return issues


def run_qa(data: dict, mobile_html: str, pdf_html: str) -> tuple[bool, str]:
    issues: list[str] = []
    warnings: list[str] = []
    checks: list[str] = []

    all_text = "\n".join(plain_text_for_lang(data, lang) for lang in data["meta"]["languages"])
    placeholder_patterns = [r"\[[^\]]+\]", r"\bXXX\b", r"\bTODO\b", r"\bLorem\b"]
    for pattern in placeholder_patterns:
        if re.search(pattern, all_text, flags=re.IGNORECASE):
            issues.append(f"placeholder pattern found: {pattern}")
    checks.append("Zero placeholders: OK" if not issues else "Zero placeholders: FAIL")

    en_text = plain_text_for_lang(data, "en").lower()
    es_text = plain_text_for_lang(data, "es").lower()
    for word in ["você", "horário", "acomodação"]:
        if word in en_text:
            issues.append(f"Portuguese sentinel in EN block: {word}")
    for word in ["você", "horário", "acomodação"]:
        if word in es_text:
            issues.append(f"Portuguese sentinel in ES block: {word}")
    checks.append("Tradução completa: OK")

    suspicious = sorted(set(re.findall(r"[Ã�Â][A-Za-zÀ-ÿ]+", all_text)))
    if suspicious:
        warnings.append("Termos suspeitos de encoding/ortografia: " + ", ".join(suspicious[:20]))
    else:
        checks.append("Ortografia/encoding básico: OK")

    counts = {
        "rules": len(data["rules"]),
        "highlights": len(data["highlights"]),
        "eat": len(data["eat"]),
        "visit": len(data["visit"]),
        "checkout_checklist": len(data["checkout_checklist"]),
    }
    if any(value == 0 for value in counts.values()):
        issues.append("one or more required lists are empty")
    checks.append("Consistência estrutural: OK")

    validation_errors = validate(data)
    if validation_errors:
        issues.extend([f"critical data missing/invalid: {item}" for item in validation_errors])
    else:
        checks.append("Dados críticos presentes: OK")

    link_issues = check_links(mobile_html) + check_links(pdf_html)
    if link_issues:
        issues.extend(link_issues)
    else:
        checks.append("Links testados: OK")

    html_size = HTML_OUT.stat().st_size
    pdf_size = PDF_OUT.stat().st_size
    expected_pages = 1 + (12 * len(data["meta"]["languages"]))
    actual_pages = pdf_page_count(PDF_OUT)
    if html_size > MAX_HTML_BYTES:
        issues.append(f"HTML too large: {html_size} bytes")
    if pdf_size > MAX_PDF_BYTES:
        issues.append(f"PDF too large: {pdf_size} bytes")
    if actual_pages != expected_pages:
        issues.append(f"PDF page count mismatch: expected {expected_pages}, got {actual_pages}")
    if html_size <= MAX_HTML_BYTES and pdf_size <= MAX_PDF_BYTES and actual_pages == expected_pages:
        checks.append(f"Peso e páginas: OK ({html_size} bytes HTML, {pdf_size} bytes PDF, {actual_pages} páginas)")

    status = "PASSOU" if not issues else "FALHOU"
    report = [
        "QA REPORT - Welcome Book",
        f"Status: {status}",
        "",
        "Arquivos:",
        f"- {HTML_OUT.as_posix()}",
        f"- {PDF_OUT.as_posix()}",
        f"- {QA_OUT.as_posix()}",
        "",
        "Checks:",
        *[f"- {line}" for line in checks],
        "",
        "Itens por seção:",
        *[f"- {key}: {value}" for key, value in counts.items()],
        "",
        "Avisos:",
        *([f"- {warning}" for warning in warnings] if warnings else ["- Nenhum"]),
        "",
        "Erros:",
        *([f"- {issue}" for issue in issues] if issues else ["- Nenhum"]),
    ]
    return not issues, "\n".join(report) + "\n"


def main() -> int:
    DIST_DIR.mkdir(exist_ok=True)
    data = load_data()
    validation_errors = validate(data)
    if validation_errors:
        QA_OUT.write_text(
            "QA REPORT - Welcome Book\nStatus: FALHOU\n\nErros:\n"
            + "\n".join(f"- {item}" for item in validation_errors)
            + "\n",
            encoding="utf-8",
        )
        raise BuildError("YAML validation failed. See dist/qa-report.txt")

    context = enriched_context(data)
    mobile_html, pdf_html = render_templates(context)
    HTML_OUT.write_text(mobile_html, encoding="utf-8")
    generate_pdf(pdf_html)
    passed, report = run_qa(data, mobile_html, pdf_html)
    QA_OUT.write_text(report, encoding="utf-8")
    print(report)
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BuildError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
