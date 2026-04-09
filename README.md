# MicroAI Command Center 🔬

## Overview
**MicroAI** is an ultra-premium, AI-driven metallurgical image analysis platform achieving Master Craft Pro-Max level accuracy (>80%). Built for Next-Gen laboratories, it replaces classical, error-prone manual metallography with adaptive computer vision and large-language model (LLM) reasoning. 

Unlike traditional platforms hardcoded only for carbon-steel, MicroAI utilizes **Color-Aware Phase Clustering** and **Material-Agnostic Physics Extraction**, allowing it to dynamically identify standard morphological anomalies in Aluminum, Brass, Titanium, and complex Superalloys.

---

## 🚀 Tech Stack

### Frontend (User Interface & Telemetry)
* **Framework:** Next.js (React 18) with TypeScript
* **Styling:** Tailwind CSS (Sci-Fi Deep Tech styling, Glassmorphism)
* **Icons & UI:** Lucide React
* **Charting:** Recharts
* **Exports:** `html2pdf.js` for instant Client-Side Archival Export
* **State Management:** Custom React Hooks & Context

### Backend (Algorithmic Processing)
* **Server Framework:** FastAPI (Python)
* **Computer Vision:** OpenCV, Scikit-Image 
* **Machine Learning:** Scikit-Learn (Gaussian Mixture Models)
* **Generative AI:** Groq Cloud API (Llama 3.3 70B Versatile)

---

## 🧠 Core Algorithmic Functions

1. **Illumination Equalization:** Adaptive morphological background envelope estimation effectively removes vignetting and shadows from raw microscopic captures.
2. **Hybrid Ridge Detection:** Fusion of `Meijering`, `Sato`, `Sobel`, and `Hessian` filters creates flawless grain boundary delineations.
3. **Adaptive RAG Merging:** (Region Adjacency Graphs) Overcomes traditional watershed over-segmentation by statistically merging pseudo-boundaries based on hierarchical weighting.
4. **Color-Aware Phase Clustering:** Uses LAB multi-channel color-space clustering to isolate Copper, Brass, and other non-ferrous phases without ignoring chrominance.
5. **LLM Contextualization Engine:** Instead of hardcoded phase guessing, backend algorithms extract raw physical descriptors (Circularity, Eccentricity, Aspect Ratios) and pass them as pure scientific context into the Groq LLM to yield Senior Metallurgist level diagnostics.

---

## 🔀 Application & User Flows

### 1. The Dashboard (Command Center) 
The entry point provides high-level telemetry on past analysis runs. Users track overarching anomaly detection rates, average system confidence, and total metallurgical reports executed under a sleek Bento-Box data grid.

### 2. Analysis Initiation
Users drag-and-drop a microscopic SEM/Optical capture, providing vital contextual calibrations (**Material Family** and **μm/px Scale Ratio**). This dynamically calibrates the backend physical equations (e.g. ASTM E112 conversion).

### 3. Core Analysis Engine
The server pipelines the image through the Python algorithmic loop. Data yields are matched and validated asynchronously.

### 4. Interactive Telemetry View
Users are presented with the processed micrograph overlay. 
- A **ClipPath interactive slider** allows scrubbing between the raw image and the AI mapping.
- The **Contextual Chatbot** allows the user to query Groq specifically regarding the current analysis JSON response (e.g., *"Why did the Hall-Petch value decrease here?"*)
- **Report Generation:** Complete analysis exported seamlessly to PDF.

### 5. Differential Comparison
Users load two distinct samples into the "Compute Delta" engine. The app extracts variables (Grain topological scale vs. Defect %) and dynamically charts the structural differences across glowing progress telemetry bars.

---

## 📁 Directory Tree Structure

```text
ai-microstructure-analyzer/
├── frontend/                     # Next.js UI Application
│   ├── app/
│   │   ├── analyze/page.tsx      # Image Upload & Context Form
│   │   ├── analysis/[id]/page.tsx# Interactive Result Viewer & Chatbot
│   │   ├── compare/page.tsx      # Differential Delta Engine
│   │   ├── reports/page.tsx      # Bento-Box Archive Viewer
│   │   ├── layout.tsx            # Global Shell (Sidebar injected)
│   │   └── page.tsx              # MicroAI Telemetry Command Center
│   ├── components/               # Abstracted UI Elements
│   │   └── Sidebar.tsx           # Application Navigation Dock
│   ├── lib/
│   │   └── mock-data.ts          # Core Types & Client Sync Layer
│   ├── tailwind.config.ts        # Master-Craft Theming Extractor
│   └── package.json
│
├── backend/                      # Python FastAPI Engine
│   ├── main.py                   # REST API routing & Chat Endpoint
│   ├── image_analysis.py         # OpenCV / Scikit-Image ML Pipeline
│   └── requirements.txt          # Python dependencies
│
└── README.md
```

## 🛠 Active Installation

1. **Global Requirements**: `Node.js 18+`, `Python 3.10+`
2. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   # Ensure GROQ_API_KEY is present in your environment
   python main.py
   ```
3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
4. Access the web app at `http://localhost:3000`
