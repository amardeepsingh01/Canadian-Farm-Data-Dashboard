from django.urls import path
from . import views

app_name = 'farm'

urlpatterns = [
    path('', views.index, name='index'),

    path('charts/', views.charts_view, name='charts'),

    path('api/trend/', views.api_trend, name='api_trend'),

    path('api/crop-value/', views.api_crop_value, name='crop_value'),

    path('comparison/', views.comparison_view, name='comparison'),
    path('api/compare/', views.api_compare, name='compare'),

    path('prediction/', views.prediction_view, name='prediction'),
    path('api/predict/', views.predict_crop, name='predict_crop'),
    path('upload/', views.upload_csv, name='upload_csv'),
    

]
