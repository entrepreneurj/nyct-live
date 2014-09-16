#!/usr/bin/env python

import os
import functools
import datetime
DIR = "google_transit"
DATE_FORMAT = "%Y%m%d"

def date_parse(date_string): 
    return datetime.datetime.strptime(date_string,DATE_FORMAT).date()

class Calendar:

    def __init__(self, *args):
        self.service_id = args[0]
        self.monday = args[1]
        self.tuesday = args[2]
        self.wednesday = args[3]
        self.thursday = args[4]
        self.friday = args[5]
        self.saturday = args[6]
        self.sunday = args[7]
        self.start_date = date_parse(args[8])
        self.end_date = date_parse(args[9])
    
    def date_in_calendar_period(self,date):
        return self.start_date <= date and self.end_date >= date
    
    def is_valid_on_date_day(self, date):
        return True if \
                getattr(self, date.strftime("%A").lower()) is "1" else False

    def is_valid(self,date = None):

        if not date:
            date = datetime.datetime.today().date()
        return True if self.date_in_calendar_period(date) and \
                self.is_valid_on_date_day(date) \
                else False

    def __repr__(self):
        return str(self.__dict__)

class ExceptionTypeAdd():
    pass
class ExceptionTypeRemove():
    pass

class ExceptionType():
    
    def __init__(self, _type):
        if _type == 1:
            self._type = ExceptionTypeAdd
        else: 
            self._type = ExceptionTypeRemove


class CalendarDate():

    def __init__(self, *args):
        self.service_id = args[0]
        self.date = date_parse(args[1])
        self.exception_type = ExceptionType(args[2])

class GTFSDataBank():


    def __init__(self, date = None, stops = None, routes = None):

        self.routes = {}
        self.stops = {}
        self.trips = {}
        self.stop_times = []
        self.target_date = date
        self.target_stops = stops
        
        # Work out necessary service ids
        self.service_ids = self.get_services_for_date()
        print self.service_ids
        self.route_ids = []
        self.parse_routes(routes)
        self.trip_ids = []
        print "Parsing Trips"
        self.parse_trips(routes)
        self.stop_ids = []
        print "Parsing Stops"
        self.parse_stops(stops)
        print "Parsing Stop Times"
        self.parse_stop_times()
        
    
    def get_services_for_date(self):

        calendars = self.parse_calendar(self.target_date)
        print calendars
        calendar_dates = self.parse_calendar_dates(self.target_date)
        return [cal.service_id for cal in calendars]
    
    def add_item(self, item):

        if item.__class__ is Stop:
            self.stops[item.stop_id]=item
        elif item.__class__ is Route:
            self.routes[item.route_id] = item
        elif item.__class__ is Trip:
            self.trips[item.trip_id] = item
        elif item.__class__ is StopTime:
            self.stop_times.append(item)
        else:
            print item, type(item), item.__class__
            throw()
    def get_route(self, route_id):
        return self.route[route_id]

    def get_stop(self, stop_id):
        return self.stops[stop_id]

    def get_trip(self, _id):
        return self.routes[_id]

    def get_stop_times(self, trip_ids, stop_ids):
        stop_time_list = []

        for st in self.stop_times:
            if st.trip_id in trip_ids and st.stop_id in stop_ids:
                stop_time_list.append(st)
        return stop_time_list

    def parse_calendar(self,date = None):
        
        file_name = os.path.join(DIR, "calendar.txt")
        f = open(file_name, 'r')
        f.readline()

        calendar=[]
        for line in f:
            calendar.append(Calendar(*line.replace("\n","").split(',')))
        f.close()
        valid_calendars =  [cal for cal in calendar if cal.is_valid( date )]
        return valid_calendars

    def parse_trips(self, routes = None):
        
        file_name = os.path.join(DIR, "trips.txt")
        f = open(file_name, 'r')
        f.readline()
        
        for line in f:
            t = Trip(*line.replace("\n","").split(','))
            if (routes is None or t.route_id in routes) and \
                t.service_id in self.service_ids :
                
                self.add_item(t)
                self.trip_ids.append(t.trip_id)
        f.close()


    def parse_stops(self, stops = None):
        
        file_name = os.path.join(DIR, "stops.txt")
        f = open(file_name, 'r')
        f.readline()
        
        for line in f:
            s = Stop(*line.replace("\n","").split(','))
            if stops is None or s.stop_id in stops:
                self.add_item(s)
                self.stop_ids.append(s.stop_id)
        f.close()
    

    def parse_stop_times(self):
        
        file_name = os.path.join(DIR, "stop_times.txt")
        f = open(file_name, 'r')
        f.readline()
        
        for line in f:
            st = StopTime(*line.replace("\n","").split(','))
            if st.trip_id in self.trip_ids and st.stop_id in self.stop_ids:
                self.add_item(st)
        f.close()

    
    def parse_routes(self, routes = None):
        
        file_name = os.path.join(DIR, "routes.txt")
        f = open(file_name, 'r')
        f.readline()
        
        for line in f:
            r = Route(*line.replace("\n","").split(','))
            if routes is None or r.route_id in routes:
                self.add_item(r)
                self.route_ids.append(r.route_id)
        f.close()

    def parse_calendar_dates(self,date = None):
        
        if not date:
            date = datetime.datetime.today().date()
        
        file_name = os.path.join(DIR, "calendar_dates.txt")
        f = open(file_name, 'r')
        f.readline()
        
        calendar_dates = []
        for line in f:
            calendar_dates.append(CalendarDate(*line.replace("\n","").split(',')))
        f.close()
        
        valid_cal_dates = [cald for cald in calendar_dates if cald.date is date]
        if len(valid_cal_dates) > 0:
            # Have not implemented calendar_dates.txt
            throw()
        return valid_cal_dates

    def get_next_five_trains(self):
        print "Getting next 5 trains"
        counter = 0 
        sts = []
        for st in self.stop_times:
            if counter is 5:
                break
            else:
                if st.stop_id in self.stop_ids and \
                    st.trip_id in self.trip_ids and \
                    st.arrival_time > datetime.datetime.now().time():

                    sts.append(st)
                    counter += 1

        return sts
class Stop():

    def __init__(self, *args):

        self.stop_id = args[0]
        self.stop_name = args[1]

    def __repr__(self):
        return str(self.__dict__)

class Route():

    def __init__(self, *args):

        self.route_id = args[1]
        self.route_short_name = args[2]


    def __repr__(self):
        return str(self.__dict__)

class Trip():

    def __init__(self, *args):
    
        self.route_id = args[0]
        self.trip_id = args[1]
        self.service_id = args[2]
        self.trip_headsign = args[3]
        self.direction_id = args[4]


    def __repr__(self):
        return str(self.__dict__)

class StopTime():

    def __init__(self, *args):

        self.trip_id = args[0]
        self.stop_id = args[1]
        try:
            self.arrival_time = \
                datetime.datetime.strptime(args[2],"%H:%M:%S").time()
        except:
            time_string = args[2]
            time_string= str(int(time_string[:2]) %24).zfill(2)+time_string[2:]
            self.arrival_time = \
                datetime.datetime.strptime(time_string,"%H:%M:%S").time()

    def __repr__(self):

        return "{0} {1} {2}".format(self.arrival_time, self.stop_id,\
                self.trip_id)
if __name__ == "__main__":
    
    stops = "J30N J30S".split()
    gtfs = GTFSDataBank(stops = stops, routes = ['J', 'Z'])
    print (gtfs.get_next_five_trains())

