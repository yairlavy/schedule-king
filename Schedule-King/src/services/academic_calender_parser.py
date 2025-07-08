import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import json
import os
from pprint import pprint

# Regular expression to match date ranges (DD.MM.YYYY or DD-DD.MM.YYYY)
DATE_CORE_PATTERN = r'(\d{1,2})(?:-(\d{1,2}))?[\.\/\s]?(\d{1,2})[\.\/\s]?(\d{4}|\d{2})'
DATE_RANGE_PATTERN = re.compile(DATE_CORE_PATTERN)

# Cache file for storing parsed academic calendar data
CACHE_FILE = 'academic_calendar_cache.json'

def should_use_cache():
    """
    Checks if the cache file exists and if it is still valid based on the summer semester end date.
    Returns True if the cache is valid, otherwise False.
    """
    if not os.path.exists(CACHE_FILE):
        print("Cache file does not exist.")
        return False

    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
            
            # Ensure the cache contains the required 'semesters' information
            semesters_in_cache = cache_data.get('semesters')
            if not semesters_in_cache:
                print("Cache data is missing 'semesters' information.")
                return False

            summer_semester_end = None
            for s in semesters_in_cache:
                if s.get('name') == 'סמסטר קיץ' and s.get('end'):
                    try:
                        # Convert the date string to a datetime object
                        summer_semester_end = datetime.fromisoformat(s['end'])
                        break
                    except ValueError:
                        print("Invalid date format in cache for summer semester end.")
                        return False

            if summer_semester_end is None:
                print("Summer semester end date not found in cache.")
                return False

            current_date = datetime.now()
            
            # Cache is valid as long as the current date is before or equal to the summer semester end date
            if current_date <= summer_semester_end:
                print(f"Cache is valid. Summer semester ends on {summer_semester_end.strftime('%Y-%m-%d')}. Current date is {current_date.strftime('%Y-%m-%d')}.")
                return True
            else:
                print(f"Cache expired. Summer semester ended on {summer_semester_end.strftime('%Y-%m-%d')}. Current date is {current_date.strftime('%Y-%m-%d')}.")
                return False

    except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
        print(f"Error reading cache file: {e}. Rebuilding cache.")
        return False

def save_to_cache(data):
    """
    Saves the parsed academic calendar data to a JSON cache file.
    Converts datetime objects to ISO 8601 strings for JSON serialization.
    """
    # Convert datetime objects to strings before saving
    serializable_data = {
        "semesters": [{"name": s["name"], "start": s["start"].isoformat(), "end": s["end"].isoformat()} for s in data.get("semesters", [])],
        "holidays": [{"title": h["title"], "start": h["start"].isoformat(), "end": h["end"].isoformat()} for h in data.get("holidays", [])]
    }
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(serializable_data, f, ensure_ascii=False, indent=4)

def load_from_cache():
    """
    Loads academic calendar data from the JSON cache file.
    Converts date strings back to datetime objects.
    """
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert date strings back to datetime objects
    for semester in data.get('semesters', []):
        semester['start'] = datetime.fromisoformat(semester['start'])
        semester['end'] = datetime.fromisoformat(semester['end'])
    for holiday in data.get('holidays', []):
        holiday['start'] = datetime.fromisoformat(holiday['start'])
        holiday['end'] = datetime.fromisoformat(holiday['end'])
        
    print("Data loaded from cache.")
    return data

def parse_all_dates(text):
    """
    Finds all date strings in the text and tries to parse them.
    Returns a list of (datetime_obj, matched_string) sorted by date.
    """
    found_dates = []
    for match in DATE_RANGE_PATTERN.finditer(text):
        try:
            start_day = int(match.group(1))
            end_day = int(match.group(2)) if match.group(2) else start_day
            month = int(match.group(3))
            year = int(match.group(4))

            current_year_2_digit = datetime.now().year % 100
            # Handle two-digit years
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
    Extracts the main event/holiday name from the raw event text.
    Removes date strings and known patterns to isolate the event title.
    """
    event = event_raw
    for _, matched_string in all_parsed_gregorian_dates:
        event = event.replace(matched_string, '')

    event = re.sub(r'\([^)]*\)', '', event)
    event = re.sub(r'תשפ"[וה]', '', event)

    known_patterns = [
        r'צום\s+[א-ת"׳\']+\s*[א-ת]*',
        r'חופשת?\s+יום\s+ירושלים',
        r'יום\s+הסטודנט',
        r'יום\s+הזיכרון\s+ו?יום\s+העצמאות',
        r'חופשת?\s+חנוכה',
        r'חופשת?\s+פורים',
        r'חופשת?\s+פסח',
        r'חופשת?\s+חג\s+שבועות',
        r'חופשת?\s+שבועות',
        r'חופשת?\s+סוכות',
        r'חופשת?\s+ראש\s+השנה',
        r'חופשת?\s+כיפור',
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

    m = re.search(r'(חופשת?\s+[^,\(\n]+|חג\s+[^,\(\n]+|צום\s+[^,\(\n]+|יום\s+[^,\(\n]+)', event)
    if m:
        title = m.group(0)
        title = re.split(r'(?:מיום|ועד יום|יום ראשון|יום שני|יום שלישי|יום רביעי|יום חמישי|יום שישי|יום שבת|יום|מ|ועד)', title)[0]
        return title.strip('-,. ')

    day_of_week_patterns = [
        r'מיום\s*', r'ועד יום\s*', r'ועד\s*',
        r'יום\s*(?:ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת)[,\s]*',
        r'ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת'
    ]
    for pattern in day_of_week_patterns:
        event = re.sub(pattern, '', event)
    event = re.sub(r'\s+', ' ', event)
    event = event.strip('-,. ')
    return event

def fetch_and_parse_academic_data(url):
    """
    Fetches the academic calendar HTML from the given URL and parses it to extract semesters and holidays.
    Returns a dictionary with 'semesters' and 'holidays' lists.
    """
    print(f"Fetching data from {url} (not from cache)...")
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return {"holidays": [], "semesters": []}
        
    soup = BeautifulSoup(response.text, "html.parser")

    holidays = []
    semester_a_start = None
    semester_a_end = None
    semester_b_start = None
    semester_b_end = None
    summer_start = None
    summer_end = None

    # Try to find the main container for the academic calendar entries
    academic_content_container = soup.find("div", class_="field__items")
    if not academic_content_container:
        academic_content_container = soup.find("div", class_="view-content")

    if not academic_content_container:
        print("Could not find academic content container.")
        return {"holidays": [], "semesters": []}

    entries = academic_content_container.find_all("div", class_="field__item")

    if not entries:
        print("Could not find any entries in the academic calendar.")
        return {"holidays": [], "semesters": []}

    for entry in entries:
        full_entry_text = entry.get_text(strip=True)

        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # Skip future academic years if the current month is before October
        if "יום ראשון ללימודים" in full_entry_text and "תשפ" in full_entry_text:
            all_parsed_gregorian_dates_in_entry = parse_all_dates(full_entry_text)
            if all_parsed_gregorian_dates_in_entry:
                first_date_in_entry = all_parsed_gregorian_dates_in_entry[0][0]
                if first_date_in_entry.year > current_year and current_month < 10:
                    continue 

        all_parsed_gregorian_dates = parse_all_dates(full_entry_text)
        if not all_parsed_gregorian_dates:
            continue

        start = all_parsed_gregorian_dates[0][0]
        end = all_parsed_gregorian_dates[-1][0] if len(all_parsed_gregorian_dates) > 1 else start

        event = clean_event_title(full_entry_text, all_parsed_gregorian_dates)

        # Add student day as a holiday
        if 'סטודנט' in event:
            holidays.append({"title": event, "start": start, "end": end})
            continue

        # Identify semester start and end dates
        if ("יום ראשון ללימודים" in full_entry_text and "סמסטר" not in full_entry_text and semester_a_start is None):
            semester_a_start = start
            continue
        if ("יום אחרון ללימודים בסמסטר א" in full_entry_text):
            semester_a_end = start
            continue
        if ("יום ראשון ללימודים בסמסטר ב" in full_entry_text):
            semester_b_start = start
            continue
        if ("יום אחרון ללימודים בסמסטר ב" in full_entry_text):
            semester_b_end = start
            continue
        if ("סמסטר קיץ" in full_entry_text):
            summer_start = start
            summer_end = end
            continue

        # Add holidays and special days
        if any(word in event for word in ["חופשת", "צום", "יום הזיכרון", "יום העצמאות", "שבועות", "ירושלים", "פורים", "פסח", "סוכות", "חנוכה", "ראש השנה", "כיפור", "ט' באב"]):
            holidays.append({"title": event, "start": start, "end": end})

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

def get_full_academic_year():
    """
    Main function to get the academic calendar.
    Checks if the cache is valid; if not, fetches and parses new data, then saves it to cache.
    Returns the academic calendar data as a dictionary.
    """
    url = "https://www.biu.ac.il/academic-year"

    # Step 1: Check if a valid cache exists
    if should_use_cache():
        return load_from_cache()
    
    # Step 2: If no valid cache, fetch and parse new data
    print("Cache is not valid or does not exist. Fetching new data...")
    result = fetch_and_parse_academic_data(url)
    
    # Step 3: Save the new data to cache
    save_to_cache(result)
    
    return result

# Debugging/testing code
if __name__ == "__main__":
    # Run the main function and pretty-print the result
    result = get_full_academic_year()
    print("\n" + "="*50)
    print("FINAL RESULT:")
    print("="*50)
    pprint(result)

    # Uncomment to manually remove the cache file for testing
    # if