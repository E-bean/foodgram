import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


def fill_ingredient_data(path):
    try:
        with open(path, encoding="utf8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1],
                )
    except IOError:
        print("no category data")


class Command(BaseCommand):
    def handle(self, *args, **options):
        fill_ingredient_data("../../data/ingredients.csv")
        print("fixtures added to DB")
