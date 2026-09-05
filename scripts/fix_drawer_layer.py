from pathlib import Path
path = Path(__file__).parents[1] / "client/src/index.css"
text = path.read_text()
text = text.replace(".drawer-scrim { position: fixed; inset: 0; z-index: 39;", ".drawer-scrim { position: fixed; inset: 0; z-index: 59;", 1)
text = text.replace(".monitor-drawer { width: 315px; position: fixed; z-index: 40;", ".monitor-drawer { width: 315px; position: fixed; z-index: 60;", 1)
path.write_text(text)
print("drawer stacking order fixed")
