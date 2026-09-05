from pathlib import Path
path = Path(__file__).parents[1] / "client/src/pages/Site.tsx"
text = path.read_text()
old = 'const protectedPage = page === "studio" || page === "history";'
new = 'const protectedPage = page !== "home" && page !== "login" && page !== "signup" && page !== "reset";'
if old not in text: raise SystemExit('protected route expression not found')
path.write_text(text.replace(old, new, 1))
print('all feature routes protected')
