import { FormEvent, useState } from "react";
import { ArrowLeft, ArrowRight, Eye, EyeOff, KeyRound, LockKeyhole, Mail, ShieldCheck } from "lucide-react";
import { toast } from "sonner";
import { Link } from "wouter";
import loginImage from "@/assets/payguard-login.jpg";
import signupImage from "@/assets/payguard-signup.jpg";

type AuthMode = "login" | "signup" | "reset";
export type AuthUser = { email: string; name: string; age?: number };

export const AUTH_USER_KEY = "payguard-user";
export const AUTH_SESSION_KEY = "payguard-session";

export function getAuthUser(): AuthUser | null {
  try { return JSON.parse(localStorage.getItem(AUTH_USER_KEY) || "null") as AuthUser | null; } catch { return null; }
}

function markSignedIn(user: AuthUser) {
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
  localStorage.setItem(AUTH_SESSION_KEY, "active");
}

export default function AuthPage({ mode, onSuccess }: { mode: AuthMode; onSuccess: (user: AuthUser) => void }) {
  const isLogin = mode === "login";
  const isReset = mode === "reset";
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState(false);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const normalizedEmail = email.trim().toLowerCase();
    if (!normalizedEmail || !normalizedEmail.includes("@")) { toast.error("Enter a valid email address."); return; }
    if (!isLogin && !isReset && (!name.trim() || !age)) { toast.error("Enter your name and age to create an account."); return; }
    if (!isLogin && !isReset && (Number(age) < 13 || Number(age) > 120)) { toast.error("Enter a valid age between 13 and 120."); return; }
    if (isReset) {
      setBusy(true);
      window.setTimeout(() => { toast.success("Reset instructions sent.", { description: `If an account exists for ${normalizedEmail}, you will receive an email shortly.` }); setBusy(false); }, 520);
      return;
    }
    if (password.length < 8) { toast.error("Use at least 8 characters for your password."); return; }
    if (!isLogin && password !== confirm) { toast.error("Passwords do not match."); return; }
    setBusy(true);
    window.setTimeout(() => {
      const saved = getAuthUser();
      if (isLogin && (!saved || saved.email !== normalizedEmail)) { toast.error("No account found for this email.", { description: "Create an account first to continue." }); setBusy(false); return; }
      const user = saved && saved.email === normalizedEmail ? saved : { email: normalizedEmail, name: name.trim(), age: Number(age) };
      markSignedIn(user);
      toast.success(isLogin ? "Welcome back to PayGuard AI." : "Your PayGuard account is ready.");
      onSuccess(user);
      setBusy(false);
    }, 520);
  };

  const visualImage = isReset || isLogin ? loginImage : signupImage;
  const eyebrow = isReset ? "ACCOUNT RECOVERY" : isLogin ? "SECURE ACCESS" : "GET STARTED";
  const heading = isReset ? "Reset your password." : isLogin ? "Welcome back." : "Create your account.";
  const description = isReset ? "Enter your email and we’ll help you get back into your workspace." : isLogin ? "Sign in to continue to your verification studio." : "Set up your private PayGuard workspace in under a minute.";

  return <main className="auth-page"><div className="auth-visual" style={{ backgroundImage: `linear-gradient(90deg, rgba(35,31,27,.94), rgba(35,31,27,.38)), url(${visualImage})` }}><Link to="/" className="auth-back"><ArrowLeft size={15} /> Back to PayGuard</Link><div className="auth-visual-copy"><span className="eyebrow">{isReset ? "A QUIETER WAY BACK IN" : isLogin ? "WELCOME BACK" : "A CALMER WAY TO CHECK"}</span><h1>{isReset ? <>Your protection,<br /><em>still here.</em></> : isLogin ? <>Trust, before<br /><em>you tap.</em></> : <>Build a safer<br /><em>second opinion.</em></>}</h1><p>{isReset ? "Recover access without losing the calm, focused workspace you built." : isLogin ? "Your verification workspace is ready when you are." : "Create a private workspace for clearer payment decisions."}</p></div><div className="auth-visual-footer"><ShieldCheck size={14} /> Stateless protection · No sensitive inputs stored</div></div><section className="auth-panel"><div className="auth-panel-inner"><Link to="/" className="auth-mobile-brand"><ShieldCheck size={17} /> PayGuard <em>AI</em></Link><div className="auth-heading"><span className="eyebrow">{eyebrow}</span><h2>{heading}</h2><p>{description}</p></div><form className="auth-form" onSubmit={submit}>{!isLogin && !isReset && <><label><span>Your name</span><div className="auth-input"><ShieldCheck size={16} /><input value={name} onChange={(event) => setName(event.target.value)} placeholder="Alex Rivera" autoComplete="name" required /></div></label><label><span>Your age</span><div className="auth-input"><ShieldCheck size={16} /><input type="number" min="13" max="120" value={age} onChange={(event) => setAge(event.target.value)} placeholder="25" autoComplete="bday-year" required /></div></label></>}<label><span>Email address</span><div className="auth-input"><Mail size={16} /><input type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" autoComplete="email" required /></div></label>{!isReset && <label><span>Password</span><div className="auth-input"><LockKeyhole size={16} /><input type={showPassword ? "text" : "password"} value={password} onChange={(event) => setPassword(event.target.value)} placeholder="At least 8 characters" autoComplete={isLogin ? "current-password" : "new-password"} required /><button type="button" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? "Hide password" : "Show password"}>{showPassword ? <EyeOff size={16} /> : <Eye size={16} />}</button></div></label>}{!isLogin && !isReset && <label><span>Confirm password</span><div className="auth-input"><LockKeyhole size={16} /><input type={showPassword ? "text" : "password"} value={confirm} onChange={(event) => setConfirm(event.target.value)} placeholder="Repeat your password" autoComplete="new-password" required /></div></label>}<button className="auth-submit" disabled={busy}>{busy ? isReset ? "Sending instructions…" : "Securing your workspace…" : isReset ? "Send reset link" : isLogin ? "Sign in" : "Create account"}{isReset ? <KeyRound size={16} /> : <ArrowRight size={16} />}</button></form>{isLogin && <Link to="/reset-password" className="forgot-link">Forgot your password? <ArrowRight size={13} /></Link>}<div className="auth-switch">{isReset ? <>Remember your password? <Link to="/login">Sign in <ArrowRight size={13} /></Link></> : isLogin ? <>New to PayGuard? <Link to="/signup">Create an account <ArrowRight size={13} /></Link></> : <>Already have an account? <Link to="/login">Sign in <ArrowRight size={13} /></Link></>}</div><div className="auth-note"><LockKeyhole size={14} /><span>Demo authentication stores a local session in this browser. Connect your production identity provider before launch.</span></div></div></section></main>;
}
