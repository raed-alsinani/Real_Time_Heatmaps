from django.urls import path
from . import views

urlpatterns = [
    path('api/real-time-sensors-data', views.real_time_sensors_data, name='real-time-sensors-data'),
    path('api/history-sensors-data', views.history_sensors_data, name='history-sensors-data'),
    path('api/site-info', views.site_info, name='site-info'),
    path('api/locations', views.all_locations, name='location'),
    path('api/site_geo_json', views.site_geo_json, name='site-geo-json'),
    path('', views.dashboard_screen, name='monitor_dashboard'),
    path('history/', views.history_dashboard, name='history'),

]
