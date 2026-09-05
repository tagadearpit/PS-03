from pathlib import Path
path = Path(__file__).parents[1] / "client/src/pages/Home.tsx"
text = path.read_text()
old = '<button className={`monitor-trigger ${monitorOpen ? "hidden" : ""}`} onClick={() => setMonitorOpen(true)}><span className="monitor-trigger-dot" /><Radio size={16} /> Live monitor <span className="monitor-trigger-count">{activityCount}</span></button>'
new = '<button className={`monitor-trigger ${monitorOpen ? "hidden" : ""}`} onClick={() => setMonitorOpen(true)} aria-label="Open live monitor" title="Open live monitor"><span className="monitor-trigger-dot" /><Radio size={17} /><span className="monitor-trigger-count">{activityCount}</span></button>'
if old not in text:
    raise SystemExit("monitor trigger not found")
path.write_text(text.replace(old, new, 1))
