# Generato manualmente, andrà bene?? :/

from django.db import migrations, models



class Migration(migrations.Migration):
    dependencies = [
        ("preventivo", "0002_auto_20230820_1132"),
    ]

    operations = [
        # define auto incrementing for order number field
        migrations.RunSQL(
            """
            CREATE SEQUENCE preventivo_preventivo_number_seq OWNED BY preventivo_preventivo.number;

            SELECT setval('preventivo_preventivo_number_seq', coalesce(max(number), 0) + 1, false)
            FROM preventivo_preventivo;
        """
        ),
    ]
