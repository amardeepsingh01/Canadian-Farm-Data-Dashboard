from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Avg, Sum
from .models import FarmProduction
import csv
from django.shortcuts import render, redirect
from .forms import UploadFileForm

# 🔹 ML IMPORTS
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import os


# 🔹 LOAD DATASET (SAFE PATH)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(BASE_DIR, 'farm', 'farm_data.csv')

df = pd.read_csv(file_path)

# Convert Yes/No → 1/0
df['irrigation_used'] = df['irrigation_used'].map({'Yes': 1, 'No': 0})

# Encode categorical data
le_crop = LabelEncoder()
le_province = LabelEncoder()

df['crop_encoded'] = le_crop.fit_transform(df['crop_type'])
df['province_encoded'] = le_province.fit_transform(df['province'])

# Target variable
df['success'] = df['average_yield_kg_per_hectare'].apply(lambda x: 1 if x > 3000 else 0)

# Features
X = df[['avg_rainfall_mm', 'avg_temperature_c', 'irrigation_used',
        'crop_encoded', 'province_encoded']]
y = df['success']

# Train model
model = DecisionTreeClassifier()
model.fit(X, y)


# 🏠 INDEX PAGE
def index(request):
    total_records = FarmProduction.objects.count()

    avg_yield = FarmProduction.objects.aggregate(
        Avg('average_yield_kg_per_hectare')
    )['average_yield_kg_per_hectare__avg']

    latest = FarmProduction.objects.order_by('-year').first()
    latest_year = latest.year if latest else None

    total_value = FarmProduction.objects.aggregate(
        Sum('total_farm_value_dollars')
    )['total_farm_value_dollars__sum']

    best_crop_data = FarmProduction.objects.values('crop_type').annotate(
        total=Sum('total_farm_value_dollars')
    ).order_by('-total').first()

    best_crop = best_crop_data['crop_type'] if best_crop_data else "N/A"


    return render(request, 'farm/index.html', {
        'total_records': total_records,
        'avg_yield': round(avg_yield, 1) if avg_yield else 0,
        'latest_year': latest_year,
        'total_value': f"${total_value:,.0f}" if total_value else 0,
        'best_crop': best_crop
    })


# 📊 CHART PAGE
def charts_view(request):
    crops = FarmProduction.objects.values_list('crop_type', flat=True).distinct()
    provinces = FarmProduction.objects.values_list('province', flat=True).distinct()

    return render(request, 'farm/charts.html', {
        'crops': crops,
        'provinces': provinces
    })


# 📈 TREND API
def api_trend(request):
    crop = request.GET.get('crop')
    province = request.GET.get('province')

    data = FarmProduction.objects.all()

    if crop:
        data = data.filter(crop_type=crop)

    if province:
        data = data.filter(province=province)

    result = data.values('year').annotate(
        avg_yield=Avg('average_yield_kg_per_hectare')
    ).order_by('year')

    labels = [str(d['year']) for d in result]
    values = [d['avg_yield'] for d in result]

    return JsonResponse({
        'labels': labels,
        'values': values
    })

# 💰 CROP VALUE API
def api_crop_value(request):
    province = request.GET.get('province')

    data = FarmProduction.objects.all()

    # 🔹 Apply province filter (IMPORTANT)
    if province:
        data = data.filter(province=province)

    # 🔹 Group by crop
    data = data.values('crop_type').annotate(
        total=Sum('total_farm_value_dollars')
    )

    labels = [d['crop_type'] for d in data]
    values = [d['total'] for d in data]

    return JsonResponse({
        'labels': labels,
        'values': values
    })


# 🔄 COMPARISON PAGE
def comparison_view(request):
    crops = FarmProduction.objects.values_list('crop_type', flat=True).distinct()
    provinces = FarmProduction.objects.values_list('province', flat=True).distinct()

    return render(request, 'farm/comparison.html', {
        'crops': crops,
        'provinces': provinces
    })


# 📊 GROUPED BAR API (COMPARISON)


def api_compare(request):
    p1 = request.GET.get('p1')
    p2 = request.GET.get('p2')
    c1 = request.GET.get('c1')
    c2 = request.GET.get('c2')
    metric = request.GET.get('metric')

    # Base queries
    data1 = FarmProduction.objects.filter(province=p1, crop_type=c1)
    data2 = FarmProduction.objects.filter(province=p2, crop_type=c2)

    # 🔹 Choose metric dynamically
    if metric == "value":
        val1 = data1.aggregate(Sum('total_farm_value_dollars'))['total_farm_value_dollars__sum']
        val2 = data2.aggregate(Sum('total_farm_value_dollars'))['total_farm_value_dollars__sum']

    elif metric == "yield":
        val1 = data1.aggregate(Avg('average_yield_kg_per_hectare'))['average_yield_kg_per_hectare__avg']
        val2 = data2.aggregate(Avg('average_yield_kg_per_hectare'))['average_yield_kg_per_hectare__avg']

    elif metric == "rainfall":
        val1 = data1.aggregate(Avg('avg_rainfall_mm'))['avg_rainfall_mm__avg']
        val2 = data2.aggregate(Avg('avg_rainfall_mm'))['avg_rainfall_mm__avg']

    elif metric == "temperature":
        val1 = data1.aggregate(Avg('avg_temperature_c'))['avg_temperature_c__avg']
        val2 = data2.aggregate(Avg('avg_temperature_c'))['avg_temperature_c__avg']

    else:
        val1 = val2 = 0

    return JsonResponse({
        "labels": [f"{p1} - {c1}", f"{p2} - {c2}"],
        "values": [val1 or 0, val2 or 0]
    })

# 📊 PREDICTION PAGE
def prediction_view(request):
    crops = FarmProduction.objects.values_list('crop_type', flat=True).distinct()
    provinces = FarmProduction.objects.values_list('province', flat=True).distinct()

    return render(request, 'farm/prediction.html', {
        'crops': crops,
        'provinces': provinces
    })


# 🔮 PREDICTION API
def predict_crop(request):
    try:
        crop = request.GET.get('crop')
        province = request.GET.get('province')

        rainfall = float(request.GET.get('rainfall') or 100)
        temperature = float(request.GET.get('temperature') or 15)
        irrigation = int(request.GET.get('irrigation') or 1)

        # Encode
        crop_val = le_crop.transform([crop])[0]
        province_val = le_province.transform([province])[0]

        # Prediction
        result = model.predict([[rainfall, temperature, irrigation, crop_val, province_val]])

        prediction = "✅ High Success" if result[0] == 1 else "❌ Low Success"

        return JsonResponse({'result': prediction})

    except Exception as e:
        return JsonResponse({'result': 'Error in prediction'})
    
from django.contrib.auth.decorators import login_required

@login_required
def upload_csv(request):
    ...

from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def upload_csv(request):
    ...
    
def upload_csv(request):
    form = UploadFileForm()

    if request.method == 'POST':
        print("📥 POST REQUEST RECEIVED")
        print(request.FILES)

        file = request.FILES.get('file')

        if not file:
            print("❌ No file received")
            return redirect('farm:index')

        print("✅ File received:", file.name)

        if form.is_valid():
            file = request.FILES['file']

            try:
                # Read file
                data = file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(data)

                temp_data = []  # 🔥 store valid rows first

                for row in reader:
                    try:
                        obj = FarmProduction(
                            year=int(row.get('year', 0)),
                            province=row.get('province', ''),
                            crop_type=row.get('crop_type', ''),
                            average_yield_kg_per_hectare=float(row.get('average_yield_kg_per_hectare') or 0),
                            total_farm_value_dollars=float(row.get('total_farm_value_dollars') or 0),
                            avg_rainfall_mm=float(row.get('avg_rainfall_mm') or 0),
                            avg_temperature_c=float(row.get('avg_temperature_c') or 0),
                            irrigation_used=row.get('irrigation_used', 'No')
                        )
                        temp_data.append(obj)

                    except Exception as e:
                        print("❌ Skipped row:", e)
                        continue

                # 🔥 ONLY delete if we have valid data
                if temp_data:
                    FarmProduction.objects.all().delete()
                    FarmProduction.objects.bulk_create(temp_data)

                    print(f"✅ Inserted {len(temp_data)} rows")

                else:
                    print("⚠️ No valid data found. Old data NOT deleted.")

                return redirect('farm:index')

            except Exception as e:
                print("❌ File processing error:", e)

    return render(request, 'farm/upload.html', {'form': form})