import pandas as pd

# Load the dataset
df = pd.read_csv("crmdata.csv")

# Show first few rows
print(df.head())

# Show missing values
print(df.isnull().sum())
