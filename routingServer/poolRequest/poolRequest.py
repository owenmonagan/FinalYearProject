import logging
from jsonProcessing import getEtaOfLeg, getEta
from googleAPIRequests import getDirections, getPlaces
from sortMembers import getPoolMembersMeetLocations, sortPoolMembersPositionInArrayByRoute
from travelRadiusMethods import calculateLastPointInRadiusIndex, calculateOrderedListOfNearestPlaces, getTravelRadius
import dataObjects

nameIndex=0
locationIndex=1
methodIndex=2

def createResponseMessage(poolLeader,poolMembers):
    logging.info("Creating Response Message")
    responseString=("ResponseMessage\n")
    leaderString="PoolLeader:"
    leaderString+=poolLeader.name+";"
    leaderString+=str(poolLeader.origin)+";"
    leaderString+=str(poolLeader.destination)+";"
    leaderString+=poolLeader.getDirections()['routes'][0]['overview_polyline']['points']+"\n"
    responseString+=leaderString
    for poolMember in poolMembers:
        memberString="PoolMember:"
        memberString+=poolMember.name+";"
        memberString+=str(poolMember.origin)+";"
        memberString+=poolMember.meetPoint.name+";"
        memberString+=str(poolMember.meetPoint.location)+";"
        memberString+=str(poolMember.meetPoint.types)+";"
        #memberString+=
        print str(getEta(poolMember.getDirections()))
        memberString+=poolMember.getDirections()['routes'][0]['overview_polyline']['points']+"\n"
        responseString+=memberString

    logging.info("response created: "+responseString)
    print(responseString)
    return responseString

def parsePoolRequest(requestString):
    indexOfFirstMember=3
    indexOfLeader=2
    logging.info("parsePoolRequest")
    lines=requestString.split("\n")
    poolDestination= lines[1].split(":")[1]
    #poolLeaderName, poolLeaderLocation, poolLeaderMethod=lines[2].split(":")[1].split(",")
    poolMembers=[]
    poolLeader=None

    #the first value in poolmembers is the poolLeader eg the driver
    for index, poolMember in enumerate(lines):
        if index>=indexOfLeader:
            poolMemberInformation=poolMember.split(":")[1].split(";")
            poolMemberName=poolMemberInformation[0]
            poolMemberLocation=poolMemberInformation[1]
            poolLMemberMethod=poolMemberInformation[2]

            if index>=indexOfFirstMember:
                poolMemberObject=dataObjects.poolMember(poolMemberName,poolMemberLocation,poolLMemberMethod)
                poolMembers.append(poolMemberObject)
                #poolMembers.append([poolMemberName,poolMemberLocation,poolLMemberMethod])
                logging.info("Parsed and stored member:")
                logging.info(poolMembers[index-indexOfFirstMember].__repr__())
            else:
                poolLeader=dataObjects.poolLeader(poolMemberName,poolMemberLocation,poolDestination,poolLMemberMethod)
                #poolLeader.append(poolMemberName)
                #poolLeader.append(poolMemberLocation)
                #poolLeader.append(poolLMemberMethod)
                logging.info("Parsed and stored leader:")
                logging.info(poolLeader.__repr__())


    logging.info("parsePoolRequest returns pool leader: "+str(poolLeader))
    logging.info("parsePoolRequest returns pool memebers: "+str(poolMembers))
    logging.info("parsePoolRequest returns pool destination: "+str(poolDestination))
    return poolLeader, poolMembers, poolDestination


#Parses Request String
#Then then gets the direct directions
#Then gets the directions to each persons location
def handlePoolRequest(requestString):
    logging.info("handlePoolRequest")
    #Set up objects
    poolLeader, poolMembers, poolDestination=parsePoolRequest(requestString)

    #extract the locations
    poolMembersMeetLocations=getPoolMembersMeetLocations(poolMembers)
    logging.info("get direct pool directions")
    #directDirections=getDirections(poolLeader[locationIndex],poolDestination,poolLeader[methodIndex],[])
    poolLeader.setWayPoints(poolMembersMeetLocations)
    poolLeader.updateDirections()
    poolDirections=poolLeader.getDirections()
    #poolDirections=getDirections(poolLeader.origin,poolLeader.destination ,poolLeader.methodOfTransport,poolMembersMeetLocations)
    #poolLeader.setDirections(poolDirections)
    #poolmember position in array corresponds to directions their leg
    poolMembers=sortPoolMembersPositionInArrayByRoute(poolMembers,poolDirections)
    #sort poolMembers so that the array starts with the first

    #for index,leg in enumerate(poolDirections['routes'][0]['legs']):
    legIndex=0
    totalSecondsFromPreviousLegs=0
    while (legIndex<len(poolMembers)):
        leg=poolDirections['routes'][0]['legs'][legIndex]
        nextLeg=poolDirections['routes'][0]['legs'][legIndex+1]
        logging.info("Calculating directions for: "+poolMembers[legIndex].name)
        seconds, minutes=getEtaOfLeg(leg)
        totalSecondsFromPreviousLegs+=seconds
        radius=getTravelRadius(poolMembers[legIndex],legIndex,poolLeader,totalSecondsFromPreviousLegs)
        places=getPlaces(poolMembers[legIndex].origin,radius)

        legPolylinePoints, indexOfLastPointInRadius=calculateLastPointInRadiusIndex(radius,poolMembers[legIndex].origin,nextLeg)
        placesNearestToTheFurthestPossibleTravelPoint=calculateOrderedListOfNearestPlaces(places,legPolylinePoints[indexOfLastPointInRadius])
        #now we assume that the closest point is optimal
        poolMembers[legIndex].setMeetPoint(placesNearestToTheFurthestPossibleTravelPoint[0])
        poolMembers[legIndex].setPlaces(placesNearestToTheFurthestPossibleTravelPoint)
        poolMembers[legIndex].setDirections()
        poolMembersMeetLocations=getPoolMembersMeetLocations(poolMembers)
        #poolDirections=getDirections(poolLeader.origin,poolLeader.destination ,poolLeader.methodOfTransport,poolMembersMeetLocations)
        poolLeader.setWayPoints(poolMembersMeetLocations)
        poolLeader.updateDirections()
        poolDirections=poolLeader.getDirections()
        legIndex+=1 #incriment
        #findRealisticPlaceToMeetLeader(placesWithinRadius,etaLeaderToMember,polyine[indexOfLastPointInRadius],poolMembers[index][methodIndex])
        #use eta of leader to get rough draft of how far one could travell

    responseMessage=createResponseMessage(poolLeader,poolMembers)
    return responseMessage


#THIS IS AN MORE EFFICIENT METHOD OF CALCULATING THE FURTHEST POINT TO WHICH THE PERSON CAN TRAVELL IN X AMOUNT OF TIME
#the member should walk the direction towards the second leg end and also the direction of which the car is coming from.
#i can pass the polyline using via so that I have the general route that I should take
#then calculate the directions to the end location hopping to use the poly line
#catch if its not possible and then try to just get the directions without via
#then I can use the places api to find points near there where the user can be picked up

def findRealisticPlaceToMeetLeader(poolMembers,poolMemberIndex,poolLeader,destination,lastPoint,places):
    placeNearestToLastPoint=0
    currentPoolRoute=poolMembers
    currentPoolRoute[poolMemberIndex][locationIndex]=placeNearestToLastPoint
    poolMemberDirections=getDirections(poolMembers[poolMemberIndex][locationIndex],destination,poolMembers[poolMemberIndex][methodIndex],)
    poolDirections=getDirections(poolMembers[poolMemberIndex][locationIndex],placeNearestToLastPoint,poolMembers[poolMemberIndex][methodIndex],)
    #poolMembers[indexOfPoolMember][locationIndex]=placeLocation


def getIdealMeetingPoints():
    pass
    #get the poly point from the next leg which is on the boundary the places radius
    #point=getPolyPointNearestToTheOuterRadius(placesRadius,directions['polyline'])
    #then find the closest place to that point
    #findClosestPlacetoPoint(point,places)
    #get directions to the nearest palce from the users location
    #eta=getdirectionsEta to the nearestplace
    #get directions
    #if the eta is approximatly
    #if eta is > half of leader eta than
    #    difference= eta - halfleaderEta
     #   how off the calculation was=  difference /eta
     #   repeat with how of the calculation was x length/poly line

def getPossibleTravelDistanceWithinLeaderEta(leaderEta, ):
    pass



def printDurations(jsonDirections):
    numSteps=len(jsonDirections['routes'][0]['legs'][0]['steps'])
    total_dist=0
    print numSteps
    for x in xrange(numSteps):
        print("Step {}:".format(x))
        print(jsonDirections['routes'][0]['legs'][0]['steps'][x]['html_instructions'])
        print(jsonDirections['routes'][0]['legs'][0]['steps'][x]['duration']['text']+"\n")
        #total_dist+=int(jsonDirections['routes'][0]['legs'][0]['steps'][x]['duration']['text'])

