from datetime import datetime

class Message:
    DATE_FORMAT = '%Y.%m.%d'
    TIME_FORMAT = '%H:%M:%S'
    DATE_SEPARATOR = '.'
    TIME_SEPARATOR = ':'
    DATETIME_SEPARATOR = ' '
    DATE_TIME_FORMAT = DATE_FORMAT + DATETIME_SEPARATOR + TIME_FORMAT

    def __init__(self, date, time, sender, text):
        self.date = date
        self.time = time
        self.datetime = date + Message.DATETIME_SEPARATOR + time
        self.sender = sender
        self.text = text

    def getMessageLength(self):
        return len(self.text)

    def getHour(self):
        return self.time.split(Message.TIME_SEPARATOR)[0]

    def getWeekDay(self):
        return datetime.strptime(self.datetime, Message.DATE_TIME_FORMAT).weekday()

    def getMonth(self):
        return self.date.split(Message.DATE_SEPARATOR)[1]

    def getYear(self):
        return self.date.split(Message.DATE_SEPARATOR)[0]

    def __str__(self):
        return "{} {} {}".format(self.datetime, self.sender, self.text)

