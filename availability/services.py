from datetime import date

from django.db.models import QuerySet
from datetime import date, datetime
from django.utils import timezone

from availability.models import WorkingHours, TimeOff
from studios.models import StudioMembership


def get_working_hours_for_date(
    membership: StudioMembership,
    target_date: date,
) -> QuerySet[WorkingHours]:

    weekday = target_date.weekday()

    working_hours_qs = WorkingHours.objects.filter(
        membership=membership,
        weekday=weekday,
        is_active=True,
    ).order_by("start_time")

    return working_hours_qs

def get_working_intervals_for_date(
    membership: StudioMembership,
    target_date: date,
) -> list[tuple[datetime, datetime]]:

    working_hours_qs = get_working_hours_for_date(
        membership,
        target_date,
    )

    intervals = []

    for working_hours in working_hours_qs:

        start = timezone.make_aware(
            datetime.combine(
                target_date,
                working_hours.start_time,
            )
        )

        end = timezone.make_aware(
            datetime.combine(
                target_date,
                working_hours.end_time,
            )
        )

        intervals.append((start, end))

    return intervals