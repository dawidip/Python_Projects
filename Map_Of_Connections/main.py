import time
import urllib, urllib2, urlparse, os
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import json, re
from sets import Set
from multiprocessing import Pool

def firewallOn():
    os.system("sudo iptables -I INPUT 1 -j LOG")
    os.system("sudo iptables -I OUTPUT 1 -j LOG")
def firewallOf():
    os.system("sudo iptables -D INPUT 1")
    os.system("sudo iptables -D OUTPUT 1")
def prepareData():
    with open( '/var/log/kern.log' , 'r' ) as f:
        read_data = f.read()

    ip_table = parseIPfromFile(read_data)
    ip_table = list(set(ip_table))
    return ip_table
def getLocalisation(IP):
    page = urllib.urlopen("http://freegeoip.net/json/" + IP)
    page = page.read()
    j = json.loads(page)
    return j["longitude"], j["latitude"]
def parseIPfromFile(data):
    upshot = []
    regex = re.compile("\d+\.\d+\.\d+\.\d+")
    matches = regex.findall(data)
    for i in matches:
        upshot.append(i)
    return upshot
def traceRoute(IP):
    os.system("sudo traceroute -I -n " + str(IP) + " > tr" + str(IP))
    with open ("tr"+str(IP), 'r') as f:
        read_data = f.read()
    os.system("rm tr" + str(IP))
   # print read_data
    return read_data

def genMap():
    fig=plt.figure()
    ax=fig.add_axes([0.1,0.1,0.8,0.8])

    m = Basemap(llcrnrlon=-180,llcrnrlat=-80,urcrnrlon=180,urcrnrlat=80,projection='merc')

    return m , ax

def addLine(mapToDraw, arg):
    (a,b) , (c,d) = arg
    if (a != 0 or b != 0) and (c != 0 or d != 0):
        mapToDraw.drawgreatcircle(a,b,c,d,linewidth=1,color='b')

def showMap(mapToShow , axToShow):
    mapToShow.drawcoastlines()
    mapToShow.fillcontinents()
    axToShow.set_title('Connections Of My PC')
    plt.show()

def fun(ip):
    route = parseIPfromFile(traceRoute(ip))
    p = "149.156.75.190"
    res = [(getLocalisation(p), getLocalisation(p))]
    for r in route:
        res.append((getLocalisation(p), getLocalisation(r)))
        p = r
    return res


#firewallOn()
#time.sleep(10)
#firewallOf()

(m, ax) = genMap()

ipTable = prepareData()

pool = Pool(processes = 100)

j = 1
args = []
print len(ipTable)
for ip in ipTable:
    if j < 100:
        args.append(ip)
    else:
        break
    j += 1

paths = pool.map_async(fun, args).get()
pool.close()

for p in paths:
    for q in p:
        addLine(m, q)

#parseIPfromFile(traceRoute("31.13.92.14"))


#addLine(m, getLocalisation("31.13.72.8"), getLocalisation("195.150.156.163"))
showMap(m,ax)


