from pathlib import Path
from PIL import Image

ASSETS = Path(__file__).parents[1] / "client" / "src" / "assets"
for source in ASSETS.glob("*.jpg"):
    image = Image.open(source).convert("RGB")
    image.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
    image.save(source, "JPEG", quality=82, optimize=True, progressive=True)
    print(f"optimized {source.name}: {image.size}")
