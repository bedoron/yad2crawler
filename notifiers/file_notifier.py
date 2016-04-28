from notifiers.notifier import Notifier


class FileNotifier(Notifier):
    def __init__(self, file_path):
        self.f = open(file_path, 'a')

    def send_notification(self, url, description, area, actual_data):
        super(FileNotifier, self).send_notification(url, description, area, actual_data)
        self.f.write("{}, {}, {}, {}".format(url, description, area, actual_data))

    def finalize(self):
        super(FileNotifier, self).finalize()
        self.f.close()

