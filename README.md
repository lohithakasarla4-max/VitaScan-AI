# VitaScan AI — Clinical Lab Report Interpreter & Health Insights

> **AI x Healthcare Track Submission**  
> VitaScan AI is a full-stack Flask application that transforms unstructured medical lab panels and blood test results into visual, actionable health insights, clinical biomarker interpretations, and targeted questions for physicians.

---

## 🚀 Features
* **Smart Biomarker Extraction:** Parses raw, unstructured text from lab reports and categorizes each marker (*Normal*, *Borderline*, *Out of Range*).
* **Interactive Chart.js Visualizations:** Renders side-by-side comparative bar charts showing patient results relative to upper clinical reference limits.
* **Plain-English Clinical Insights:** Translates complex medical terminology into clear explanations.
* **Physician & Lifestyle Action Plan:** Generates 4 tailored questions to ask a doctor and 3 evidence-based lifestyle/dietary steps.
* **One-Click Demo Fallback:** Includes a pre-loaded sample metabolic and lipid panel for instant testing and live demonstrations.

---

## 🛠️ Tech Stack
* **Backend:** Python, Flask, Google Gemini API (`google-genai` SDK)
* **Frontend:** Tailwind CSS, Chart.js, HTML5
* **AI Architecture:** Structured JSON generation with strict clinical prompt constraints

---

## ⚙️ Setup & Local Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/vitascan-ai.git](https://github.com/your-username/vitascan-ai.git)
   cd vitascan-ai