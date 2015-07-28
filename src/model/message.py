from datetime import datetime

class Message:
    DATE_TIME_FORMAT = '%Y.%m.%d %H:%M:%S'

    def __init__(self, date, time, sender, text):
        self.date = date
        self.time = time
        self.datetime = date + ' ' + time
        self.sender = sender
        self.text = text

    def getMessageLength(self):
        return len(self.text)

    def getHour(self):
        return self.time.split(':')[0]

    def getWeekDay(self):
        return datetime.strptime(self.datetime, Message.DATE_TIME_FORMAT).weekday()

    def getMonth(self):
        return self.date.split('.')[1]

    def getYear(self):
        return self.date.split('.')[0]

    def __str__(self):
        return "{} {} {}".format(self.datetime, self.sender, self.text)
