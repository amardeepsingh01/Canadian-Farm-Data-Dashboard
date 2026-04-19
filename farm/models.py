from django.db import models

class FarmProduction(models.Model):
    year = models.IntegerField()
    province = models.CharField(max_length=50)
    crop_type = models.CharField(max_length=50)
    average_yield_kg_per_hectare = models.FloatField()
    total_farm_value_dollars = models.FloatField()
    avg_rainfall_mm = models.FloatField()
    avg_temperature_c = models.FloatField()
    irrigation_used = models.BooleanField()

    def __str__(self):
        return f"{self.crop_type} - {self.year}"