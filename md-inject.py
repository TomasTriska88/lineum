import re
from bs4 import BeautifulSoup
from pathlib import Path
import html2text

# 📁 Kořenová složka
BASE_FOLDER = Path.cwd()

# 📁 Markdown soubory ke zpracování
MD_PATHS = [
    BASE_FOLDER / "readme.md",
    BASE_FOLDER / "todo.md",
    *BASE_FOLDER.glob("whitepaper/**/*.md"),
    *BASE_FOLDER.glob("hypotheses/**/*.md")
]

def inject_markdown_from_html(md_path: Path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    pattern = r'<!--\s*include:([\w\-\/]+)#([\w\-]+)\s*-->'
    matches = re.findall(pattern, md_content)

    if not matches:
        return False

    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.body_width = 0

    for subpath, element_id in matches:
        # Rozdělení části cesty (např. no_artefacts/spec3_true)
        parts = subpath.strip().split('/')
        if len(parts) != 2:
            print(f"⚠️ Neplatná include syntaxe: {subpath} – očekáváno ve formátu slozka/spec")
            continue

        folder = f"output_{parts[0]}"
        spec = parts[1]
        html_filename = f"{spec}_lineum_report.html"
        html_path = BASE_FOLDER / folder / spec / html_filename

        if not html_path.exists():
            print(f"⚠️ HTML soubor nenalezen: {html_path}")
            continue

        with open(html_path, 'r', encoding='utf-8') as html_file:
            soup = BeautifulSoup(html_file, 'html.parser')
            section = soup.find(id=element_id)
            if not section:
                print(f"⚠️ ID '{element_id}' nebyl nalezen v souboru: {html_filename}")
                continue

            markdown_text = converter.handle(str(section)).strip()
            tag = f"<!-- include:{subpath}#{element_id} -->"
            md_content = md_content.replace(tag, markdown_text)

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"✅ Vloženo do: {md_path.relative_to(BASE_FOLDER)}")
    return True

# 🚀 Spuštění
if __name__ == "__main__":
    any_changes = False
    for md_path in MD_PATHS:
        if md_path.exists():
            result = inject_markdown_from_html(md_path)
            any_changes = any_changes or result
    if not any_changes:
        print("ℹ️ Žádné include značky nebyly nalezeny.")
