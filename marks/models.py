import uuid

from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class AcademicYear(models.Model):
    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active:
            AcademicYear.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class Class(models.Model):
    SECTION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]
    name = models.CharField(max_length=20)
    section = models.CharField(max_length=1, choices=SECTION_CHOICES)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='classes')
    class_teacher = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='classes')

    class Meta:
        unique_together = ['name', 'section', 'academic_year']
        ordering = ['name', 'section']

    def __str__(self):
        return f"{self.name}{self.section} ({self.academic_year})"


class Subject(models.Model):
    SUBJECT_TYPES = [
        ('core', 'Core Subject'),
        ('elective', 'Elective'),
        ('language', 'Language'),
        ('practical', 'Practical'),
    ]
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    subject_type = models.CharField(max_length=20, choices=SUBJECT_TYPES, default='core')
    max_marks = models.PositiveIntegerField(default=100)
    pass_marks = models.PositiveIntegerField(default=33)
    classes = models.ManyToManyField(Class, related_name='subjects')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Teacher(models.Model):
    ROLE_CHOICES = [
        ('teacher', 'Teacher'),
        ('ahm', 'Assistant House Master/Matron'),
        ('hm', 'House Master/Matron'),
        ('other', 'Other duty'),
    ]
    APPROVAL_CHOICES = [
        ('pending', 'Pending approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='teacher_profile')
    phone = models.CharField(max_length=15, blank=True)
    subjects = models.ManyToManyField(Subject, related_name='teachers', blank=True)
    assigned_classes = models.ManyToManyField(Class, related_name='subject_teachers', blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='teacher')
    duties = models.CharField(max_length=255, blank=True, help_text='Additional duties, such as house or club responsibility')
    approval_status = models.CharField(max_length=12, choices=APPROVAL_CHOICES, default='approved')
    date_joined = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Student(models.Model):
    APPROVAL_CHOICES = [
        ('pending', 'Pending approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    admission_number = models.CharField(max_length=20, unique=True)
    roll_number = models.CharField(max_length=10)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students')
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='student_profile')
    admission_date = models.DateField()
    is_active = models.BooleanField(default=True)
    approval_status = models.CharField(max_length=12, choices=APPROVAL_CHOICES, default='approved')
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)

    class Meta:
        unique_together = ['roll_number', 'student_class']
        ordering = ['student_class', 'roll_number']

    def __str__(self):
        return f"{self.admission_number} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Exam(models.Model):
    EXAM_TYPES = [
        ('unit_test', 'Unit Test'),
        ('monthly_test', 'Monthly Test'),
        ('quarterly', 'Quarterly Exam'),
        ('half_yearly', 'Half Yearly Exam'),
        ('annual', 'Annual Exam'),
        ('pre_board', 'Pre-Board Exam'),
        ('board', 'Board Exam'),
    ]
    name = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='exams')
    classes = models.ManyToManyField(Class, related_name='exams')
    start_date = models.DateField()
    end_date = models.DateField()
    is_published = models.BooleanField(default=False)
    weightage = models.DecimalField(max_digits=5, decimal_places=2, default=100.00, help_text="Weightage for final calculation")

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.exam_type})"


class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='marks')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='marks')
    marks_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    is_absent = models.BooleanField(default=False)
    graded_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_marks')
    graded_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ['student', 'subject', 'exam']
        ordering = ['student', 'exam', 'subject']

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.exam}: {self.marks_obtained}"

    @property
    def percentage(self):
        if self.subject.max_marks > 0:
            return round((float(self.marks_obtained) / self.subject.max_marks) * 100, 2)
        return 0

    @property
    def is_pass(self):
        return float(self.marks_obtained) >= self.subject.pass_marks

    @property
    def grade(self):
        percentage = self.percentage
        if percentage >= 90:
            return 'A1'
        elif percentage >= 80:
            return 'A2'
        elif percentage >= 70:
            return 'B1'
        elif percentage >= 60:
            return 'B2'
        elif percentage >= 50:
            return 'C1'
        elif percentage >= 40:
            return 'C2'
        elif percentage >= 33:
            return 'D'
        else:
            return 'E'


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    total_marks = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    max_total_marks = models.PositiveIntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rank = models.PositiveIntegerField(null=True, blank=True)
    grade = models.CharField(max_length=2, blank=True)
    is_pass = models.BooleanField(default=False)
    calculated_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'exam']
        ordering = ['exam', 'rank']

    def __str__(self):
        return f"{self.student} - {self.exam}: {self.percentage}% (Rank: {self.rank})"

    def calculate_result(self):
        marks = Marks.objects.filter(student=self.student, exam=self.exam)
        self.max_total_marks = sum(m.subject.max_marks for m in marks)
        self.total_marks = sum(float(m.marks_obtained) for m in marks if not m.is_absent)
        if self.max_total_marks > 0:
            self.percentage = round((self.total_marks / self.max_total_marks) * 100, 2)
        else:
            self.percentage = 0
        self.is_pass = all(m.is_pass for m in marks if not m.is_absent)
        if self.percentage >= 90:
            self.grade = 'A1'
        elif self.percentage >= 80:
            self.grade = 'A2'
        elif self.percentage >= 70:
            self.grade = 'B1'
        elif self.percentage >= 60:
            self.grade = 'B2'
        elif self.percentage >= 50:
            self.grade = 'C1'
        elif self.percentage >= 40:
            self.grade = 'C2'
        elif self.percentage >= 33:
            self.grade = 'D'
        else:
            self.grade = 'E'
        self.save()


class ParentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parent_profile')
    students = models.ManyToManyField(Student, related_name='parents', blank=True)
    phone = models.CharField(max_length=15, blank=True)
    relationship = models.CharField(max_length=40, default='Parent')

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='present')
    marked_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='attendance_records')
    remarks = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'student__roll_number']
        constraints = [models.UniqueConstraint(fields=['student', 'date'], name='unique_student_attendance_date')]


class Achievement(models.Model):
    CATEGORY_CHOICES = [
        ('academic', 'Academic'),
        ('sports', 'Sports'),
        ('arts', 'Arts & Culture'),
        ('service', 'Leadership & Service'),
        ('other', 'Other'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='academic')
    description = models.TextField(blank=True)
    achieved_on = models.DateField()
    issuer = models.CharField(max_length=120, blank=True)
    evidence_url = models.URLField(blank=True)
    created_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='achievements_created')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-achieved_on', '-created_at']


class StudyMaterial(models.Model):
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='study_materials')
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True, related_name='study_materials')
    uploaded_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='study_materials')
    file = models.FileField(upload_to='study_materials/', blank=True)
    external_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Assignment(models.Model):
    title = models.CharField(max_length=160)
    instructions = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='assignments')
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='assignments')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='assignments')
    due_date = models.DateField()
    attachment = models.FileField(upload_to='assignments/', blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date', '-created_at']


class AssignmentSubmission(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('late', 'Late'),
    ]
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='assignment_submissions')
    response = models.TextField(blank=True)
    attachment = models.FileField(upload_to='assignment_submissions/', blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='submitted')
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']
        constraints = [models.UniqueConstraint(fields=['assignment', 'student'], name='unique_assignment_submission')]


class DisciplinaryAction(models.Model):
    ACTION_CHOICES = [
        ('note', 'Note'),
        ('warning', 'Warning'),
        ('counselling', 'Counselling'),
        ('action', 'Disciplinary Action'),
    ]
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='disciplinary_actions')
    reported_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='disciplinary_actions')
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, default='note')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='low')
    incident_date = models.DateField()
    description = models.TextField()
    resolution = models.TextField(blank=True)
    parent_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-incident_date', '-created_at']


class StudentRole(models.Model):
    ROLE_CHOICES = [
        ('captain', 'Captain'),
        ('vice_captain', 'Vice Captain'),
        ('prefect', 'Prefect'),
        ('other', 'Other role'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='roles')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    title = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-is_active', '-start_date']

    def __str__(self):
        return self.title or self.get_role_display()


class StudentLeave(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='leaves')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='requested')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_student_leaves')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']


class StudentClassChangeRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='class_change_requests')
    requested_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_change_requests')
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_class_change_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']


class PerformanceShare(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='performance_shares')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='performance_shares')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']