from pathlib import Path
path = Path(__file__).parents[1] / "client/src/pages/Home.tsx"
text = path.read_text()
text = text.replace('type AnalysisResult = {\n', '''type UpiDetails = {
  upi_id?: string | null;
  display_name?: string | null;
  phone_number?: string | null;
  amount?: string | null;
  currency?: string | null;
  note?: string | null;
  merchant_code?: string | null;
  confidence?: "low" | "medium" | "high";
};

type AnalysisResult = {
''')
text = text.replace('  threats: Threat[];\n  timestamp: string;', '  threats: Threat[];\n  upiDetails?: UpiDetails | null;\n  plainEnglish: string;\n  timestamp: string;')
text = text.replace('  timestamp: "Just now",\n};', '  plainEnglish: "This payment identity looks consistent with the visible merchant context. Review the payee name and amount before approving anything.",\n  upiDetails: { upi_id: "bluetokai@icici", display_name: "Blue Tokai Coffee", amount: "420.00", currency: "INR", confidence: "high" },\n  timestamp: "Just now",\n};', 1)
text = text.replace('  const [toastMessage, setToastMessage] = useState("Awaiting next input");', '  const [toastMessage, setToastMessage] = useState("Awaiting next input");\n  const [explanationOpen, setExplanationOpen] = useState(false);')
text = text.replace('        setToastMessage("Analysis complete");', '        setExplanationOpen(false);\n        setToastMessage("Analysis complete");')
old = '      setResult({ ...backendResult, actionDetail: backendResult.action_detail, timestamp: backendResult.timestamp, threats: backendResult.threats.map((threat) => ({ ...threat, icon: threat.severity === "safe" ? CheckCircle2 : threat.severity === "suspicious" ? AlertTriangle : ShieldAlert })) });'
new = '      setResult({ ...backendResult, actionDetail: backendResult.action_detail, timestamp: backendResult.timestamp, plainEnglish: backendResult.plain_english || `${backendResult.summary} ${backendResult.action_detail}`, upiDetails: backendResult.upi_details, threats: backendResult.threats.map((threat) => ({ ...threat, icon: threat.severity === "safe" ? CheckCircle2 : threat.severity === "suspicious" ? AlertTriangle : ShieldAlert })) });'
if old not in text: raise SystemExit('backend result mapping not found')
text = text.replace(old, new)
text = text.replace('      setActivityCount((count) => count + 1);\n      setToastMessage("Gemini analysis complete");', '      setActivityCount((count) => count + 1);\n      setExplanationOpen(false);\n      setToastMessage("Gemini analysis complete");', 1)
needle = '<div className="action-banner result-reveal"><div className="action-icon">{result.severity === "safe" ? <CheckCircle2 size={17} /> : <ShieldAlert size={17} />}</div><div><strong>{result.action}</strong><span>{result.actionDetail}</span></div></div>'
insert = needle + '''{result.upiDetails && <div className="upi-details-card result-reveal"><div className="upi-details-heading"><div><div className="section-kicker"><span className="kicker-bar" /> UPI IDENTITY FOUND</div><h4>Payment information</h4></div><span className={`confidence-badge confidence-${result.upiDetails.confidence || "low"}`}>{result.upiDetails.confidence || "low"} confidence</span></div><div className="upi-details-grid">{result.upiDetails.display_name && <div><span>Name</span><strong>{result.upiDetails.display_name}</strong></div>}{result.upiDetails.upi_id && <div><span>UPI ID</span><strong>{result.upiDetails.upi_id}</strong></div>}{result.upiDetails.phone_number && <div><span>Phone number</span><strong>{result.upiDetails.phone_number}</strong></div>}{result.upiDetails.amount && <div><span>Amount</span><strong>{result.upiDetails.currency || "INR"} {result.upiDetails.amount}</strong></div>}{result.upiDetails.note && <div><span>Payment note</span><strong>{result.upiDetails.note}</strong></div>}{result.upiDetails.merchant_code && <div><span>Merchant code</span><strong>{result.upiDetails.merchant_code}</strong></div>}</div><p className="upi-disclaimer">Shown only from QR/OCR/text evidence. Confirm the recipient independently before paying.</p></div>}'''
if needle not in text: raise SystemExit('action banner not found')
text = text.replace(needle, insert, 1)
old_explain = '<button className="explain-button result-reveal" onClick={() => toast.info("Plain-English explanation copied to your workspace.")}><Sparkles size={14} /> Explain in plain English <ArrowUpRight size={14} /></button>'
new_explain = '<button className="explain-button result-reveal" onClick={() => setExplanationOpen((open) => !open)}><Sparkles size={14} /> {explanationOpen ? "Hide plain-English explanation" : "Explain in plain English"} <ArrowUpRight size={14} /></button>{explanationOpen && <div className="plain-english-panel result-reveal"><Sparkles size={15} /><p>{result.plainEnglish}</p></div>}'
if old_explain not in text: raise SystemExit('explain button not found')
text = text.replace(old_explain, new_explain, 1)
path.write_text(text)

api = Path(__file__).parents[1] / "client/src/lib/api.ts"
at = api.read_text()
at = at.replace('  trace_id: string;\n};', '''  trace_id: string;
  plain_english: string;
  upi_details?: {
    upi_id?: string | null;
    display_name?: string | null;
    phone_number?: string | null;
    amount?: string | null;
    currency?: string | null;
    note?: string | null;
    merchant_code?: string | null;
    confidence?: "low" | "medium" | "high";
  } | null;
};''')
api.write_text(at)
print('frontend UPI details added')
