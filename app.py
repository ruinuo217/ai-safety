"""
AI 工安解決方案 — Portfolio 首頁

一個入口，三個專案 Demo
啟動方式：
  cd ~/portfolio
  uvicorn app:app --reload --host 0.0.0.0 --port 8080
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI(title="AI 工安解決方案")

HTML = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI-Powered Construction Safety</title>
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
:root{
  --bg:#000;--surface:rgba(255,255,255,0.04);--surface-hover:rgba(255,255,255,0.08);
  --border:rgba(255,255,255,0.08);--border-hover:rgba(255,255,255,0.18);
  --text-primary:rgba(255,255,255,0.92);--text-secondary:rgba(255,255,255,0.55);
  --text-tertiary:rgba(255,255,255,0.35);--accent:#2997ff;--accent-green:#30d158;
  --radius:20px;--radius-sm:12px;
}
html{scroll-behavior:smooth;}
body{
  font-family:"SF Pro Display","SF Pro Text",-apple-system,BlinkMacSystemFont,
    "Helvetica Neue","Segoe UI","Microsoft JhengHei",sans-serif;
  background:var(--bg);color:var(--text-primary);
  min-height:100vh;-webkit-font-smoothing:antialiased;
  text-rendering:optimizeLegibility;
}

/* ── Nav ── */
nav{
  position:fixed;top:0;left:0;right:0;z-index:100;
  background:rgba(0,0,0,0.72);backdrop-filter:saturate(180%) blur(20px);
  -webkit-backdrop-filter:saturate(180%) blur(20px);
  border-bottom:1px solid rgba(255,255,255,0.06);
}
nav .inner{
  max-width:1080px;margin:0 auto;padding:0 24px;
  height:52px;display:flex;align-items:center;justify-content:space-between;
}
nav .logo{font-size:15px;font-weight:600;letter-spacing:-0.3px;color:var(--text-primary);}
nav .links{display:flex;gap:28px;}
nav .links a{
  font-size:13px;color:var(--text-secondary);text-decoration:none;
  transition:color 0.2s;letter-spacing:0.01em;
}
nav .links a:hover{color:var(--text-primary);}

/* ── Hero ── */
.hero{
  padding:160px 24px 100px;text-align:center;
  background:radial-gradient(ellipse 80% 60% at 50% -10%,rgba(41,151,255,0.12),transparent);
}
.hero .overline{
  font-size:16px;font-weight:500;color:var(--accent);
  letter-spacing:0.04em;margin-bottom:16px;
}
.hero h1{
  font-size:clamp(40px,7vw,72px);font-weight:700;
  letter-spacing:-0.03em;line-height:1.08;
  margin-bottom:20px;
  background:linear-gradient(180deg,#fff 0%,rgba(255,255,255,0.6) 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.hero .subtitle{
  font-size:clamp(17px,2.2vw,21px);color:var(--text-secondary);
  max-width:640px;margin:0 auto 40px;line-height:1.6;font-weight:400;
  letter-spacing:-0.01em;
}
.hero .cta-row{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;}
.btn-filled{
  display:inline-flex;align-items:center;gap:6px;
  padding:12px 28px;border-radius:980px;border:none;cursor:pointer;
  background:var(--accent);color:#fff;font-size:15px;font-weight:500;
  text-decoration:none;transition:all 0.25s;letter-spacing:-0.01em;
}
.btn-filled:hover{background:#0077ed;transform:scale(1.03);}
.btn-ghost{
  display:inline-flex;align-items:center;gap:6px;
  padding:12px 28px;border-radius:980px;cursor:pointer;
  background:transparent;border:1.5px solid rgba(255,255,255,0.2);
  color:var(--text-primary);font-size:15px;font-weight:500;
  text-decoration:none;transition:all 0.25s;letter-spacing:-0.01em;
}
.btn-ghost:hover{border-color:rgba(255,255,255,0.5);background:rgba(255,255,255,0.05);}

/* ── Section titles ── */
.section{padding:100px 24px;max-width:1080px;margin:0 auto;}
.section-label{
  font-size:14px;font-weight:600;color:var(--accent);
  letter-spacing:0.06em;text-transform:uppercase;margin-bottom:8px;
}
.section-title{
  font-size:clamp(32px,4.5vw,48px);font-weight:700;
  letter-spacing:-0.025em;line-height:1.12;margin-bottom:14px;
}
.section-sub{
  font-size:17px;color:var(--text-secondary);max-width:560px;line-height:1.6;
  margin-bottom:56px;
}

/* ── Featured project ── */
.featured{
  border-radius:var(--radius);overflow:hidden;position:relative;
  background:linear-gradient(165deg,#0a1628 0%,#0c1e3a 40%,#0a1628 100%);
  border:1px solid rgba(41,151,255,0.15);padding:56px 48px;
  transition:border-color 0.4s;
}
.featured:hover{border-color:rgba(41,151,255,0.35);}
.featured::before{
  content:"";position:absolute;top:-1px;left:50%;transform:translateX(-50%);
  width:240px;height:1px;
  background:linear-gradient(90deg,transparent,var(--accent),transparent);
}
.featured .badge{
  display:inline-block;padding:5px 14px;border-radius:980px;
  background:rgba(41,151,255,0.12);color:var(--accent);
  font-size:12px;font-weight:600;letter-spacing:0.05em;
  text-transform:uppercase;margin-bottom:24px;
}
.featured h3{
  font-size:32px;font-weight:700;letter-spacing:-0.02em;margin-bottom:16px;
}
.featured .desc{
  font-size:16px;color:var(--text-secondary);line-height:1.7;
  max-width:580px;margin-bottom:32px;
}
.featured .flow{
  display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:32px;
}
.flow-step{
  padding:8px 18px;border-radius:var(--radius-sm);
  background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);
  font-size:13px;font-weight:500;color:var(--text-primary);
}
.flow-arrow{color:var(--text-tertiary);font-size:16px;}
.featured .tags{display:flex;gap:8px;flex-wrap:wrap;}
.tag{
  padding:5px 14px;border-radius:980px;font-size:12px;font-weight:500;
  background:rgba(255,255,255,0.06);color:var(--text-secondary);
  letter-spacing:0.01em;
}
.featured .link-row{margin-top:32px;}

/* ── Project grid ── */
.projects-grid{
  display:grid;grid-template-columns:repeat(3,1fr);gap:16px;
}
@media(max-width:860px){.projects-grid{grid-template-columns:1fr;}}
.project-card{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--radius);padding:36px 32px;
  text-decoration:none;color:var(--text-primary);display:flex;flex-direction:column;
  transition:all 0.35s cubic-bezier(.25,.46,.45,.94);position:relative;overflow:hidden;
}
.project-card:hover{
  background:var(--surface-hover);border-color:var(--border-hover);
  transform:translateY(-4px);
}
.project-card .card-num{
  font-size:48px;font-weight:800;
  background:linear-gradient(180deg,rgba(255,255,255,0.08),rgba(255,255,255,0.02));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  line-height:1;margin-bottom:20px;letter-spacing:-0.04em;
}
.project-card h3{font-size:20px;font-weight:600;letter-spacing:-0.015em;margin-bottom:10px;}
.project-card .desc{
  font-size:14px;color:var(--text-secondary);line-height:1.65;
  margin-bottom:20px;flex:1;
}
.project-card .tags{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:16px;}
.project-card .card-footer{
  display:flex;align-items:center;justify-content:space-between;
  padding-top:16px;border-top:1px solid var(--border);
}
.project-card .port{font-size:12px;color:var(--text-tertiary);}
.project-card .arrow{
  width:28px;height:28px;border-radius:50%;
  background:rgba(255,255,255,0.06);
  display:flex;align-items:center;justify-content:center;
  font-size:14px;color:var(--text-secondary);
  transition:all 0.25s;
}
.project-card:hover .arrow{background:var(--accent);color:#fff;}

/* ── Tech strip ── */
.tech-strip{
  padding:60px 24px;text-align:center;
  border-top:1px solid var(--border);border-bottom:1px solid var(--border);
}
.tech-strip .label{
  font-size:12px;font-weight:600;color:var(--text-tertiary);
  letter-spacing:0.1em;text-transform:uppercase;margin-bottom:24px;
}
.tech-list{
  display:flex;gap:32px;justify-content:center;flex-wrap:wrap;
  max-width:800px;margin:0 auto;
}
.tech-item{
  font-size:15px;font-weight:500;color:var(--text-secondary);
  letter-spacing:-0.01em;transition:color 0.2s;
}
.tech-item:hover{color:var(--text-primary);}

/* ── Footer ── */
footer{
  padding:48px 24px;text-align:center;
}
footer p{font-size:13px;color:var(--text-tertiary);letter-spacing:-0.01em;}
footer a{color:var(--text-secondary);text-decoration:none;transition:color 0.2s;}
footer a:hover{color:var(--accent);}

/* ── Animation ── */
@keyframes fadeUp{
  from{opacity:0;transform:translateY(24px);}
  to{opacity:1;transform:translateY(0);}
}
.hero,.featured,.project-card,.section-label,.section-title,.section-sub{
  animation:fadeUp 0.7s ease-out both;
}
.project-card:nth-child(2){animation-delay:0.08s;}
.project-card:nth-child(3){animation-delay:0.16s;}
</style>
</head>
<body>

<!-- Nav -->
<nav>
  <div class="inner">
    <div class="logo">Reyna Kao</div>
    <div class="links">
      <a href="#featured">Featured</a>
      <a href="#projects">Projects</a>
      <a href="https://github.com/ruinuo217" target="_blank">GitHub</a>
    </div>
  </div>
</nav>

<!-- Hero -->
<section class="hero">
  <div class="overline">AI Engineering Portfolio</div>
  <h1>Construction Safety,<br>Reimagined with AI.</h1>
  <p class="subtitle">
    End-to-end AI solutions for workplace safety monitoring &mdash;
    from real-time image detection to automated alerting and reporting.
  </p>
  <div class="cta-row">
    <a class="btn-filled" href="#featured">View Featured Project &darr;</a>
    <a class="btn-ghost" href="https://github.com/ruinuo217" target="_blank">GitHub &nearr;</a>
  </div>
</section>

<!-- Featured Project -->
<div class="section" id="featured">
  <div class="section-label">Featured</div>
  <div class="section-title">Full-Stack AI Safety System</div>
  <div class="section-sub">
    End-to-end pipeline: image input to human-readable reports, fully automated.
  </div>

  <a class="featured" href="http://127.0.0.1:8003" target="_blank" style="display:block;text-decoration:none;color:inherit;">
    <div class="badge">Core Project</div>
    <h3>Construction Safety Image Recognition<br>&amp; AI Alert System</h3>
    <div class="desc">
      Trained YOLOv8 for helmet detection, introduced KMeans auto-calibrated
      confidence thresholds to replace manual tuning. Built with LangGraph
      StateGraph for high/low risk routing, 3-retry loops, and
      Human-in-the-Loop supervisor review. LLM generates daily summary reports.
    </div>
    <div class="flow">
      <span class="flow-step">YOLOv8 Inference</span>
      <span class="flow-arrow">&rarr;</span>
      <span class="flow-step">KMeans Calibration</span>
      <span class="flow-arrow">&rarr;</span>
      <span class="flow-step">LangGraph Workflow</span>
      <span class="flow-arrow">&rarr;</span>
      <span class="flow-step">LLM Report</span>
    </div>
    <div class="tags">
      <span class="tag">YOLOv8</span>
      <span class="tag">LangGraph</span>
      <span class="tag">LangChain</span>
      <span class="tag">FastAPI</span>
      <span class="tag">scikit-learn</span>
      <span class="tag">KMeans</span>
      <span class="tag">Gemini API</span>
      <span class="tag">pandas</span>
    </div>
    <div class="link-row">
      <span class="btn-filled" style="font-size:14px;padding:10px 24px;">
        Launch Demo &rarr;
      </span>
    </div>
  </a>
</div>

<!-- Other Projects -->
<div class="section" id="projects">
  <div class="section-label">Projects</div>
  <div class="section-title">More Explorations</div>
  <div class="section-sub">
    Each project is independently built, covering AI engineering,
    frontend development, and system design.
  </div>

  <div class="projects-grid">
    <a class="project-card" href="http://127.0.0.1:8001" target="_blank">
      <div class="card-num">01</div>
      <h3>AI Safety Monitor</h3>
      <div class="desc">
        Upload construction site photos &rarr; Gemini multimodal AI detects violations &rarr;
        structured JSON report with regulations and alerts.
      </div>
      <div class="tags">
        <span class="tag">Gemini Vision</span>
        <span class="tag">JSON Schema</span>
        <span class="tag">Pillow</span>
      </div>
      <div class="card-footer">
        <span class="port">Port 8001</span>
        <span class="arrow">&nearr;</span>
      </div>
    </a>

    <a class="project-card" href="http://127.0.0.1:8000" target="_blank">
      <div class="card-num">02</div>
      <h3>RAG Knowledge Bot</h3>
      <div class="desc">
        Upload FAQ docs &rarr; embedding vector index &rarr; semantic search &rarr;
        Gemini generates precise answers with source citations.
      </div>
      <div class="tags">
        <span class="tag">RAG</span>
        <span class="tag">Embedding</span>
        <span class="tag">Cosine Similarity</span>
      </div>
      <div class="card-footer">
        <span class="port">Port 8000</span>
        <span class="arrow">&nearr;</span>
      </div>
    </a>

    <a class="project-card" href="http://127.0.0.1:8002" target="_blank">
      <div class="card-num">03</div>
      <h3>LLM Orchestration</h3>
      <div class="desc">
        Violation event &rarr; LangChain auto-executes 5-step AI pipeline:
        analyze &rarr; classify &rarr; lookup &rarr; alert &rarr; notify.
      </div>
      <div class="tags">
        <span class="tag">LangChain</span>
        <span class="tag">LCEL</span>
        <span class="tag">SafetyState</span>
      </div>
      <div class="card-footer">
        <span class="port">Port 8002</span>
        <span class="arrow">&nearr;</span>
      </div>
    </a>
  </div>
</div>

<!-- Tech Strip -->
<div class="tech-strip">
  <div class="label">Tech Stack</div>
  <div class="tech-list">
    <span class="tech-item">YOLOv8</span>
    <span class="tech-item">LangGraph</span>
    <span class="tech-item">LangChain</span>
    <span class="tech-item">FastAPI</span>
    <span class="tech-item">Gemini API</span>
    <span class="tech-item">RAG</span>
    <span class="tech-item">scikit-learn</span>
    <span class="tech-item">pandas</span>
    <span class="tech-item">Python</span>
  </div>
</div>

<!-- Footer -->
<footer>
  <p>Built by Reyna Kao &middot; <a href="https://github.com/ruinuo217" target="_blank">GitHub</a></p>
</footer>

</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML
