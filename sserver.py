import SocketServer
import socket
from apiclient.discovery import build
#import requests
import urllib2, json


api_key ='API_KEY_HERE'

class DirectionsServer (SocketServer.BaseRequestHandler):

    def handle(self):
        clientLocation=self.request.recv(1024).decode("ascii")
        print(clientLocation)
        #do the directions using client location
        #return estimated time
        #jsonFile=requests.get("https://maps.googleapis.com/maps/api/directions/json?origin=Cork&destination=Dublin&key=AIzaSyAoUGzwRMXGeO9X8_QApT6cB85FOV2ec9Y")
        jsonFile=urllib2.urlopen("https://maps.googleapis.com/maps/api/directions/json?origin=Cork&destination=Dublin&key=API_KEY_HERE")
        values = json.load(jsonFile)
        jsonFile.close()

        dur = values['routes']
        print(dur)
        self.request.sendall(clientLocation.encode("ascii"))



if __name__== "__main__":
    HOST, PORT = "localhost", 3200
    server = SocketServer.TCPServer((HOST, PORT), DirectionsServer)
    ip, port = server.server_address
    server.serve_forever()
