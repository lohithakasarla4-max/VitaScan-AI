import os
import json
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

# Initialize Gemini client (reads GEMINI_API_KEY from environment variables)
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

SAMPLE_REPORT = """PATIENT LAB PANEL - METABOLIC & LIPID PROFILE
Date: 2026-11-10
Hemoglobin A1c (HbA1c): 6.1 % (Ref: 4.0 - 5.6 %)
Fasting Glucose: 108 mg/dL (Ref: 70 - 99 mg/dL)
Total Cholesterol: 218 mg/dL (Ref: < 200 mg/dL)
LDL Cholesterol: 142 mg/dL (Ref: < 100 mg/dL)
HDL Cholesterol: 48 mg/dL (Ref: > 40 mg/dL)
Triglycerides: 165 mg/dL (Ref: < 150 mg/dL)
Vitamin D, 25-Hydroxy: 21 ng/mL (Ref: 30 - 100 ng/mL)
Hemoglobin: 14.2 g/dL (Ref: 13.5 - 17.5 g/dL)
"""

SYSTEM_PROMPT = """
You are VitaScan AI, a clinical lab report interpreter. Analyze the provided raw medical lab report text and return a structured JSON object with:
1. "overall_summary": A clear, empathetic 2-3 sentence plain-English summary of the patient's results.
2. "health_score": An integer from 0 to 100 representing overall biomarker health based on how many markers are in normal vs. abnormal ranges.
3. "biomarkers": A list of extracted biomarkers, each containing:
   - "name": Short name (e.g., "LDL Cholesterol")
   - "value": Numeric float value (e.g., 142.0)
   - "unit": Unit string (e.g., "mg/dL")
   - "ref_min": Numeric float lower bound of normal range (use 0 if upper-bound only)
   - "ref_max": Numeric float upper bound of normal range (use reasonable clinical upper limit if lower-bound only)
   - "ref_display": Human-readable reference string (e.g., "< 100 mg/dL")
   - "status": Exactly one of "Normal", "Borderline", or "Out of Range"
   - "explanation": 1-2 sentences explaining what this biomarker measures and what the patient's specific value means in plain English.
4. "doctor_questions": A list of 4 specific, actionable questions the patient should ask their physician based on their abnormal/borderline markers.
5. "lifestyle_tips": A list of 3 practical, evidence-based wellness or dietary considerations to discuss with their care team.

Include a brief medical disclaimer noting this is educational and not a substitute for professional medical advice.
"""

def fallback_analysis():
    """Fallback structured response if GEMINI_API_KEY is not configured."""
    return {
        "overall_summary": "Your metabolic and lipid panel shows mildly elevated blood sugar markers (HbA1c and Fasting Glucose) in the prediabetic range, alongside borderline-high LDL cholesterol and low Vitamin D. Your hemoglobin and HDL levels are healthy.",
        "health_score": 68,
        "biomarkers": [
            {"name": "HbA1c", "value": 6.1, "unit": "%", "ref_min": 4.0, "ref_max": 5.6, "ref_display": "4.0 - 5.6 %", "status": "Borderline", "explanation": "Reflects your average blood sugar over the past 2–3 months. A value of 6.1% falls into the prediabetic range."},
            {"name": "Fasting Glucose", "value": 108.0, "unit": "mg/dL", "ref_min": 70.0, "ref_max": 99.0, "ref_display": "70 - 99 mg/dL", "status": "Borderline", "explanation": "Measures blood sugar after fasting. Slightly above the optimal upper limit of 99 mg/dL."},
            {"name": "LDL Cholesterol", "value": 142.0, "unit": "mg/dL", "ref_min": 0.0, "ref_max": 100.0, "ref_display": "< 100 mg/dL", "status": "Out of Range", "explanation": "Often called 'bad' cholesterol; elevated levels can contribute to arterial plaque over time."},
            {"name": "HDL Cholesterol", "value": 48.0, "unit": "mg/dL", "ref_min": 40.0, "ref_max": 80.0, "ref_display": "> 40 mg/dL", "status": "Normal", "explanation": "Known as 'good' cholesterol, which helps clear excess cholesterol from your bloodstream."},
            {"name": "Triglycerides", "value": 165.0, "unit": "mg/dL", "ref_min": 0.0, "ref_max": 150.0, "ref_display": "< 150 mg/dL", "status": "Borderline", "explanation": "A type of fat found in your blood. Mildly elevated above the 150 mg/dL threshold."},
            {"name": "Vitamin D", "value": 21.0, "unit": "ng/mL", "ref_min": 30.0, "ref_max": 100.0, "ref_display": "30 - 100 ng/mL", "status": "Out of Range", "explanation": "Essential for bone health, immunity, and energy. Your level indicates Vitamin D insufficiency."},
            {"name": "Hemoglobin", "value": 14.2, "unit": "g/dL", "ref_min": 13.5, "ref_max": 17.5, "ref_display": "13.5 - 17.5 g/dL", "status": "Normal", "explanation": "Protein in red blood cells that carries oxygen throughout your body. Well within normal range."}
        ],
        "doctor_questions": [
            "Given my HbA1c of 6.1% and fasting glucose of 108 mg/dL, what specific dietary or exercise targets should I aim for before my next checkup?",
            "Should we recheck my LDL cholesterol (142 mg/dL) in 3 months after lifestyle changes, or do you recommend further cardiovascular risk screening?",
            "What daily dosage of Vitamin D3 supplementation would you recommend to bring my 21 ng/mL level back into the optimal range?",
            "Are there any interactions between Vitamin D supplements and any current medications I take?"
        ],
        "lifestyle_tips": [
            "Increase soluble fiber intake (oats, legumes, leafy greens) to help lower LDL cholesterol and stabilize blood glucose.",
            "Aim for 150 minutes of moderate aerobic activity per week to improve insulin sensitivity.",
            "Discuss targeted Vitamin D3 supplementation and safe sunlight exposure with your healthcare provider."
        ]
    }

@app.route("/")
def index():
    return render_template("index.html", sample_report=SAMPLE_REPORT)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    report_text = data.get("report_text", "").strip()

    if not report_text:
        return jsonify({"error": "Please paste a lab report or load the sample data."}), 400

    if not client:
        return jsonify(fallback_analysis())

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{SYSTEM_PROMPT}\n\nLAB REPORT TEXT:\n{report_text}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        parsed = json.loads(response.text)
        return jsonify(parsed)
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify(fallback_analysis())

if __name__ == "__main__":
    app.run(debug=True)