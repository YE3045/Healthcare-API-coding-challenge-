import random

def analyze_patient_data(patients):
    results = []
    for patient in patients:
        alert = {
            "id": patient["id"],
            "name": patient["name"],
            "risk_score": random.randint(0, 100),
            "alert": "HIGH" if random.randint(0, 1) else "LOW"
        }
        results.append(alert)
    return results

def summarize_alerts(results):
    high_risks = sum(1 for r in results if r["alert"] == "HIGH")
    return {"total": len(results), "high_risks": high_risks}
