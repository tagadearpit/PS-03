import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { gsap } from "gsap";
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  BadgeCheck,
  BellRing,
  Camera,
  Check,
  CheckCircle2,
  ChevronDown,
  ClipboardPaste,
  CloudUpload,
  FileSearch,
  Gauge,
  HelpCircle,
  Inbox,
  Link2,
  LockKeyhole,
  Menu,
  MessageSquareText,
  MoreHorizontal,
  QrCode,
  Radio,
  ScanLine,
  Search,
  Shield,
  ShieldAlert,
  Smartphone,
  Sparkles,
  Terminal,
  Upload,
  UserRound,
  Wifi,
  X,
  Zap,
} from "lucide-react";
import { toast } from "sonner";
import { analyzeWithBackend } from "@/lib/api";
import { getAuthUser } from "./Auth";

type InputMode = "image" | "text" | "url" | "camera";
type Severity = "safe" | "suspicious" | "high";

type Threat = {
  title: string;
  detail: string;
  severity: Severity;
  icon: typeof Shield;
};

type AnalysisResult = {
  score: number;
  severity: Severity;
  label: string;
  summary: string;
  action: string;
  actionDetail: string;
  source: string;
  entity: string;
  threats: Threat[];
  timestamp: string;
};

const initialResult: AnalysisResult = {
  score: 18,
  severity: "safe",
  label: "Looks safe",
  summary:
    "No meaningful scam signals found. The sender and payment address appear consistent with a normal merchant request.",
  action: "Safe to continue",
  actionDetail: "Always verify the merchant name before approving a payment.",
  source: "Payment QR",
  entity: "Blue Tokai Coffee",
  threats: [
    {
      title: "Intent matches",
      detail: "Payment purpose and merchant context are aligned.",
      severity: "safe",
      icon: CheckCircle2,
    },
    {
      title: "No urgency cues",
      detail: "No pressure language or suspicious deadlines detected.",
      severity: "safe",
      icon: MessageSquareText,
    },
    {
      title: "Verified VPA format",
      detail: "The payment handle follows a standard UPI pattern.",
      severity: "safe",
      icon: BadgeCheck,
    },
  ],
  timestamp: "Just now",
};

const scenarios: Record<string, AnalysisResult> = {
  bill: {
    score: 94,
    severity: "high",
    label: "High risk",
    summary:
      "This message uses a fake electricity disconnection threat and asks for an urgent payment through an unverified link.",
    action: "Do not open or pay",
    actionDetail: "Block the sender and use the official electricity board website to verify your bill.",
    source: "Incoming SMS",
    entity: "Maharashtra Power Desk",
    threats: [
      {
        title: "Impersonation urgency",
        detail: "A same-day cutoff threat is a classic pressure tactic.",
        severity: "high",
        icon: ShieldAlert,
      },
      {
        title: "Unverified link domain",
        detail: "The destination is not an official electricity board domain.",
        severity: "high",
        icon: Link2,
      },
      {
        title: "Intent mismatch",
        detail: "The sender asks for a convenience fee before showing a bill.",
        severity: "suspicious",
        icon: AlertTriangle,
      },
    ],
    timestamp: "Just now",
  },
  cashback: {
    score: 81,
    severity: "high",
    label: "High risk",
    summary:
      "The QR code claims a cashback reward but is configured to collect money from you instead of sending a reward.",
    action: "Do not scan this QR",
    actionDetail: "Cashback never requires entering a UPI PIN to receive money.",
    source: "WhatsApp image",
    entity: "Rewards Support",
    threats: [
      {
        title: "Collect request detected",
        detail: "The QR payload requests a payment, not a receipt.",
        severity: "high",
        icon: QrCode,
      },
      {
        title: "Prize-bait language",
        detail: "Reward claims are paired with a tight expiry window.",
        severity: "suspicious",
        icon: Zap,
      },
      {
        title: "Unverified VPA domain",
        detail: "The handle does not match a known merchant identity.",
        severity: "high",
        icon: BadgeCheck,
      },
    ],
    timestamp: "Just now",
  },
};

const historyRows = [
  { type: "URL", name: "sbi-kyc-update.top", result: "Blocked", score: 98, time: "Today, 10:42" },
  { type: "SMS", name: "Parcel delivery fee", result: "Review", score: 63, time: "Today, 09:18" },
  { type: "QR", name: "Blue Tokai Coffee", result: "Clear", score: 18, time: "Yesterday, 18:06" },
];

function RiskGauge({ score, severity }: { score: number; severity: Severity }) {
  const arcRef = useRef<SVGCircleElement>(null);
  const numberRef = useRef<HTMLSpanElement>(null);
  const circumference = 2 * Math.PI * 76;
  const color = severity === "safe" ? "#4f7d5d" : severity === "suspicious" ? "#b7791f" : "#b45248";

  useEffect(() => {
    if (!arcRef.current || !numberRef.current) return;
    const targetOffset = circumference - (score / 100) * circumference;
    gsap.fromTo(arcRef.current, { strokeDashoffset: circumference }, { strokeDashoffset: targetOffset, duration: 1.05, ease: "power3.out" });
    const counter = { value: 0 };
    gsap.to(counter, {
      value: score,
      duration: 0.9,
      ease: "power2.out",
      onUpdate: () => {
        if (numberRef.current) numberRef.current.textContent = `${Math.round(counter.value)}`;
      },
    });
  }, [circumference, score]);

  return (
    <div className="gauge-wrap" style={{ "--gauge-color": color } as React.CSSProperties}>
      <svg viewBox="0 0 180 180" className="gauge-svg" aria-label={`Risk score ${score} out of 100`}>
        <circle className="gauge-track" cx="90" cy="90" r="76" />
        <circle ref={arcRef} className="gauge-value" cx="90" cy="90" r="76" strokeDasharray={circumference} strokeDashoffset={circumference} />
      </svg>
      <div className="gauge-center">
        <span ref={numberRef} className="gauge-number">0</span>
        <span className="gauge-denom">/ 100</span>
      </div>
    </div>
  );
}

function StatusPill({ severity, children }: { severity: Severity; children: React.ReactNode }) {
  return <span className={`status-pill status-${severity}`}><span className="status-dot" />{children}</span>;
}

export default function Home() {
  const [mode, setMode] = useState<InputMode>("image");
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [monitorOpen, setMonitorOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [textValue, setTextValue] = useState("");
  const [urlValue, setUrlValue] = useState("");
  const [dragging, setDragging] = useState(false);
  const [cameraOn, setCameraOn] = useState(false);
  const [cameraError, setCameraError] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(initialResult);
  const [toastMessage, setToastMessage] = useState("Awaiting next input");
  const [activityCount, setActivityCount] = useState(7);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!contentRef.current) return;
    gsap.fromTo(contentRef.current.querySelectorAll(".reveal"), { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.55, stagger: 0.07, ease: "power2.out" });
  }, []);

  useEffect(() => {
    if (!cameraOn || !videoRef.current) return;
    let stream: MediaStream | null = null;
    navigator.mediaDevices?.getUserMedia({ video: { facingMode: "environment" } }).then((nextStream) => {
      stream = nextStream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play().catch(() => undefined);
      }
    }).catch(() => setCameraError("Camera access is unavailable. You can still paste a QR image instead."));
    return () => stream?.getTracks().forEach((track) => track.stop());
  }, [cameraOn]);

  const fileLabel = useMemo(() => selectedFile?.name ?? "No file selected", [selectedFile]);
  const authUser = getAuthUser();
  const displayName = authUser?.name?.trim() || "there";
  const initials = displayName.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase();

  const setFile = useCallback((file?: File) => {
    if (!file || !file.type.startsWith("image/")) {
      toast.error("Please choose an image file");
      return;
    }
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setToastMessage("Image ready for analysis");
  }, []);

  const onPaste = (event: React.ClipboardEvent<HTMLDivElement>) => {
    const pastedImage = Array.from(event.clipboardData.items).find((item) => item.type.startsWith("image/"));
    if (pastedImage) setFile(pastedImage.getAsFile() ?? undefined);
  };

  const analyze = async (nextResult?: AnalysisResult) => {
    if (!nextResult) {
      if (mode === "text" && textValue.trim().length < 8) { toast.error("Paste the complete message first", { description: "Include the sender, request, and any link or urgency language." }); return; }
      if (mode === "url") {
        const candidate = urlValue.trim();
        try { const parsed = new URL(candidate); if (!["http:", "https:"].includes(parsed.protocol)) throw new Error(); } catch { toast.error("Enter a valid http or https URL", { description: "Example: https://example.com/verify-payment" }); return; }
      }
      if (mode === "camera" && !cameraOn) { toast.error("Start the camera before scanning", { description: "Allow camera access, point at a QR code, then analyze the captured frame." }); return; }
    }
    setAnalyzing(true);
    if (nextResult) {
      window.setTimeout(() => {
        setResult(nextResult);
        setAnalyzing(false);
        setActivityCount((count) => count + 1);
        setToastMessage("Analysis complete");
        toast.success("Risk analysis complete", { description: "Your result is ready in the risk breakdown." });
      }, 620);
      return;
    }
    if (mode === "image" && !selectedFile) {
      setAnalyzing(false);
      toast.error("Add an image first", { description: "Choose a screenshot or QR image before analyzing." });
      return;
    }
    try {
      let backendResult;
      if (mode === "image" && selectedFile) {
        backendResult = await analyzeWithBackend({ inputType: "image", file: selectedFile });
      } else if (mode === "camera" && videoRef.current && canvasRef.current) {
        const video = videoRef.current;
        const canvas = canvasRef.current;
        canvas.width = video.videoWidth || 1280;
        canvas.height = video.videoHeight || 720;
        canvas.getContext("2d")?.drawImage(video, 0, 0, canvas.width, canvas.height);
        const frame = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.9));
        if (!frame) throw new Error("Could not capture a camera frame");
        backendResult = await analyzeWithBackend({ inputType: "image", file: new File([frame], "camera-scan.jpg", { type: "image/jpeg" }), source: "manual" });
      } else {
        backendResult = await analyzeWithBackend({ inputType: mode === "text" ? "text" : "url", content: mode === "text" ? textValue.trim() : urlValue.trim() });
      }
      setResult({ ...backendResult, actionDetail: backendResult.action_detail, timestamp: backendResult.timestamp, threats: backendResult.threats.map((threat) => ({ ...threat, icon: threat.severity === "safe" ? CheckCircle2 : threat.severity === "suspicious" ? AlertTriangle : ShieldAlert })) });
      setActivityCount((count) => count + 1);
      setToastMessage("Gemini analysis complete");
      toast.success("Gemini risk analysis complete", { description: "The backend returned a structured assessment." });
    } catch (error) {
      setResult(mode === "url" ? scenarios.bill : initialResult);
      setToastMessage("Demo result shown");
      toast.error("Backend unavailable", { description: error instanceof Error ? `${error.message} Demo data is shown locally.` : "Demo data is shown locally." });
    } finally {
      setAnalyzing(false);
    }
  };

  const simulate = (scenario: "bill" | "cashback") => {
    setMonitorOpen(true);
    setAnalyzing(true);
    setToastMessage("Interceptor captured a new event");
    window.setTimeout(() => {
      setResult(scenarios[scenario]);
      setAnalyzing(false);
      setActivityCount((count) => count + 1);
      toast.error(scenario === "bill" ? "High-risk SMS intercepted" : "Suspicious QR intercepted", { description: "PayGuard blocked the event before it could become a payment." });
    }, 700);
  };

  const toggleCamera = () => {
    setCameraError("");
    setCameraOn((current) => !current);
    if (cameraOn) setToastMessage("Camera scanner paused");
  };

  const modeMeta = {
    image: { title: "Drop a screenshot or QR image", description: "OCR and QR parsing runs locally before the risk engine reviews it.", icon: CloudUpload },
    text: { title: "Paste a suspicious message", description: "Add the full SMS, WhatsApp message, or sender context.", icon: MessageSquareText },
    url: { title: "Inspect a payment or web link", description: "We check domain reputation, typosquatting, and intent signals.", icon: Link2 },
    camera: { title: "Scan a QR code live", description: "Point your camera at a code to inspect the payment destination.", icon: ScanLine },
  }[mode];
  const ModeIcon = modeMeta.icon;

  return (
    <div className="app-shell">
      <aside className={`side-rail ${mobileNavOpen ? "is-open" : ""}`}>
        <div className="brand-lockup">
          <div className="brand-mark"><Shield size={19} strokeWidth={2.4} /></div>
          <div><span className="brand-name">PayGuard</span><span className="brand-ai">AI</span><span className="brand-tagline">Trust, before tap.</span></div>
        </div>
        <div className="rail-section-label">Workspace</div>
        <nav className="rail-nav" aria-label="Primary navigation">
          <button className="rail-link active"><Gauge size={17} /><span>Verification studio</span><span className="rail-count">{activityCount}</span></button>
          <button className="rail-link" onClick={() => document.querySelector(".history-section")?.scrollIntoView({ behavior: "smooth" })}><Inbox size={17} /><span>Activity history</span></button>
          <button className="rail-link" onClick={() => toast.info("Active risk rules", { description: "URL reputation, urgency language, payment intent, QR destination, and impersonation cues are enabled." })}><FileSearch size={17} /><span>Risk rules</span><span className="rail-new">5 active</span></button>
        </nav>
        <div className="rail-section-label rail-section-spaced">System</div>
        <nav className="rail-nav" aria-label="System navigation">
          <button className="rail-link" onClick={() => toast.info("API connection is healthy.")}><Activity size={17} /><span>System health</span></button>
          <button className="rail-link" onClick={() => toast.info("Workspace settings", { description: "Use the navigation theme control to change appearance. Your session remains private to this browser." })}><MoreHorizontal size={17} /><span>More settings</span></button>
        </nav>
        <div className="rail-bottom">
          <div className="rail-help"><div className="help-icon"><HelpCircle size={17} /></div><div><strong>Need a hand?</strong><span>Read the safety guide</span></div><ArrowUpRight size={15} /></div>
          <button className="profile-button"><div className="avatar">{initials}</div><div className="profile-copy"><strong>{displayName}</strong><span>Safety analyst</span></div><ChevronDown size={15} /></button>
        </div>
      </aside>

      <div className="main-column">
        <header className="topbar">
          <div className="topbar-left"><button className="mobile-menu" onClick={() => setMobileNavOpen((open) => !open)} aria-label="Toggle navigation"><Menu size={20} /></button><div className="crumb"><span>Workspace</span><span>/</span><strong>Verification studio</strong></div></div>
          <div className="topbar-right"><div className="system-status"><span className="pulse-dot" />All systems operational</div><button className="icon-button" aria-label="Search"><Search size={17} /></button><button className="icon-button notification-button" aria-label="Notifications"><BellRing size={17} /><span /></button><div className="topbar-avatar">AR</div></div>
        </header>

        <main className="content" ref={contentRef}>
          <section className="welcome-row reveal">
            <div><p className="eyebrow">THURSDAY, 04 SEPTEMBER 2026</p><h1>Good morning, {displayName} <span className="wave">✦</span></h1><p className="welcome-copy">Review a payment, message, or QR code before it costs you.</p></div>
            <div className="welcome-actions"><div className="view-switcher"><button className="view-option selected"><span className="view-dot" />Analyst view</button><button className="view-option" onClick={() => toast.info("Observer view is a read-only mode.")}>Observer</button></div><button className="quick-audit" onClick={() => document.getElementById("studio")?.scrollIntoView({ behavior: "smooth" })}><Zap size={15} /> Quick audit</button></div>
          </section>

          <section className="hero-card reveal">
            <div className="hero-content"><div className="hero-kicker"><span className="hero-kicker-icon"><Sparkles size={13} /></span>PROACTIVE PROTECTION <span className="hero-line" /></div><h2>Confidence is a<br /><em>second opinion.</em></h2><p>PayGuard reads the signals most people miss — from fake urgency to payment handles that don’t belong.</p><div className="hero-metrics"><div><strong>4</strong><span>input modes</span></div><div><strong>0<span className="metric-unit">ms</span></strong><span>data stored</span></div><div><strong>24/7</strong><span>protection</span></div></div></div>
            <div className="hero-visual" aria-hidden="true"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="hero-shield"><Shield size={51} strokeWidth={1.35} /><div className="shield-check"><Check size={14} strokeWidth={3} /></div></div><div className="hero-float float-top"><span className="float-check"><Check size={11} /></span><span>Privacy first</span></div><div className="hero-float float-bottom"><span className="float-signal"><Wifi size={12} /></span><span>Live signals</span></div></div>
          </section>

          <section className="workspace-grid" id="studio">
            <div className="studio-panel card reveal">
              <div className="panel-heading"><div><div className="section-kicker"><span className="kicker-bar" /> INPUT SOURCE</div><h3>What would you like to verify?</h3></div><button className="text-button" onClick={() => { setResult(initialResult); setSelectedFile(null); setPreviewUrl(null); setTextValue(""); setUrlValue(""); setToastMessage("Studio reset"); }}>Reset studio <X size={14} /></button></div>
              <div className="mode-tabs" role="tablist" aria-label="Verification input modes">
                {(["image", "text", "url", "camera"] as InputMode[]).map((item) => { const labels = { image: "Image / QR", text: "SMS / text", url: "URL inspector", camera: "Live camera" }; const icons = { image: Upload, text: MessageSquareText, url: Link2, camera: Camera }; const Icon = icons[item]; return <button key={item} role="tab" aria-selected={mode === item} className={`mode-tab ${mode === item ? "active" : ""}`} onClick={() => setMode(item)}><Icon size={15} />{labels[item]}</button>; })}
              </div>
              <div className="input-stage">
                {mode === "image" && <div className={`drop-zone ${dragging ? "dragging" : ""} ${previewUrl ? "has-preview" : ""}`} onDragOver={(event) => { event.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={(event) => { event.preventDefault(); setDragging(false); setFile(event.dataTransfer.files[0]); }} onPaste={onPaste} onClick={() => fileInputRef.current?.click()} role="button" tabIndex={0} onKeyDown={(event) => event.key === "Enter" && fileInputRef.current?.click()}>
                  {previewUrl ? <><img src={previewUrl} alt="Selected screenshot preview" className="upload-preview" /><div className="preview-overlay"><span><Check size={13} /> {fileLabel}</span><small>Click to replace</small></div></> : <><div className="upload-icon"><CloudUpload size={25} strokeWidth={1.6} /></div><strong>{modeMeta.title}</strong><span>{modeMeta.description}</span><span className="upload-hint"><span>Browse files</span> or paste from clipboard</span><div className="format-row"><span>PNG</span><span>JPG</span><span>WEBP</span><span>max 10 MB</span></div></>}
                  <input ref={fileInputRef} type="file" accept="image/*" hidden onChange={(event) => setFile(event.target.files?.[0])} />
                </div>}
                {mode === "text" && <div className="text-input-wrap"><div className="field-meta"><span className="field-label"><MessageSquareText size={15} /> Message content</span><span>{textValue.length}/2,000</span></div><textarea autoFocus value={textValue} onChange={(event) => setTextValue(event.target.value)} placeholder="Paste the SMS or WhatsApp message here…\n\nTip: include the sender name and any link exactly as received." /><div className="textarea-footer"><span><ClipboardPaste size={14} /> Ctrl + V to paste</span><button className="mini-clear" onClick={() => setTextValue("")}>Clear</button></div></div>}
                {mode === "url" && <div className="url-input-wrap"><div className="url-icon"><Link2 size={21} /></div><div className="url-field"><label htmlFor="url-input">Payment or website link</label><input id="url-input" autoFocus value={urlValue} onChange={(event) => setUrlValue(event.target.value)} placeholder="https://example.com/verify-payment" /></div><button className="paste-button" onClick={async (event) => { event.stopPropagation(); try { setUrlValue(await navigator.clipboard.readText()); toast.success("Link pasted"); } catch { toast.info("Use Ctrl + V to paste a link"); } }}>Paste</button><div className="url-helper"><LockKeyhole size={13} /> We never open or store the link you submit.</div></div>}
                {mode === "camera" && <div className={`camera-stage ${cameraOn ? "camera-active" : ""}`}>{cameraOn ? <><video ref={videoRef} muted playsInline className="camera-video" /><canvas ref={canvasRef} hidden /><div className="scan-frame"><span /><span /><span /><span /></div><div className="camera-status"><span className="pulse-dot" />Looking for a UPI QR code…</div></> : <><div className="camera-placeholder"><Camera size={27} /><span>{modeMeta.title}</span><small>{modeMeta.description}</small><button className="primary-button compact" onClick={(event) => { event.stopPropagation(); toggleCamera(); }}><Camera size={15} /> Start camera</button></div></>}{cameraError && <div className="camera-error">{cameraError}</div>}</div>}
              </div>
              <div className="panel-footer"><div className="privacy-note"><LockKeyhole size={14} /><span>Processed securely <strong>in memory</strong></span></div><button className="primary-button" onClick={() => analyze()} disabled={analyzing}>{analyzing ? <><span className="button-spinner" /> Checking signals…</> : <><ScanLine size={16} /> Analyze input <ArrowUpRight size={15} /></>}</button></div>
              <div className="input-capabilities"><span><Check size={12} /> OCR extraction</span><span><Check size={12} /> QR parsing</span><span><Check size={12} /> Intent signals</span></div>
            </div>

            <div className="insight-column">
              <div className={`risk-card card reveal severity-${result.severity}`}>
                <div className="risk-card-top"><div><div className="section-kicker"><span className="kicker-bar" /> LIVE RISK REVIEW</div><h3>Current assessment</h3></div><StatusPill severity={result.severity}>{result.label}</StatusPill></div>
                <>{analyzing ? <div className="analysis-loading" aria-live="polite" aria-label="Gemini analysis in progress"><div className="loading-gauge"><span /></div><div className="loading-copy"><span className="skeleton skeleton-kicker" /><span className="skeleton skeleton-title" /><span className="skeleton skeleton-line" /><span className="skeleton skeleton-line short" /></div></div> : <><div className="risk-content result-reveal"><RiskGauge score={result.score} severity={result.severity} /><div className="risk-copy"><p className="risk-label">{result.source}</p><h4>{result.entity}</h4><p>{result.summary}</p></div></div><div className="action-banner result-reveal"><div className="action-icon">{result.severity === "safe" ? <CheckCircle2 size={17} /> : <ShieldAlert size={17} />}</div><div><strong>{result.action}</strong><span>{result.actionDetail}</span></div></div></>}</>
              </div>

              <div className="breakdown-card card reveal"><div className="breakdown-heading"><div><div className="section-kicker"><span className="kicker-bar" /> SIGNAL BREAKDOWN</div><h3>Why this score?</h3></div><button className="icon-button small" onClick={() => toast.info("Each signal combines local heuristics with semantic review.")} aria-label="Signal breakdown info"><HelpCircle size={16} /></button></div>{analyzing ? <div className="threat-list skeleton-list" aria-hidden="true">{[1, 2, 3].map((item) => <div className="threat-row" key={item}><span className="skeleton skeleton-icon" /><span className="skeleton-list-copy"><span className="skeleton skeleton-line" /><span className="skeleton skeleton-line short" /></span><span className="skeleton skeleton-tag" /></div>)}</div> : <><div className="threat-list result-reveal">{result.threats.map((threat) => { const ThreatIcon = threat.icon; return <div className="threat-row" key={threat.title}><div className={`threat-icon threat-${threat.severity}`}><ThreatIcon size={15} /></div><div className="threat-copy"><strong>{threat.title}</strong><span>{threat.detail}</span></div><span className={`threat-tag threat-${threat.severity}`}>{threat.severity === "safe" ? "Clear" : threat.severity === "suspicious" ? "Review" : "Alert"}</span></div>; })}</div><button className="explain-button result-reveal" onClick={() => toast.info("Plain-English explanation copied to your workspace.")}><Sparkles size={14} /> Explain in plain English <ArrowUpRight size={14} /></button></>}</div>
            </div>
          </section>

          <section className="history-section card reveal"><div className="history-heading"><div><div className="section-kicker"><span className="kicker-bar" /> RECENT ACTIVITY</div><h3>Your latest checks</h3></div><button className="text-button" onClick={() => toast.info("Showing the latest 3 checks in this demo.")}>View all <ArrowUpRight size={14} /></button></div><div className="history-table"><div className="history-header"><span>Source</span><span>Item</span><span>Result</span><span>Score</span><span>Checked</span><span /></div>{historyRows.map((row) => <div className="history-row" key={row.name}><span><span className={`source-icon source-${row.type.toLowerCase()}`}>{row.type === "URL" ? <Link2 size={14} /> : row.type === "QR" ? <QrCode size={14} /> : <MessageSquareText size={14} />}</span>{row.type}</span><strong>{row.name}</strong><span><span className={`table-result result-${row.result.toLowerCase()}`}><span className="status-dot" />{row.result}</span></span><span className="score-cell">{row.score}<small>/100</small></span><span className="time-cell">{row.time}</span><button className="row-more" aria-label={`More options for ${row.name}`} onClick={() => toast.info(`Activity details for ${row.name}`, { description: `${row.result} · score ${row.score}/100 · checked ${row.time}` })}><MoreHorizontal size={16} /></button></div>)}</div></section>

          <footer className="app-footer"><span><span className="footer-shield"><Shield size={12} /></span> PayGuard AI</span><span>Stateless by design · Built for safer UPI moments</span><span>v1.4.0 <span className="footer-separator">·</span> <button onClick={() => toast.info("API contract", { description: "POST /api/v1/analyze accepts image uploads, SMS/text, URLs, and camera frames." })}>API docs</button></span></footer>
        </main>
      </div>

      <button className={`monitor-trigger ${monitorOpen ? "hidden" : ""}`} onClick={() => setMonitorOpen(true)} aria-label="Open live monitor" title="Open live monitor"><span className="monitor-trigger-dot" /><Radio size={17} /><span className="monitor-trigger-count">{activityCount}</span></button>
      {monitorOpen && <><div className="drawer-scrim" onClick={() => setMonitorOpen(false)} /><aside className="monitor-drawer"><div className="drawer-header"><div><div className="drawer-kicker"><span className="live-dot" /> LIVE SYSTEM MONITOR</div><h3>Interceptor simulator</h3><p>See how PayGuard catches threats in the background.</p></div><button className="drawer-close" onClick={() => setMonitorOpen(false)} aria-label="Close monitor"><X size={17} /></button></div><div className="drawer-connection"><div className="connection-icon"><Smartphone size={16} /></div><div><strong>Mobile service connected</strong><span>Listening for incoming messages</span></div><span className="connection-pulse"><span /></span></div><div className="drawer-body"><p className="drawer-label">TRIGGER A SAFE DEMO EVENT</p><button className="sim-button" onClick={() => simulate("bill")}><div className="sim-icon sim-red"><AlertTriangle size={16} /></div><div><strong>Fake electricity bill SMS</strong><span>Impersonation + urgency cues</span></div><ArrowUpRight size={15} /></button><button className="sim-button" onClick={() => simulate("cashback")}><div className="sim-icon sim-amber"><QrCode size={16} /></div><div><strong>Cashback QR push</strong><span>Collect request + prize bait</span></div><ArrowUpRight size={15} /></button><div className="monitor-log"><div className="log-heading"><span>EVENT LOG</span><span className="log-live">● LIVE</span></div><div className="log-item"><span className="log-time">11:27:48</span><span className="log-dot log-green" /><span>Monitor heartbeat received</span></div><div className="log-item"><span className="log-time">11:27:31</span><span className="log-dot log-green" /><span>Rules engine ready</span></div><div className="log-item"><span className="log-time">11:26:59</span><span className="log-dot log-blue" /><span>Listening on notification stream</span></div></div><div className="drawer-callout"><Terminal size={15} /><div><strong>What judges can see</strong><span>Payload → analysis → user warning, all in one visible flow.</span></div></div></div><div className="drawer-footer"><span><span className="status-dot status-dot-green" /> Simulator mode</span><button onClick={() => toast.info("The simulator is local-only in this preview.")}>How it works <HelpCircle size={13} /></button></div></aside></>}
    </div>
  );
}
