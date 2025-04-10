import re
import os
from pathlib import Path
from PIL import Image
from bs4 import BeautifulSoup, Comment

root = Path(__file__).parent
html_path = root / "index.dev.html"
dev_html_path = root / "index.dev.html"
img_dir = root / "sources" / "img" / "portfolio_images"

if not html_path.exists():
    html_path = dev_html_path

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

img_pattern = r"sources/img/portfolio_images/([0-9]{1,3})\.(jpg|png)"
found_images = set(re.findall(img_pattern, html_content))
used_images = {f"{num}.{ext}" for num, ext in found_images}
actual_images = {img.name for img in img_dir.glob("*.jpg")} | {img.name for img in img_dir.glob("*.png")}

unused_images = actual_images - used_images
for img in unused_images:
    try:
        os.remove(img_dir / img)
    except FileNotFoundError:
        pass

converted_images = {}
for num, ext in found_images:
    original = img_dir / f"{num}.{ext}"
    webp_path = img_dir / f"{num}.webp"
    if not webp_path.exists() and original.exists():
        with Image.open(original) as im:
            im.save(webp_path, "webp")
    if original.exists():
        os.remove(original)
    converted_images[f"sources/img/portfolio_images/{num}.{ext}"] = f"sources/img/portfolio_images/{num}.webp"

soup = BeautifulSoup(html_content, "html.parser")

for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
    comment.extract()

for tag in soup.find_all(["img", "source", "a"]):
    for attr in ["src", "href", "srcset"]:
        if tag.has_attr(attr):
            if tag[attr] in converted_images:
                tag[attr] = converted_images[tag[attr]]

updated_html = str(soup)

with open(dev_html_path, "w", encoding="utf-8") as f:
    f.write(updated_html)

with open(root / "index.dev.html", "w", encoding="utf-8") as f:
    f.write(updated_html)