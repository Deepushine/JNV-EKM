from django.urls import path
from . import views

app_name = 'marks'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('academic-years/', views.AcademicYearListView.as_view(), name='academic_year_list'),
    path('academic-years/add/', views.AcademicYearCreateView.as_view(), name='academic_year_create'),
    path('academic-years/<int:pk>/edit/', views.AcademicYearUpdateView.as_view(), name='academic_year_update'),
    path('academic-years/<int:pk>/delete/', views.AcademicYearDeleteView.as_view(), name='academic_year_delete'),

    path('classes/', views.ClassListView.as_view(), name='class_list'),
    path('classes/add/', views.ClassCreateView.as_view(), name='class_create'),
    path('classes/<int:pk>/edit/', views.ClassUpdateView.as_view(), name='class_update'),
    path('classes/<int:pk>/', views.ClassDetailView.as_view(), name='class_detail'),

    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('subjects/add/', views.SubjectCreateView.as_view(), name='subject_create'),
    path('subjects/<int:pk>/edit/', views.SubjectUpdateView.as_view(), name='subject_update'),

    path('teachers/', views.TeacherListView.as_view(), name='teacher_list'),
    path('teachers/add/', views.TeacherCreateView.as_view(), name='teacher_create'),
    path('teachers/<int:pk>/edit/', views.TeacherUpdateView.as_view(), name='teacher_update'),

    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/add/', views.StudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_update'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),

    path('exams/', views.ExamListView.as_view(), name='exam_list'),
    path('exams/add/', views.ExamCreateView.as_view(), name='exam_create'),
    path('exams/<int:pk>/edit/', views.ExamUpdateView.as_view(), name='exam_update'),
    path('exams/<int:pk>/', views.ExamDetailView.as_view(), name='exam_detail'),

    path('marks/entry/<int:exam_id>/<int:class_id>/', views.marks_entry, name='marks_entry'),
    path('results/calculate/<int:exam_id>/', views.calculate_results, name='calculate_results'),
    path('results/sheet/<int:exam_id>/<int:class_id>/', views.result_sheet, name='result_sheet'),
    path('report-card/<int:student_id>/<int:exam_id>/', views.student_report_card, name='report_card'),

    path('export/marks/<int:exam_id>/<int:class_id>/', views.export_marks_excel, name='export_marks_excel'),
    path('export/report-card/<int:student_id>/<int:exam_id>/', views.export_report_card_pdf, name='export_report_card_pdf'),

    path('analytics/class/<int:class_id>/', views.class_performance, name='class_performance'),
    path('analytics/subject/<int:subject_id>/', views.subject_analysis, name='subject_analysis'),

    path('api/student/<int:student_id>/exam/<int:exam_id>/', views.api_student_marks, name='api_student_marks'),
]