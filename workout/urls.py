from django.contrib import admin
from django.urls import path
from workout import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Pusta ścieżka '' oznacza stronę główną (http://127.0.0.1:8080/)
    path('', views.dashboard, name='dashboard'),
    path('dodaj/', views.add_workout, name='add_workout'),
    path('trening/<int:pk>/', views.workout_detail, name='workout_detail'),
    path('seria/<int:set_id>/usun/', views.delete_set, name='delete_set'),
    path('seria/<int:set_id>/edytuj/', views.edit_set, name='edit_set'),
    path('workout/<int:pk>/delete', views.delete_workout, name='delete_workout'),
    path('metrics/add', views.add_daily_metrics, name='add_daily_metrics'),
    path('import-hevy/', views.upload_hevy_csv, name="upload_hevy_csv"),
    path('import-wagi/', views.upload_hevy_measurements, name='upload_hevy_measurements'),
]

