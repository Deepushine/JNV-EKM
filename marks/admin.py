from django.contrib import admin
from .models import (
    AcademicYear, Class, Subject, Teacher, Student,
    Exam, Marks, Result, ParentProfile, Attendance, Achievement,
    StudyMaterial, Assignment, AssignmentSubmission, DisciplinaryAction,
    PerformanceShare
)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_active', 'classes_count']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['-start_date']
    
    def classes_count(self, obj):
        return obj.classes.count()
    classes_count.short_description = 'Classes'


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'section', 'academic_year', 'class_teacher', 'students_count', 'subjects_count']
    list_filter = ['academic_year', 'section']
    search_fields = ['name']
    ordering = ['academic_year', 'name', 'section']
    raw_id_fields = ['class_teacher']
    
    def students_count(self, obj):
        return obj.students.filter(is_active=True).count()
    students_count.short_description = 'Students'
    
    def subjects_count(self, obj):
        return obj.subjects.count()
    subjects_count.short_description = 'Subjects'


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'subject_type', 'max_marks', 'pass_marks', 'classes_count', 'teachers_count']
    list_filter = ['subject_type']
    search_fields = ['name', 'code']
    ordering = ['name']
    filter_horizontal = ['classes']
    
    def classes_count(self, obj):
        return obj.classes.count()
    classes_count.short_description = 'Classes'
    
    def teachers_count(self, obj):
        return obj.teachers.count()
    teachers_count.short_description = 'Teachers'


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'email', 'phone', 'subjects_count', 'is_active', 'date_joined']
    list_filter = ['is_active', 'subjects']
    search_fields = ['employee_id', 'first_name', 'last_name', 'email']
    ordering = ['last_name', 'first_name']
    filter_horizontal = ['subjects']
    
    def subjects_count(self, obj):
        return obj.subjects.count()
    subjects_count.short_description = 'Subjects'
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Name'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['admission_number', 'roll_number', 'full_name', 'student_class', 'gender', 'date_of_birth', 'phone', 'is_active']
    list_filter = ['student_class', 'gender', 'is_active', 'student_class__academic_year']
    search_fields = ['admission_number', 'roll_number', 'first_name', 'last_name', 'father_name', 'mother_name']
    ordering = ['student_class', 'roll_number']
    raw_id_fields = ['student_class']
    date_hierarchy = 'admission_date'
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Name'


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'academic_year', 'start_date', 'end_date', 'classes_count', 'weightage', 'is_published']
    list_filter = ['exam_type', 'academic_year', 'is_published']
    search_fields = ['name']
    ordering = ['-start_date']
    filter_horizontal = ['classes']
    date_hierarchy = 'start_date'
    
    def classes_count(self, obj):
        return obj.classes.count()
    classes_count.short_description = 'Classes'


class MarksInline(admin.TabularInline):
    model = Marks
    extra = 0
    raw_id_fields = ['student', 'subject', 'exam', 'graded_by']
    readonly_fields = ['graded_date']


@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'exam', 'marks_obtained', 'percentage', 'grade', 'is_absent', 'graded_by', 'graded_date']
    list_filter = ['exam', 'exam__academic_year', 'subject', 'student__student_class', 'is_absent']
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_number', 'student__roll_number', 'subject__name']
    ordering = ['-exam__start_date', 'student__student_class', 'student__roll_number', 'subject__name']
    raw_id_fields = ['student', 'subject', 'exam', 'graded_by']
    readonly_fields = ['graded_date']
    list_select_related = ['student', 'student__student_class', 'subject', 'exam', 'graded_by']


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'total_marks', 'max_total_marks', 'percentage', 'grade', 'rank', 'is_pass', 'calculated_date']
    list_filter = ['exam', 'exam__academic_year', 'grade', 'is_pass']
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_number', 'student__roll_number']
    ordering = ['exam', 'rank']
    raw_id_fields = ['student', 'exam']
    readonly_fields = ['calculated_date']
    list_select_related = ['student', 'student__student_class', 'exam']


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'relationship', 'phone']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']
    filter_horizontal = ['students']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'marked_by', 'remarks']
    list_filter = ['status', 'date', 'student__student_class']
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_number']
    date_hierarchy = 'date'


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['student', 'title', 'category', 'achieved_on', 'issuer', 'created_by']
    list_filter = ['category', 'achieved_on']
    search_fields = ['student__first_name', 'student__last_name', 'title', 'issuer']


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'student_class', 'subject', 'uploaded_by', 'is_published', 'created_at']
    list_filter = ['is_published', 'subject', 'student_class']
    search_fields = ['title', 'description']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'student_class', 'subject', 'teacher', 'due_date', 'is_published']
    list_filter = ['is_published', 'student_class', 'subject', 'due_date']
    search_fields = ['title', 'instructions']


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'status', 'grade', 'submitted_at', 'reviewed_at']
    list_filter = ['status', 'assignment__student_class']
    search_fields = ['assignment__title', 'student__first_name', 'student__last_name']


@admin.register(DisciplinaryAction)
class DisciplinaryActionAdmin(admin.ModelAdmin):
    list_display = ['student', 'action_type', 'severity', 'incident_date', 'parent_visible', 'reported_by']
    list_filter = ['action_type', 'severity', 'parent_visible', 'incident_date']
    search_fields = ['student__first_name', 'student__last_name', 'description', 'resolution']


@admin.register(PerformanceShare)
class PerformanceShareAdmin(admin.ModelAdmin):
    list_display = ['student', 'token', 'is_active', 'expires_at', 'created_by', 'created_at']
    list_filter = ['is_active', 'expires_at']
    search_fields = ['student__first_name', 'student__last_name', 'token']
    readonly_fields = ['token', 'created_at']