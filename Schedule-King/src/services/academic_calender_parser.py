import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
from pprint import pprint

# Regular expression to match date ranges (DD.MM.YYYY or DD-DD.MM.YYYY)
DATE_CORE_PATTERN = r'(\d{1,2})(?:-(\d{1,2}))?[\.\/\s]?(\d{1,2})[\.\/\s]?(\d{4}|\d{2})'
DATE_RANGE_PATTERN = re.compile(DATE_CORE_PATTERN)

def parse_all_dates(text):
    """
    Finds all date strings in the text and tries to parse them.
    Returns a list of (datetime_obj, matched_string) tuples, sorted by date.
    """
    found_dates = []
    for match in DATE_RANGE_PATTERN.finditer(text):
        try:
            # Extract day, month, year from regex groups
            start_day = int(match.group(1))
            end_day = int(match.group(2)) if match.group(2) else start_day
            month = int(match.group(3))
            year = int(match.group(4))

            # Handle 2-digit years by inferring the century
            current_year_2_digit = datetime.now().year % 100
            if year < 100:
                if year >= current_year_2_digit - 5 and year <= current_year_2_digit + 10:
                    year += 2000
                else:
                    year += 1900

            date_obj = datetime(year, month, start_day)
            matched_string = match.group(0)

            found_dates.append((date_obj, matched_string))
        except ValueError:
            # Skip invalid dates
            continue
    
    # Sort dates chronologically
    found_dates.sort(key=lambda x: x[0])
    return found_dates

def clean_event_title(event_raw, all_parsed_gregorian_dates):
    """
    Extracts the main event/holiday name from the raw event text using a hybrid approach:
    1. First, tries to match known holiday/event patterns (e.g., 'צום י"ז תמוז', 'צום ט' באב', 'חופשת יום ירושלים', 'יום הסטודנט', 'יום הזיכרון ויום העצמאות').
    2. If not found, uses a generic regex and split logic as fallback.
    """
    event = event_raw
    # Remove all identified Gregorian date strings
    for _, matched_string in all_parsed_gregorian_dates:
        event = event.replace(matched_string, '')

    # Remove text in parentheses
    event = re.sub(r'\([^)]*\)', '', event)
    # Remove Hebrew year
    event = re.sub(r'תשפ"[וה]', '', event)

    # 1. Try to match known holiday/event patterns
    known_patterns = [
        r'צום\s+[א-ת"׳\']+\s+[א-ת]+',  # e.g., 'צום י"ז תמוז', 'צום ט' באב'
        r'חופשת?\s+יום\s+ירושלים',      # 'חופשת יום ירושלים'
        r'יום\s+הסטודנט',                # 'יום הסטודנט'
        r'יום\s+הזיכרון\s+ו?יום\s+העצמאות', # 'יום הזיכרון ויום העצמאות'
        r'חופשת?\s+חנוכה',
        r'חופשת?\s+פורים',
        r'חופשת?\s+פסח',
        r'חופשת?\s+חג\s+שבועות',
        r'חופשת?\s+שבועות',
        r'חופשת?\s+סוכות',
        r'חופשת?\s+חג\s+הפסח',
        r'חופשת?\s+חג\s+הסוכות',
        r'חופשת?\s+יום',
        r'חופשת?\s+[^,\(]+',
        r'חג\s+[א-ת"׳\']+\s*[א-ת]*',
        r'יום\s+ירושלים',
    ]
    for pat in known_patterns:
        m = re.search(pat, event)
        if m:
            return m.group(0).strip('-,. ')

    # 2. Fallback: generic pattern and split on weekday/preposition
    m = re.search(r'(חופשת?\s+[^,\(\n]+|חג\s+[^,\(\n]+|צום\s+[^,\(\n]+|יום\s+[^,\(\n]+)', event)
    if m:
        title = m.group(0)
        # Remove trailing weekday/preposition phrases
        title = re.split(r'(?:מיום|ועד יום|יום ראשון|יום שני|יום שלישי|יום רביעי|יום חמישי|יום שישי|יום שבת|יום|מ|ועד)', title)[0]
        return title.strip('-,. ')

    # Fallback: remove weekday/preposition words and clean up
    day_of_week_patterns = [
        r'מיום\s*', r'ועד יום\s*', r'ועד\s*',
        r'יום\s*(?:ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת)[,\s]*',
        r'ראשון', r'שני', r'שלישי', r'רביעי', r'חמישי', r'שישי', r'שבת'
    ]
    for pattern in day_of_week_patterns:
        event = re.sub(pattern, '', event)
    event = re.sub(r'\s+', ' ', event)
    event = event.strip('-,. ')
    return event

def get_full_academic_year():
    """
    Fetches and parses the academic calendar from the university website.
    Extracts holidays and semester periods with their start/end dates.
    Returns a dictionary with 'semesters' and 'holidays' lists.
    """
    url = "https://www.biu.ac.il/academic-year"
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")

    holidays = []
    # Temporary variables for semester dates
    semester_a_start = None
    semester_a_end = None
    semester_b_start = None
    semester_b_end = None
    summer_start = None
    summer_end = None

    # Find the main content container for the academic calendar
    academic_content_container = soup.find("div", class_="field__items")
    if not academic_content_container:
        academic_content_container = soup.find("div", class_="view-content")

    if not academic_content_container:
        # Return empty if no content found
        return {"holidays": [], "semesters": []}

    # Find all entries (each event/row) in the calendar
    entries = academic_content_container.find_all("div", class_="field__item")

    if not entries:
        # Return empty if no entries found
        return {"holidays": [], "semesters": []}

    for entry in entries:
        full_entry_text = entry.get_text(strip=True)

        # Ignore next year's event ("יום ראשון ללימודים - תשפ"ו")
        if ("יום ראשון ללימודים" in full_entry_text and "-" in full_entry_text) or ("תשפ\"ו" in full_entry_text and "יום ראשון ללימודים" in full_entry_text):
            continue

        # Parse all Gregorian dates in the entry
        all_parsed_gregorian_dates = parse_all_dates(full_entry_text)
        if not all_parsed_gregorian_dates:
            continue

        # Use the first and last parsed dates as start and end
        start = all_parsed_gregorian_dates[0][0]
        end = all_parsed_gregorian_dates[-1][0] if len(all_parsed_gregorian_dates) > 1 else start

        # Clean and extract the event title
        event = clean_event_title(full_entry_text, all_parsed_gregorian_dates)

        # Always add any event containing 'סטודנט' to holidays
        if 'סטודנט' in event:
            holidays.append({"title": event, "start": start, "end": end})
            continue

        # Detect semester A start
        if ("יום ראשון ללימודים" in full_entry_text and "סמסטר" not in full_entry_text and semester_a_start is None):
            semester_a_start = start
            continue
        # Detect semester A end
        if ("יום אחרון ללימודים בסמסטר א" in full_entry_text):
            semester_a_end = start
            continue
        # Detect semester B start
        if ("יום ראשון ללימודים בסמסטר ב" in full_entry_text):
            semester_b_start = start
            continue
        # Detect semester B end
        if ("יום אחרון ללימודים בסמסטר ב" in full_entry_text):
            semester_b_end = start
            continue
        # Detect summer semester
        if ("סמסטר קיץ" in full_entry_text):
            summer_start = start
            summer_end = end
            continue

        # Holidays detection (improved)
        if any(word in event for word in ["חופשת", "צום", "יום הזיכרון", "יום העצמאות", "שבועות", "ירושלים"]):
            holidays.append({"title": event, "start": start, "end": end})

    # Build semesters array
    semesters = []
    if semester_a_start and semester_a_end:
        semesters.append({"name": "סמסטר א'", "start": semester_a_start, "end": semester_a_end})
    if semester_b_start and semester_b_end:
        semesters.append({"name": "סמסטר ב'", "start": semester_b_start, "end": semester_b_end})
    if summer_start and summer_end:
        semesters.append({"name": "סמסטר קיץ", "start": summer_start, "end": summer_end})

    return {
        "semesters": semesters,
        "holidays": holidays
    }

if __name__ == "__main__":
    # Pretty-print the parsed academic year data
    result = get_full_academic_year()
    print("\n" + "="*50)
    print("FINAL RESULT:")
    print("="*50)
    pprint(result)