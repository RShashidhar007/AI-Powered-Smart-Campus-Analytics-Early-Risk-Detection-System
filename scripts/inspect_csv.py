import pandas as pd
path = r'c:\Users\HP\OneDrive\Desktop\programs\AI-Powered-Smart-Campus-Analytics\AI-Powered-Smart-Campus-Analytics-Early-Risk-Detection-System\data\student_data.csv'
df = pd.read_csv(path)
print("Columns:", df.columns.tolist())
print("Shape:", df.shape)
print("\nFirst 3 rows:")
print(df.head(3).to_string())
print("\nUnique departments:", df['department'].unique().tolist() if 'department' in df.columns else 'N/A')
print("Unique semesters:", df['semester'].unique().tolist() if 'semester' in df.columns else 'N/A')
