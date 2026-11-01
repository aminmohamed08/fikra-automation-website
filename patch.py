import re, shutil

DESC = ("Fikra Automation digitalise votre café ou restaurant : menus QR intelligents, "
        "avis Google automatisés et workflows n8n. Demandez un devis gratuit.")

rules = [
    (r'<meta name="description" content="[^"]*" />', 
     f'<meta name="description" content="{DESC}" />'),
    (r'<meta property="og:description" content="[^"]*" />', 
     f'<meta property="og:description" content="{DESC}" />'),
    (r'<meta name="twitter:description" content="[^"]*" />', 
     f'<meta name="twitter:description" content="{DESC}" />'),
]

with open("index.html", encoding="utf-8", newline="") as f:
    html = f.read()

for pattern, new in rules:
    found = len(re.findall(pattern, html))
    assert found == 1, f"Expected 1 match, found {found} for: {pattern}"
    html = re.sub(pattern, lambda m: new, html)

shutil.copy("index.html", "index.html.bak")

with open("index.html", "w", encoding="utf-8", newline="") as f:
    f.write(html)

print("Done: 3 tags updated, backup saved as index.html.bak")