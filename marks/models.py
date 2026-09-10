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
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    subjects = models.ManyToManyField(Subject, related_name='teachers', blank=True)
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
    admission_date = models.DateField()
    is_active = models.BooleanField(default=True)
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