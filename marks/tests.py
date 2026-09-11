from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AcademicYear, Class, Exam, Marks, Student, Subject, Teacher


class MarksWorkspaceTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin_user = user_model.objects.create_superuser(
            username='Admin@JNV', password='Marks@JNV', email='admin@example.com'
        )
        self.teacher_user = user_model.objects.create_user(
            username='teacher-test', password='test-pass'
        )
        self.teacher = Teacher.objects.create(
            employee_id='TEST-T', first_name='Test', last_name='Teacher',
            email='teacher-test@example.com', user=self.teacher_user,
        )
        academic_year = AcademicYear.objects.create(
            name='Test 2026', start_date=date(2026, 6, 1), end_date=date(2027, 3, 31),
        )
        self.student_class = Class.objects.create(
            name='9', section='A', academic_year=academic_year,
            class_teacher=self.teacher,
        )
        self.student = Student.objects.create(
            admission_number='TEST-S', roll_number='1', first_name='Test', last_name='Student',
            gender='O', date_of_birth=date(2012, 1, 1), student_class=self.student_class,
            father_name='Parent', mother_name='Parent', address='School', phone='0000000000',
            admission_date=date(2026, 6, 1),
        )

    def create_exam_with_subjects(self):
        maths = Subject.objects.create(name='Mathematics', code='TEST-MATH')
        english = Subject.objects.create(name='English', code='TEST-ENG')
        maths.classes.add(self.student_class)
        english.classes.add(self.student_class)
        self.teacher.subjects.add(maths)
        exam = Exam.objects.create(
            name='Unit Test', exam_type='unit_test', academic_year=self.student_class.academic_year,
            start_date=date(2026, 7, 1), end_date=date(2026, 7, 1),
        )
        exam.classes.add(self.student_class)
        return exam, maths, english

    def test_root_is_single_login_portal(self):
        response = self.client.get(reverse('marks:home'))
        self.assertRedirects(response, reverse('marks:login'))
        response = self.client.post(reverse('marks:login'), {
            'username': 'Admin@JNV', 'password': 'Marks@JNV',
        })
        self.assertRedirects(response, reverse('marks:dashboard'))

    def test_workspace_loads_for_admin(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('marks:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'JNV MarkFlow')

    def test_teacher_can_edit_only_assigned_subject_column(self):
        exam, maths, english = self.create_exam_with_subjects()
        self.client.force_login(self.teacher_user)
        response = self.client.get(reverse('marks:marks_entry', args=[exam.id, self.student_class.id]))
        self.assertContains(response, 'TEST-MATH')
        self.assertNotContains(response, 'TEST-ENG')
        self.client.post(reverse('marks:marks_entry', args=[exam.id, self.student_class.id]), {
            f'marks_{self.student.id}_{maths.id}': '88',
            f'marks_{self.student.id}_{english.id}': '99',
        })
        self.assertTrue(Marks.objects.filter(student=self.student, subject=maths, exam=exam).exists())
        self.assertFalse(Marks.objects.filter(student=self.student, subject=english, exam=exam).exists())

    def test_admin_cannot_publish_incomplete_marks(self):
        exam, maths, english = self.create_exam_with_subjects()
        Marks.objects.create(student=self.student, subject=maths, exam=exam, marks_obtained=85)
        self.client.force_login(self.admin_user)
        self.client.post(reverse('marks:calculate_results', args=[exam.id]))
        exam.refresh_from_db()
        self.assertFalse(exam.is_published)

    def test_excel_export_contains_roster_before_publication(self):
        exam, maths, english = self.create_exam_with_subjects()
        Marks.objects.create(student=self.student, subject=maths, exam=exam, marks_obtained=85)
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('marks:export_marks_excel', args=[exam.id, self.student_class.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertIn(b'PK', response.content[:2])
