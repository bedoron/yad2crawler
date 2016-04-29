import importlib
from logging import DEBUG, INFO, WARN, ERROR

# Crawl settings
ITERATION_SLEEP_SEC =   60*15       # 15 min

# Locations (latitude, longitude, radius, name)
LOCATIONS = [
    (32.080584, 34.780591, 0.7, "Rabin square"),
    (32.072375, 34.779196, 0.7, "Bima square"),
]
# OSVersion	5.0.2
crawl_parameters = {
    "CatID": 2,             # apartment
    "CityID": 1800.0,
    "SubCatID": 2,          # rent
#    "AreaID": 48,           # tlv centers
    "HomeTypeID": 1.0,
    "FromRooms": 2,         # min rooms
    "ToRooms": 2.5,         # max rooms
    "FromPrice": 4000,      # min price
    "ToPrice": 6000,        # max price
    "FromFloor": 1.0,
    "PriceType": 0,
    "PetsInHouse": None,    # Allow pets - or ignore param
    "Parking": None         # With parking
}

crawl_filter = {
    'onlyWithPhoto': False,
    'noRealEstate': False,
    'maxAge': 2
}


# Mail settings
mail_notifier = {
    "user": "some gmail user",
    "password": "some gmail pass",
    "recipient": "some gmail target email",
    "subject": "Yad2: new @{area}: {description}"
}

file_notifier = {
    'file_path': 'output.csv'
}

# Selected notifier
# notifier_settings  = mail_notifier
#notifier = getattr(importlib.import_module("notifiers.mail_notifier"), 'MailNotifier')

notifier_settings = file_notifier
notifier = getattr(importlib.import_module("notifiers.file_notifier"), 'FileNotifier')


# Log
LOG_LEVEL = DEBUG
LOG_FILE = 'yad2.log'
LOG_FORMAT = "%(asctime)s [%(levelname)-5.5s]  %(message)s"

# Proxy
PROXY = {
     "http":  "localhost:8888",
     "https": "localhost:8888",
}