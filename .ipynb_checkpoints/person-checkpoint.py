from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from collections import namedtuple
from datetime import datetime, date
import pytz
from zoneinfo import ZoneInfo
import re
import vedastro
from datetime import datetime
import pycountry
import swisseph as swe



Coordinates = namedtuple('Coordinates', ['latitude', 'longitude'])

class Person:
    def __init__(self, first_name, last_name, city_of_birth, country_of_birth, date_of_birth, time_of_birth, gender):
        self.first_name = first_name
        self.last_name = last_name
        self.city_of_birth = city_of_birth
        self.gender = self._parse_gender(gender)
        self.city_of_birth = self.city_of_birth[0].upper() + self.city_of_birth[1:].lower()
        self.country_of_birth = country_of_birth
        self.country_of_birth = self.country_of_birth[0].upper() + self.country_of_birth[1:].lower()
        self.date_of_birth = self._parse_date(date_of_birth)
        self.time_of_birth = self._parse_time(time_of_birth)
        self.birth_coordinates = self._get_birth_coordinates()

    def _parse_gender(self, gender):
        try:
            gender = str(gender)
            if gender == 'F' or 'female' in gender.lower().strip():
               return vedastro.Gender.Female
            else:
                return vedastro.Gender.Male
        except:
            return vedastro.Gender.Male
            
    def _parse_date(self, date_str):
        try:
            parsed_date = datetime.strptime(date_str, "%d/%m/%Y").date()
            # Verify it's a valid date (e.g., not 31/02/2021)
            if parsed_date != date(parsed_date.year, parsed_date.month, parsed_date.day):
                raise ValueError
            return parsed_date.strftime("%d/%m/%Y")
        except ValueError:
            print("Invalid date format or impossible date. Please use DD/MM/YYYY")
            return None 
        
    def _parse_time(self, time_str):
        time_str = time_str.replace(" ", "").upper()
        is_pm = 'PM' in time_str
        
        time_str = time_str.replace('AM', '').replace('PM', '')
        
        try:
            parsed_time = datetime.strptime(time_str, "%I:%M:%S" if ":" in time_str else "%I:%M")
        except ValueError:
            try:
                parsed_time = datetime.strptime(time_str, "%H:%M:%S" if time_str.count(":")==2 else "%H:%M")
            except ValueError:
                print("Invalid time format. Please use HH:MM or HH:MM:SS, optionally followed by AM/PM")
                return None        
        if is_pm and parsed_time.hour != 12:
            parsed_time = parsed_time.replace(hour=parsed_time.hour + 12)
        elif not is_pm and parsed_time.hour == 12:
            parsed_time = parsed_time.replace(hour=0)
        
        return parsed_time.strftime("%H:%M")

    def _get_birth_coordinates(self):
        geolocator = Nominatim(user_agent="my_person_app")
        try:
            location = geolocator.geocode(f"{self.city_of_birth}, {self.country_of_birth}")
            if location:
                self.latitude = location.latitude
                self.longitude = location.longitude
                return Coordinates(latitude=location.latitude, longitude=location.longitude)
            else:
                print("Location not found")
                return None
        except (GeocoderTimedOut, GeocoderUnavailable):
            print("Geocoding service unavailable. Please try again later.")
            self.longitude = None
            self.latitude = None
            return None
            
    def _get_gmt_offset(self):
        try:
            # Convert country name to country code
            country = pycountry.countries.search_fuzzy(self.country_of_birth)[0]
            country_code = country.alpha_2

            # Get timezones for the country
            country_timezones = pytz.country_timezones.get(country_code)
            
            if country_timezones:
                # Use the first timezone for the country
                timezone = pytz.timezone(country_timezones[0])
                offset = timezone.utcoffset(datetime.now())
                return f"{offset.days * 24 + offset.seconds // 3600:+03d}:00"
            else:
                print(f"No timezone found for {self.country_of_birth}. Using IST.")
                return "+05:30"  # Default to IST if timezone not found
        except LookupError:
            print(f"Country not found: {self.country_of_birth}. Using IST.")
            return "+05:30"
        except Exception as e:
            print(f"Error determining GMT offset: {str(e)}. Using IST.")
            return "+05:30"

    def __str__(self):
        coord_str = f"({self.birth_coordinates.latitude}, {self.birth_coordinates.longitude})" if self.birth_coordinates else "Unknown"
        return (f"Name: {self.first_name} {self.last_name}\n"
                f"Place of Birth: {self.city_of_birth}, {self.country_of_birth}\n"
                f"Time of Birth: {self.time_of_birth}\n"
                f"Birth Coordinates: {coord_str}")
        
    def get_geolocation_object(self):
        self._get_birth_coordinates()
        loc_string = self.city_of_birth + ", " + self.country_of_birth
        if self.latitude == None:
            self.latitude = 28.613 # Delhi
        if self.longitude == None:
            self.longitude = 77.209 # Delhi 
        try:
            self.geolocation = vedastro.GeoLocation(loc_string, self.longitude, self.latitude)
        except Exception as e:
            print(f"An exception occurred in Vedastro: {repr(e)}")
        return self.geolocation

    def get_time_object(self):
        self._get_birth_coordinates()
        offset = self._get_gmt_offset()
        time = self.time_of_birth
        date = self.date_of_birth
        self.get_geolocation_object()
        time_str = time + " " + date + " " + offset
        try:
            obj =  vedastro.Time(time_str, self.geolocation)
            self.time_obj = obj
            return obj
        except Exception as e:
            print(f"An exception occurred in Vedastro: {repr(e)}")
            return None