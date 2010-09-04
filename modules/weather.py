from PertBase import PertBase
import urllib2
import ConfigParser
import xml.etree.cElementTree as ET

class PertModule(PertBase):
    def __init__(self, lcd, wait):
        PertBase.__init__(self, lcd, wait)
        # Load config stuff
        config = ConfigParser.SafeConfigParser()
        config.read(['config/weather.conf'])
        self.station = config.get("Current", "Station")
        
        try:
            f = urllib2.urlopen("http://api.wunderground.com/weatherstation/WXCurrentObXML.asp?ID=%s" % self.station)
            xml = f.read()
            f.close()
            self.weather = ET.XML(xml)
        except:
            self.lcd.display_string("Weather retrieval failed.")
    
    def update(self):
        # Pull in some data.
        weather = self.weather
        temp = float(weather.find("temp_c").text)
        temp_fail = float(weather.find("temp_f").text)
        location = weather.find("location").find("neighborhood").text
        wind_speed = float(weather.find("wind_mph").text)
        wind_direction = weather.find("wind_dir").text
        rain_last_hour = float(weather.find("precip_1hr_metric").text)
        rain_today = float(weather.find("precip_today_metric").text)
        humidity = int(weather.find("relative_humidity").text)
        
        # Display
        self.lcd.set_line(1, location)
        self.lcd.set_line(2, "Temp: %s\xDFC / %s\xDFF" % (temp, int(round(temp_fail))))
        self.lcd.set_line(3, "Wind: %s mph %s" % (wind_speed, wind_direction))
        self.lcd.set_line(4, "Humidity: %s%%" % humidity)