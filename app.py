from flask import Flask, render_template
import pandas as pd
import os
import matplotlib.pyplot as plt
import io
import base64
from fuzzywuzzy import fuzz

app = Flask(__name__)

# Load CRM Data
data_path = "crmdata.csv"

if os.path.exists(data_path):
    crm_data = pd.read_csv(data_path)
else:
    crm_data = pd.DataFrame(columns=["Name", "Email", "Phone", "Address", "Company"])

# Function to calculate data accuracy
def calculate_accuracy(df):
    total_records = len(df)
    if total_records == 0:
        return 0  # Avoid division by zero

    missing_values = df.isnull().sum().sum()
    duplicates = detect_duplicates(df)

    corrected_df = fill_missing_data(df.copy())
    missing_values_after = corrected_df.isnull().sum().sum()

    duplicate_count = len(duplicates)

    # Accuracy formula: ((Clean Records) / Total Records) * 100
    clean_records = total_records - (missing_values + duplicate_count)
    accuracy = (clean_records / total_records) * 100
    return round(accuracy, 2)

# Generate Accuracy Chart
def generate_accuracy_chart(accuracy):
    labels = ["Clean Data", "Duplicates + Missing"]
    values = [accuracy, 100 - accuracy]
    colors = ["#28a745", "#dc3545"]  # Green & Red

    plt.figure(figsize=(5, 5))
    plt.pie(values, labels=labels, autopct="%1.1f%%", colors=colors, startangle=140)
    plt.title("CRM Data Accuracy")

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

# Generate Duplicate Chart
def generate_duplicate_chart():
    duplicates = detect_duplicates(crm_data)
    duplicate_names = [crm_data.iloc[i]["Name"] for i, j in duplicates]
    duplicate_counts = pd.Series(duplicate_names).value_counts()

    plt.figure(figsize=(8, 5))
    duplicate_counts.plot(kind="bar", color="blue")
    plt.xlabel("Customer Name")
    plt.ylabel("Duplicate Count")
    plt.title("Duplicate Records in CRM")
    plt.xticks(rotation=45)

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

# Generate Missing Data Chart
def generate_missing_data_chart():
    missing_counts = crm_data.isnull().sum()
    missing_counts = missing_counts[missing_counts > 0]  # Remove columns with no missing values

    if missing_counts.empty:
        return None  # No missing data, return nothing

    plt.figure(figsize=(6, 6))
    missing_counts.plot(kind="pie", autopct="%1.1f%%", colors=["red", "orange", "yellow"])
    plt.title("Missing Data in CRM")

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

# Detect duplicates
def detect_duplicates(df):
    duplicates = []
    for i, row1 in df.iterrows():
        for j, row2 in df.iterrows():
            if i >= j:
                continue
            similarity = fuzz.ratio(str(row1["Name"]), str(row2["Name"]))
            email_match = row1["Email"] == row2["Email"]
            if similarity > 80 or email_match:
                duplicates.append((i, j))
    return duplicates

# Fill missing data
def fill_missing_data(df):
    for col in ["Name", "Email", "Phone", "Address", "Company"]:
        df[col].fillna("Unknown", inplace=True)
    return df

@app.route("/")
def index():
    return render_template("index.html", data=crm_data.to_dict(orient="records"))

@app.route("/graphs")
def graphs():
    duplicate_chart = generate_duplicate_chart()
    missing_chart = generate_missing_data_chart() if crm_data.isnull().sum().sum() > 0 else None
    return render_template("graphs.html", duplicate_chart=duplicate_chart, missing_chart=missing_chart)

@app.route("/duplicates")
def duplicates():
    duplicate_pairs = detect_duplicates(crm_data)
    duplicate_records = [
        (crm_data.iloc[i].to_dict(), crm_data.iloc[j].to_dict())
        for i, j in duplicate_pairs
    ]
    return render_template("duplicates.html", duplicates=duplicate_records)

@app.route("/corrections")
def corrections():
    corrected_data = fill_missing_data(crm_data.copy())
    return render_template("corrections.html", data=corrected_data.to_dict(orient="records"))

@app.route("/accuracy")
def accuracy():
    accuracy_score = calculate_accuracy(crm_data)
    accuracy_chart = generate_accuracy_chart(accuracy_score)
    return render_template("accuracy.html", accuracy=accuracy_score, accuracy_chart=accuracy_chart)

if __name__ == "__main__":
    app.run(debug=True)
