from pathlib import Path
path = Path(__file__).parents[1] / "client/src/pages/Site.tsx"
text = path.read_text()
text = text.replace('Laptop, Link as LinkIcon, Menu, Moon, QrCode', 'Laptop, Link as LinkIcon, LogOut, Menu, Moon, QrCode')
text = text.replace('"guide" | "login" | "signup";', '"guide" | "login" | "signup" | "reset";')
text = text.replace('if (path === "/signup") return "signup"; return "home";', 'if (path === "/signup") return "signup"; if (path === "/reset-password") return "reset"; return "home";')
old = '<div className="nav-status"><span />Protected</div>{signedIn ? <Link to="/studio" className="nav-signin nav-account" onClick={() => setMobileOpen(false)}>Open studio</Link> : <Link to="/login" className="nav-signin" onClick={() => setMobileOpen(false)}>Sign in <ArrowUpRight size={13} /></Link>}'
new = '<div className="nav-status"><span />Protected</div>{signedIn ? <><Link to="/studio" className="nav-signin nav-account" onClick={() => setMobileOpen(false)}>Open studio</Link><button className="nav-signin nav-logout" onClick={() => window.dispatchEvent(new Event("payguard:logout"))} aria-label="Log out" title="Log out"><LogOut size={14} /></button></> : <Link to="/login" className="nav-signin" onClick={() => setMobileOpen(false)}>Sign in <ArrowUpRight size={13} /></Link>}'
if old not in text: raise SystemExit('nav auth action not found')
text = text.replace(old, new, 1)
text = text.replace('<SiteNav dark={dark} setDark={setDark} mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} signedIn={signedIn} />', '<SiteNav dark={dark} setDark={setDark} mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} signedIn={signedIn} />', 1)
needle = 'useEffect(() => { const onPop = () => setPage(getPage()); window.addEventListener("popstate", onPop); return () => window.removeEventListener("popstate", onPop); }, []);'
replacement = 'useEffect(() => { const onPop = () => setPage(getPage()); const onLogout = () => { localStorage.removeItem("payguard-user"); localStorage.removeItem("payguard-session"); setUser(null); window.history.pushState({}, "", "/"); setPage("home"); toast.success("You have been logged out."); }; window.addEventListener("popstate", onPop); window.addEventListener("payguard:logout", onLogout); return () => { window.removeEventListener("popstate", onPop); window.removeEventListener("payguard:logout", onLogout); }; }, []);'
if needle not in text: raise SystemExit('site effect not found')
text = text.replace(needle, replacement, 1)
text = text.replace('page === "login" || page === "signup"', 'page === "login" || page === "signup" || page === "reset"')
text = text.replace('<AuthPage mode={page}', '<AuthPage mode={page === "reset" ? "reset" : page}')
path.write_text(text)
print('logout and reset route added')
