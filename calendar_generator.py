#!/usr/bin/env python
# coding:utf8


# Below are the code references for this script file:

# Calendar generator — https://www.fzu.cz/~dominecf/calendar/index.html
# fzu.cz/~dominecf/calendar/cal.py — https://www.fzu.cz/~dominecf/calendar/cal.py

# vitchyr/StudyPlanner: A python script that helps students study throughout the semester, instead of having to cram before exams.
# https://github.com/vitchyr/StudyPlanner


import calendar
import datetime
import sys
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
import itertools


def get_json(fname):
    """Load and parse a JSON file."""
    with open(fname, 'r', encoding='utf8') as f:
        return json.load(f)


def iso_day(d):
    """Converts a day abbreviation (e.g., 'M' for Monday) to its ISO weekday number."""
    return {
        'M': 1,  # Monday
        'T': 2,  # Tuesday
        'W': 3,  # Wednesday
        'R': 4,  # Thursday
        'F': 5,  # Friday
        'S': 6,  # Saturday
        'U': 7,  # Sunday
        '1': 1,  # Monday (alternative)
        '2': 2,  # Tuesday (alternative)
        '3': 3,  # Wednesday (alternative)
        '4': 4,  # Thursday (alternative)
        '5': 5,  # Friday (alternative)
        '6': 6,  # Saturday (alternative)
        '7': 7,  # Sunday (alternative)
    }[d]


# Parsing a comma-separated list of numbers and range specifications in Python — https://gist.github.com/kgaughan/2491663
def get_frames_sequence(expression):
    """
    Parse range expressions into list of integers.
    Parse a string like '1-3,5,7-9' into a list of integers [1,2,3,5,7,8,9].
    """
    result = set()
    for part in expression.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            result.update(range(start, end + 1))
        else:
            result.add(int(part))
    return sorted(result)


def create_schedule(class_definition, data, custom_style, month, date_rows):
    """Populate calendar with class schedule data."""
    semester_start_day = datetime.datetime.strptime(class_definition["semester_start_day"], '%Y-%m-%d').date()

    for lesson in class_definition["lessons"]:
        day_lessons = {}
        for wd in lesson["week_day"]:
            weeks = get_frames_sequence(wd["week"])
            iso_day_num = iso_day(wd["day"])
            lessons = get_frames_sequence(wd["lesson"])

            for week in weeks:
                delta = datetime.timedelta(weeks=week - 1, days=iso_day_num - 1)
                lesson_date = semester_start_day + delta
                if lesson_date.month != month:
                    continue

                try:
                    row_idx = date_rows.index(lesson_date) + 1  # +1 for header row
                except ValueError:
                    continue

                # Merge lesson periods
                sorted_lessons = sorted(lessons)
                start_col = sorted_lessons[0] + 1  # +1 for week/day column
                end_col = sorted_lessons[-1] + 1

                # Create cell content
                cell_content = "{}\n{} {}".format(lesson['name'], lesson['student'], wd['room'])
                data[row_idx][start_col] = cell_content

                # Add styling
                custom_style.extend([
                    ('SPAN', (start_col, row_idx), (end_col, row_idx)),
                    ('BACKGROUND', (start_col, row_idx), (end_col, row_idx), colors.palegreen),
                    ('LEADING', (start_col, row_idx), (end_col, row_idx), 10),  # Set line spacing for this cell
                ])

# calendar_generator.py 3
# this will generate a monthly calendar for the current year, so it is "2025 03"
# calendar_generator.py 4 2026
# this will generate a monthly calendar for "2026 03"

# Parse command line arguments
if len(sys.argv) > 1:
    m = int(sys.argv[1])
else:
    m = datetime.date.today().month

if len(sys.argv) > 2:
    y = int(sys.argv[2])
else:
    y = datetime.date.today().year

# Load class data
class_definition_filename = "class-of-semester-2024-2025-2.json"
class_definition = get_json(class_definition_filename)
semester_start_day = datetime.datetime.strptime(class_definition["semester_start_day"], '%Y-%m-%d').date()

# Setup PDF document

# For English font, you could use arial.ttf and arial.ttc
# For Chinese font, you could use Microsoft YaHei font, if under Windows7, should have msyh.ttf file,
# for windows 10, it should have msyh.ttc file
# Choose the font name below
try:
    pdfmetrics.registerFont(TTFont('msyh', 'C:/Windows/Fonts/msyh.ttf'))
except:
    print("try to load msyh.ttf failed, so try msyh.ttc instead for windows 10")
    pdfmetrics.registerFont(TTFont('msyh', 'C:/Windows/Fonts/msyh.ttc'))

# Register Consolas font (non-serif monospaced)
try:
    pdfmetrics.registerFont(TTFont('Consolas', 'C:/Windows/Fonts/consola.ttf'))  # Consolas font
except:
    print("Consolas font not found. Using default font instead.")

doc = SimpleDocTemplate("calendar_{}_{:02d}.pdf".format(y, m),
                        leftMargin=1 * cm, rightMargin=1 * cm,
                        topMargin=1 * cm, bottomMargin=1 * cm)

# Generate calendar data
cal = calendar.Calendar()
date_rows = []
data = []
highlight_lines = []

# Create header
# the time is from 08:00 to 22:00
# ['2021-03', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00']
# header = ["%d-%02d" % (y,m)] + ["%02d:00"%t for t in range(8, 22, 2)]
# let's define our own, which has something like:
# header = ["%d-%02d" % (y, m)] + ["%d" % t for t in range(1, 10, 1)]  # 1-9 represents 9 lessons
# Define the table header: year-month followed by lesson numbers (1-9)
# header = ["%d-%02d" % (y, m)] + ["%d" % t for t in range(1, 10, 1)]  # 1-9 represents 9 lessons
lesson_times = [
    "1\n8:00-8:45",
    "2\n8:50-9:35",
    "3\n9:55-10:40",
    "4\n10:45-11:30",
    "5\n11:35-12:20",
    "6\n13:30-14:15",
    "7\n14:20-15:05",
    "8\n15:15-16:00",
    "9\n16:05-16:50"
]

# Create the header with year-month followed by lesson numbers and time ranges
header = ["Week", "{}-{:02d}".format(y, m)] + lesson_times
data.append(header)

# Generate date rows
line_count = 0

# flatten the weeks in month
for day in itertools.chain(*cal.monthdatescalendar(y, m)):
    if day.month != m:
        continue

    line_count += 1

    # for Saturday and Sunday, use a different background
    if day.weekday() in (5, 6):
        highlight_lines.append(line_count)

    # Calculate week number
    delta_days = (day - semester_start_day).days
    week_num = delta_days // 7 + 1

    # Create row
    day_name = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"][day.weekday()]
    # if you want Chinese weekday name, use below statement
    # day_name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][day.weekday()]

    row = [str(week_num), "{:02d} {}".format(day.day, day_name)] + [''] * len(lesson_times)
    data.append(row)
    date_rows.append(day)

# Add footer header
data.append(header.copy())
# Now, the data structure looks like:
# [['2021-03', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
#  ['01 MON', '', '', '', '', '', '', '', '', ''],
#  ['02 TUE', '', '', '', '', '', '', '', '', ''],
#  ...
#  ['31 WED', '', '', '', '', '', '', '', '', '']]
# Create table style



style = [
    ('FONT', (0, 0), (-1, -1), 'msyh'),
#    ('FONT', (1, 0), (1, -1), 'Consolas'),  # Monospaced font for the second column
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('FONTSIZE', (2, 0), (-1, 0), 7),    # First row (header) font size is 7
    ('FONTSIZE', (2, -1), (-1, -1), 7),  # Last row, columns 2 to last, font size is 7
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('ALIGN', (1, 1), (1, -2), 'LEFT'),  # Left-align column 2, excluding first and last rows
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
    ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
    # Apply LEADING to the first row (header)
    ('LEADING', (0, 0), (-1, 0), 10),  # Set line spacing for the header
    # Apply LEADING to the last row (footer)
    ('LEADING', (0, -1), (-1, -1), 10),  # Set line spacing for the footer
]

# Merge week number cells
current_week = None
merge_start = 1
for i in range(1, len(data) - 1):
    week = data[i][0]
    if week == current_week:
        continue

    if current_week is not None:
        style.append(('SPAN', (0, merge_start), (0, i - 1)))
    current_week = week
    merge_start = i

if current_week is not None:
    style.append(('SPAN', (0, merge_start), (0, len(data) - 2)))

# Highlight weekends
for line in highlight_lines:
    style.append(('BACKGROUND', (1, line), (-1, line), colors.lightgrey))

# Add class schedule
create_schedule(class_definition, data, style, m, date_rows)

# Create table
col_widths = [1.2 * cm, 1.5 * cm] + [1.5 * cm] * len(lesson_times)

# Define row height
row_heights = [0.8 * cm]  # First row height is 1.0 cm
for i in range(1, len(data) - 1):
    row_heights.append(0.8 * cm)  # Middle rows height is 0.8 cm
row_heights.append(0.8 * cm)  # Last row height is 1.0 cm

table = Table(data, colWidths=col_widths, rowHeights=row_heights)
table.setStyle(TableStyle(style))

# Add title with smaller font size
styles = getSampleStyleSheet()
title_style = styles['Title']
title_style.fontSize = 14  # Reduce font size to 14
title_text = "{} {:02d} Calendar".format(y, m)
title = Paragraph(title_text, title_style)

# Add a Spacer to reduce vertical space between title and table
spacer = Spacer(1, -0.3 * cm)  # 0.2 cm vertical space

# Generate PDF
doc.build([title, spacer, table])

print("Generated calendar_{}_{:02d}.pdf".format(y, m))