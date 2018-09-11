from websocket import create_connection
from datetime import datetime
from smtplib import SMTP


class WebSocket:
    """ Base class for websocket api classes to inherit from """

    def __init__(self):
        self.socket = None
        self.connect()

    def connect(self):
        self.socket = create_connection(self.url)

    def close(self):
        self.socket.close()

    def reconnect(self):
        self.close()
        self.connect()


class StreamingError:
    """ Psuedo exception class for any issues that occur while streaming.
        This will log the issue and notify user. """

    def __init__(self,msg):
        self.msg = msg
        print(msg)
        self._log()
        self._notify()

    def _log(self):
        with open("StreamLog","a+") as log:
            log.write(datetime.now(),"--> " + self.msg)

    # change this to text message
    def _notify(self):
        """ send email to user to user with event
        specific message and subject "AlgoTrader Alert" """
        server = SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_address, email_password)
        FROM = email_address
        TO = email_address
        SUBJECT = "Streaming Alert"
        MESSAGE = 'Subject: {}\n\n{}'.format(SUBJECT, self.msg)
        server.sendmail(FROM, TO, MESSAGE)
        server.quit()
