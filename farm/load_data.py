import pandas as pd
from .models import FarmProduction

def run():
    df = pd.read_csv("farm.csv")

    for _, row in df.iterrows():
        FarmProduction.objects.create(
            year=row['year'],
            province=row['province'],
            crop_type=row['crop_type'],
            average_yield_kg_per_hectare=row['average_yield_kg_per_hectare'],
            total_farm_value_dollars=row['total_farm_value_dollars'],
            avg_rainfall_mm=row['avg_rainfall_mm'],
            avg_temperature_c=row['avg_temperature_c'],
            irrigation_used=True if row['irrigation_used']=='Yes' else False
        )