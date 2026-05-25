# frontend/templates_config.py
import pytz
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="frontend/templates")


def format_melbourne_datetime(value):
    if not value:
        return ""

    if value.tzinfo is None:
        value = value.replace(tzinfo=pytz.UTC)

    local = value.astimezone(pytz.timezone("Australia/Melbourne"))
    return local.strftime("%d/%m/%Y %H:%M:%S %Z")


templates.env.filters["melbourne_datetime"] = format_melbourne_datetime
