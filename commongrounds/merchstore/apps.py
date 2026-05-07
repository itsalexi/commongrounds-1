from django.apps import AppConfig


class MerchstoreConfig(AppConfig):
    name = 'merchstore'

    def ready(self):
        import merchstore.signals
