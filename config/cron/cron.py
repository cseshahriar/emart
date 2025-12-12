"""PMS > cron.py"""
from django.core.management import call_command


def db_backup():
    try:
        call_command('dbbackup')
        call_command('mediabackup')
    except Exception as e:
        print(e)
        pass
