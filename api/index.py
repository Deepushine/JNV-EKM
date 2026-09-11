import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jnv_marks.settings')

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

application = get_wsgi_application()

if os.environ.get('DATABASE_URL'):
	call_command('migrate', interactive=False, verbosity=0)
	if all(os.environ.get(key) for key in (
		'ADMIN_USERNAME', 'ADMIN_PASSWORD', 'TEACHER_USERNAME', 'TEACHER_PASSWORD',
	)):
		call_command('seed_initial_data', verbosity=0)
