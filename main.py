"""
DemoMed Healthcare API Assessment
Author: adeyemi akano
Version: 2.0
"""

import json
import os
import requests
import time
from utils import analyze_patient_data, summarize_alerts

API_KEY = os.environ.get("DEMOMED_API_KEY")

if not API_KEY:
    raise EnvironmentError("❌ DEMOMED_API_KEY not found. Please set it as a GitHub Secret.")

DATA_FILE = "data/sample_patients.json"
RESULT_FILE = "data/results.json"
API_URL = "https://api.demomedhealth.io/v2/submit"
MAX_RETRIES = 3

def submit_to_api(payload):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"📡 Attempt {attempt}: Submitting results...")
            response = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=15
            )
            if response.status_code == 200:
                print("✅ Submission successful!")
                return response.json()
            else:
                print(f"⚠️ API returned {response.status_code}: {response.text}")
        except requests.exceptions.Timeout:
            print("⏳ Request timed out. Retrying...")
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
        time.sleep(2 * attempt)
    raise ConnectionError("🚨 Failed to submit after multiple attempts.")

def main():
    print("🔍 Loading patient data...")
    with open(DATA_FILE, "r") as f:
        patient_data = json.load(f)
    print("🧠 Analyzing records...")
    results = analyze_patient_data(patient_data)
    summary = summarize_alerts(results)
    payload = {
        "analysis_summary": summary,
        "alerts": results,
        "submitted_by": "Owolabi Samuel",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    print("💾 Saving local results...")
    with open(RESULT_FILE, "w") as out:
        json.dump(payload, out, indent=2)
    print("🚀 Submitting analysis to DemoMed API...")
    api_response = submit_to_api(payload)
    print("📄 API Response:")
    print(json.dumps(api_response, indent=2))

if __name__ == "__main__":
    main()
