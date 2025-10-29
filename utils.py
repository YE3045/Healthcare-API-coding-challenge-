def parse_bp(bp):
    """Parse blood pressure into systolic and diastolic"""
    if not bp or "/" not in bp:
        return None, None
    try:
        systolic, diastolic = bp.split("/")
        return int(systolic), int(diastolic)
    except ValueError:
        return None, None

def calculate_risk(patient):
    """Calculate BP, Temp, Age risk and check data quality"""
    invalid = False

    # Blood Pressure
    systolic, diastolic = parse_bp(patient.get("blood_pressure"))
    if systolic is None or diastolic is None:
        bp_score = 0
        invalid = True
    elif systolic < 120 and diastolic < 80:
        bp_score = 1
    elif 120 <= systolic <= 129 and diastolic < 80:
        bp_score = 2
    elif 130 <= systolic <= 139 or 80 <= diastolic <= 89:
        bp_score = 3
    elif systolic >= 140 or diastolic >= 90:
        bp_score = 4
    else:
        bp_score = 0

    # Temperature
    temp = patient.get("temperature")
    if temp is None or not isinstance(temp, (int, float)):
        temp_score = 0
        invalid = True
    elif temp <= 99.5:
        temp_score = 0
    elif 99.6 <= temp <= 100.9:
        temp_score = 1
    else:
        temp_score = 2

    # Age
    age = patient.get("age")
    if age is None or not isinstance(age, (int, float)):
        age_score = 0
        invalid = True
    elif age < 40:
        age_score = 1
    elif 40 <= age <= 65:
        age_score = 1
    else:
        age_score = 2

    return bp_score, temp_score, age_score, invalid
