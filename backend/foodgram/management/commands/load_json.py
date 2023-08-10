import json
import os

from django.core.management.base import BaseCommand
from foodgram.models import Ingredient


class Command(BaseCommand):

    path = os.path.abspath('data/ingredients.json')

    def handle(self, *args, **kwargs):
        with open(self.path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for note in data:
            Ingredient.objects.get_or_create(**note)
