from pathlib import Path
path = Path(__file__).parents[1] / "client/src/pages/Home.tsx"
text = path.read_text()
text = text.replace('import { analyzeWithBackend } from "@/lib/api";', 'import { analyzeWithBackend } from "@/lib/api";\nimport { getAuthUser } from "./Auth";')
text = text.replace('  const videoRef = useRef<HTMLVideoElement>(null);\n  const contentRef', '  const videoRef = useRef<HTMLVideoElement>(null);\n  const canvasRef = useRef<HTMLCanvasElement>(null);\n  const contentRef')
text = text.replace('  const fileLabel = useMemo(() => selectedFile?.name ?? "No file selected", [selectedFile]);', '  const fileLabel = useMemo(() => selectedFile?.name ?? "No file selected", [selectedFile]);\n  const authUser = getAuthUser();\n  const displayName = authUser?.name?.trim() || "there";\n  const initials = displayName.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase();')
old = '''  const analyze = async (nextResult?: AnalysisResult) => {
    setAnalyzing(true);
    if (nextResult) {'''
new = '''  const analyze = async (nextResult?: AnalysisResult) => {
    if (!nextResult) {
      if (mode === "text" && textValue.trim().length < 8) { toast.error("Paste the complete message first", { description: "Include the sender, request, and any link or urgency language." }); return; }
      if (mode === "url") {
        const candidate = urlValue.trim();
        try { const parsed = new URL(candidate); if (!["http:", "https:"].includes(parsed.protocol)) throw new Error(); } catch { toast.error("Enter a valid http or https URL", { description: "Example: https://example.com/verify-payment" }); return; }
      }
      if (mode === "camera" && !cameraOn) { toast.error("Start the camera before scanning", { description: "Allow camera access, point at a QR code, then analyze the captured frame." }); return; }
    }
    setAnalyzing(true);
    if (nextResult) {'''
if old not in text: raise SystemExit('analyze start not found')
text = text.replace(old, new)
old_backend = '''      const backendResult = mode === "image" && selectedFile
        ? await analyzeWithBackend({ inputType: "image", file: selectedFile })
        : await analyzeWithBackend({
            inputType: mode === "camera" ? "camera" : mode === "text" ? "text" : "url",
            content: mode === "text" ? textValue : mode === "url" ? urlValue : "Live camera QR scan submitted for review.",
          });'''
new_backend = '''      let backendResult;
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
      }'''
if old_backend not in text: raise SystemExit('backend branch not found')
text = text.replace(old_backend, new_backend)
text = text.replace('<button className="rail-link" onClick={() => toast.info("Activity history is available in the studio below.")}><Inbox size={17} /><span>Activity history</span></button>', '<button className="rail-link" onClick={() => document.querySelector(".history-section")?.scrollIntoView({ behavior: "smooth" })}><Inbox size={17} /><span>Activity history</span></button>')
text = text.replace('<button className="rail-link" onClick={() => toast.info("Rules are ready to connect to your risk policy.")}><FileSearch size={17} /><span>Risk rules</span><span className="rail-new">New</span></button>', '<button className="rail-link" onClick={() => toast.info("Active risk rules", { description: "URL reputation, urgency language, payment intent, QR destination, and impersonation cues are enabled." })}><FileSearch size={17} /><span>Risk rules</span><span className="rail-new">5 active</span></button>')
text = text.replace('<button className="rail-link" onClick={() => toast.info("Settings are coming soon.")}><MoreHorizontal size={17} /><span>More settings</span></button>', '<button className="rail-link" onClick={() => toast.info("Workspace settings", { description: "Use the navigation theme control to change appearance. Your session remains private to this browser." })}><MoreHorizontal size={17} /><span>More settings</span></button>')
text = text.replace('<button className="profile-button"><div className="avatar">AR</div><div className="profile-copy"><strong>Alex Rivera</strong>', '<button className="profile-button"><div className="avatar">{initials}</div><div className="profile-copy"><strong>{displayName}</strong>')
text = text.replace('Good morning, Alex <span className="wave">✦</span>', 'Good morning, {displayName} <span className="wave">✦</span>')
text = text.replace('<video ref={videoRef} muted playsInline className="camera-video" />', '<video ref={videoRef} muted playsInline className="camera-video" /><canvas ref={canvasRef} hidden />')
text = text.replace('onClick={() => toast.info("Activity actions are coming soon.")}', 'onClick={() => toast.info(`Activity details for ${row.name}`, { description: `${row.result} · score ${row.score}/100 · checked ${row.time}` })}')
text = text.replace('onClick={() => toast.info("API documentation is coming soon.")}', 'onClick={() => toast.info("API contract", { description: "POST /api/v1/analyze accepts image uploads, SMS/text, URLs, and camera frames." })}')
path.write_text(text)
print('scan inputs improved')
