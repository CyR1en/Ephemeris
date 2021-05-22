import datetime
import json


class EventTime(dict):
    def __init__(self, date_time=None, time_zone='America/Los_Angeles'):
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        if date_time is None:
            self.dateTime = now
        else:
            self.dateTime = date_time
        self.timeZone = time_zone
        super().__init__(self.__dict__)


class Event(dict):
    def __init__(self,
                 summary='Ephemeris Event',
                 location=None,
                 description='Event tracked by Ephemeris activity tracker',
                 start=None,
                 end=None,
                 recurrence=None,
                 attendees=None,
                 reminders=None
                 ):
        if summary is not None:
            if summary == '':
                summary = 'Ephemeris Event'
            self.summary = summary
        if location is not None:
            self.location = location
        if description is not None:
            if description == '':
                description = 'Event tracked by Ephemeris activity tracker'
            self.description = description

        # Setup start and end time
        if start is not None:
            self.start = start
        else:
            self.start = EventTime()
        if end is not None:
            self.end = end
        else:
            self.end = EventTime()
        if recurrence is not None:
            self.recurrence = recurrence
        if attendees is not None:
            self.attendees = attendees
        if reminders is not None:
            self.reminders = reminders
        super().__init__(self.__dict__)

    def as_json(self):
        return json.dumps(self.__dict__)
