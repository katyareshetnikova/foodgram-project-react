import re

from django.core.exceptions import ValidationError


def validator_username(value):
    if not re.match(r'^[\w.@+-]+\Z', value):
        raise ValidationError(
            'Недопустимые символы в имени пользователя.'
        )
