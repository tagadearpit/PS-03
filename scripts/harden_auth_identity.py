from pathlib import Path
path = Path(__file__).parents[1] / "client/src/pages/Auth.tsx"
text = path.read_text()
text = text.replace('type AuthUser = { email: string; name: string };', 'export type AuthUser = { email: string; name: string; age?: number };')
text = text.replace('  const [name, setName] = useState("");\n  const [password', '  const [name, setName] = useState("");\n  const [age, setAge] = useState("");\n  const [password')
text = text.replace('    if (isReset) {', '    if (!isLogin && !isReset && (!name.trim() || !age)) { toast.error("Enter your name and age to create an account."); return; }\n    if (!isLogin && !isReset && (Number(age) < 13 || Number(age) > 120)) { toast.error("Enter a valid age between 13 and 120."); return; }\n    if (isReset) {')
text = text.replace('      if (isLogin && saved && saved.email !== normalizedEmail) { toast.error("No local account found for this email.", { description: "Create an account first to continue." }); setBusy(false); return; }\n      const user = saved && saved.email === normalizedEmail ? saved : { email: normalizedEmail, name: name.trim() || normalizedEmail.split("@")[0] };', '      if (isLogin && (!saved || saved.email !== normalizedEmail)) { toast.error("No account found for this email.", { description: "Create an account first to continue." }); setBusy(false); return; }\n      const user = saved && saved.email === normalizedEmail ? saved : { email: normalizedEmail, name: name.trim(), age: Number(age) };')
old = '{!isLogin && !isReset && <label><span>Your name</span><div className="auth-input"><ShieldCheck size={16} /><input value={name} onChange={(event) => setName(event.target.value)} placeholder="Alex Rivera" autoComplete="name" /></div></label>}'
new = '{!isLogin && !isReset && <><label><span>Your name</span><div className="auth-input"><ShieldCheck size={16} /><input value={name} onChange={(event) => setName(event.target.value)} placeholder="Alex Rivera" autoComplete="name" required /></div></label><label><span>Your age</span><div className="auth-input"><ShieldCheck size={16} /><input type="number" min="13" max="120" value={age} onChange={(event) => setAge(event.target.value)} placeholder="25" autoComplete="bday-year" required /></div></label></>}'
if old not in text: raise SystemExit('name field not found')
text = text.replace(old, new)
text = text.replace('      <div className="auth-switch">{isReset ?', '      <div className="auth-switch">{isReset ?') if False else text
path.write_text(text)
print('auth identity hardened')
