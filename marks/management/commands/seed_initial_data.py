import os
from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from marks.models import AcademicYear, Class, Teacher


class Command(BaseCommand):
    help = 'Create the initial MarkFlow accounts, academic year, and classes.'

    def handle(self, *args, **options):
        admin_username = os.environ.get('ADMIN_USERNAME')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        teacher_username = os.environ.get('TEACHER_USERNAME')
        teacher_password = os.environ.get('TEACHER_PASSWORD')
        if not all((admin_username, admin_password, teacher_username, teacher_password)):
            raise CommandError(
                'Set ADMIN_USERNAME, ADMIN_PASSWORD, TEACHER_USERNAME, and TEACHER_PASSWORD.'
            )

        user_model = get_user_model()
        admin, _ = user_model.objects.get_or_create(username=admin_username)
        admin.is_staff = True
        admin.is_superuser = True
        admin.is_active = True
        admin.set_password(admin_password)
        admin.save()

        teacher_user, _ = user_model.objects.get_or_create(username=teacher_username)
        teacher_user.is_active = True
        teacher_user.is_staff = False
        teacher_user.is_superuser = False
        teacher_user.set_password(teacher_password)
        teacher_user.save()

        academic_year, _ = AcademicYear.objects.get_or_create(
            name='2026-27',
            defaults={
                'start_date': date(2026, 6, 1),
                'end_date': date(2027, 3, 31),
                'is_active': True,
            },
        )
        if not academic_year.is_active:
            academic_year.is_active = True
            academic_year.save(update_fields=['is_active'])

        teacher, _ = Teacher.objects.get_or_create(
            employee_id='TEACHERS-JNV',
            defaults={
                'first_name': 'JNV',
                'last_name': 'Teacher',
                'email': f'{teacher_username.lower()}@jnv.local',
            },
        )
        teacher.user = teacher_user
        teacher.is_active = True
        teacher.approval_status = 'approved'
        teacher.save()

        classes = [
            Class.objects.get_or_create(name=str(grade), section=section, academic_year=academic_year)[0]
            for grade in range(6, 13)
            for section in ('A', 'B')
        ]
        teacher.assigned_classes.set(classes)

        self.stdout.write(self.style.SUCCESS(
            f'Initial MarkFlow data ready: {len(classes)} classes, admin {admin_username}, teacher {teacher_username}.'
        ))
