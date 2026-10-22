from artists.models import ProfessionalProfile


def create_professional_profile(user):
    professional, created = ProfessionalProfile.objects.get_or_create(
        user=user
    )

    return professional