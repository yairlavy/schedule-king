import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
from pprint import pprint

# Regular expression to match date ranges (DD.MM.YYYY or DD-DD.MM.YYYY)
DATE_CORE_PATTERN = r'(\d{1,2})(?:-(\d{1,2}))?[\.\/\s]?(\d{1,2})[\.\/\s]?(\d{4}|\d{2})'
DATE_RANGE_PATTERN = re.compile(DATE_CORE_PATTERN)

def parse_all_gregorian_dates(text):
    """
    Finds all Gregorian date strings in the text and tries to parse them.
    Returns a list of (datetime_obj, matched_string) tuples, sorted by date.
    """
    found_dates = []
    for match in DATE_RANGE_PATTERN.finditer(text):
        try:
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
            continue
    
    found_dates.sort(key=lambda x: x[0])
    return found_dates

def clean_event_title(event_raw, all_parsed_gregorian_dates):
    """
    Clean the event title by removing dates and Hebrew calendar information.
    """
    event = event_raw
    
    # Remove all identified Gregorian date strings
    for _, matched_string in all_parsed_gregorian_dates:
        event = event.replace(matched_string, '')
    
    # Remove Hebrew date patterns and common phrases
    hebrew_patterns = [
        r'(?:מיום\s*)?יום\s*(?:ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת)[,\s]*[^,]*?ב(?:תשרי|חשון|כסלו|טבת|שבט|אדר|אדר א|אדר ב|ניסן|אייר|סיון|תמוז|אב|אלול)\s*תשפ"(?:ה|ו)[,\s]*',
        r'\s*ועד\s*',
        r'מיום\s*',
        r'יום\s*(?:ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת)[,\s]*',
        r'[,\s]*ב(?:תשרי|חשון|כסלו|טבת|שבט|אדר|אדר א|אדר ב|ניסן|אייר|סיון|תמוז|אב|אלול)\s*תשפ"(?:ה|ו)',
        r'[,\s]*כ"[א-ת]\s*',
        r'[,\s]*י"[א-ת]\s*',
        r'[,\s]*[א-ת]"[א-ת]\s*',
    ]
    
    for pattern in hebrew_patterns:
        event = re.sub(pattern, '', event)
    
    # Remove specific phrases
    cleanup_phrases = [
        "*ביום זה הלימודים יסתיימו בשעה 18:00",
        "*ביום זה הלימודים יתקיימו בזום",
        "(אין לקיים בחינות)",
        "(הוקדם)",
        "(אין לימודים)",
        "מ",  # Remove trailing "מ" from ranges
    ]
    
    for phrase in cleanup_phrases:
        event = event.replace(phrase, "")
    
    # General cleanup
    event = re.sub(r'\s+', ' ', event).strip()
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
    semesters = {
        "semester_a": {"name": "סמסטר א'", "start": None, "end": None},
        "semester_b": {"name": "סמסטר ב'", "start": None, "end": None},
        "summer_semester": {"name": "סמסטר קיץ", "start": None, "end": None}
    }

    print(f"DEBUG: Fetched page content length: {len(response.text)} bytes")

    # Find the main content container
    academic_content_container = soup.find("div", class_="field__items")
    if not academic_content_container:
        academic_content_container = soup.find("div", class_="view-content")

    if not academic_content_container:
        print("DEBUG: No academic calendar content container found.")
        return {"holidays": [], "semesters": []}
    else:
        print(f"DEBUG: Found main container: {academic_content_container.name} with class {academic_content_container.get('class')}")

    entries = academic_content_container.find_all("div", class_="field__item")

    if not entries:
        print("DEBUG: No entries found.")
        return {"holidays": [], "semesters": []}
    else:
        print(f"DEBUG: Found {len(entries)} entries.")

    current_year = datetime.now().year
    next_year = current_year + 1

    for i, entry in enumerate(entries):
        print(f"\nDEBUG: Processing entry {i+1}/{len(entries)}")
        full_entry_text = entry.get_text(strip=True)
        print(f"DEBUG: Full entry text: '{full_entry_text}'")

        # Skip next year's events (events with מקף indicating next year)
        if f"תשפ\"ו" in full_entry_text and "יום ראשון ללימודים" in full_entry_text:
            print("DEBUG: Skipping next year's event")
            continue

        all_parsed_gregorian_dates = parse_all_gregorian_dates(full_entry_text)

        if not all_parsed_gregorian_dates:
            print(f"DEBUG: No valid dates found in entry {i+1}. Skipping.")
            continue

        # Determine start and end dates
        start = all_parsed_gregorian_dates[0][0]
        if len(all_parsed_gregorian_dates) > 1:
            last_matched_string = all_parsed_gregorian_dates[-1][1]
            match_last = DATE_RANGE_PATTERN.search(last_matched_string)
            if match_last:
                end_day_last = int(match_last.group(2)) if match_last.group(2) else int(match_last.group(1))
                month_last = int(match_last.group(3))
                year_last = int(match_last.group(4))

                current_year_2_digit = datetime.now().year % 100
                if year_last < 100:
                    if year_last >= current_year_2_digit - 5 and year_last <= current_year_2_digit + 10:
                        year_last += 2000
                    else:
                        year_last += 1900
                end = datetime(year_last, month_last, end_day_last)
            else:
                end = start
        else:
            end = start

        # Clean event title
        event = clean_event_title(full_entry_text, all_parsed_gregorian_dates)
        print(f"DEBUG: Cleaned event: '{event}', Start: {start}, End: {end}")

        # Categorize events
        if any(word in event for word in ["חופשת", "צום", "יום הזיכרון", "יום העצמאות"]):
            holidays.append({"title": event, "start": start, "end": end})
            print(f"DEBUG: Added to holidays: '{event}'")
            
        elif "יום ראשון ללימודים" in full_entry_text and "תשפ\"ה" in full_entry_text:
            # This is the start of semester A
            semesters["semester_a"]["start"] = start
            print(f"DEBUG: Set semester A start: {start}")
            
        elif "יום אחרון ללימודים בסמסטר א" in full_entry_text:
            # End of semester A
            semesters["semester_a"]["end"] = start
            print(f"DEBUG: Set semester A end: {start}")
            
        elif "יום ראשון ללימודים בסמסטר ב" in full_entry_text:
            # Start of semester B
            semesters["semester_b"]["start"] = start
            print(f"DEBUG: Set semester B start: {start}")
            
        elif "יום אחרון ללימודים בסמסטר ב" in full_entry_text:
            # End of semester B
            semesters["semester_b"]["end"] = start
            print(f"DEBUG: Set semester B end: {start}")
            
        elif "סמסטר קיץ" in full_entry_text:
            # Summer semester
            semesters["summer_semester"]["start"] = start
            semesters["summer_semester"]["end"] = end
            print(f"DEBUG: Set summer semester: {start} to {end}")

    # Convert semesters dict to list, filtering out incomplete semesters
    semester_list = []
    for sem_key, sem_data in semesters.items():
        if sem_data["start"] is not None:
            # If end date is missing, estimate it (except for summer which should have both dates)
            if sem_data["end"] is None:
                if sem_key == "semester_a":
                    # Semester A typically ends before semester B starts
                    if semesters["semester_b"]["start"]:
                        sem_data["end"] = semesters["semester_b"]["start"] - timedelta(days=1)
                    else:
                        sem_data["end"] = sem_data["start"] + timedelta(weeks=15)
                elif sem_key == "semester_b":
                    # Semester B typically ends before summer or extends for ~15 weeks
                    if semesters["summer_semester"]["start"]:
                        sem_data["end"] = semesters["summer_semester"]["start"] - timedelta(days=1)
                    else:
                        sem_data["end"] = sem_data["start"] + timedelta(weeks=15)
            
            semester_list.append({
                "name": sem_data["name"],
                "start": sem_data["start"],
                "end": sem_data["end"]
            })
            print(f"DEBUG: Final semester - {sem_data['name']}: {sem_data['start']} to {sem_data['end']}")

    return {
        "semesters": semester_list,
        "holidays": holidays
    }

if __name__ == "__main__":
    # Pretty-print the parsed academic year data
    result = get_full_academic_year()
    print("\n" + "="*50)
    print("FINAL RESULT:")
    print("="*50)
    pprint(result)