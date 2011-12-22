from PertBase import PertBase
import urllib, urllib2
import ConfigParser
import xml.etree.cElementTree as ET
import time, calendar

class EVESkill(object):
    def __init__(self, type_id, level, start_sp, end_sp, start_time, end_time):
        super(EVESkill, self).__init__()
        self.type_id = type_id
        self.level = level
        self.start_sp = start_sp
        self.end_sp = end_sp
        self.start_time = start_time
        self.end_time = end_time
        self.name = PertModule.SkillIDs[self.type_id]
        

class PertModule(PertBase):
    def __init__(self, lcd, wait):
        PertBase.__init__(self, lcd, wait)
        # Load config stuff
        config = ConfigParser.SafeConfigParser()
        config.read(['config/eve.conf'])
        self.keyID = config.get("API", "ID")
        self.vCode = config.get("API", "VerificationCode")
        if PertModule.CharacterID is None:
            # We have to look all this fun stuff up, too.
            char_name = config.get("Character", "Name")
            chars = self.api_request("account/Characters")
            chars = chars.find("result").find("rowset").findall("row")
            for char in chars:
                if char.get('name').lower() == char_name.lower():
                    # We found it!
                    PertModule.CharacterName = char.get('name')
                    PertModule.CharacterID = int(char.get('characterID'))
                    PertModule.CorpID = int(char.get('corporationID'))
                    break
            if PertModule.CharacterID is None:
                return
        # Get the corp ticker
        corp = self.api_request("corp/CorporationSheet", corporationID=PertModule.CorpID)
        if corp is not None:
            PertModule.CorpTicker = corp.find('result').find('ticker').text
    
    def api_request(self, endpoint, **args):
        try:
            args['vCode'] = self.vCode
            args['keyID'] = self.keyID
            f = urllib2.urlopen("https://api.eveonline.com/%s.xml.aspx?%s" % (endpoint, urllib.urlencode(args)), None, 3);
            xml = f.read()
            f.close()
            return ET.XML(xml)
        except:
            return None

    def parse_time(self, t):
        return calendar.timegm(time.strptime(t, "%Y-%m-%d %H:%M:%S"))

    def perform_update(self):
        character = self.api_request("eve/CharacterInfo", characterID=PertModule.CharacterID)
        PertModule.NextUpdate = self.parse_time(character.find("cachedUntil").text)
        character = character.find("result")
        PertModule.CurrentBalance = float(character.find("accountBalance").text)
        PertModule.CurrentSystem = character.find("lastKnownLocation").text

        # And the skill queue!
        skills = self.api_request("char/SkillQueue", characterID=PertModule.CharacterID).find("result").find("rowset")
        PertModule.SkillQueue = [EVESkill(int(x.get('typeID')), int(x.get('level')), int(x.get('startSP')), 
                                    int(x.get('endSP')), self.parse_time(x.get('startTime')), self.parse_time(x.get('endTime'))) 
                                    for x in skills.findall("row")]
    
    def get_current_skill(self):
        now = time.time()
        for skill in PertModule.SkillQueue:
            if skill.end_time > now:
                return skill
        return None
    
    def format_skill_level(self, level):
        return level
        #return ['0', 'I', 'II', 'III', 'IV', 'V'][level]

    def format_time_interval(self, seconds):
        weeks = seconds // (86400 * 7)
        seconds -= weeks * 86400 * 7
        days = seconds // 86400
        seconds -= days * 86400
        hours = seconds // 3600
        seconds -= hours * 3600
        minutes = seconds // 60
        seconds = seconds % 60

        parts = []
        if weeks > 0:
            parts.append("%iw" % weeks)
        if days > 0:
            parts.append("%id" % days)
        if hours > 0:
            parts.append("%ih" % hours)
        if minutes > 0:
            parts.append("%im" % minutes)
        return ''.join(parts)


    def update(self):
        self.lcd.set_line(1, PertModule.CharacterName)
        # Refresh the information every hour
        if PertModule.NextUpdate is None or PertModule.NextUpdate < time.time():
            self.lcd.set_line(2, "Updating...")
            self.perform_update()
        
        self.lcd.set_line(3, "{:,.0f} ISK".format(PertModule.CurrentBalance))
        self.lcd.set_line(2, "%s %5s" % (PertModule.CurrentSystem.ljust(14)[:14], PertModule.CorpTicker))
        skill = self.get_current_skill()
        if skill is not None:
            self.lcd.set_line(4, skill.name, suffix=" %s (%s)" % (self.format_skill_level(skill.level), self.format_time_interval(skill.end_time - time.time())), scrolling=True)
        else:
            self.lcd.set_line(4, "No skill in training")

# We have to store information in "static" properties because the actual class is re-instantiated every time it's displayed.
# In retrospect, this is dumb.
PertModule.CharacterID = None
PertModule.CharacterName = None
PertModule.CorpID = None
PertModule.CorpTicker = None
PertModule.SkillQueue = None
PertModule.CurrentBalance = None
PertModule.CurrentSystem = None
PertModule.NextUpdate = None

PertModule.SkillIDs = {
    3300: "Gunnery",
    3301: "Small Hybrid Turret",
    3302: "Small Projectile Turret",
    3303: "Small Energy Turret",
    3304: "Medium Hybrid Turret",
    3305: "Medium Projectile Turret",
    3306: "Medium Energy Turret",
    3307: "Large Hybrid Turret",
    3308: "Large Projectile Turret",
    3309: "Large Energy Turret",
    3310: "Rapid Firing",
    3311: "Sharpshooter",
    3312: "Motion Prediction",
    3315: "Surgical Strike",
    3316: "Controlled Bursts",
    3317: "Trajectory Analysis",
    3318: "Weapon Upgrades",
    11082: "Small Railgun Specialization",
    11083: "Small Beam Laser Specialization",
    11084: "Small Autocannon Specialization",
    11207: "Advanced Weapon Upgrades",
    12201: "Small Artillery Specialization",
    12202: "Medium Artillery Specialization",
    12203: "Large Artillery Specialization",
    12204: "Medium Beam Laser Specialization",
    12205: "Large Beam Laser Specialization",
    12206: "Medium Railgun Specialization",
    12207: "Large Railgun Specialization",
    12208: "Medium Autocannon Specialization",
    12209: "Large Autocannon Specialization",
    12210: "Small Blaster Specialization",
    12211: "Medium Blaster Specialization",
    12212: "Large Blaster Specialization",
    12213: "Small Pulse Laser Specialization",
    12214: "Medium Pulse Laser Specialization",
    12215: "Large Pulse Laser Specialization",
    20327: "Capital Energy Turret",
    21666: "Capital Hybrid Turret",
    21667: "Capital Projectile Turret",
    22043: "Tactical Weapon Reconfiguration",
    3319: "Missile Launcher Operation",
    3320: "Rockets",
    3321: "Standard Missiles",
    3322: "FoF Missiles",
    3323: "Defender Missiles",
    3324: "Heavy Missiles",
    3325: "Torpedoes",
    3326: "Cruise Missiles",
    12441: "Missile Bombardment",
    12442: "Missile Projection",
    20209: "Rocket Specialization",
    20210: "Standard Missile Specialization",
    20211: "Heavy Missile Specialization",
    20212: "Cruise Missile Specialization",
    20213: "Torpedo Specialization",
    20312: "Guided Missile Precision",
    20314: "Target Navigation Prediction",
    20315: "Warhead Upgrades",
    21071: "Rapid Launch",
    21668: "Citadel Torpedoes",
    25718: "Heavy Assault Missile Specialization",
    25719: "Heavy Assault Missiles",
    28073: "Bomb Deployment",
    32435: "Citadel Cruise Missiles",
    3184: "ORE Industrial",
    3327: "Spaceship Command",
    3328: "Gallente Frigate",
    3329: "Minmatar Frigate",
    3330: "Caldari Frigate",
    3331: "Amarr Frigate",
    3332: "Gallente Cruiser",
    3333: "Minmatar Cruiser",
    3334: "Caldari Cruiser",
    3335: "Amarr Cruiser",
    3336: "Gallente Battleship",
    3337: "Minmatar Battleship",
    3338: "Caldari Battleship",
    3339: "Amarr Battleship",
    3340: "Gallente Industrial",
    3341: "Minmatar Industrial",
    3342: "Caldari Industrial",
    3343: "Amarr Industrial",
    3344: "Gallente Titan",
    3345: "Minmatar Titan",
    3346: "Caldari Titan",
    3347: "Amarr Titan",
    3755: "Jove Frigate",
    3758: "Jove Cruiser",
    9955: "Polaris",
    10264: "Concord",
    11075: "Jove Industrial",
    11078: "Jove Battleship",
    12092: "Interceptors",
    12093: "Covert Ops",
    12095: "Assault Ships",
    12096: "Logistics",
    12097: "Destroyers",
    12098: "Interdictors",
    12099: "Battlecruisers",
    16591: "Heavy Assault Ships",
    17940: "Mining Barge",
    19430: "Omnipotent",
    19719: "Transport Ships",
    20342: "Advanced Spaceship Command",
    20524: "Amarr Freighter",
    20525: "Amarr Dreadnought",
    20526: "Caldari Freighter",
    20527: "Gallente Freighter",
    20528: "Minmatar Freighter",
    20530: "Caldari Dreadnought",
    20531: "Gallente Dreadnought",
    20532: "Minmatar Dreadnought",
    20533: "Capital Ships",
    22551: "Exhumers",
    22761: "Recon Ships",
    23950: "Command Ships",
    24311: "Amarr Carrier",
    24312: "Caldari Carrier",
    24313: "Gallente Carrier",
    24314: "Minmatar Carrier",
    28374: "Capital Industrial Ships",
    28609: "Heavy Interdictors",
    28615: "Electronic Attack Ships",
    28656: "Black Ops",
    28667: "Marauders",
    29029: "Jump Freighters",
    29637: "Industrial Command Ships",
    30650: "Amarr Strategic Cruiser",
    30651: "Caldari Strategic Cruiser",
    30652: "Gallente Strategic Cruiser",
    30653: "Minmatar Strategic Cruiser",
    3348: "Leadership",
    3349: "Skirmish Warfare",
    3350: "Siege Warfare",
    3351: "Siege Warfare Specialist",
    3352: "Information Warfare Specialist",
    3354: "Warfare Link Specialist",
    11569: "Armored Warfare Specialist",
    11572: "Skirmish Warfare Specialist",
    11574: "Wing Command",
    20494: "Armored Warfare",
    20495: "Information Warfare",
    22536: "Mining Foreman",
    22552: "Mining Director",
    24764: "Fleet Command",
    3363: "Corporation Management",
    3364: "Station Management",
    3365: "Starbase Management",
    3366: "Factory Management",
    3367: "Refinery Management",
    3368: "Ethnic Relations",
    3369: "CFO Training",
    3370: "Chief Science Officer",
    3371: "Public Relations",
    3372: "Intelligence Analyst",
    3373: "Starbase Defense Management",
    3731: "Megacorp Management",
    3732: "Empire Control",
    11584: "Anchoring",
    12241: "Sovereignty",
    3380: "Industry",
    3381: "Amarr Tech",
    3382: "Caldari Tech",
    3383: "Gallente Tech",
    3384: "Minmatar Tech",
    3385: "Refining",
    3386: "Mining",
    3387: "Mass Production",
    3388: "Production Efficiency",
    3389: "Refinery Efficiency",
    3390: "Mobile Refinery Operation",
    3391: "Mobile Factory Operation",
    11395: "Deep Core Mining",
    12180: "Arkonor Processing",
    12181: "Bistot Processing",
    12182: "Crokite Processing",
    12183: "Dark Ochre Processing",
    12184: "Gneiss Processing",
    12185: "Hedbergite Processing",
    12186: "Hemorphite Processing",
    12187: "Jaspet Processing",
    12188: "Kernite Processing",
    12189: "Mercoxit Processing",
    12190: "Omber Processing",
    12191: "Plagioclase Processing",
    12192: "Pyroxeres Processing",
    12193: "Scordite Processing",
    12194: "Spodumain Processing",
    12195: "Veldspar Processing",
    12196: "Scrapmetal Processing",
    16281: "Ice Harvesting",
    18025: "Ice Processing",
    22578: "Mining Upgrades",
    24268: "Supply Chain Management",
    24625: "Advanced Mass Production",
    25544: "Gas Cloud Harvesting",
    26224: "Drug Manufacturing",
    28373: "Ore Compression",
    28585: "Industrial Reconfiguration",
    3392: "Mechanics",
    3393: "Repair Systems",
    3394: "Hull Upgrades",
    3395: "Frigate Construction",
    3396: "Industrial Construction",
    3397: "Cruiser Construction",
    3398: "Battleship Construction",
    3400: "Outpost Construction",
    16069: "Remote Armor Repair Systems",
    21803: "Capital Repair Systems",
    22242: "Capital Ship Construction",
    22806: "EM Armor Compensation",
    22807: "Explosive Armor Compensation",
    22808: "Kinetic Armor Compensation",
    22809: "Thermic Armor Compensation",
    24568: "Capital Remote Armor Repair Systems",
    25863: "Salvaging",
    26252: "Jury Rigging",
    26253: "Armor Rigging",
    26254: "Astronautics Rigging",
    26255: "Drones Rigging",
    26256: "Electronic Superiority Rigging",
    26257: "Projectile Weapon Rigging",
    26258: "Energy Weapon Rigging",
    26259: "Hybrid Weapon Rigging",
    26260: "Launcher Rigging",
    26261: "Shield Rigging",
    27902: "Remote Hull Repair Systems",
    27906: "Tactical Logistics Reconfiguration",
    27936: "Capital Remote Hull Repair Systems",
    28879: "Nanite Operation",
    28880: "Nanite Interfacing",
    3402: "Science",
    3403: "Research",
    3405: "Biology",
    3406: "Laboratory Operation",
    3408: "Reverse Engineering",
    3409: "Metallurgy",
    3410: "Astrogeology",
    3411: "Cybernetics",
    3412: "Astrometrics",
    11433: "High Energy Physics",
    11441: "Plasma Physics",
    11442: "Nanite Engineering",
    11443: "Hydromagnetic Physics",
    11444: "Amarrian Starship Engineering",
    11445: "Minmatar Starship Engineering",
    11446: "Graviton Physics",
    11447: "Laser Physics",
    11448: "Electromagnetic Physics",
    11449: "Rocket Science",
    11450: "Gallentean Starship Engineering",
    11451: "Nuclear Physics",
    11452: "Mechanical Engineering",
    11453: "Electronic Engineering",
    11454: "Caldari Starship Engineering",
    11455: "Quantum Physics",
    11487: "Astronautic Engineering",
    11529: "Molecular Engineering",
    11858: "Hypernet Science",
    12179: "Research Project Management",
    13278: "Archaeology",
    20433: "Talocan Technology",
    21718: "Hacking",
    21789: "Sleeper Technology",
    21790: "Caldari Encryption Methods",
    21791: "Minmatar Encryption Methods",
    23087: "Amarr Encryption Methods",
    23121: "Gallente Encryption Methods",
    23123: "Takmahl Technology",
    23124: "Yan Jung Technology",
    24242: "Infomorph Psychology",
    24270: "Scientific Networking",
    24562: "Jump Portal Generation",
    24563: "Doomsday Operation",
    24606: "Cloning Facility Operation",
    24624: "Advanced Laboratory Operation",
    25530: "Neurotoxin Recovery",
    25538: "Nanite Control",
    25739: "Astrometric Rangefinding",
    25810: "Astrometric Pinpointing",
    25811: "Astrometric Acquisition",
    28164: "Thermodynamics",
    30324: "Defensive Subsystem Technology",
    30325: "Engineering Subsystem Technology",
    30326: "Electronic Subsystem Technology",
    30327: "Offensive Subsystem Technology",
    30788: "Propulsion Subsystem Technology",
    3413: "Engineering",
    3416: "Shield Operation",
    3417: "Energy Systems Operation",
    3418: "Energy Management",
    3419: "Shield Management",
    3420: "Tactical Shield Manipulation",
    3421: "Energy Pulse Weapons",
    3422: "Shield Emission Systems",
    3423: "Energy Emission Systems",
    3424: "Energy Grid Upgrades",
    3425: "Shield Upgrades",
    11204: "Advanced Energy Grid Upgrades",
    11206: "Advanced Shield Upgrades",
    11566: "Thermic Shield Compensation",
    12365: "EM Shield Compensation",
    12366: "Kinetic Shield Compensation",
    12367: "Explosive Shield Compensation",
    21059: "Shield Compensation",
    21802: "Capital Shield Operation",
    24571: "Capital Shield Emission Systems",
    24572: "Capital Energy Emission Systems",
    3426: "Electronics",
    3427: "Electronic Warfare",
    3428: "Long Range Targeting",
    3429: "Targeting",
    3430: "Multitasking",
    3431: "Signature Analysis",
    3432: "Electronics Upgrades",
    3433: "Sensor Linking",
    3434: "Weapon Disruption",
    3435: "Propulsion Jamming",
    3551: "Survey",
    11208: "Advanced Sensor Upgrades",
    11579: "Cloaking",
    12368: "Hypereuclidean Navigation",
    19759: "Long Distance Jamming",
    19760: "Frequency Modulation",
    19761: "Signal Dispersion",
    19766: "Signal Suppression",
    19767: "Turret Destabilization",
    19921: "Target Painting",
    19922: "Signature Focusing",
    21603: "Cynosural Field Theory",
    27911: "Projected Electronic Counter Measures",
    28604: "Tournament Observation",
    28631: "Imperial Navy Security Clearance",
    3436: "Drones",
    3437: "Scout Drone Operation",
    3438: "Mining Drone Operation",
    3439: "Repair Drone Operation",
    3440: "Salvage Drone Operation",
    3441: "Heavy Drone Operation",
    3442: "Drone Interfacing",
    12305: "Drone Navigation",
    12484: "Amarr Drone Specialization",
    12485: "Minmatar Drone Specialization",
    12486: "Gallente Drone Specialization",
    12487: "Caldari Drone Specialization",
    22172: "TEST Drone Skill",
    22541: "Mining Drone Specialization",
    23069: "Fighters",
    23566: "Electronic Warfare Drone Interfacing",
    23594: "Sentry Drone Interfacing",
    23599: "Propulsion Jamming Drone Interfacing",
    23606: "Drone Sharpshooting",
    23618: "Drone Durability",
    24241: "Combat Drone Operation",
    24613: "Advanced Drone Interfacing",
    32339: "Fighter Bombers",
    3443: "Trade",
    3444: "Retail",
    3445: "Black Market Trading",
    3446: "Broker Relations",
    3447: "Visibility",
    3448: "Smuggling",
    11015: "Test",
    12834: "General Freight",
    13069: "Starship Freight",
    13070: "Mineral Freight",
    13071: "Munitions Freight",
    13072: "Drone Freight",
    13073: "Raw Material Freight",
    13074: "Consumable Freight",
    13075: "Hazardous Material Freight",
    16594: "Procurement",
    16595: "Daytrading",
    16596: "Wholesale",
    16597: "Margin Trading",
    16598: "Marketing",
    16622: "Accounting",
    18580: "Tycoon",
    25233: "Corporation Contracting",
    25235: "Contracting",
    28261: "Tax Evasion",
    3449: "Navigation",
    3450: "Afterburner",
    3451: "Fuel Conservation",
    3452: "Acceleration Control",
    3453: "Evasive Maneuvering",
    3454: "High Speed Maneuvering",
    3455: "Warp Drive Operation",
    3456: "Jump Drive Operation",
    21610: "Jump Fuel Conservation",
    21611: "Jump Drive Calibration",
    3355: "Social",
    3356: "Negotiation",
    3357: "Diplomacy",
    3358: "Fast Talk",
    3359: "Connections",
    3361: "Criminal Connections",
    3362: "DED Connections",
    3893: "Mining Connections",
    3894: "Distribution Connections",
    3895: "Security Connections",
    20127: "Stealth Bombers Fake Skill",
    30532: "Amarr Defensive Systems",
    30536: "Amarr Electronic Systems",
    30537: "Amarr Offensive Systems",
    30538: "Amarr Propulsion Systems",
    30539: "Amarr Engineering Systems",
    30540: "Gallente Defensive Systems",
    30541: "Gallente Electronic Systems",
    30542: "Caldari Electronic Systems",
    30543: "Minmatar Electronic Systems",
    30544: "Caldari Defensive Systems",
    30545: "Minmatar Defensive Systems",
    30546: "Gallente Engineering Systems",
    30547: "Minmatar Engineering Systems",
    30548: "Caldari Engineering Systems",
    30549: "Caldari Offensive Systems",
    30550: "Gallente Offensive Systems",
    30551: "Minmatar Offensive Systems",
    30552: "Caldari Propulsion Systems",
    30553: "Gallente Propulsion Systems",
    30554: "Minmatar Propulsion Systems",
    2403: "Advanced Planetology",
    2406: "Planetology",
    2495: "Interplanetary Consolidation",
    2505: "Command Center Upgrades",
    13279: "Remote Sensing"
}
