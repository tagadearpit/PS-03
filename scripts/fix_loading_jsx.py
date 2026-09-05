from pathlib import Path
path = Path(__file__).parents[1] / "client/src/pages/Home.tsx"
text = path.read_text()
text = text.replace(': <div className="threat-list result-reveal">{result.threats.map((threat) => {', ': <><div className="threat-list result-reveal">{result.threats.map((threat) => {', 1)
needle = '</div><button className="explain-button" onClick={() => toast.info("Plain-English explanation copied to your workspace.")}>'
text = text.replace(needle, '</div><button className="explain-button result-reveal" onClick={() => toast.info("Plain-English explanation copied to your workspace.")}>', 1)
text = text.replace('<Sparkles size={14} /> Explain in plain English <ArrowUpRight size={14} /></button></div>\n            </div>', '<Sparkles size={14} /> Explain in plain English <ArrowUpRight size={14} /></button></>}\n            </div>', 1)
path.write_text(text)
print("jsx fixed")
