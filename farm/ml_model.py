import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder

def train_model():
    df = pd.read_csv("farm_data.csv")

    # Convert Yes/No → 1/0
    df['irrigation_used'] = df['irrigation_used'].map({'Yes': 1, 'No': 0})

    # Encode categorical data
    le_crop = LabelEncoder()
    le_province = LabelEncoder()

    df['crop_encoded'] = le_crop.fit_transform(df['crop_type'])
    df['province_encoded'] = le_province.fit_transform(df['province'])

    # Target (success)
    df['success'] = df['average_yield_kg_per_hectare'].apply(lambda x: 1 if x > 3000 else 0)

    # Features (NOW 5 factors)
    X = df[['avg_rainfall_mm', 'avg_temperature_c', 'irrigation_used',
            'crop_encoded', 'province_encoded']]

    y = df['success']

    model = DecisionTreeClassifier()
    model.fit(X, y)

    return model, le_crop, le_province