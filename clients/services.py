from clients.models import ClientProfile


def create_client_profile(user):
    client, _ = ClientProfile.objects.get_or_create(
        user=user
    )

    return client