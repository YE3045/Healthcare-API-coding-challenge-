import requests
import time

API_KEY = "ak_c222a42bd24576faa5902c6dea6d32892b33d6c3d1c9647c"
BASE_URL = "https://assessment.ksensetech.com/api"

headers = {"x-api-key": API_KEY}


def get_all_patients():
    """Retrieve all patients with pagination and retry logic."""
    all_patients = []
    page = 1
    retries = 3

    while True:
        try:
            response = requests.get(f"{BASE_URL}/patients?page={page}&limit=5", headers=headers)
            if response.status_code == 429:
                print("Rate limit hit. Retrying...")
                time.sleep(2)
                continue
            if response.status_code >= 500:
                if retries > 0:
                    print("Server error. Retrying...")
                    retries -= 1
                    time.sleep(1)
                    continue
                else:
                    break

            data = response.json()
            patients = data.get("data", [])
            if not patients:
                break

            all_patients.extend(patients)

            if not data["pagination"]["hasNext"]:
                break

            page += 1
            time.sleep(0.2)

        except Exception as e:
            print("Error:", e)
            break

    return all_patients


def parse_bp(bp_value):
    """Extract and evaluate blood pressure."""
    try:
        if not bp_value or "/" not in bp_value:
            return 0
        systolic, diastolic = bp_value.split("/")
        systolic = int(systolic.strip()) if systolic.strip().isdigit() else None
        diastolic = int(diastolic.strip()) if diastolic.strip().isdigit() else None

        if systolic is None or diastolic is None:
            return 0

        if systolic < 120 and diastolic < 80:
            return 1
        elif 120 <= systolic <= 129 and diastolic < 80:
            return 2
        elif (130 <= systolic <= 139) or (80 <= diastolic <= 89):
            return 3
        elif systolic >= 140 or diastolic >= 90:
            return 4
        else:
            return 0
    except:
        return 0


def parse_temp(temp_value):
    """Evaluate temperature."""
    try:
        temp = float(temp_value)
        if temp <= 99.5:
            return 0
        elif 99.6 <= temp <= 100.9:
            return 1
        elif temp >= 101.0:
            return 2
        else:
            return 0
    except:
        return 0


def parse_age(age_value):
    """Evaluate age risk."""
    try:
        age = int(age_value)
        if age < 40:
            return 1
        elif 40 <= age <= 65:
            return 1
        elif age > 65:
            return 2
        else:
            return 0
    except:
        return 0


def detect_data_quality(patient):
    """Identify invalid or missing data."""
    issues = []

    bp = patient.get("blood_pressure")
    temp = patient.get("temperature")
    age = patient.get("age")

    if not bp or "/" not in str(bp):
        issues.append("bp")
    else:
        parts = bp.split("/")
        if not (parts[0].strip().isdigit() and parts[1].strip().isdigit()):
            issues.append("bp")

    if not isinstance(temp, (int, float)):
        try:
            float(temp)
        except:
            issues.append("temp")

    if not isinstance(age, int):
        try:
            int(age)
        except:
            issues.append("age")

    return len(issues) > 0


def main():
    patients = get_all_patients()
    high_risk, fever, data_issues = [], [], []

    for p in patients:
        pid = p.get("patient_id")

        bp_score = parse_bp(p.get("blood_pressure"))
        temp_score = parse_temp(p.get("temperature"))
        age_score = parse_age(p.get("age"))
        total_score = bp_score + temp_score + age_score

        if total_score >= 4:
            high_risk.append(pid)
        try:
            if float(p.get("temperature", 0)) >= 99.6:
                fever.append(pid)
        except:
            pass

        if detect_data_quality(p):
            data_issues.append(pid)

    high_risk = list(set(high_risk))
    fever = list(set(fever))
    data_issues = list(set(data_issues))

    payload = {
        "high_risk_patients": high_risk,
        "fever_patients": fever,
        "data_quality_issues": data_issues
    }

    print("Submitting results...")
    response = requests.post(f"{BASE_URL}/submit-assessment", headers=headers, json=payload)
    print(response.json())


if __name__ == "__main__":
    main()
