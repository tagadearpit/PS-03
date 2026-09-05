from pathlib import Path
path = Path(__file__).parents[1] / "client/src/pages/Home.tsx"
text = path.read_text()
needle = '<Sparkles size={14} /> Explain in plain English <ArrowUpRight size={14} /></button></>}\n            </div>'
replacement = '<Sparkles size={14} /> Explain in plain English <ArrowUpRight size={14} /></button></>}</div>\n            </div>'
if needle not in text:
    raise SystemExit("closing tag location not found")
path.write_text(text.replace(needle, replacement, 1))
print("closing tag fixed")
