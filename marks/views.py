from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Avg, Count, Q, F
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.db import transaction
import csv
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from io import BytesIO

from .models import (
    AcademicYear, Class, Subject, Teacher, Student,
    Exam, Marks, Result
)


@login_required
def dashboard(request):
    active_year = AcademicYear.objects.filter(is_active=True).first()
    total_students = Student.objects.filter(is_active=True).count()
    total_teachers = Teacher.objects.filter(is_active=True).count()
    total_classes = Class.objects.count()
    total_subjects = Subject.objects.count()
    recent_exams = Exam.objects.all()[:5]
    pending_results = Exam.objects.filter(is_published=False).count()

    context = {
        'active_year': active_year,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_classes': total_classes,
        'total_subjects': total_subjects,
        'recent_exams': recent_exams,
        'pending_results': pending_results,
    }
    return render(request, 'marks/dashboard.html', context)


class AcademicYearListView(ListView):
    model = AcademicYear
    template_name = 'marks/academic_year_list.html'
    context_object_name = 'years'
    paginate_by = 10


class AcademicYearCreateView(CreateView):
    model = AcademicYear
    template_name = 'marks/academic_year_form.html'
    fields = ['name', 'start_date', 'end_date', 'is_active']
    success_url = reverse_lazy('academic_year_list')


class AcademicYearUpdateView(UpdateView):
    model = AcademicYear
    template_name = 'marks/academic_year_form.html'
    fields = ['name', 'start_date', 'end_date', 'is_active']
    success_url = reverse_lazy('academic_year_list')


class AcademicYearDeleteView(DeleteView):
    model = AcademicYear
    template_name = 'marks/academic_year_confirm_delete.html'
    success_url = reverse_lazy('academic_year_list')


class ClassListView(ListView):
    model = Class
    template_name = 'marks/class_list.html'
    context_object_name = 'classes'
    paginate_by = 20

    def get_queryset(self):
        queryset = Class.objects.select_related('academic_year', 'class_teacher').all()
        academic_year = self.request.GET.get('academic_year')
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['academic_years'] = AcademicYear.objects.all()
        return context


class ClassCreateView(CreateView):
    model = Class
    template_name = 'marks/class_form.html'
    fields = ['name', 'section', 'academic_year', 'class_teacher']
    success_url = reverse_lazy('class_list')


class ClassUpdateView(UpdateView):
    model = Class
    template_name = 'marks/class_form.html'
    fields = ['name', 'section', 'academic_year', 'class_teacher']
    success_url = reverse_lazy('class_list')


class ClassDetailView(DetailView):
    model = Class
    template_name = 'marks/class_detail.html'
    context_object_name = 'class_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = self.object.students.filter(is_active=True)
        context['students'] = students
        context['subjects'] = self.object.subjects.all()
        return context


class SubjectListView(ListView):
    model = Subject
    template_name = 'marks/subject_list.html'
    context_object_name = 'subjects'
    paginate_by = 20


class SubjectCreateView(CreateView):
    model = Subject
    template_name = 'marks/subject_form.html'
    fields = ['name', 'code', 'subject_type', 'max_marks', 'pass_marks', 'classes']
    success_url = reverse_lazy('subject_list')


class SubjectUpdateView(UpdateView):
    model = Subject
    template_name = 'marks/subject_form.html'
    fields = ['name', 'code', 'subject_type', 'max_marks', 'pass_marks', 'classes']
    success_url = reverse_lazy('subject_list')


class TeacherListView(ListView):
    model = Teacher
    template_name = 'marks/teacher_list.html'
    context_object_name = 'teachers'
    paginate_by = 20


class TeacherCreateView(CreateView):
    model = Teacher
    template_name = 'marks/teacher_form.html'
    fields = ['employee_id', 'first_name', 'last_name', 'email', 'phone', 'subjects', 'is_active']
    success_url = reverse_lazy('teacher_list')


class TeacherUpdateView(UpdateView):
    model = Teacher
    template_name = 'marks/teacher_form.html'
    fields = ['employee_id', 'first_name', 'last_name', 'email', 'phone', 'subjects', 'is_active']
    success_url = reverse_lazy('teacher_list')


class StudentListView(ListView):
    model = Student
    template_name = 'marks/student_list.html'
    context_object_name = 'students'
    paginate_by = 30

    def get_queryset(self):
        queryset = Student.objects.select_related('student_class', 'student_class__academic_year').filter(is_active=True)
        student_class = self.request.GET.get('class')
        if student_class:
            queryset = queryset.filter(student_class_id=student_class)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(admission_number__icontains=search) |
                Q(roll_number__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.all()
        return context


class StudentCreateView(CreateView):
    model = Student
    template_name = 'marks/student_form.html'
    fields = ['admission_number', 'roll_number', 'first_name', 'last_name', 'gender',
              'date_of_birth', 'student_class', 'father_name', 'mother_name',
              'address', 'phone', 'email', 'admission_date', 'photo']
    success_url = reverse_lazy('student_list')


class StudentUpdateView(UpdateView):
    model = Student
    template_name = 'marks/student_form.html'
    fields = ['admission_number', 'roll_number', 'first_name', 'last_name', 'gender',
              'date_of_birth', 'student_class', 'father_name', 'mother_name',
              'address', 'phone', 'email', 'admission_date', 'photo', 'is_active']
    success_url = reverse_lazy('student_list')


class StudentDetailView(DetailView):
    model = Student
    template_name = 'marks/student_detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['marks'] = Marks.objects.filter(student=self.object).select_related('subject', 'exam', 'exam__academic_year')
        context['results'] = Result.objects.filter(student=self.object).select_related('exam')
        return context


class ExamListView(ListView):
    model = Exam
    template_name = 'marks/exam_list.html'
    context_object_name = 'exams'
    paginate_by = 20

    def get_queryset(self):
        queryset = Exam.objects.prefetch_related('classes').all()
        academic_year = self.request.GET.get('academic_year')
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['academic_years'] = AcademicYear.objects.all()
        return context


class ExamCreateView(CreateView):
    model = Exam
    template_name = 'marks/exam_form.html'
    fields = ['name', 'exam_type', 'academic_year', 'classes', 'start_date', 'end_date', 'weightage']
    success_url = reverse_lazy('exam_list')


class ExamUpdateView(UpdateView):
    model = Exam
    template_name = 'marks/exam_form.html'
    fields = ['name', 'exam_type', 'academic_year', 'classes', 'start_date', 'end_date', 'weightage', 'is_published']
    success_url = reverse_lazy('exam_list')


class ExamDetailView(DetailView):
    model = Exam
    template_name = 'marks/exam_detail.html'
    context_object_name = 'exam'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = self.object.classes.all()
        return context


@login_required
def marks_entry(request, exam_id, class_id):
    exam = get_object_or_404(Exam, id=exam_id)
    student_class = get_object_or_404(Class, id=class_id)
    students = student_class.students.filter(is_active=True)
    subjects = student_class.subjects.all()

    if request.method == 'POST':
        with transaction.atomic():
            for student in students:
                for subject in subjects:
                    marks_key = f'marks_{student.id}_{subject.id}'
                    absent_key = f'absent_{student.id}_{subject.id}'
                    remarks_key = f'remarks_{student.id}_{subject.id}'

                    marks_value = request.POST.get(marks_key)
                    is_absent = request.POST.get(absent_key) == 'on'
                    remarks = request.POST.get(remarks_key, '')

                    if marks_value or is_absent:
                        marks_obj, created = Marks.objects.update_or_create(
                            student=student,
                            subject=subject,
                            exam=exam,
                            defaults={
                                'marks_obtained': marks_value if marks_value and not is_absent else 0,
                                'is_absent': is_absent,
                                'graded_by': request.user.teacher if hasattr(request.user, 'teacher') else None,
                                'remarks': remarks,
                            }
                        )
        messages.success(request, 'Marks saved successfully!')
        return redirect('marks_entry', exam_id=exam.id, class_id=student_class.id)

    existing_marks = Marks.objects.filter(exam=exam, student__in=students).select_related('student', 'subject')
    marks_dict = {(m.student_id, m.subject_id): m for m in existing_marks}

    context = {
        'exam': exam,
        'student_class': student_class,
        'students': students,
        'subjects': subjects,
        'marks_dict': marks_dict,
    }
    return render(request, 'marks/marks_entry.html', context)


@login_required
def calculate_results(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.method == 'POST':
        with transaction.atomic():
            for student_class in exam.classes.all():
                students = student_class.students.filter(is_active=True)
                for student in students:
                    marks = Marks.objects.filter(student=student, exam=exam)
                    if marks.exists():
                        result, created = Result.objects.update_or_create(
                            student=student,
                            exam=exam,
                            defaults={}
                        )
                        result.calculate_result()

        exam.is_published = True
        exam.save()
        messages.success(request, 'Results calculated and published successfully!')
        return redirect('exam_detail', pk=exam.id)

    context = {'exam': exam}
    return render(request, 'marks/calculate_results.html', context)


@login_required
def result_sheet(request, exam_id, class_id):
    exam = get_object_or_404(Exam, id=exam_id)
    student_class = get_object_or_404(Class, id=class_id)
    students = student_class.students.filter(is_active=True)

    results = Result.objects.filter(exam=exam, student__in=students).select_related('student')
    results = sorted(results, key=lambda x: float(x.percentage), reverse=True)

    for idx, result in enumerate(results, 1):
        result.rank = idx
        result.save()

    subjects = student_class.subjects.all()

    context = {
        'exam': exam,
        'student_class': student_class,
        'results': results,
        'subjects': subjects,
    }
    return render(request, 'marks/result_sheet.html', context)


@login_required
def student_report_card(request, student_id, exam_id):
    student = get_object_or_404(Student, id=student_id)
    exam = get_object_or_404(Exam, id=exam_id)
    marks = Marks.objects.filter(student=student, exam=exam).select_related('subject')
    result = Result.objects.filter(student=student, exam=exam).first()

    if not result:
        result = Result(student=student, exam=exam)
        result.calculate_result()

    context = {
        'student': student,
        'exam': exam,
        'marks': marks,
        'result': result,
        'school_name': 'Jawahar Navodaya Vidyalaya, Ernakulam',
    }
    return render(request, 'marks/report_card.html', context)


@login_required
def export_marks_excel(request, exam_id, class_id):
    exam = get_object_or_404(Exam, id=exam_id)
    student_class = get_object_or_404(Class, id=class_id)
    students = student_class.students.filter(is_active=True)
    subjects = student_class.subjects.all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{exam.name} Marks"

    header_font = Font(bold=True, size=12)
    header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    header_font_white = Font(bold=True, size=12, color='FFFFFF')
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)

    ws.merge_cells('A1:F1')
    ws['A1'] = 'JAWAHAR NAVODAYA VIDYALAYA, ERNAKULAM'
    ws['A1'].font = Font(bold=True, size=16)
    ws['A1'].alignment = Alignment(horizontal='center')

    ws.merge_cells('A2:F2')
    ws['A2'] = f'{exam.name} - {exam.exam_type}'
    ws['A2'].font = Font(bold=True, size=14)
    ws['A2'].alignment = Alignment(horizontal='center')

    ws.merge_cells('A3:F3')
    ws['A3'] = f'Class: {student_class.name}{student_class.section} | Academic Year: {student_class.academic_year}'
    ws['A3'].font = Font(size=12)
    ws['A3'].alignment = Alignment(horizontal='center')

    row = 5
    headers = ['Roll No', 'Admission No', 'Student Name']
    for subject in subjects:
        headers.append(f'{subject.name}\n({subject.max_marks})')
    headers.extend(['Total', 'Max Total', 'Percentage', 'Grade', 'Rank'])

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col, value=header)
        cell.font = header_font_white
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border

    results = Result.objects.filter(exam=exam, student__in=students).select_related('student')
    results = sorted(results, key=lambda x: float(x.percentage), reverse=True)

    for idx, result in enumerate(results, 1):
        row += 1
        student = result.student
        marks = Marks.objects.filter(student=student, exam=exam).select_related('subject')
        marks_dict = {m.subject_id: m for m in marks}

        ws.cell(row=row, column=1, value=student.roll_number).border = thin_border
        ws.cell(row=row, column=1).alignment = center_align
        ws.cell(row=row, column=2, value=student.admission_number).border = thin_border
        ws.cell(row=row, column=2).alignment = center_align
        ws.cell(row=row, column=3, value=student.full_name).border = thin_border

        col = 4
        for subject in subjects:
            mark = marks_dict.get(subject.id)
            if mark:
                if mark.is_absent:
                    cell_value = 'AB'
                else:
                    cell_value = f"{mark.marks_obtained}/{subject.max_marks}"
            else:
                cell_value = '-'
            cell = ws.cell(row=row, column=col, value=cell_value)
            cell.border = thin_border
            cell.alignment = center_align
            col += 1

        ws.cell(row=row, column=col, value=float(result.total_marks)).border = thin_border
        ws.cell(row=row, column=col).alignment = center_align
        col += 1
        ws.cell(row=row, column=col, value=result.max_total_marks).border = thin_border
        ws.cell(row=row, column=col).alignment = center_align
        col += 1
        ws.cell(row=row, column=col, value=f"{result.percentage}%").border = thin_border
        ws.cell(row=row, column=col).alignment = center_align
        col += 1
        ws.cell(row=row, column=col, value=result.grade).border = thin_border
        ws.cell(row=row, column=col).alignment = center_align
        col += 1
        ws.cell(row=row, column=col, value=result.rank).border = thin_border
        ws.cell(row=row, column=col).alignment = center_align

    for column_cells in ws.columns:
        max_length = 0
        column = column_cells[0].column_letter
        for cell in column_cells:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 20)
        ws.column_dimensions[column].width = adjusted_width

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{exam.name}_{student_class.name}{student_class.section}_marks.xlsx"'
    wb.save(response)
    return response


@login_required
def export_report_card_pdf(request, student_id, exam_id):
    pass


@login_required
def class_performance(request, class_id):
    student_class = get_object_or_404(Class, id=class_id)
    exams = Exam.objects.filter(classes=student_class).order_by('-start_date')

    exam_data = []
    for exam in exams:
        students = student_class.students.filter(is_active=True)
        results = Result.objects.filter(exam=exam, student__in=students)
        if results.exists():
            avg_percentage = results.aggregate(avg=Avg('percentage'))['avg']
            pass_count = results.filter(is_pass=True).count()
            total_count = results.count()
            pass_percentage = (pass_count / total_count * 100) if total_count > 0 else 0
            exam_data.append({
                'exam': exam,
                'avg_percentage': round(avg_percentage, 2) if avg_percentage else 0,
                'pass_percentage': round(pass_percentage, 2),
                'total_students': total_count,
            })

    context = {
        'student_class': student_class,
        'exam_data': exam_data,
    }
    return render(request, 'marks/class_performance.html', context)


@login_required
def subject_analysis(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    exams = Exam.objects.filter(classes__subjects=subject).distinct().order_by('-start_date')

    exam_analysis = []
    for exam in exams:
        marks = Marks.objects.filter(subject=subject, exam=exam).select_related('student')
        if marks.exists():
            total_students = marks.count()
            present_students = marks.filter(is_absent=False).count()
            absent_students = total_students - present_students
            passed = marks.filter(is_absent=False, marks_obtained__gte=subject.pass_marks).count()
            failed = present_students - passed
            avg_marks = marks.filter(is_absent=False).aggregate(avg=Avg('marks_obtained'))['avg']
            max_marks = marks.filter(is_absent=False).aggregate(max=Max('marks_obtained'))['max']
            min_marks = marks.filter(is_absent=False).aggregate(min=Min('marks_obtained'))['min']

            exam_analysis.append({
                'exam': exam,
                'total_students': total_students,
                'present_students': present_students,
                'absent_students': absent_students,
                'passed': passed,
                'failed': failed,
                'pass_percentage': round((passed / present_students * 100), 2) if present_students > 0 else 0,
                'avg_marks': round(avg_marks, 2) if avg_marks else 0,
                'max_marks': max_marks,
                'min_marks': min_marks,
            })

    context = {
        'subject': subject,
        'exam_analysis': exam_analysis,
    }
    return render(request, 'marks/subject_analysis.html', context)


@login_required
def api_student_marks(request, student_id, exam_id):
    student = get_object_or_404(Student, id=student_id)
    exam = get_object_or_404(Exam, id=exam_id)
    marks = Marks.objects.filter(student=student, exam=exam).select_related('subject')

    data = []
    for mark in marks:
        data.append({
            'subject': mark.subject.name,
            'subject_code': mark.subject.code,
            'max_marks': mark.subject.max_marks,
            'marks_obtained': float(mark.marks_obtained),
            'percentage': mark.percentage,
            'grade': mark.grade,
            'is_absent': mark.is_absent,
        })

    result = Result.objects.filter(student=student, exam=exam).first()
    if result:
        data.append({
            'total_marks': float(result.total_marks),
            'max_total_marks': result.max_total_marks,
            'percentage': float(result.percentage),
            'grade': result.grade,
            'rank': result.rank,
            'is_pass': result.is_pass,
        })

    return JsonResponse({'marks': data})