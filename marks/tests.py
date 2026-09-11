from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AcademicYear, Class, ParentProfile, PerformanceShare, Student, Teacher


class PortalAccessTests(TestCase):
	def setUp(self):
		user_model = get_user_model()
		self.teacher_user = user_model.objects.create_user(username='teacher-test', password='test-pass')
		self.student_user = user_model.objects.create_user(username='student-test', password='test-pass')
		self.parent_user = user_model.objects.create_user(username='parent-test', password='test-pass')
		self.teacher = Teacher.objects.create(
			employee_id='TEST-T', first_name='Test', last_name='Teacher',
			email='teacher-test@example.com', user=self.teacher_user,
		)
		academic_year = AcademicYear.objects.create(
			name='Test 2026', start_date=date(2026, 6, 1), end_date=date(2027, 3, 31),
		)
		student_class = Class.objects.create(
			name='9', section='A', academic_year=academic_year, class_teacher=self.teacher,
		)
		self.student = Student.objects.create(
			admission_number='TEST-S', roll_number='1', first_name='Test', last_name='Student',
			gender='O', date_of_birth=date(2012, 1, 1), student_class=student_class,
			father_name='Parent', mother_name='Parent', address='School', phone='0000000000',
			admission_date=date(2026, 6, 1), user=self.student_user,
		)
		parent = ParentProfile.objects.create(user=self.parent_user)
		parent.students.add(self.student)
		self.share = PerformanceShare.objects.create(student=self.student, created_by=self.parent_user)

	def test_home_is_public(self):
		response = self.client.get(reverse('marks:home'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Hello,')

	def test_teacher_portal_loads(self):
		self.client.login(username='teacher-test', password='test-pass')
		response = self.client.get(reverse('marks:portal_dashboard'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Teaching tools')

	def test_student_and_parent_portals_load(self):
		self.client.login(username='student-test', password='test-pass')
		self.assertEqual(self.client.get(reverse('marks:portal_dashboard')).status_code, 200)
		self.assertEqual(self.client.get(reverse('marks:teacher_create_assignment')).status_code, 302)
		self.client.logout()
		self.client.login(username='parent-test', password='test-pass')
		self.assertEqual(self.client.get(reverse('marks:portal_dashboard')).status_code, 200)

	def test_share_page_is_public_and_tokenized(self):
		response = self.client.get(reverse('marks:shared_performance', args=[self.share.token]))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.student.full_name)
