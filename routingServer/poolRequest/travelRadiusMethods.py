import logging
from dataObjects import place
from jsonProcessing import convertPlaceToObject, mergerEachStepsPoints

def calculateLastPointInRadiusIndex(radius,location,legHeadingToNextDestination):
    logging.info("Calculate Last Point In radius")
    lastPointIndex=0
    polyline=mergerEachStepsPoints(legHeadingToNextDestination)
    for index, point in enumerate(polyline):
        if isPointInRadius(point, location, radius):
            lastPointIndex=index
    logging.info("Point at index "+str(index)+" is the last one in the radius")
    return polyline, lastPointIndex


def isPointInRadius(point, location, radius):
    logging.info("Point: "+str(point)+" In Radius: "+str(radius)+" of user location: "+str(location))
    differenceInLatitude=abs(point[0]-location[0])
    differenceInLongitude=abs(point[1]-location[1])
    pointIsInRadius= (differenceInLatitude<radius) and (differenceInLongitude<radius)
    logging.info("Point: "+str(point)+"is in radius is "+str(pointIsInRadius))
    return pointIsInRadius

def calculateOrderedListOfNearestPlaces(places,point):
    logging.info("OrderingPlacesByNearestToPoint: "+str(point))
    print "PLaces:"+str(places)
    sortedPlaces=[]
    for placeIndex, place in enumerate(places['results']):
        placeObj=convertPlaceToObject(place)
        differenceLat=placeObj.location[0]-point[0]
        differenceLng=placeObj.location[1]-point[1]
        distanceAway=abs(differenceLat)+abs(differenceLng)
        #sortedPlaces.append((distanceAway,differenceLat,differenceLng,placeIndex))
        placeObj.setMeetPointInformation(point,distanceAway,differenceLat,differenceLng)
        sortedPlaces.append(placeObj)
        logging.info("place is "+str(distanceAway)+" away from "+str(point))
    sortedPlaces=sorted(sortedPlaces, key=lambda nearPlace: nearPlace.distanceFromPoint)
    logging.info(sortedPlaces[0].name+" is the closest:"+str(sortedPlaces[0].distanceFromPoint))
    return sortedPlaces

def getTravelRadius(poolMember,index,poolLeader,eta):
    logging.info("Getting Places within Travel Radius")
    #walking is 80.49 meters a minute
    #2.7 miles - 54 minutes (lots of traffic lights, basically no hills) = 20 minutes / mile [0]
    #cycling .5 of driving
    #leaderMethodvsMemberMethod=0

    #currently assuming the poolLeader is driving
    #therefor if member is driving then split is 50/50 aka .5
    conversionValue=0
    metersPerMinute=0

    if(poolMember.methodOfTransport=='driving'):
        metersPerMinute=240
        conversionValue=0.5
    elif(poolMember.methodOfTransport=='walking'):
        metersPerMinute=80
        conversionValue=0.1
    elif(poolMember.methodOfTransport=='bicycling'):
        metersPerMinute=160
        conversionValue=0.25
    else:
        #stationary
        logging.info(poolMember.name+" is stationary: ("+poolMember.methodOfTransport+")")
        metersPerMinute=0
    #not correct need to do calculations of car vs walking walking vs bike etc
    etaMinutes=eta/60
    #possible distance travled in the eta * the actual distance the person can make it in that time
    placesRadius=(etaMinutes* metersPerMinute)*conversionValue
    logging.info(poolMember.name+" can travel "+str(placesRadius)+" meters")
    return placesRadius