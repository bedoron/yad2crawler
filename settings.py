import importlib
from logging import DEBUG, INFO, WARN, ERROR

# Crawl settings
ITERATION_SLEEP_SEC =   60*15       # 15 min

# Apartments

# Query settings
# CAT_ID                  = 2         # apartment
# SUB_CAT_ID              = 2         # rent
# AREA_ID                 = 48        # tlv center
# FROM_ROOMS              = 2         # min rooms
# TO_ROOMS                = 3         # max rooms
# FROM_PRICE              = 5000      # min price
# TO_PRICE                = 7000      # max price
# ONLY_PETS_ALLOWED       = False     # remove without pets
# ONLY_WITH_PARKING       = False     # remove without parking
# ONLY_PRIVATE            = False     # remove 'tivuh'
# ONLY_WITH_PHOTO         = False     # remove without photos
# MAX_AGE_DAYS            = 2         # remove older than 2 days

# Locations (latitude, longitude, radius, name)
LOCATIONS = [
    (32.080584, 34.780591, 0.7, "Rabin square"),
    (32.072375, 34.779196, 0.7, "Bima square"),
]

crawl_parameters = {
    "CatID": 2,             # apartment
    "SubCatId": 2,          # rent
    "AreaID": 48,           # tlv center
    "PriceType": 0,
    "HomeTypeID": None,
    "FromRooms": 2,         # min rooms
    "ToRooms": 2.5,         # max rooms
    "FromPrice": 4000,      # min price
    "ToPrice": 5000,        # max price
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
# notifier = notifiers.mail_notifier

notifier_settings = file_notifier
notifier = getattr(importlib.import_module("notifiers.file_notifier"), 'FileNotifier')


# Log
LOG_LEVEL = DEBUG
LOG_FILE = 'yad2.log'
LOG_FORMAT = "%(asctime)s [%(levelname)-5.5s]  %(message)s"

# Proxy
PROXY = {
    # "http":  "localhost:8888",
    # "https": "localhost:8888",
}