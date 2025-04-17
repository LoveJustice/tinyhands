import os
import sys
from subprocess import run

def run_django_command(command):
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'dreamsuite.settings.local'
    return run(['python', 'application/manage.py', command], env=env)

def dev():
    run_django_command('runserver')

def migrate():
    run_django_command('migrate')

def test():
    run_django_command('test')

def shell():
    run_django_command('shell')

if __name__ == '__main__':
    command = sys.argv[1]
    globals()[command]() 