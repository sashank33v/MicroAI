"""
AI Microstructure Analyzer - FastAPI Backend
Handles image upload, analysis orchestration, reports, and mock data for demo.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid
import os
import shutil
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ── Groq Setup ──
from groq import Groq
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ── Conditional imports ──
try:
    import image_analysis
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False

# ── Pydantic Models ──

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    avatar: str
    role: str

class Phase(BaseModel):
    name: str
    percentage: float
    color: str

class DefectRegion(BaseModel):
    type: str
    location: str
    severity: str
    area_percentage: float
    circularity: Optional[float] = None
    aspect_ratio: Optional[float] = None

class GrainStats(BaseModel):
    count: int
    avg_size_um: float
    min_size_um: float
    max_size_um: float
    std_dev: float
    astm_number: float
    avg_circularity: Optional[float] = None
    avg_eccentricity: Optional[float] = None
    grain_uniformity: Optional[float] = None
    avg_aspect_ratio: Optional[float] = None
    intercept_grain_size_um: Optional[float] = None

class GrainDistBin(BaseModel):
    range: str
    count: int
    min_um: Optional[float] = None
    max_um: Optional[float] = None

class ImageQuality(BaseModel):
    sharpness: float
    contrast: float
    noise_score: float
    resolution: float
    dynamic_range: float
    overall: float
    histogram_quality: Optional[float] = None

class AnalysisResult(BaseModel):
    id: str
    image_id: str
    image_name: str
    material_type: str
    grain_stats: GrainStats
    phases: List[Phase]
    defects: List[DefectRegion]
    defect_percentage: float
    confidence: float
    ai_explanation: str
    processing_time: float
    status: str
    created_at: str
    overlay_base64: Optional[str] = None
    boundary_base64: Optional[str] = None
    original_base64: Optional[str] = None
    image_quality: Optional[ImageQuality] = None
    grain_distribution: Optional[List[GrainDistBin]] = None

class ChatRequest(BaseModel):
    message: str
    context: dict

class ReportCreate(BaseModel):
    analysis_id: str
    title: str
    notes: Optional[str] = None

class Report(BaseModel):
    id: str
    analysis_id: str
    title: str
    notes: str
    created_at: str

class CompareRequest(BaseModel):
    analysis_id_a: str
    analysis_id_b: str

# ── Upload Directory ──
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Mock Data ──

MOCK_USER = UserResponse(
    id="usr_001", name="Dr. Sarah Chen", email="sarah.chen@lab.edu", avatar="SC", role="researcher"
)

MOCK_ANALYSES: list[AnalysisResult] = [
    AnalysisResult(
        id="an_001", image_id="img_001", image_name="low_carbon_steel_1020.tiff",
        material_type="Low Carbon Steel (AISI 1020)",
        grain_stats=GrainStats(count=142, avg_size_um=45.3, min_size_um=12.1, max_size_um=98.7, std_dev=18.4, astm_number=6.2),
        phases=[Phase(name="Ferrite", percentage=85.0, color="#60a5fa"), Phase(name="Pearlite", percentage=15.0, color="#f97316")],
        defects=[
            DefectRegion(type="Porosity", location="Center-left quadrant", severity="Minor", area_percentage=1.8),
            DefectRegion(type="Micro-void", location="Upper-right boundary", severity="Negligible", area_percentage=0.5),
        ],
        defect_percentage=2.3, confidence=87.0,
        ai_explanation="The microstructure reveals a predominantly ferritic matrix with pearlite colonies distributed along grain boundaries, characteristic of low carbon steel (0.15-0.25%C). Equiaxed grain morphology suggests normalizing or full annealing. Average grain size of 45.3 \u03bcm (ASTM 6.2) indicates moderate refinement, predicting approximate tensile strength of 420-480 MPa. Minor porosity (2.3%) is localized and unlikely to affect bulk mechanical properties significantly.",
        processing_time=3.2, status="completed", created_at="2026-04-08T14:30:00Z",
    ),
    AnalysisResult(
        id="an_002", image_id="img_002", image_name="stainless_304_sample.tiff",
        material_type="Austenitic Stainless Steel (304)",
        grain_stats=GrainStats(count=98, avg_size_um=62.1, min_size_um=22.5, max_size_um=115.3, std_dev=24.7, astm_number=5.1),
        phases=[Phase(name="Austenite", percentage=95.0, color="#34d399"), Phase(name="Delta Ferrite", percentage=5.0, color="#a78bfa")],
        defects=[DefectRegion(type="Inclusion", location="Lower-right quadrant", severity="Negligible", area_percentage=0.5)],
        defect_percentage=0.5, confidence=92.0,
        ai_explanation="Clean austenitic microstructure typical of solution-annealed 304 stainless steel. The fully recrystallized equiaxed grains with annealing twins confirm proper heat treatment. Minimal delta ferrite (5%) is within specification. Excellent corrosion resistance and formability expected. No significant defects detected.",
        processing_time=2.8, status="completed", created_at="2026-04-07T09:15:00Z",
    ),
    AnalysisResult(
        id="an_003", image_id="img_003", image_name="dual_phase_steel.tiff",
        material_type="Dual Phase Steel (DP600)",
        grain_stats=GrainStats(count=215, avg_size_um=28.7, min_size_um=8.3, max_size_um=67.4, std_dev=14.2, astm_number=7.5),
        phases=[Phase(name="Ferrite", percentage=70.0, color="#60a5fa"), Phase(name="Martensite", percentage=30.0, color="#ef4444")],
        defects=[DefectRegion(type="Inclusion", location="Upper-left quadrant", severity="Minor", area_percentage=1.2)],
        defect_percentage=1.2, confidence=84.0,
        ai_explanation="Dual-phase microstructure with ferrite matrix and martensite islands. Fine grain size (28.7 \u03bcm, ASTM 7.5) indicates controlled rolling and intercritical annealing. The ferrite-martensite combination delivers excellent strength-ductility balance. Estimated tensile strength 580-650 MPa with 20-25% elongation. Minor inclusions (1.2%) are non-critical.",
        processing_time=3.5, status="completed", created_at="2026-04-06T16:45:00Z",
    ),
    AnalysisResult(
        id="an_004", image_id="img_004", image_name="gray_cast_iron.tiff",
        material_type="Gray Cast Iron (Class 30)",
        grain_stats=GrainStats(count=67, avg_size_um=89.4, min_size_um=34.2, max_size_um=178.5, std_dev=38.1, astm_number=3.8),
        phases=[
            Phase(name="Pearlite", percentage=60.0, color="#f97316"),
            Phase(name="Ferrite", percentage=25.0, color="#60a5fa"),
            Phase(name="Graphite Flakes", percentage=15.0, color="#6b7280"),
        ],
        defects=[DefectRegion(type="Graphite clustering", location="Center region", severity="Moderate", area_percentage=4.1)],
        defect_percentage=4.1, confidence=79.0,
        ai_explanation="Gray cast iron microstructure showing Type A graphite flakes in a pearlitic-ferritic matrix. Flake graphite morphology provides good vibration damping and machinability. Coarse grain size (89.4 \u03bcm) and irregular graphite distribution suggest moderate cooling rate. Estimated tensile strength 200-250 MPa. The graphite clustering (4.1%) in the center region warrants attention for load-bearing applications.",
        processing_time=4.1, status="completed", created_at="2026-04-05T11:20:00Z",
    ),
    AnalysisResult(
        id="an_005", image_id="img_005", image_name="tool_steel_d2.tiff",
        material_type="Tool Steel (AISI D2)",
        grain_stats=GrainStats(count=187, avg_size_um=15.2, min_size_um=4.8, max_size_um=42.1, std_dev=9.3, astm_number=9.0),
        phases=[
            Phase(name="Tempered Martensite", percentage=75.0, color="#ef4444"),
            Phase(name="Retained Austenite", percentage=15.0, color="#34d399"),
            Phase(name="Chromium Carbides", percentage=10.0, color="#fbbf24"),
        ],
        defects=[DefectRegion(type="Carbide clustering", location="Upper-right quadrant", severity="Moderate", area_percentage=3.8)],
        defect_percentage=3.8, confidence=81.0,
        ai_explanation="High-carbon high-chromium tool steel showing tempered martensite matrix with chromium carbide particles. Very fine grain size (15.2 \u03bcm, ASTM 9.0) from controlled heat treatment provides excellent hardness (58-62 HRC). Retained austenite (15%) is slightly elevated; sub-zero treatment could improve dimensional stability. Carbide clustering in upper-right quadrant may reduce impact toughness locally.",
        processing_time=3.9, status="completed", created_at="2026-04-04T08:55:00Z",
    ),
]

MOCK_REPORTS: list[Report] = [
    Report(id="rpt_001", analysis_id="an_001", title="Steel 1020 - Batch QC Report", notes="Acceptable quality. Minor porosity within spec.", created_at="2026-04-08T15:00:00Z"),
    Report(id="rpt_002", analysis_id="an_002", title="SS304 Solution Anneal Verification", notes="Confirmed proper heat treatment. Ready for service.", created_at="2026-04-07T10:00:00Z"),
    Report(id="rpt_003", analysis_id="an_004", title="Cast Iron Evaluation", notes="Graphite clustering noted. Recommend re-melt for critical parts.", created_at="2026-04-05T12:00:00Z"),
]

# ── App Setup ──

app = FastAPI(title="AI Microstructure Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Auth Routes ──

@app.post("/api/auth/login")
async def login(body: UserLogin):
    if body.email == "sarah.chen@lab.edu" and body.password == "demo123":
        return {"user": MOCK_USER.model_dump(), "token": "demo_token_" + uuid.uuid4().hex[:8]}
    raise HTTPException(401, "Invalid credentials")

@app.post("/api/auth/register")
async def register(body: UserRegister):
    return {"user": {"id": "usr_" + uuid.uuid4().hex[:6], "name": body.name, "email": body.email, "avatar": body.name[:2].upper(), "role": "student"}, "token": "tok_" + uuid.uuid4().hex[:8]}

@app.get("/api/auth/me")
async def get_current_user():
    return MOCK_USER.model_dump()

# ── Upload Route ──

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    image_id = "img_" + uuid.uuid4().hex[:8]
    ext = os.path.splitext(file.filename or "image.png")[1] or ".png"
    save_path = os.path.join(UPLOAD_DIR, f"{image_id}{ext}")
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"image_id": image_id, "filename": file.filename, "path": save_path, "size": os.path.getsize(save_path)}

# ── Analysis Routes ──

@app.post("/api/analyze/{image_id}")
async def run_analysis(image_id: str, material_type: str = Query("Unknown"), scale_um_per_px: float = Query(0.5)):
    # Check if image exists in uploads
    matching = [f for f in os.listdir(UPLOAD_DIR) if f.startswith(image_id)]
    if matching and CV_AVAILABLE:
        image_path = os.path.join(UPLOAD_DIR, matching[0])
        try:
            result = image_analysis.analyze_microstructure(image_path, scale_um_per_px=scale_um_per_px, material_type=material_type)
            analysis_id = "an_" + uuid.uuid4().hex[:6]
            # Build grain stats with new fields
            gs_data = result["grain_stats"]
            grain_stats = GrainStats(**gs_data)
            # Build image quality
            iq_data = result.get("image_quality", {})
            image_quality = ImageQuality(**iq_data) if iq_data else None
            # Build grain distribution
            gd_data = result.get("grain_distribution", [])
            grain_dist = [GrainDistBin(**b) for b in gd_data] if gd_data else None
            # Infer material type from phases
            phase_names = [p["name"].lower() for p in result["phases"]]
            if any("martensite" in n for n in phase_names) and any("ferrite" in n for n in phase_names):
                mat_type = "Dual Phase Steel (Ferrite-Martensite)"
            elif any("martensite" in n for n in phase_names):
                mat_type = "Martensitic Steel"
            elif any("pearlite" in n for n in phase_names) and any("ferrite" in n for n in phase_names):
                mat_type = "Carbon Steel (Ferrite-Pearlite)"
            elif any("bainite" in n for n in phase_names):
                mat_type = "Bainitic Steel"
            elif any("graphite" in n for n in phase_names):
                mat_type = "Cast Iron"
            else:
                mat_type = "Metallic Alloy - Automated Detection"
            analysis = AnalysisResult(
                id=analysis_id, image_id=image_id, image_name=matching[0],
                material_type=mat_type,
                grain_stats=grain_stats,
                phases=[Phase(**p) for p in result["phases"]],
                defects=[DefectRegion(**d) for d in result["defects"]],
                defect_percentage=result["defect_percentage"],
                confidence=result["confidence"],
                ai_explanation=result["ai_explanation"],
                processing_time=result["processing_time"],
                status="completed", created_at=datetime.utcnow().isoformat() + "Z",
                overlay_base64=result.get("overlay_base64"),
                boundary_base64=result.get("boundary_base64"),
                original_base64=result.get("original_base64"),
                image_quality=image_quality,
                grain_distribution=grain_dist,
            )
            MOCK_ANALYSES.insert(0, analysis)
            return analysis.model_dump()
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(500, f"Analysis failed: {str(e)}")
    # Fallback: return first mock analysis with updated id
    fallback = MOCK_ANALYSES[0].model_dump()
    fallback["id"] = "an_" + uuid.uuid4().hex[:6]
    fallback["image_id"] = image_id
    fallback["created_at"] = datetime.utcnow().isoformat() + "Z"
    return fallback

@app.get("/api/analyses")
async def list_analyses(limit: int = Query(20, ge=1, le=100)):
    return MOCK_ANALYSES[:limit]

@app.get("/api/analyses/{analysis_id}")
async def get_analysis(analysis_id: str):
    for a in MOCK_ANALYSES:
        if a.id == analysis_id:
            return a.model_dump()
    raise HTTPException(404, "Analysis not found")

# ── Reports Routes ──

@app.get("/api/reports")
async def list_reports():
    return MOCK_REPORTS

@app.post("/api/reports")
async def create_report(body: ReportCreate):
    report = Report(
        id="rpt_" + uuid.uuid4().hex[:6], analysis_id=body.analysis_id,
        title=body.title, notes=body.notes or "", created_at=datetime.utcnow().isoformat() + "Z",
    )
    MOCK_REPORTS.insert(0, report)
    return report.model_dump()

@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    for r in MOCK_REPORTS:
        if r.id == report_id:
            return r.model_dump()
    raise HTTPException(404, "Report not found")

@app.delete("/api/reports/{report_id}")
async def delete_report(report_id: str):
    for i, r in enumerate(MOCK_REPORTS):
        if r.id == report_id:
            MOCK_REPORTS.pop(i)
            return {"ok": True}
    raise HTTPException(404, "Report not found")

# ── Compare Route ──

@app.post("/api/compare")
async def compare_analyses(body: CompareRequest):
    a, b = None, None
    for an in MOCK_ANALYSES:
        if an.id == body.analysis_id_a:
            a = an
        if an.id == body.analysis_id_b:
            b = an
    if not a or not b:
        raise HTTPException(404, "One or both analyses not found")
    return {
        "a": a.model_dump(), "b": b.model_dump(),
        "comparison": {
            "grain_size_diff": round(abs(a.grain_stats.avg_size_um - b.grain_stats.avg_size_um), 1),
            "confidence_diff": round(abs(a.confidence - b.confidence), 1),
            "defect_diff": round(abs(a.defect_percentage - b.defect_percentage), 1),
            "summary": f"Analysis A ({a.material_type}) has {'finer' if a.grain_stats.avg_size_um < b.grain_stats.avg_size_um else 'coarser'} grain structure compared to B ({b.material_type}). "
                       f"Defect levels: A={a.defect_percentage}%, B={b.defect_percentage}%.",
        },
    }

# ── Chat Route ──

@app.post("/api/chat")
async def chat_with_ai(body: ChatRequest):
    if not groq_client:
        ctx = body.context
        reply = (
            f"### Metallurgical Analysis Insight (Offline Mode)\n\n"
            f"I am currently in **Offline Mode** because no `GROQ_API_KEY` was detected. "
            f"However, based on the vision telemetry for this **{ctx.get('material_type', 'Sample')}**:\n\n"
            f"- **Grain Distribution**: Optimized detection of `{ctx.get('grain_stats', {}).get('count')}` regions.\n"
            f"- **Structural Integrity**: The defect percentage is **{ctx.get('defect_percentage', 0):.2f}%**, "
            f"which is {'within' if ctx.get('defect_percentage', 0) < 5 else 'outside'} typical safety tolerances.\n"
            f"- **Crystalline State**: Mean grain size of **{ctx.get('grain_stats', {}).get('avg_size_um', 0)} μm** detected.\n\n"
            f"To enable deep metallurgical modeling and interactive engineering advice, please configure a Groq API key."
        )
        return {"reply": reply}
    
    ctx = body.context
    phases_text = ', '.join([f"{p.get('name')} ({p.get('percentage')}%)" for p in ctx.get('phases', [])])
    system_prompt = (
        f"You are a Senior Metallurgical Scientist with 25 years of experience in materials engineering, microscopy, and failure analysis.\n"
        f"The user is viewing an AI microstructure analysis report for the material family: {ctx.get('material_type', 'Unknown')}.\n"
        f"Relevant Stats: Grain Count: {ctx.get('grain_stats', {}).get('count')}, Avg Grain Size: {ctx.get('grain_stats', {}).get('avg_size_um')} um, Defect %: {ctx.get('defect_percentage')}%.\n"
        f"Phases Detected: {phases_text}\n\n"
        f"CRITICAL FORMATTING INSTRUCTIONS:\n"
        f"1. You MUST use rich Markdown formatting extensively.\n"
        f"2. Incorporate organized **Data Tables** (Markdown `| col | col |`) for comparative insights or metrics.\n"
        f"3. Where requested or relevant, create beautiful **ASCII-art flowsheets / tree-diagrams** inside ```text code blocks to illustrate metallurgical processes (e.g., cooling curves, phase transformations).\n"
        f"4. Use lists, bold text, and blockquotes to make the output highly readable and visually striking.\n"
        f"Do not refuse to answer. Provide your best estimate as a senior engineer."
    )
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": body.message}
            ],
            temperature=0.4,
            max_tokens=300
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

# ── Dashboard Stats ──

@app.get("/api/dashboard/stats")
async def dashboard_stats():
    total = len(MOCK_ANALYSES)
    avg_conf = round(sum(a.confidence for a in MOCK_ANALYSES) / total, 1) if total else 0
    return {
        "total_analyses": total,
        "total_reports": len(MOCK_REPORTS),
        "avg_confidence": avg_conf,
        "avg_grain_size": round(sum(a.grain_stats.avg_size_um for a in MOCK_ANALYSES) / total, 1) if total else 0,
        "total_defects_found": sum(len(a.defects) for a in MOCK_ANALYSES),
    }

# ── Run ──

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
