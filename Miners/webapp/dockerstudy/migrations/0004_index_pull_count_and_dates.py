from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dockerstudy', '0003_grypescanresult_remove_dockerhubuser_idx_username_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='Image',
            index=models.Index(fields=['pull_count'], name='idx_pull_count'),
        ),

        migrations.AddIndex(
            model_name='Image',
            index=models.Index(fields=['created_at'], name='idx_created_at'),
        ),

        migrations.AddIndex(
            model_name='Image',
            index=models.Index(fields=['updated_at'], name='idx_updated_at'),
        ),
    ]

