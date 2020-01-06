import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for app in os.listdir(BASE_DIR):
    if os.path.isdir(app):
        migrations = os.path.join(BASE_DIR, app, 'migrations')
        if os.path.exists(migrations):
            for logfile in os.listdir(migrations):
                if not logfile.startswith('__'):
                    os.remove(os.path.join(migrations, logfile))
                    print('Del', os.path.join(migrations, logfile))
print('Done')