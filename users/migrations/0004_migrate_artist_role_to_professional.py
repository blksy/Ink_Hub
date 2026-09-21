from django.db import migrations


def migrate_artist_to_professional(apps, schema_editor):
    User = apps.get_model("users", "User")

    User.objects.filter(
        role="ARTIST"
    ).update(
        role="PROFESSIONAL"
    )


def migrate_professional_to_artist(apps, schema_editor):
    User = apps.get_model("users", "User")

    User.objects.filter(
        role="PROFESSIONAL"
    ).update(
        role="ARTIST"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_alter_user_role"),
    ]

    operations = [
        migrations.RunPython(
            migrate_artist_to_professional,
            migrate_professional_to_artist,
        ),
    ]