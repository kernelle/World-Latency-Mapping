import os
import sys
import math
import time
from datetime import datetime

startnumber = 41
folder = "globalping.io.ioriver"
places = [ "Asia", "North-America", "South-America", "Europe", "Oceania", "Africa" ]
subdomains = [ "git", "cf", "cdn", "gcore", "netlify", "staticapp", "vercel", "regular", "fastly", "ioriver", "cfioriver" ]
#subdomains = [ "ioriver", "cfioriver" ]
# 66 = visit all places with 1 probes
globalping_limit = 66
#packets_per_place = math.floor(( globalping_limit / len(places) ) / len( subdomains ) )
packets_per_place = 1

test = False
wait_before_start = 0
for i, arg in enumerate( sys.argv ):
    if arg == '-l' or arg == '--limit' :
        globalping_limit = int(sys.argv[i+1])
    if arg == '-w' or arg == '--wait' :
        wait_before_start = int(sys.argv[i+1])
    if arg == '-s' or arg == '--start' :
        startnumber = int(sys.argv[i+1])
    if arg == '-f' or arg == '--folder' :
        folder = sys.argv[i+1]
    if arg == '--test':
        test = True
    if arg == '-h' or arg == '--help':
        print("-l #\t--Set limit for probes per hour")
        print("-s #\t--Set number for tests, increments from this point")
        print("-w #\t--Wait minutes before starting")
        print("-f \"#\"\t--Set folder name")
        print("--test \t--Don't execute command")
        exit(0)

testtimes = math.floor( globalping_limit / ( ( len(places) * len(subdomains) ) * packets_per_place ) )
#testtimes = 5
testnumber = startnumber

print("Checking places...")
if wait_before_start > 0:
    print(f"{datetime.now()}: Waiting {wait_before_start} minutes before starting...")
    time.sleep( wait_before_start * 60 )

#for testNr in range(testtimes):
donepings = 0
while True:
    print(f"Limit: {globalping_limit}\tPpP: {packets_per_place}\tFolder: {folder}")
    print(f"Testing { startnumber - testnumber + testtimes} times")
    print(f"Test {testnumber}")
    for place in places:
        for sd in subdomains:
            # Maybe change this to 2d array of url and names
            url = f"https://{sd}.martijn.sh/"
            if sd == "staticapp":
                url = "https://martijn.static.domains/"
            elif sd == "regular":
                url = "https://martijn.sh/"

            donepings+=packets_per_place
            if not test:
                os.popen(f'globalping http {url} -J --method GET --limit {packets_per_place} -F {place} > {folder}/{testnumber}.{sd}.{packets_per_place}.{place}')
                time.sleep(1)
            else:
                print('Testing...')
            print(f'{donepings}: globalping http {url} -J --method GET --limit {packets_per_place} -F {place} > {folder}/{testnumber}.{sd}.{packets_per_place}.{place}')

    testnumber+=1
    if testnumber < startnumber + testtimes:
        if not test:
            print(f"{datetime.now()}: Waiting a minute")
            time.sleep(60)
        else:
            print(f"{datetime.now()}: Waiting a second")
            time.sleep(1)
    else:
        startnumber = testnumber
        donepings = 0
        if not test:
            print(f"{datetime.now()}: Waiting 12 hours")
            time.sleep( 43200 ) #4200
        else:
            print(f"{datetime.now()}: Waiting 5 seconds")
            time.sleep( 5 )


print("Done!")
