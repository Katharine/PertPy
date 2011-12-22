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
        self.location = config.get("Forecast", "Location")
        
        try:
            f = urllib2.urlopen("http://api.wunderground.com/auto/wui/geo/ForecastXML/index.xml?query=%s" % self.location, None, 3);
            xml = f.read()
            f.close()
            self.forecast = ET.XML(xml)
        except:
            self.lcd.display_string("Forecast retrieval failed.")
    
    def update(self):
        forecast = self.forecast
        # Show the next four days:
        days = forecast.find("simpleforecast").findall("forecastday")
        i = 1
        for daily in days:
            day = daily.find("date").find("weekday").text[0:3]
            conditions = daily.find("conditions").text
            self.lcd.set_line(i, conditions, prefix="%s: " % day, scrolling=True)
            i += 1
            if i > 4:
                break
