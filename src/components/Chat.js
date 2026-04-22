import { useState, useRef, useEffect, useCallback } from "react";
import { C, Card } from "../utils/helpers";
import { CHAT_RESPONSES } from "../data/personas";

export default function Chat({ p }) {
  const firstName = p.name.split(" ")[0];
  const [msgs, setMsgs] = useState([
    { role:"ai", text:`Hi ${firstName}, I'm your SecureWealth coach. Your health score is ${p.score}/100 — ${p.scoreLabel}. What would you like to work on today?` }
  ]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const endRef = useRef();

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs, typing]);

  const speak = (text) => {
    const s = new SpeechSynthesisUtterance(text);
    s.lang = "en-IN"; s.rate = 1; s.pitch = 1;
    window.speechSynthesis.speak(s);
  };

  const send = useCallback((text) => {
    if (!text.trim()) return;
    setMsgs(m => [...m, { role:"user", text }]);
    setInput("");
    setTyping(true);
    setTimeout(() => {
      const l = text.toLowerCase();
      let resp = CHAT_RESPONSES.default;
      if (l.includes("home")||l.includes("goal")) resp = CHAT_RESPONSES.home;
      else if (l.includes("sip")||l.includes("market")) resp = CHAT_RESPONSES.sip;
      else if (l.includes("risk")) resp = CHAT_RESPONSES.risk;
      else if (l.includes("tax")||l.includes("80c")) resp = CHAT_RESPONSES.tax;
      setTyping(false);
      setMsgs(m => [...m, { role:"ai", text: resp }]);
      speak(resp);
    }, 1200);
  }, []);

  const startListening = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { alert("Speech not supported"); return; }
    const r = new SR(); r.lang = "en-IN"; r.start();
    r.onresult = (e) => { const t = e.results[0][0].transcript; setInput(t); send(t); };
  };

  const starters = [
    "How can I reach my home goal faster?",
    "Should I continue SIPs in this market?",
    "What's my biggest financial risk?",
    "How to maximise 80C tax savings?",
  ];

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <h2 style={{ fontSize: 20, fontWeight: 600, color: C.text, letterSpacing: "-0.3px" }}>AI wealth coach</h2>
        <p style={{ fontSize: 13, color: C.textMuted, marginTop: 3 }}>SecureWealth advisor</p>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 14 }}>
        {starters.map((s,i)=>(
          <button key={i} onClick={()=>send(s)}
            style={{ padding: "6px 12px", borderRadius: C.r, background: C.surface, border: `1px solid ${C.border}`, color: C.textSub, fontSize: 12, cursor: "pointer", fontFamily: "inherit", transition: "all 0.15s" }}
            onMouseEnter={e=>{e.currentTarget.style.borderColor=C.ink;e.currentTarget.style.color=C.text}}
            onMouseLeave={e=>{e.currentTarget.style.borderColor=C.border;e.currentTarget.style.color=C.textSub}}>
            {s}
          </button>
        ))}
      </div>

      <Card style={{ display: "flex", flexDirection: "column", height: 420 }}>
        <div style={{ flex: 1, overflowY: "auto", paddingBottom: 8 }}>
          {msgs.map((m,i)=>(
            <div key={i} style={{ display: "flex", gap: 10, marginBottom: 12, flexDirection: m.role==="user"?"row-reverse":"row" }}>
              <div style={{
                width: 28, height: 28, borderRadius: "50%", flexShrink: 0,
                background: m.role==="ai" ? C.ink : C.bg,
                border: `1px solid ${C.border}`,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 11, fontWeight: 600, color: m.role==="ai"?"#fff":C.textSub
              }}>
                {m.role==="ai" ? "W" : p.name[0]}
              </div>
              <div style={{
                maxWidth: "74%", padding: "9px 13px", borderRadius: 10, fontSize: 13,
                lineHeight: 1.55, whiteSpace: "pre-line",
                background: m.role==="ai" ? C.bg : C.ink,
                border: `1px solid ${C.border}`,
                color: m.role==="ai" ? C.text : "#fff"
              }}>
                {m.text}
              </div>
            </div>
          ))}
          {typing && (
            <div style={{ display: "flex", gap: 10, marginBottom: 12 }}>
              <div style={{ width:28,height:28,borderRadius:"50%",background:C.ink,border:`1px solid ${C.border}`,display:"flex",alignItems:"center",justifyContent:"center",fontSize:11,fontWeight:600,color:"#fff" }}>W</div>
              <div style={{ padding:"9px 13px",borderRadius:10,background:C.bg,border:`1px solid ${C.border}`,display:"flex",gap:4,alignItems:"center" }}>
                {[0,1,2].map(i=><span key={i} style={{ width:5,height:5,borderRadius:"50%",background:C.borderDark,display:"inline-block",animation:`bounce 1s ${i*0.15}s infinite` }}/>)}
              </div>
            </div>
          )}
          <div ref={endRef}/>
        </div>
        <div style={{ borderTop: `1px solid ${C.border}`, paddingTop: 12, display: "flex", gap: 8 }}>
          <input value={input} onChange={e=>setInput(e.target.value)}
            onKeyDown={e=>e.key==="Enter"&&!e.shiftKey&&(e.preventDefault(),send(input))}
            placeholder="Ask anything..."
            style={{ flex:1, background:C.bg, border:`1px solid ${C.border}`, borderRadius:C.r, padding:"9px 13px", color:C.text, fontSize:13, outline:"none", fontFamily:"inherit" }}/>
          <button onClick={startListening}
            style={{ width:38,height:38,borderRadius:C.r,background:C.bg,border:`1px solid ${C.border}`,cursor:"pointer",display:"flex",alignItems:"center",justifyContent:"center" }}>
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <rect x="4.5" y="1" width="5" height="7" rx="2.5" stroke={C.textSub} strokeWidth="1.2"/>
              <path d="M2 7a5 5 0 0010 0" stroke={C.textSub} strokeWidth="1.2" strokeLinecap="round"/>
              <line x1="7" y1="12" x2="7" y2="14" stroke={C.textSub} strokeWidth="1.2" strokeLinecap="round"/>
            </svg>
          </button>
          <button onClick={()=>send(input)}
            style={{ width:38,height:38,borderRadius:C.r,background:C.ink,border:"none",cursor:"pointer",display:"flex",alignItems:"center",justifyContent:"center" }}>
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M2 12L12 7L2 2V6L9 7L2 8V12Z" fill="white"/>
            </svg>
          </button>
        </div>
      </Card>
    </div>
  );
}