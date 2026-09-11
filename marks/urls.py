from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'marks'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', LoginView.as_view(template_name='marks/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('school-setup/', views.school_setup, name='school_setup'),
    path('marks/entry/<int:exam_id>/<int:class_id>/', views.marks_entry, name='marks_entry'),
    path('results/calculate/<int:exam_id>/', views.calculate_results, name='calculate_results'),
    path('results/sheet/<int:exam_id>/<int:class_id>/', views.result_sheet, name='result_sheet'),
    path('report-card/<int:student_id>/<int:exam_id>/', views.student_report_card, name='report_card'),

    path('export/marks/<int:exam_id>/<int:class_id>/', views.export_marks_excel, name='export_marks_excel'),
    path('export/report-card/<int:student_id>/<int:exam_id>/', views.export_report_card_pdf, name='export_report_card_pdf'),

]