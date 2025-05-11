from datetime import datetime, timedelta, date
from typing import Tuple, Union
import math, xlwt

from django.http import HttpResponse
from django.utils import timezone

from dateutil import parser

import logging

logger = logging.getLogger(__name__)


def convert_timedelta_to_h_m_s(duration: timedelta) -> Tuple[int, int, int]:

    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    return hours, minutes, seconds


def convert_timedelta_to_h_m(duration: timedelta) -> Tuple[int, int]:

    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60

    return hours, minutes


def get_days_hours_minutes(total_minutes: int) -> str:
    MINUTES_PER_HOUR = 60
    MINUTES_PER_DAY = 1440

    if not total_minutes:
        return "0 minutes"

    total_days = int(total_minutes // MINUTES_PER_DAY)
    total_hours = int((total_minutes % MINUTES_PER_DAY) // MINUTES_PER_HOUR)
    total_mins = int((total_minutes % MINUTES_PER_DAY) % MINUTES_PER_HOUR)

    res = ""

    if total_days:
        res = f"{total_days} days {total_hours} hours {total_mins} minutes"
    elif total_hours:
        res = f"{total_hours} hours {total_mins} minutes"
    else:
        res = f"{total_mins} minutes"

    return res


def round_up_in_multiple(number: int, multiple: int = 5) -> int:
    return math.ceil(number / multiple) * multiple


def manage_start_end_date(start_date, end_date, duration=15) -> Tuple[date, date]:
    """
    Function which accepts two dates and returns appropriate dates as per current date
    """

    today = date.today()

    if type(start_date) is str and type(end_date) is str:
        try:
            start_date = parser.parse(start_date).date()
            end_date = parser.parse(end_date).date()
        except parser.ParserError as pe:
            start_date = None
            end_date = None

    if type(start_date) is not date or type(end_date) is not date:
        end_date = today
        start_date = end_date - timedelta(days=duration)

    if not start_date and not end_date:
        end_date = today
        start_date = end_date - timedelta(days=duration)

    elif start_date > end_date:
        start_date, end_date = end_date, start_date

    elif not start_date and end_date:
        if end_date > today:
            end_date = today
        start_date = end_date - timedelta(days=duration)

    elif start_date and not end_date:
        if start_date > today:
            end_date = today
            start_date = end_date - timedelta(days=duration)
        else:
            end_date = start_date + timedelta(days=duration)

    return start_date, end_date


def calculate_days_between_dates(
    start_date: Union[date, datetime], end_date: Union[date, datetime]
) -> int:

    if type(start_date) not in (date, datetime) or type(end_date) not in (date, datetime):
        return 1

    try:
        no_of_days = abs((end_date - start_date).days)
    except AttributeError:
        no_of_days = 1

    return no_of_days


def json_to_excel(headers, data, name):

    sheet = HttpResponse(content_type="application/ms-excel")
    sheet["Content-Disposition"] = f'attachment; filename="{name}.xls"'
    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet(name)

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = headers

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    try:
        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()

        for row in data:
            row_num += 1
            for col_num in range(len(row)):
                try:
                    ws.write(row_num, col_num, row[col_num], font_style)
                except Exception as e:
                    logger.exception(e)

        wb.save(sheet)
        return sheet

    except Exception as e:
        logger.exception(e)

        return None
