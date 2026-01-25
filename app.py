import os
import gradio as gr
from pypdf import PdfReader
import requests

# Groq API key (set: export GROQ_API_KEY="gsk_...")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY is None:
    raise ValueError("Set GROQ_API_KEY env var!")

def extract_pdf_text(pdf_file):
    if pdf_file is None:
        return ""
    reader = PdfReader(pdf_file)
    pages_text = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages_text.append(text)
    return "\n\n".join(pages_text)[:10000]

def analyze_proposal(proposal_text):
    if not proposal_text.strip():
        return "No text extracted from PDF."
    
    # TWO-STEP ANALYSIS: 1) Summary → 2) Critical Analysis
    prompt = f"""
You are a **VP of Strategy** reviewing business proposals. Follow this **exact 2-step process**:

**STEP 1: 1-PARAGRAPH SUMMARY** (objective facts only)
What is the proposal? Core idea? Budget? Timeline? Expected ROI?

**STEP 2: CRITICAL FEASIBILITY ANALYSIS** using **industry-standard metrics**:

**MARKET METRICS** (benchmark vs competitors):
- TAM/SAM/SOM: Realistic market size?
- Market Growth Rate: Industry expanding?
- Competition: Who's winning? Differentiation?
- CAC vs LTV: Acquisition cost vs customer value?

**FINANCIAL METRICS** (stress test numbers):
- ROI Reality Check: Aggressive/Realistic/Too optimistic?
- Payback Period: <6mo=excellent, 6-12mo=good, >12mo=risky
- Gross Margin: >60% ideal for SaaS, 30-50% retail
- Unit Economics: CAC < 1/3 LTV?

**EXECUTION METRICS**:
- Team Skills: Experience match?
- Timeline: Realistic for scope?
- Technical Risk: Dependencies/scalability?

**FEASIBILITY VERDICT**: FEASIBLE / FEASIBLE w/ADJUSTMENTS / NOT FEASIBLE

**OUTPUT EXACT FORMAT**:

---

**📄 EXECUTIVE SUMMARY**
[1 paragraph]

**📊 FEASIBILITY ANALYSIS**

**MARKET (0-10):**
- [Score] - [Reasoning vs benchmarks]

**FINANCIALS (0-10):**
- [Score] - [ROI/Payback stress test]

**EXECUTION (0-10):**
- [Score] - [Team/timeline risks]

**OVERALL SCORE: X/10**
**VERDICT: [FEASIBLE/FEASIBLE w/ADJUSTMENTS/NOT FEASIBLE]**

**🔴 TOP 3 RED FLAGS:**
1. [Critical flaw #1]
2. [Critical flaw #2]
3. [Critical flaw #3]

**✅ 3 RECOMMENDATIONS:**
1. [Fix #1]
2. [Fix #2]
3. [Fix #3]

---

Proposal:
{proposal_text}

Be brutally honest. Use real industry benchmarks. Never sugarcoat.
"""
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 1200,
    }
    
    try:
        resp = requests.post(url, json=data, headers=headers, timeout=45)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_pdf(pdf_file):
    text = extract_pdf_text(pdf_file)
    return analyze_proposal(text)

demo = gr.Interface(
    fn=analyze_pdf,
    inputs=gr.File(label="📁 Upload Business Proposal PDF", file_types=[".pdf"]),
    outputs=gr.Textbox(label="📊 Professional Analysis", lines=30),
    title="🚀 Business Feasibility Analyzer Pro",
    description="AI-powered analysis with market benchmarks, financial stress tests, and honest feedback."
)

if __name__ == "__main__":
    demo.launch(share=True)
