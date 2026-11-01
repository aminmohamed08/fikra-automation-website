#!/usr/bin/env python3
"""
Splits the current bilingual index.html into two static entry points:

    dist/index.html      French  (https://app.fikra-automation.com/)
    dist/ar/index.html   Arabic  (https://app.fikra-automation.com/ar/)

Usage:  python3 split_languages.py [path/to/index.html] [output_dir]

Safety: every edit must match EXACTLY ONE place in the source. If anything
differs from the expected text, the script aborts and writes nothing.
The JavaScript logic, Supabase code, modals and CSS are not rewritten; only
the small, listed spots are changed.
"""
import html as htmllib
import pathlib
import re
import sys

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "index.html")
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "dist")
BASE = "https://app.fikra-automation.com"
SRC_TEXT = SRC.read_text(encoding="utf-8")


def die(msg):
    sys.exit("ABORT (nothing written): " + msg)


def sub1(pattern, repl, text, label=""):
    new, n = re.subn(pattern, lambda m: repl, text)
    if n != 1:
        die(f"expected 1 match for {label or pattern}, found {n}")
    return new


def repn(old, new, text, n=1, label=""):
    found = text.count(old)
    if found != n:
        die(f"expected {n} match(es) for {label or old!r}, found {found}")
    return text.replace(old, new)


# ---------------------------------------------------------------- Arabic strings read from the page's own I18N block
m = re.search(r"\n\s*ar: \{\s*docTitle", SRC_TEXT)
if not m:
    die("could not locate the Arabic I18N block")
AR_BLOCK = SRC_TEXT[m.start():]


def ar_text(key):
    mm = re.search(r"\b%s: '((?:[^'\\]|\\.)*)'" % re.escape(key), AR_BLOCK)
    if not mm:
        die(f"Arabic text for '{key}' not found in I18N.ar")
    return mm.group(1).replace("\\'", "'")


STATIC_KEYS = [
    "skipLink", "heroBadge", "heroTitle", "heroIntro", "heroCta", "heroCta2",
    "servicesTitle", "servicesSub", "faqTitle", "faqSub", "cvTitle", "cvSub", "cvDownload",
    "requestTitle", "requestSub", "contactTitle", "contactSub",
]

CFG = {
    "fr": dict(
        code="fr", dir="ltr", url=BASE + "/",
        title="Fikra Automation | فكرة أتمتة – Automatisation de tâches et de processus au Maroc",
        desc="Fikra Automation digitalise votre café ou restaurant : menus QR intelligents, avis Google automatisés et workflows n8n. Demandez un devis gratuit.",
        locale="fr_FR", alt_locale="ar_MA",
        hreflang=[("fr", BASE + "/"), ("ar", BASE + "/ar/"), ("x-default", BASE + "/")],
    ),
    "ar": dict(
        code="ar", dir="rtl", url=BASE + "/ar/",
        title="فكرة أتمتة | Fikra Automation – أتمتة الأعمال والمهام في المغرب",
        desc="فكرة أتمتة: قوائم QR ذكية، وجمع تقييمات Google تلقائياً، وأتمتة n8n مخصصة لمطعمك أو مقهاك أو محلك. طور نشاطك بكل ثقة واطلب استشارتك المجانية اليوم.",
        locale="ar_MA", alt_locale="fr_FR",
        hreflang=[("ar", BASE + "/ar/"), ("fr", BASE + "/"), ("x-default", BASE + "/")],
    ),
}


def build(cfg):
    h = SRC_TEXT
    code = cfg["code"]
    q = lambda s: htmllib.escape(s, quote=True)

    # ---------- <head>: language, title, descriptions, canonical, hreflang, Open Graph, Twitter
    h = sub1(r'<html lang="fr" dir="ltr" class="scroll-smooth">',
             f'<html lang="{code}" dir="{cfg["dir"]}" class="scroll-smooth">', h, "<html> tag")
    h = sub1(r"<title>[^<]*</title>", f"<title>{q(cfg['title'])}</title>", h, "<title>")
    h = sub1(r'<meta name="description" content="[^"]*" />',
             f'<meta name="description" content="{q(cfg["desc"])}" />', h, "meta description")
    h = sub1(r'<meta property="og:description" content="[^"]*" />',
             f'<meta property="og:description" content="{q(cfg["desc"])}" />', h, "og:description")
    h = sub1(r'<meta name="twitter:description" content="[^"]*" />',
             f'<meta name="twitter:description" content="{q(cfg["desc"])}" />', h, "twitter:description")
    h = sub1(r'<meta property="og:title" content="[^"]*" />',
             f'<meta property="og:title" content="{q(cfg["title"])}" />', h, "og:title")
    h = sub1(r'<meta name="twitter:title" content="[^"]*" />',
             f'<meta name="twitter:title" content="{q(cfg["title"])}" />', h, "twitter:title")
    h = sub1(r'<meta property="og:url" content="[^"]*" />',
             f'<meta property="og:url" content="{cfg["url"]}" />', h, "og:url")
    h = sub1(r'<meta property="og:locale" content="[^"]*" />',
             f'<meta property="og:locale" content="{cfg["locale"]}" />', h, "og:locale")
    h = sub1(r'<meta property="og:locale:alternate" content="[^"]*" />',
             f'<meta property="og:locale:alternate" content="{cfg["alt_locale"]}" />', h, "og:locale:alternate")

    links = [f'<link rel="canonical" href="{cfg["url"]}" />']
    links += [f'<link rel="alternate" hreflang="{l}" href="{u}" />' for l, u in cfg["hreflang"]]
    h = sub1(r'<link rel="canonical"[^>]*/>\s*<link rel="alternate" hreflang="fr"[^>]*/>\s*'
             r'<link rel="alternate" hreflang="ar"[^>]*/>\s*<link rel="alternate" hreflang="x-default"[^>]*/>',
             "\n  ".join(links), h, "canonical + hreflang block")

    # ---------- JSON-LD: the WebPage node describes THIS page only
    i = h.index('"@type": "WebPage"')
    head, tail = h[:i], h[i:]
    tail = repn('"url": "https://app.fikra-automation.com/",', f'"url": "{cfg["url"]}",', tail, label="WebPage url")
    tail = repn('"name": "فكرة أتمتة | Fikra Automation – أتمتة الأعمال والمهام في المغرب",',
                f'"name": "{cfg["title"]}",', tail, label="WebPage name")
    tail = sub1(r'"description": "Services d\'automatisation de tâches et de processus au Maroc[^"]*",',
                f'"description": "{cfg["desc"]}",', tail, "WebPage description")
    tail = repn('"inLanguage": ["fr", "ar"]', f'"inLanguage": "{code}"', tail, label="WebPage inLanguage")
    if code == "ar":
        tail = repn('"@id": "https://app.fikra-automation.com/#webpage",',
                    '"@id": "https://app.fikra-automation.com/ar/#webpage",', tail, label="WebPage @id")
    h = head + tail

    # ---------- Language switcher: real links, static in the HTML (crawlable without JavaScript)
    fr_cls = "text-white" if code == "fr" else "text-brand-dark"
    ar_cls = "text-white" if code == "ar" else "text-brand-dark"
    fr_cur = ' aria-current="page"' if code == "fr" else ""
    ar_cur = ' aria-current="page"' if code == "ar" else ""
    switch = (
        '<span id="lang-pill" class="lang-pill" aria-hidden="true"></span>\n'
        f'          <a href="/" hreflang="fr" lang="fr" data-code="fr" class="lang-btn u-press text-center {fr_cls}"{fr_cur}>FR</a>\n'
        f'          <a href="/ar/" hreflang="ar" lang="ar" data-code="ar" class="lang-btn u-press text-center {ar_cls}"{ar_cur}>عربي</a>'
    )
    h = sub1(r'<span id="lang-pill" class="lang-pill" aria-hidden="true"></span>', switch, h, "lang pill")

    # ---------- JavaScript: only the language bootstrap changes
    h = repn("/* ===== 3) CONFIG ===== */",
             "/* ===== 3) CONFIG ===== */\n"
             f"    const PAGE_LANG = '{code}';   // language of this static entry point (fr = /, ar = /ar/)",
             h, label="CONFIG marker")
    h = sub1(r"let saved = CONFIG\.defaultLang;\s*try \{ saved = localStorage\.getItem\(CONFIG\.storageKey\) \|\| CONFIG\.defaultLang; \} catch \(e\) \{ /\* ignore \*/ \}\s*applyLang\(saved\);",
             "applyLang(PAGE_LANG);", h, "init language")
    h = repn("\n    buildLangToggle();\n", "\n", h, label="buildLangToggle() call (switcher is now static links)")
    h = repn("$$('#lang-toggle button')", "$$('#lang-toggle a')", h, label="toggle selector")
    h = repn("b.setAttribute('aria-pressed', String(on));",
             "if (on) b.setAttribute('aria-current', 'page'); else b.removeAttribute('aria-current');",
             h, label="aria-pressed")

    if code == "fr":
        return h

    # ---------- Arabic page only
    # 1) Root-absolute asset paths so they resolve from /ar/
    h = repn('href="logo-mybusiness_fikra-automation.png"', 'href="/logo-mybusiness_fikra-automation.png"', h, 2, "favicon links")
    h = repn('src="logo-mybusiness_fikra-automation.png"', 'src="/logo-mybusiness_fikra-automation.png"', h, label="navbar logo")
    h = repn('src="photo_without_bg-removebg-preview.png"', 'src="/photo_without_bg-removebg-preview.png"', h, label="portrait")
    h = repn('href="cv.pdf"', 'href="/cv.pdf"', h, label="CV link")
    h = repn("file: 'python_certificate.pdf'", "file: '/python_certificate.pdf'", h, label="python certificate")
    h = repn("file: 'certificate-AEO_Fundamentals.png'", "file: '/certificate-AEO_Fundamentals.png'", h, label="AEO certificate")

    # 2) FAQPage structured data generated by JS must point at the /ar/ page
    h = repn("'@id': 'https://app.fikra-automation.com/#faq',", "'@id': 'https://app.fikra-automation.com/ar/#faq',", h, label="faq @id")
    h = repn("isPartOf: { '@id': 'https://app.fikra-automation.com/#webpage' },",
             "isPartOf: { '@id': 'https://app.fikra-automation.com/ar/#webpage' },", h, label="faq isPartOf")

    # 3) Pre-render the visible static body text in Arabic (body only, never the scripts)
    idx = h.index("/* ===== 3) CONFIG")
    script_start = h.rindex("<script>", 0, idx)
    body_start = h.index("<body")
    body = h[body_start:script_start]
    for key in STATIC_KEYS:
        body = sub1(r'data-i18n="%s">[^<]*<' % key, f'data-i18n="{key}">{ar_text(key)}<', body, f"static text '{key}'")
    body = repn('aria-label="Navigation principale" data-i18n-aria="navLabel"',
                f'aria-label="{ar_text("navLabel")}" data-i18n-aria="navLabel"', body, label="nav aria-label")
    body = repn('aria-label="Langue" data-i18n-aria="langLabel"',
                f'aria-label="{ar_text("langLabel")}" data-i18n-aria="langLabel"', body, label="lang aria-label")
    for fr_li, ar_li in [
        ("Automatisation de workflows (n8n, Make, Zapier)", "أتمتة سير العمل (n8n وMake وZapier)"),
        ("Scripts et bots sur mesure (Python, JavaScript, Telegram, WhatsApp)", "سكربتات وروبوتات مخصصة (Python وJavaScript وتيليغرام وواتساب)"),
        ("Automatisation de tableurs et rapports (Excel, Google Sheets)", "أتمتة الجداول والتقارير (Excel وGoogle Sheets)"),
        ("<li>Assistants IA</li>", "<li>مساعدون بالذكاء الاصطناعي</li>"),
        ("Saisie et synchronisation de données", "إدخال البيانات ومزامنتها"),
        ("<li>Audit de processus</li>", "<li>تدقيق العمليات</li>"),
        ("Carte de fidélité digitale pour cafés et restaurants", "بطاقة ولاء رقمية للمقاهي والمطاعم"),
    ]:
        body = repn(fr_li, ar_li, body, label=f"noscript item '{fr_li}'")
    h = h[:body_start] + body + h[script_start:]
    return h


fr_html, ar_html = build(CFG["fr"]), build(CFG["ar"])

(OUT / "ar").mkdir(parents=True, exist_ok=True)
(OUT / "index.html").write_text(fr_html, encoding="utf-8", newline="")
(OUT / "ar" / "index.html").write_text(ar_html, encoding="utf-8", newline="")
print(f"OK  {OUT / 'index.html'}  ({len(fr_html):,} chars)")
print(f"OK  {OUT / 'ar' / 'index.html'}  ({len(ar_html):,} chars)")