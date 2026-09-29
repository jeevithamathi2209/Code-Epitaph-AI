# Code Epitaph AI

### Legacy System Intelligence & Dependency Risk Analysis

Code Epitaph AI is a software-engineering intelligence platform that analyzes legacy system dependencies, identifies structural risks, detects unusual component patterns using AI, simulates component failures, and generates modernization priorities.

## Key Features

* **Dependency Analysis** — Visualizes component relationships using NetworkX.
* **Risk Intelligence** — Calculates component risk and engineering priority.
* **AI Anomaly Detection** — Uses Isolation Forest to identify unusual structural patterns.
* **Failure Simulation** — Performs what-if analysis for component failures.
* **Modernization Roadmap** — Prioritizes components for refactoring and modernization.
* **Interactive Dashboard** — Provides system-wide insights through Streamlit.

## Architecture


Legacy Data
    ↓
Preprocessing
    ↓
Dependency Graph
    ↓
Risk & Priority Analysis
    ↓
AI Anomaly Detection
    ↓
Failure Simulation
    ↓
Modernization Roadmap
```

## Tech Stack

**Python · Pandas · NumPy · Scikit-learn · NetworkX · Plotly · Streamlit**

### AI

**Isolation Forest — Unsupervised Anomaly Detection**

Analyzes:

* Risk score
* Dependency complexity
* Failure impact
* Graph centrality
* Priority score

## Project Structure

```text
Code Epitaph AI/
├── app.py
├── data/
├── src/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── legacy_analyzer.py
│   ├── risk_engine.py
│   ├── graph_engine.py
│   └── anomaly_engine.py
├── requirements.txt
└── README.md
```

## Run Locally

```bash
git clone <repository-url>
cd Code-Epitaph-AI
pip install -r requirements.txt
streamlit run app.py

## Project Focus

**Legacy System Analysis · Dependency Intelligence · AI Anomaly Detection · Failure Impact Analysis · Software Modernization**
