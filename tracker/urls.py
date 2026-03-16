from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('sessions/', views.session_list, name='session_list'),
    path('sessions/new/', views.session_new, name='session_new'),
    path('sessions/<int:pk>/', views.session_detail, name='session_detail'),
    path('sessions/<int:pk>/edit/', views.session_edit, name='session_edit'),
    path('sessions/<int:pk>/delete/', views.session_delete, name='session_delete'),

    # AJAX API
    path('api/sessions/<int:session_pk>/exercises/', views.api_add_exercise, name='api_add_exercise'),
    path('api/exercises/<int:exercise_pk>/delete/', views.api_delete_exercise, name='api_delete_exercise'),
    path('api/exercises/<int:exercise_pk>/sets/', views.api_add_set, name='api_add_set'),
    path('api/sets/<int:set_pk>/update/', views.api_update_set, name='api_update_set'),
    path('api/sets/<int:set_pk>/delete/', views.api_delete_set, name='api_delete_set'),
    path('api/sessions/<int:session_pk>/', views.api_session_data, name='api_session_data'),
]
