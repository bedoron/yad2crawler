from datetime           import datetime
from itertools          import ifilter
from json               import loads
from time               import sleep

from client             import Yad2Client
from db                 import ApartmentDatabase
from geo                import haversine_distance
from log                import Log
from notifiers.mail_notifier import MailNotifier
from page_parser        import PageParser
from re                 import findall, search
import settings
from win32com.client    import Dispatch


class Yad2Crawler(object):
    def __init__(self):
        self.log = Log()

        self.client = Yad2Client()
        self.notifier = settings.notifier(**settings.notifier_settings)

        self.db = ApartmentDatabase('yad2.db')
        self.client.add_cookie('PRID', 'xx')

        self.apartment_type = ['Private']
        if not settings.crawl_filter['noRealEstate']:
            self.apartment_type.append('Trade')


    def get_prid(self, html):
        hf = Dispatch('htmlfile')
        hf.writeln(html + "\n<script>document.write(\"<meta name='PRID' content='\" +genPid()+ \"'>\")</script>")
        prid = next(ifilter(lambda m: m.name == 'PRID', hf.getElementsByTagName('meta')), None)
        return prid.content if prid else None


    def get_prlst(self, html):
        prlst = ''
        for m in findall(r'String.fromCharCode\(\d*\)', html):
            match = search('\d+', m)
            if match:
                prlst += chr(int(match.group()))
                
        return prlst        


    def get_page(self, page = 1):
        url = "http://m.yad2.co.il/API/MadorResults.php"    

        def transform_web_to_web_values(val):
            if type(val) == type(True):
                return 1 if val else 0
            return val

        fix_parameters = { k: transform_web_to_web_values(v) for k, v in settings.crawl_parameters.items() if v is not None }
        fix_parameters.update({"Page": page})

        return self.client.get_url(url, args = fix_parameters)
    

    def crawl_apartments(self, json):
        for apr in json:
            if apr['Type'] != 'Ad':
                continue

            if not all([val in apr.keys() for val in ['latitude', 'longitude', 'RecordID', 'URL', 'img', 'Line1', 'Line2', 'Line3', 'Line4']]):
                continue

            latitude = apr['latitude']
            longitude = apr['longitude']
            record_id = apr['RecordID']
            url = apr['URL']
            img = apr['img']
            address = apr['Line1']
            description = apr['Line2']
            price = apr['Line3']
            date = apr['Line4']

            self.log.debug(".. Checking %s", record_id)

            if settings.crawl_filter['onlyWithPhoto'] and "missingAdPic.jpg" in img:
                self.log.debug(".. Filtering for missing img")
                continue

            area = next(ifilter(lambda (lat, lon, r, name): haversine_distance((latitude, longitude), (lat, lon)) <= r,
                                settings.LOCATIONS), None)
            if not area:
                self.log.debug(".. Filtering for no matching area")
                continue
            
            area_name = area[3]

            if (datetime.now() - datetime.strptime(date, "%d-%m-%Y")).days > settings.crawl_filter['maxAge']:
                self.log.debug(".. Filtering for old update date")
                continue

            if self.db.id_exists(record_id):
                self.log.debug(".. Already exists in database")
                self.db.update_last_seen(record_id)
                continue

            self.log.info(".. Found new match %s at %s", record_id, area_name)

            self.notify_apartment(url, address, area_name)

            self.db.add_new(record_id, area_name, address, description, price, url)
            self.log.debug(".. Added to database")

            self.log.debug(".. OK")


    def notify_apartment(self, url, description, area):
        self.log.debug(".. Sending notification")
        data = self.get_apartment_page(url)
        self.notifier.send_notification(url, description, area, data)

    def get_apartment_page(self, url):
        errors = True
        prid = None

        self.log.debug(".. Getting page %s", url)
        
        while errors:        
            
            html = self.client.get_url(url)
            
            if "Please activate javascript to view this site" in html:
                self.log.debug(".... Using IE to calculate PRID")
                prid = self.get_prid(html)            
                
            elif "bot, spider, crawler" in html:
                self.log.debug(".... Clearing cookies")
                self.client.clear_cookies()
  
            else:
                prlst = self.get_prlst(html)
                prid = prlst if prlst != '' else None
                errors = False

            if prid:
                self.log.debug(".... Setting PRID=%s", prid)
                self.client.add_cookie('PRID', prid)

        return self.create_apartment_body(html, url)

    def create_apartment_body(self, html, url):
        pp = PageParser(html)
        return pp.create_apartment_page(url)


    def crawl(self):
        iteration_sleep = 0
        while True:
            try:
                self.log.info("going to sleep (%d min)", iteration_sleep / 60)
                sleep(iteration_sleep)

                self.log.info("Starting scan")
                page = 1
                more = True

                while more:
                    self.log.info("Requesting page #%d", page)

                    data = self.get_page(page)
                    json = loads(data)

                    for type in filter(lambda x: x in json and 'Results' in json[x], self.apartment_type):
                        self.log.info(".. Checking %s apartments...", type)
                        self.crawl_apartments(json[type]['Results'])

                    more = True if json['MoreResults'] == 1 else False
                    page += 1

                iteration_sleep = settings.ITERATION_SLEEP_SEC
            except RuntimeError as e:
                self.log.error(e)
                break

            except Exception as e:
                self.log.error(e)
                iteration_sleep = settings.ITERATION_SLEEP_SEC_ERROR

        self.notifier.finalize()