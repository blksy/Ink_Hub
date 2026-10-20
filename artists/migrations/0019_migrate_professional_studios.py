from django.db import migrations


def migrate_professional_studios(apps, schema_editor):
    ProfessionalProfile = apps.get_model(
        "artists",
        "ProfessionalProfile",
    )
    Service = apps.get_model(
        "artists",
        "Service",
    )
    Studio = apps.get_model(
        "studios",
        "Studio",
    )
    StudioMembership = apps.get_model(
        "studios",
        "StudioMembership",
    )

    for profile in ProfessionalProfile.objects.all():
        if not profile.studio_name:
            continue

        studio = Studio.objects.create(
            name=profile.studio_name,
            location=profile.location,
        )

        StudioMembership.objects.create(
            studio=studio,
            professional=profile,
            role="OWNER",
            status="ACTIVE",
        )

        studio.categories.set(
            profile.categories.all()
        )

        Service.objects.filter(
            professional=profile,
            studio__isnull=True,
        ).update(
            studio=studio
        )


class Migration(migrations.Migration):

    dependencies = [
        ("artists", "0018_migrate_service_professionals"),
        ("studios", "0003_studio_categories"),
    ]

    operations = [
        migrations.RunPython(
            migrate_professional_studios,
            migrations.RunPython.noop,
        ),
    ]