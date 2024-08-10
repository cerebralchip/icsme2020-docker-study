import sys
import os
import django
import itertools
import string

# Dynamically find the project root directory (assuming the script is in a subdirectory of the project)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')
django.setup()

from dockerstudy import models

try:
    models.ImageNameCrawlerTask.objects.all().delete()
    print('Delete all rows in ImageNameCrawlerTask table')
except:
    print('nothing to delete')

characters = list(string.ascii_lowercase)
characters.extend([str(i) for i in range(10)])
keywords = list(itertools.product(characters,repeat = 3))
keywords = [''.join(item) for item in keywords]

print('num of rows to be added:', len(keywords))

all_data = [models.ImageNameCrawlerTask(keyword = keyword) for keyword in keywords]

print('Bulk Saving...')

models.ImageNameCrawlerTask.objects.bulk_create(all_data, batch_size=999)