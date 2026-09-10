import pandas as pd

# Load the raw dataset
df = pd.read_csv("data/jobs_raw.csv")

print("Original number of jobs:", len(df))

# Remove spaces from column names
df.columns = df.columns.str.strip()

# Clean text columns
text_columns = [
    "Job_Title",
    "Company_Name",
    "URL",
    "Location",
    "Experience",
    "Salary",
    "Skills_Required",
    "Matched_Keywords"
]

for column in text_columns:
    df[column] = df[column].fillna("").astype(str).str.strip()

# Remove duplicate jobs using URL
df = df.drop_duplicates(subset="URL")

# Clean extra spaces inside Skills_Required
df["Skills_Required"] = (
    df["Skills_Required"]
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

# Save cleaned dataset
df.to_csv("data/jobs_cleaned.csv", index=False)

print("Cleaned number of jobs:", len(df))
print("Cleaned data saved successfully!")