from django.db import migrations


def migrate_employee_services(apps, schema_editor):
    Service = apps.get_model(
        "artists",
        "Service",
    )
    StudioMembership = apps.get_model(
        "studios",
        "StudioMembership",
    )
    EmployeeService = apps.get_model(
        "studios",
        "EmployeeService",
    )

    for service in Service.objects.all():
        if not service.studio_id:
            continue

        for professional in service.professionals.all():
            membership = StudioMembership.objects.filter(
                studio_id=service.studio_id,
                professional_id=professional.id,
                status="ACTIVE",
            ).first()

            if membership is None:
                continue

            EmployeeService.objects.get_or_create(
                membership_id=membership.id,
                service_id=service.id,
                defaults={
                    "price": service.price,
                    "duration_minutes": service.duration_minutes,
                    "is_active": service.is_active,
                },
            )


class Migration(migrations.Migration):

    dependencies = [
        (
            "artists",
            "0019_migrate_professional_studios",
        ),
        (
            "studios",
            "0005_alter_employeeservice_duration_minutes_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(
            migrate_employee_services,
            migrations.RunPython.noop,
        ),
    ]