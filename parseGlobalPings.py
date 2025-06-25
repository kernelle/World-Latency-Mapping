import json
from tabulate import tabulate
import glob
import sys

# Searchterms are the different deployements we are comparing,
#   reflecing in their filenames surrounded by 2 dots. Example: 1.git.100.world
#searchterms = [ "git", "cf", "cdn", "gcore", "netlify", "staticapp", "vercel", "regular", "fastly", "ioriver", "cfioriver"  ]
searchterms = [ "vercel",  "ioriver", "cf", "git", "cdn", "staticapp", "fastly", "regular", "netlify", "gcore", "cfioriver"  ]
#searchterms = [ "cf" ]

#can be overwritted by the -f flag
folder = "globalping.io.equalrandom"

#Defaults
showonlytest = ""
pretty_or_csv = False
sortParameter = "continent"
only_world = False
exclude_filter = ""
last_test_in_files = [0, ""]

for i, arg in enumerate( sys.argv ):
    if arg == '-n':
        showonlytest = sys.argv[i+1]
    if arg == '-c':
        sortParameter = "region"
    if arg == '-o':
        pretty_or_csv = True
    if arg == '-e' or arg == '--exclude':
        exclude_filter = sys.argv[i+1]
    if arg == '-w':
        only_world = True
    if arg == '-f':
        folder = sys.argv[i+1]
    if arg == '--help' or arg == '-h':
        print("Parser for globalping.io's Output")
        print("\t-n # \t-- Select only files starting with '#.'")
        print("\t-f VAL\t-- Folder containing all the output files")
        print("\t-e VAL\t-- Filter away any matching probes")
        print("\t-c \t-- Sort by continents instead of regions")
        print("\t-w \t-- Only show global value")
        print("\t-o \t-- csv output")
        exit(0)

def percentile_90( arr ):
    s = sorted( arr)
    index = int( 0.9 * (len(s) - 1) )
    return s[index]

def average(arr):
    return round( sum( arr ) / len( arr ) )

def loadFile( filename ):
    with open(filename, 'r') as file:
        #print(filename)
        return json.load( file )

def getTestNumberFromString( filename, place ):
    return int(filename.split( place, 1 )[0].split( "/", 1 )[1].strip('.'))

def parseDownloadtimes( ftp, place ):
    global last_test_in_files
    resultsProbes = [ ]

    for i,filename in enumerate( ftp ):

        try:
            data = loadFile( filename )
            # Combine all read data into one array
            for probe in data['results']:
                resultsProbes.append( probe )

            testnumber = getTestNumberFromString(filename, place)
            if testnumber > last_test_in_files[0]:
                last_test_in_files = [ testnumber, data['updatedAt'] ]

        except:
            print(f'Error reading {filename}')


    # "total", "download", "firstByte", "dns", "tls",  "tcp", longlats
    combined = [[], [], [], [], [], [], []]

    # to combine into regions
    combinedBuckets = { }
    #
    for i in resultsProbes:
        b = False
        if i['result']["status"] == "finished":
            if i["result"]["timings"]["total"] != None and ( i["probe"][sortParameter].lower().find( exclude_filter.lower() ) == -1 or exclude_filter == "" ):
                # 1) This is used to calulate the global averages
                #print(i)
                rC = 0
                for attr, value in i['result']['timings'].items():
                    combined[rC].append(value)
                    rC+=1
                #longlats
                combined[6].append( ( i['probe']["longitude"], i['probe']["latitude"] ) )

                # 2) 2) sort into regions
                for attr, value in combinedBuckets.items():
                    if attr == i["probe"][sortParameter] :
                        combinedBuckets[attr].append( i["result"]["timings"]["total"] )
                        b = True

                if not b:
                    combinedBuckets[ i["probe"][sortParameter] ] = [ i["result"]["timings"]["total"] ]

    return { "regions": combinedBuckets, "all": combined, "probes": len(combined[0]) }

def sortFilesIntoCategories( srch, fltopa):
    sortinghat = { }
    for filename in fltopa:
        for category in srch:
            if f"{showonlytest}.{category}." in filename:
                if category not in sortinghat:
                    sortinghat[ category ] = [ ]
                sortinghat[ category ].append( filename )
    return sortinghat

def main():
    filesToParse = glob.glob(folder+"/*")
    sortinghat = sortFilesIntoCategories(searchterms, filesToParse)
    if not pretty_or_csv:
        print(f"Reading {len(filesToParse)} files...")


    for category in sortinghat:
        allTimes = parseDownloadtimes( sortinghat[ category ], category )
        averages = allTimes["all"]

        if(len(averages[0]) != 0):
            toprint = []

            #Hold 'World'-data to add to top later
            resultFirst = [ "World", average(averages[0]), percentile_90(averages[0]), allTimes["probes"] ]

            count = 0
            #print(averages[6])
            for pr in averages[6]:
                # Time to first Byte = pos 2
                bs = f"{averages[6][count][0]}, {averages[6][count][1]}, {averages[2][count]}"
                count+=1
                #print(bs)
            #print(allTimes["regions"])

            builderRegionprint = [ ]
            cregion = 0
            for attr, times in allTimes["regions"].items():
                ctimes = 0
                #builderRegionprint = attr
                if len(builderRegionprint) <= ctimes:
                    builderRegionprint.append(category)
                for time in times:
                    builderRegionprint[ctimes] += ','+str(time)
                ctimes+=1
                cregion+=1
            print(builderRegionprint[0])

            if not only_world:
                for attr, averageCon in allTimes["regions"].items():
                    result = [ attr, average(averageCon), percentile_90(averageCon), len(averageCon) ]
                    toprint.append( result );

            toprint.sort( key=lambda x: x[2] )

            toprint.insert(0, resultFirst)
            #continue;
            if pretty_or_csv:
                print(f"Subdomain, Average, 90th%, Probes")
                for item in toprint:
                    print(f"{category}: {item[0]},{item[1]},{item[2]},{item[3]}")
            else:
                print(tabulate( toprint, headers=[ category, "Average", "90th%", "Probes" ], tablefmt="pretty"))
        else:
            if not pretty_or_csv:
                print(f"{category}: Empty list")
    print(f"\nLast Test Number: {last_test_in_files[0]}\tAt: {last_test_in_files[1]}")

main()
