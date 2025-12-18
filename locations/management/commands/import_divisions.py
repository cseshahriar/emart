import json

from django.core.management.base import BaseCommand

from locations.models import Division


class Command(BaseCommand):
    help = "Import divisions from JSON file"
    # python manage.py import_divisions ./fixtures/data/bd-divisions.json

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file", type=str, help="Path to divisions JSON file"
        )

    def handle(self, *args, **options):
        json_file = options["json_file"]

        try:
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            divisions = data.get("divisions", [])

            created_count = 0

            for item in divisions:
                district, created = Division.objects.update_or_create(
                    id=int(item["id"]),
                    defaults={
                        "name": item["name"],
                        "bn_name": item["bn_name"],
                    },
                )

                if created:
                    created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"✔ Successfully imported {created_count} districts"
                )
            )

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR("❌ JSON file not found"))
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR("❌ Invalid JSON file"))
