from django.db import models
from django.core.exceptions import ValidationError

class WorkingHours(models.Model):
    membership = models.ForeignKey(
        "studios.StudioMembership",
        on_delete=models.CASCADE,
        related_name="working_hours",
    )

    weekday = models.PositiveSmallIntegerField(
        choices=[
            (0, "Poniedziałek"),
            (1, "Wtorek"),
            (2, "Środa"),
            (3, "Czwartek"),
            (4, "Piątek"),
            (5, "Sobota"),
            (6, "Niedziela"),
        ]
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    is_active = models.BooleanField(
        default=True
    )
  
    def clean(self):
        super().clean()

        if (
            self.start_time is not None
            and self.end_time is not None
            and self.start_time >= self.end_time
        ):
            raise ValidationError({
                "end_time": "End time must be after start time."
            })

        if self.weekday is not None and not 0 <= self.weekday <= 6:
            raise ValidationError({
                "weekday": "Weekday must be between 0 and 6."
            })

        if (
            not self.is_active
            or not self.membership_id
            or self.weekday is None
            or self.start_time is None
            or self.end_time is None
        ):
            return

        conflicting_hours = WorkingHours.objects.filter(
            membership_id=self.membership_id,
            weekday=self.weekday,
           is_active=True,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
       ).exclude(pk=self.pk)

        if conflicting_hours.exists():
            raise ValidationError({
                "start_time": "Working hours overlap with an existing interval."
            })


    def __str__(self):
        return (
            f"{self.membership.professional} - "
            f"{self.get_weekday_display()} "
            f"({self.start_time} - {self.end_time})"
        )