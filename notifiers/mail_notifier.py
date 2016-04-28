from smtplib          import SMTP, SMTPAuthenticationError

from notifiers.notifier import Notifier


class MailNotifier(Notifier):
    def __init__(self, user, password, recipient, subject):
        self.mail = user
        self.password = password
        self.recipient = recipient
        self.subject = subject

    def finalize(self):
        super(MailNotifier, self).finalize()

    def send_notification(self, url, description, area, actual_data):
        subject = self.subject.format(**locals())
        msg = self._build_message(actual_data, subject)
        self._send_message(msg)

    def _build_message(self, actual_data, subject):
        headers = [
            u"from: " + self.mail,
            u"subject: " + subject,
            u"to: " + self.recipient,
            u"mime-version: 1.0",
            u"content-type: text/html"
        ]

        headers = u"\r\n".join(headers)
        msg = (headers + u"\r\n\r\n" + actual_data).encode("utf-8")
        return msg

    def _send_message(self, mail_body):
        try:
            session = SMTP(u"smtp.gmail.com", 587)
            session.ehlo()
            session.starttls()
            session.login(self.mail, self.password)
            session.sendmail(self.mail, self.recipient, mail_body)
            session.quit()
        except SMTPAuthenticationError:
            raise RuntimeError("Wrong mail settings")
