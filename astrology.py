import swisseph as swe
from datetime import datetime, timedelta

class Astrology:
    def __init__(self, person):
        self.person = person
        self.jd = self._calculate_julian_day()
        self.ayanamsa = self._calculate_ayanamsa()
        self.zodiac_sign = self._calculate_zodiac_sign()
        self.moon_sign = self._calculate_moon_sign()
        self.ascendant = self._calculate_ascendant()
        self.nakshatra = self._calculate_nakshatra()
        #self.sunrise, self.sunset = self._calculate_sunrise_sunset()
        self.vashya = self._calculate_vashya()
        self.yoni = self._calculate_yoni()
        self.gan = self._calculate_gan()
        self.nadi = self._calculate_nadi()
        self.sign_lord = self._calculate_sign_lord()
        self.nakshatra_lord = self._calculate_nakshatra_lord()
        self.charan = self._calculate_charan()
        self.tithi = self._calculate_tithi()
        self.tatva = self._calculate_tatva()
        self.name_alphabet = self._calculate_name_alphabet()
        self.paya = self._calculate_paya()

    def _calculate_julian_day(self):
        """
        Calculate the Julian day number for the birth date and time.
        Julian day is used as a standard reference point for astronomical calculations.
        """
        dob = datetime.strptime(self.person.date_of_birth, "%d/%m/%Y")
        time = self.person.time_of_birth.split(':')
        return swe.julday(dob.year, dob.month, dob.day, float(time[0]) + float(time[1])/60)

    def _calculate_ayanamsa(self):
        """
        Calculate the Ayanamsa (precession of the equinoxes) for the birth date.
        Ayanamsa is used to convert between the tropical and sidereal zodiacs.
        """
        return swe.get_ayanamsa(self.jd)

    def _calculate_zodiac_sign(self):
        """
        Calculate the zodiac sign (Rashi) based on the Sun's position at birth.
        The zodiac sign represents the general characteristics and tendencies of a person.
        """
        sun_pos = swe.calc_ut(self.jd, swe.SUN)[0]
        sun_sign = int(sun_pos[0] / 30)
        return self._get_zodiac_name(sun_sign)

    def _calculate_moon_sign(self):
        """
        Calculate the Moon sign (Janma Rashi) based on the Moon's position at birth.
        The Moon sign is considered very important in Vedic astrology, representing emotions and the inner self.
        """
        moon_pos = swe.calc_ut(self.jd, swe.MOON)[0]
        moon_sign = int(moon_pos[0] / 30)
        return self._get_zodiac_name(moon_sign)

    def _calculate_ascendant(self):
        """
        Calculate the Ascendant (Lagna) sign based on the eastern horizon at birth.
        The Ascendant represents one's outward behavior and physical appearance.
        """
        ascendant = swe.houses(self.jd, self.person.latitude, self.person.longitude)[0][0]
        ascendant_sign = int(ascendant / 30)
        return self._get_zodiac_name(ascendant_sign)

    def _calculate_nakshatra(self):
        """
        Calculate the Nakshatra (lunar mansion) based on the Moon's position at birth.
        Nakshatras provide more detailed information about a person's characteristics and life events.
        """
        moon_pos = swe.calc_ut(self.jd, swe.MOON)[0]
        nakshatra = int(moon_pos[0] * 3 / 40)
        return self._get_nakshatra_name(nakshatra)

    def _calculate_sunrise_sunset(self):
        """
        Calculate the sunrise and sunset times for the birth date and location.
        These times are used in various astrological calculations and interpretations.
        """
        t_rise = swe.rise_trans(self.jd, swe.SUN, self.person.longitude, self.person.latitude, 0, 1)[1][0]
        t_set = swe.rise_trans(self.jd, swe.SUN, self.person.longitude, self.person.latitude, 0, 2)[1][0]
        rise_dt = swe.jdut1_to_utc(t_rise)[0]
        set_dt = swe.jdut1_to_utc(t_set)[0]
        return rise_dt.strftime("%H:%M"), set_dt.strftime("%H:%M")

    def _calculate_vashya(self):
        """
        Determine the Vashya (creature category) of the zodiac sign.
        Vashya is used in compatibility analysis and general characteristic assessment.
        """
        vashyas = ["Chatushpad", "Jalchar", "Vanchar", "Chatushpad", "Manav", "Keet", 
                   "Jalchar", "Keet", "Manav", "Chatushpad", "Manav", "Jalchar"]
        return vashyas[self._get_zodiac_index(self.zodiac_sign)]

    def _calculate_yoni(self):
        """
        Determine the Yoni (animal symbol) associated with the birth Nakshatra.
        Yoni is used in compatibility assessment, especially for marriage matching.
        """
        yonis = ["Horse", "Elephant", "Sheep", "Snake", "Dog", "Cat", "Rat", "Cow", "Buffalo", 
                 "Tiger", "Hare", "Monkey", "Mongoose", "Lion", "Horse", "Elephant", "Sheep", 
                 "Snake", "Dog", "Cat", "Rat", "Cow", "Buffalo", "Tiger", "Hare", "Monkey", "Mongoose"]
        return yonis[self._get_nakshatra_index(self.nakshatra)]

    def _calculate_gan(self):
        """
        Determine the Gan (temperament) of the birth Nakshatra.
        Gan classifies Nakshatras into divine (Deva), human (Manushya), or demon (Rakshasa) categories.
        """
        gans = ["Deva", "Manushya", "Rakshasa"]
        return gans[self._get_nakshatra_index(self.nakshatra) % 3]

    def _calculate_nadi(self):
        """
        Determine the Nadi (pulse) of the birth Nakshatra.
        Nadi is used in compatibility matching, especially for marriage.
        """
        nadis = ["Aadi", "Madhya", "Antya"]
        return nadis[self._get_nakshatra_index(self.nakshatra) % 3]

    def _calculate_sign_lord(self):
        """
        Determine the planetary lord of the zodiac sign.
        The sign lord is considered the ruler or significator of that sign.
        """
        lords = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", 
                 "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
        return lords[self._get_zodiac_index(self.zodiac_sign)]

    def _calculate_nakshatra_lord(self):
        """
        Determine the planetary lord of the birth Nakshatra.
        The Nakshatra lord influences the characteristics and events related to that Nakshatra.
        """
        lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
        return lords[self._get_nakshatra_index(self.nakshatra) % 9]

    def _calculate_charan(self):
        """
        Calculate the Charan (quarter) of the birth Nakshatra.
        Charan is used in determining the Pada Lagna and in naming ceremonies.
        """
        moon_pos = swe.calc_ut(self.jd, swe.MOON)[0]
        return (int(moon_pos[0] * 3 / 40) % 4) + 1

    def _calculate_tithi(self):
        """
        Calculate the Tithi (lunar day) at the time of birth.
        Tithi is used in determining auspicious times and in various Hindu rituals.
        """
        moon_pos = swe.calc_ut(self.jd, swe.MOON)[0]
        sun_pos = swe.calc_ut(self.jd, swe.SUN)[0]
        tithi = (moon_pos[0] - sun_pos[0]) % 360 / 12
        return int(tithi) + 1

    def _calculate_tatva(self):
        """
        Determine the Tatva (element) of the zodiac sign.
        Tatva represents the elemental nature and is used in compatibility and characteristic analysis.
        """
        tatvas = ["Fire", "Earth", "Air", "Water", "Ether"]
        return tatvas[self._get_zodiac_index(self.zodiac_sign) % 5]

    def _calculate_name_alphabet(self):
        """
        Determine the suggested first letter of the name based on the birth Nakshatra and Charan.
        This is often used in naming ceremonies in Hindu tradition.
        """
        alphabets = [
            ["Chu", "Che", "Cho", "La"],
            ["Li", "Lu", "Le", "Lo"],
            ["A", "I", "U", "E"],
            ["O", "Va", "Vi", "Vo"],
            ["Ma", "Mi", "Mu", "Me"],
            ["Mo", "Ta", "Ti", "Tu"],
            ["Te", "To", "Pa", "Pi"],
            ["Pu", "Sha", "Na", "Tha"],
            ["Pe", "Po", "Ra", "Ri"],
            ["Ru", "Re", "Ro", "Ta"],
            ["Ti", "Tu", "Te", "To"],
            ["Na", "Ni", "Nu", "Ne"],
            ["No", "Ya", "Yi", "Yu"],
            ["Ye", "Yo", "Bha", "Bhi"],
            ["Bhu", "Dha", "Pha", "Dha"],
            ["Bhe", "Bho", "Ja", "Ji"],
            ["Ju", "Je", "Jo", "Gha"],
            ["Ga", "Gi", "Gu", "Ge"],
            ["Go", "Sa", "Si", "Su"],
            ["Se", "So", "Da", "Di"],
            ["Du", "Tha", "Jha", "Jna"],
            ["De", "Do", "Cha", "Chi"],
            ["Chu", "Che", "Cho", "La"],
            ["Li", "Lu", "Le", "Lo"],
            ["A", "I", "U", "E"],
            ["O", "Va", "Vi", "Vo"],
            ["Ve", "Vo", "Ka", "Ki"]
        ]
        return alphabets[self._get_nakshatra_index(self.nakshatra)][self.charan - 1]

    def _calculate_paya(self):
        """
        Determine the Paya (attribute) of the zodiac sign.
        Paya represents the quality or nature of the sign and is used in various astrological analyses.
        """
        payas = ["Gold", "Silver", "Copper"]
        return payas[self._get_zodiac_index(self.zodiac_sign) % 3]

    def _get_zodiac_name(self, index):
        """Helper function to get the name of a zodiac sign from its index."""
        zodiac_signs = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", 
                        "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"]
        return zodiac_signs[index]

    def _get_nakshatra_name(self, index):
        """Helper function to get the name of a Nakshatra from its index."""
        nakshatras = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
                      "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", 
                      "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", 
                      "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", 
                      "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
        return nakshatras[index]

    def _get_zodiac_index(self, zodiac_name):
        """Helper function to get the index of a zodiac sign from its name."""
        zodiac_signs = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", 
                        "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"]
        return zodiac_signs.index(zodiac_name)

    def _get_nakshatra_index(self, nakshatra_name):
        """Helper function to get the index of a Nakshatra from its name."""
        nakshatras = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
                      "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", 
                      "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", 
                      "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", 
                      "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
        return nakshatras.index(nakshatra_name)
        
    def __str__(self):
        return (f"Vedic Astrological Profile for {self.person.first_name} {self.person.last_name}:\n"
                f"Date of Birth: {self.person.date_of_birth}\n"
                f"Time of Birth: {self.person.time_of_birth}\n"
                f"Place of Birth: {self.person.city_of_birth}, {self.person.country_of_birth}\n"
                f"Latitude: {self.person.latitude}, Longitude: {self.person.longitude}\n"
                f"Ayanamsa: {self.ayanamsa:.2f}\n"
                #f"Sunrise: {self.sunrise}, Sunset: {self.sunset}\n"
                f"Sun Sign (Rashi): {self.zodiac_sign}\n"
                f"Moon Sign (Janma Rashi): {self.moon_sign}\n"
                f"Ascendant (Lagna): {self.ascendant}\n"
                f"Nakshatra: {self.nakshatra}\n"
                f"Vashya: {self.vashya}\n"
                f"Yoni: {self.yoni}\n"
                f"Gan: {self.gan}\n"
                f"Nadi: {self.nadi}\n"
                f"Sign Lord: {self.sign_lord}\n"
                f"Nakshatra Lord: {self.nakshatra_lord}\n"
                f"Charan: {self.charan}\n"
                f"Tithi: {self.tithi}\n"
                f"Tatva: {self.tatva}\n"
                f"Name Alphabet: {self.name_alphabet}\n"
                f"Paya: {self.paya}")