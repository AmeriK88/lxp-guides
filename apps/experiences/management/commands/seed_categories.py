from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.experiences.models import Category


DEFAULT_CATEGORIES = [
    "Volcanes",
    "Senderismo",
    "Playas",
    "Gastronomía",
    "Cultura",
    "Familia",
    "Aventura",
    "Miradores",
    "Bodegas",
    "Actividades acuáticas",
]


class Command(BaseCommand):
    help = "Create default categories for LanzaXperience"

    def handle(self, *args, **options):
        created_count = 0

        for name in DEFAULT_CATEGORIES:
            slug = slugify(name)
            obj, created = Category.objects.get_or_create(
                slug=slug,
                defaults={"name": name},
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Done. Created {created_count} categories."))
