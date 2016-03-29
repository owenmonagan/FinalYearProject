from googleAPIRequests import getLatLong, getDirections
class poolMember():
    def __init__(self, name, origin, methodOfTransport):
                self.name = name
                self.origin = getLatLong(origin)
                self.originString=origin
                self.methodOfTransport = methodOfTransport
                self.meetPoint= None
                self.placesNear=None
                self.directionsToMeetPoint=None


    def setMeetPoint(self,meetPoint):
        self.meetPoint=meetPoint

    def setPlaces(self,places):
        self.placesNear=places

    def setDirections(self):
        self.directionsToMeetPoint=getDirections(self.origin,self.meetPoint.location,self.methodOfTransport,[])

    def getDirections(self):
        return self.directionsToMeetPoint

    def __repr__(self):
            return repr((self.name, self.origin, self.methodOfTransport, self.directionsToMeetPoint,self.placesNear,self.meetPoint))

class place():
    def __init__(self,name,location,types):
        self.name=name
        self.location= location
        self.types=types
        self.membersMeetPoint=None
        self.distanceFromPoint=None
        self.distanceLat=None
        self.distanceLng=None

    def setMeetPointInformation(self,membersMeetPoint,distanceFromPoint,distanceLat,distanceLng):
        self.membersMeetPoint=membersMeetPoint
        self.distanceFromPoint=distanceFromPoint
        self.distanceLat=distanceLat
        self.distanceLng=distanceLng



class poolLeader(poolMember):

    def __init__(self, name, origin, destination, methodOfTransport):
            self.name = name
            self.origin = getLatLong(origin)
            self.originString=origin
            self.destination = getLatLong(destination)
            self.destinationString = destination
            self.methodOfTransport = methodOfTransport
            self.directions=None
            self.wayPoints=None

    def setWayPoints(self, waypoints):
        self.wayPoints=waypoints

    def updateDirections(self):
        self.directions=getDirections(self.origin,self.destination,self.methodOfTransport,self.wayPoints)

    def getDirections(self):
        return self.directions

    def __repr__(self):
        return repr((self.name, self.origin, self.destination, self.methodOfTransport,self.directions,self.wayPoints))
