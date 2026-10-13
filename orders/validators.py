from datetime import date
from django.core.exceptions import ValidationError
import re


def validate_future_date(value):
    if value < date.today():
        raise ValidationError("Delivery date cannot be in the past.")
    

def validate_indian_pin(value):
    if not re.fullmatch(r"^[1-9][0-9]{5}",value):
        raise ValidationError("Enter a valid Indian PIN code")
