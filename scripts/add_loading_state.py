from pathlib import Path

path = Path(__file__).parents[1] / "client/src/pages/Home.tsx"
text = path.read_text()
old = '<div className="risk-content"><RiskGauge score={result.score} severity={result.severity} /><div className="risk-copy"><p className="risk-label">{result.source}</p><h4>{result.entity}</h4><p>{result.summary}</p></div></div>\n                <div className="action-banner"><div className="action-icon">{result.severity === "safe" ? <CheckCircle2 size={17} /> : <ShieldAlert size={17} />}</div><div><strong>{result.action}</strong><span>{result.actionDetail}</span></div></div>'
new = '<>{analyzing ? <div className="analysis-loading" aria-live="polite" aria-label="Gemini analysis in progress"><div className="loading-gauge"><span /></div><div className="loading-copy"><span className="skeleton skeleton-kicker" /><span className="skeleton skeleton-title" /><span className="skeleton skeleton-line" /><span className="skeleton skeleton-line short" /></div></div> : <><div className="risk-content result-reveal"><RiskGauge score={result.score} severity={result.severity} /><div className="risk-copy"><p className="risk-label">{result.source}</p><h4>{result.entity}</h4><p>{result.summary}</p></div></div><div className="action-banner result-reveal"><div className="action-icon">{result.severity === "safe" ? <CheckCircle2 size={17} /> : <ShieldAlert size={17} />}</div><div><strong>{result.action}</strong><span>{result.actionDetail}</span></div></div></>}</>'
if old not in text:
    raise SystemExit("risk markup not found")
text = text.replace(old, new, 1)
old2 = '<div className="threat-list">{result.threats.map((threat) => {'
new2 = '{analyzing ? <div className="threat-list skeleton-list" aria-hidden="true">{[1, 2, 3].map((item) => <div className="threat-row" key={item}><span className="skeleton skeleton-icon" /><span className="skeleton-list-copy"><span className="skeleton skeleton-line" /><span className="skeleton skeleton-line short" /></span><span className="skeleton skeleton-tag" /></div>)}</div> : <div className="threat-list result-reveal">{result.threats.map((threat) => {'
if old2 not in text:
    raise SystemExit("threat markup not found")
text = text.replace(old2, new2, 1)
path.write_text(text)
print("loading state inserted")
