from dataObjects import place
import logging
from polyline.codec import PolylineCodec

def getEta(directions):
    logging.info("Get total route eta")
    etaInSeconds=0
    for leg in directions['routes'][0]['legs']:
        seconds, textMins=getEtaOfLeg(leg)
        etaInSeconds+=seconds
    return etaInSeconds

def getEtaOfLeg(leg):
    logging.info("Get Eta of leg")
    seconds=int(leg['duration']['value'])
    minutesString=leg['duration']['text']
    logging.info("Eta is: "+minutesString)
    return seconds,minutesString

def getEtaOfLegsBeforeInclusive(directions,index):
    logging.info("get Eta Of Legs Before Inclusive")
    total_seconds=0
    for legCount in index:
        seconds, minutesString=getEtaOfLeg(directions['legs'][index])
        total_seconds+=seconds
    logging.info("Total Seconds till arrival: "+str(total_seconds))

def convertPlaceToObject(jsonPlace):
    logging.info("Converting Place to Object")
    lat=float(jsonPlace['geometry']['location']['lat'])
    lng=float(jsonPlace['geometry']['location']['lng'])
    location=lat,lng
    name=jsonPlace['name']
    types=jsonPlace['types']
    placeObject=place(name,location,types)
    logging.info(name+" converted")
    return placeObject

def mergerEachStepsPoints(leg):
    logging.info("Merging legs points into one")
    points=[]
    for step in leg['steps']:
        stepPoints=get_points_from_polyline(step['polyline']['points'])
        points= points+stepPoints
    logging.info("Leg polyline points generated")
    return points

def get_points_from_polyline(encoded_polyline):
    logging.info("decoding polyline points: "+str(encoded_polyline))
    points=PolylineCodec().decode(encoded_polyline)
    return points


