from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Student, Marks, Result, Class


@receiver(post_save, sender=Student)
def student_post_save(sender, instance, created, **kwargs):
    if created:
        pass


@receiver(post_save, sender=Marks)
def marks_post_save(sender, instance, created, **kwargs):
    pass


@receiver(post_delete, sender=Marks)
def marks_post_delete(sender, instance, **kwargs):
    pass


@receiver(post_save, sender=Result)
def result_post_save(sender, instance, created, **kwargs):
    pass