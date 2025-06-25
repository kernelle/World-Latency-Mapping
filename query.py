import random
import traceback
import subprocess
import time
import requests
import os
import json

from multiprocessing.pool import ThreadPool, Pool

FNULL = open(os.devnull, 'w')


def get_random_ip():
    return '.'.join(map(str, [random.randint(0, 255) for i in range(4)]))

def ping_ip(ip, lat, lon):

    try:
        t0 = time.time()
        status = subprocess.call(['ping', '-c1', '-t500', ip], stdout=FNULL, stderr=FNULL)
        if status != 0:
            return None
        #else:
            #geo = get_location(ip)
            #print(geo)
        responseTime = time.time() - t0
        print(f"{ip}, {lat}, {lon}, {responseTime}")
        return ip, lat, lon, responseTime
    except:
        traceback.print_exc()

if __name__ == '__main__':
    pool = ThreadPool(processes=100)
    f = open('log.txt', 'a')

    def cb(result):
        if result is None:
            return
        print(result)
        ip, lat, lon, t = result
        print(f"{f}, {lat}, {lon}, {t}")
        #print(f, lat, lon, t)

    import geoip2.database
    with geoip2.database.Reader('GeoLite2-City.mmdb') as reader:
        ipstolookup = []
        with open('Replies1.json', 'r') as file:
            ipstolookup = json.load( file )
        for line in open('rtts.txt', 'r') :
            if line[0] == 'l':
                ip = line.split('ip')[1].split('ttl')[0].rstrip(' ').strip('=')
                rttSplit = line.split('rtt')[1].strip(' ms\n').lstrip('=')
                #ipstolookup.append([ ip, rttSplit ])

        #print(ipstolookup)
        logfilecontent = ""
        for server in ipstolookup:
            #response = reader.city( server[0])
            try:
                response = reader.city( server['ip'])
            except:
                continue
            #print(response)
            #exit(0)
            #ip, lat, lon, time = server[0], response.location.latitude, response.location.longitude, server[1]
            #logfilecontent+= f"{response.continent.names['en']} {lat} {lon} {time}\n"
            #logfilecontent+= f"{lat} {lon} {time}\n"
            logfilecontent+= f"{server['ip']}\n"
        #geo = geolite2.MaxMindDb(filename="GeoLite2-City.mmdb").reader()
        print(logfilecontent)

        #for i in range(10000):
            #ip = get_random_ip()

            #try:

                #print(f'{ip}: Pinging')
            #match = geolite2.lookup(ip)
            #if match is None or match.location is None:
             #   continue
                #lat, lon = match.location.latitude, match.location.longitude
                #pool.apply_async(ping_ip, args=(ip, lat, lon), callback=cb)
            #except:
            #    continue
               # print(f'{ip}: Not in DB')
                #break


    #pool.close()
    #pool.join()

    #f.close()
