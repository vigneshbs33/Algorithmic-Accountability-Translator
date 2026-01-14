# Algorithmic Accountability Translator
## AlgoTranslator - Making AI Algorithms Transparent for Everyone

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-3178C6.svg)](https://www.typescriptlang.org/)

<div align="center">
  <img src="https://img.shields.io/badge/NLP-Product-8b5cf6?style=for-the-badge" alt="NLP Product" />
  <img src="https://img.shields.io/badge/Open%20Source-100%25-10b981?style=for-the-badge" alt="Open Source" />
</div>

<br/>

<p align="center">
  <strong>🔗 Created by <a href="https://vigneshbs.xyz">Vignesh B S</a></strong> | © 2026 All Rights Reserved
</p>

---

<p align="center">
  <img src="https://img.shields.io/badge/Filter%20Bubble%20Detection-✓-10b981" alt="Filter Bubble Detection" />
  <img src="https://img.shields.io/badge/Bias%20Analysis-✓-10b981" alt="Bias Analysis" />
  <img src="https://img.shields.io/badge/Echo%20Chamber%20Detection-✓-10b981" alt="Echo Chamber" />
  <img src="https://img.shields.io/badge/AI%20Generated%20Reports-✓-10b981" alt="AI Reports" />
</p>

---

## 🎯 What is AlgoTranslator?

**AlgoTranslator** is a production-grade NLP product that reverse-engineers social media recommendation algorithms and translates their behavior into plain language that anyone can understand.

### The Problem We Solve

| 🚫 The Problem | ✅ Our Solution |
|----------------|-----------------|
| Algorithms are black boxes | We make them transparent |
| Filter bubbles trap users | We detect & measure them |
| Bias is invisible | We quantify & visualize it |
| Tech jargon confuses people | We generate plain-language reports |

---

## ✨ Features

### 🔍 **Filter Bubble Detection**
Identifies when recommendation algorithms trap users in echo chambers, with severity scoring.

### 📊 **Multi-Dimensional Bias Analysis**
- Political bias detection (left/center/right)
- Sensationalism scoring
- Clickbait detection
- Fact vs Opinion ratio

### 👥 **10 Synthetic Personas**
Test how different user types experience the same platform:
- Progressive Activist
- Conservative Traditional  
- Tech Enthusiast
- Political Moderate
- And 6 more...

### 📝 **AI-Powered Reports**
GPT-4 or Claude generates human-readable "contracts" explaining algorithm behavior in simple terms.

### 📈 **Beautiful Visualizations**
- Diversity radar charts
- Echo chamber timeline
- Bias distribution pie charts
- Topic modeling clusters

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/vigneshbs33/Algorithmic-Accountability-Translator.git
cd Algorithmic-Accountability-Translator

# Start everything with Docker
docker-compose up -d

# Open in browser
# Landing Page: http://localhost:3000
# Dashboard: http://localhost:3000/dashboard
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

```bash
# Backend
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn api.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│   React 18 + TypeScript + Recharts                             │
│   Landing Page • Dashboard • Analysis • Contracts               │
└───────────────────────────────┬─────────────────────────────────┘
                                │ REST API
┌───────────────────────────────▼─────────────────────────────────┐
│                          BACKEND                                │
│                        FastAPI + Python                         │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────┤
│   Scrapers  │     NLP     │     ML      │  Contract   │  Tasks  │
│ Reddit/YT   │  BERTopic   │  Diversity  │  Generator  │  Celery │
│ Rate Limit  │  Stance     │  Echo Det   │  GPT/Claude │  Redis  │
│             │  Bias       │  XGBoost    │             │         │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴────┬────┘
       │             │             │             │           │
┌──────▼──────┐┌─────▼─────┐┌──────▼──────┐┌─────▼─────┐┌────▼────┐
│ PostgreSQL  ││  MongoDB  ││    Redis    ││  OpenAI   ││  APIs   │
│ (Structured)││   (Raw)   ││  (Cache)    ││  Claude   ││  Reddit │
│             ││           ││             ││           ││  YouTube│
└─────────────┘└───────────┘└─────────────┘└───────────┘└─────────┘
```

---

## 📊 Key Metrics Explained

| Metric | What It Means | Healthy Range |
|--------|---------------|---------------|
| **Diversity Score** | How varied your content is | 0.6 - 1.0 ✅ |
| **Echo Chamber Score** | How trapped in a bubble | 0.0 - 0.4 ✅ |
| **Bias Score** | Political slant strength | 0.0 - 0.3 ✅ |
| **Sensationalism** | Emotional manipulation level | 0.0 - 0.3 ✅ |

---

## 🧠 Technology Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance API framework |
| **BERTopic** | Topic modeling with transformers |
| **SpaCy** | Entity recognition |
| **Transformers** | Stance & bias detection |
| **XGBoost** | Recommendation pattern analysis |
| **Celery + Redis** | Background task processing |
| **PostgreSQL + MongoDB** | Data storage |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI framework |
| **TypeScript** | Type safety |
| **Recharts** | Data visualization |
| **React Query** | Data fetching |
| **Vite** | Build tooling |

---

## 📁 Project Structure

```
AlgoTranslator/
├── backend/                 # Python FastAPI backend
│   ├── api/                 # REST endpoints
│   ├── scrapers/            # Reddit & YouTube collectors
│   ├── nlp/                 # NLP analysis pipeline
│   │   ├── topic_modeling.py      # BERTopic
│   │   ├── stance_detection.py    # Stance classifier
│   │   ├── bias_detection.py      # Multi-faceted bias
│   │   ├── entity_extraction.py   # SpaCy NER
│   │   └── sentiment.py           # Sentiment analysis
│   ├── ml/                  # ML analysis modules
│   │   ├── diversity_metrics.py   # Filter bubble measurement
│   │   ├── echo_chamber.py        # Echo detection
│   │   └── recommendation_patterns.py  # Pattern analysis
│   ├── generation/          # Contract generation
│   ├── database/            # PostgreSQL & MongoDB
│   ├── personas/            # 10 user profiles
│   └── tasks/               # Celery background tasks
│
├── frontend/                # React TypeScript frontend
│   └── src/
│       ├── components/
│       │   ├── LandingPage/       # Product landing page
│       │   ├── Dashboard/         # Main dashboard
│       │   ├── Personas/          # Persona viewer
│       │   ├── Analysis/          # Analysis charts
│       │   └── Contracts/         # Contract viewer
│       └── services/              # API client
│
├── docker-compose.yml       # Full stack deployment
└── README.md                # You are here!
```

---

## 🔧 Configuration

Create a `.env` file from the template:

```bash
cp .env.example .env
```

### Required API Keys

| Service | Purpose | Where to Get |
|---------|---------|--------------|
| Reddit API | Scrape Reddit content | [Reddit Apps](https://www.reddit.com/prefs/apps) |
| YouTube API | Scrape YouTube content | [Google Cloud Console](https://console.cloud.google.com/) |
| OpenAI *or* Anthropic | Generate contracts | [OpenAI](https://platform.openai.com/) / [Anthropic](https://www.anthropic.com/) |

> 💡 **Note**: The product works in demo mode without API keys!

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Fork & clone
git clone https://github.com/YOUR_USERNAME/Algorithmic-Accountability-Translator.git

# Create branch
git checkout -b feature/amazing-feature

# Make changes & commit
git commit -m "Add amazing feature"

# Push & create PR
git push origin feature/amazing-feature
```

---

## � License

```
MIT License

Copyright (c) 2026 Vignesh B S

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software.
```

---

## 👤 About the Creator

<table>
  <tr>
    <td>
      <strong>Vignesh B S</strong><br/>
      NLP Researcher & Full Stack Developer<br/><br/>
      🌐 <a href="https://vigneshbs.xyz">vigneshbs.xyz</a><br/>
      🐙 <a href="https://github.com/vigneshbs33">@vigneshbs33</a>
    </td>
  </tr>
</table>

*"I believe technology should be understandable by everyone, not just engineers. AlgoTranslator is my contribution to making AI algorithms more transparent and accountable."*

---

## 📞 Contact & Links

| | |
|---|---|
| 🌐 **Portfolio** | [vigneshbs.xyz](https://vigneshbs.xyz) |
| 🐙 **GitHub** | [@vigneshbs33](https://github.com/vigneshbs33) |
| 📦 **This Repo** | [Algorithmic-Accountability-Translator](https://github.com/vigneshbs33/Algorithmic-Accountability-Translator) |
| 🐛 **Report Bug** | [Issues](https://github.com/vigneshbs33/Algorithmic-Accountability-Translator/issues) |

---

<p align="center">
  <strong>⭐ Star this repo if you find it useful!</strong>
</p>



<p align="center">
  <b>AlgoTranslator - Making AI Algorithms Transparent for Everyone</b><br/>
  <i>"Understanding algorithms shouldn't require a PhD"</i>
</p>
