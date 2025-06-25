import math
import numpy as np
from annoy import AnnoyIndex
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from mpl_toolkits import basemap
import traceback

#This value scales the heatmap colours to our range
#Highlights Europe
vmin, vmax = 0.0, 0.2 #.1
#Highlight World
#vmin, vmax = 0, 0.3

# Lower is higher fidelity 0.25 deff
maxrender = 0.25

def ll_to_3d(lat, lon):
    lat *= math.pi / 180
    lon *= math.pi / 180
    x = math.cos(lat) * math.cos(lon)
    z = math.cos(lat) * math.sin(lon)
    y = math.sin(lat)
    return [x, y, z]

coords = {}
for line in open('log.txt'):
    try:
        # print(line.strip().split())
        lat, lon, t = map(float, line.strip().split())
        t = t/1000
        #t = 1-t

    except:
        #print( 'could not parse', line)
        #traceback.print_exc()
        continue
    coords.setdefault((lat, lon), []).append(t)

ai = AnnoyIndex(3, 'angular')
xs, ys, ts = [], [], []

for k, t in coords.items():
    lat, lon = k
    t = np.median(t) # dedup ips with same lat/long
    p = ll_to_3d(lat, lon)
    ai.add_item(len(ts), p)
    xs.append(lon)
    ys.append(lat)
    ts.append(t)

print('building index...')
ai.build(10)

print('building up data points')

#Change amount of datapoints here default 0.25
lons = np.arange(-180, 180, maxrender)
#The original code had -90, 90 to lessen render times
# -180 to 180 will render the entire planet
lats = np.arange(-90, 90, maxrender)
X, Y = np.meshgrid(lons, lats)
Z = np.zeros(X.shape)

count = 0
for i, _ in np.ndenumerate(Z):
    lon, lat = X[i], Y[i]

    v = ll_to_3d(lat, lon)

    js = ai.get_nns_by_vector(v, 50)
    all_ts = [ts[j] for j in js]
    #cutoff = np.percentile(all_ts, 90)
    cutoff = np.max(all_ts)
    p = np.mean([t for t in all_ts if t < cutoff])
    Z[i] = np.clip(p, vmin, vmax)

    count += 1
    if count % 1000 == 0:
        print(count, np.prod(Z.shape))

print('plotting')
#resolution l<i<h<f
'''
maps = [
    ('nyc', (20, 20), basemap.Basemap(projection='ortho',lat_0=30,lon_0=-30,resolution='l')),
    ('asia', (20, 20), basemap.Basemap(projection='ortho',lat_0=23,lon_0=105,resolution='l')),
    ('europe', (20, 20), basemap.Basemap(projection='ortho',lat_0=15,lon_0=9,resolution='f')),
    ('world', (20, 10), basemap.Basemap(projection='cyl', llcrnrlat=-60,urcrnrlat=80,  llcrnrlon=-180,urcrnrlon=180,resolution='c'))
]
'''

#97 is EU central
maps = ['world']
restDiv = 1

# This generates a map for every degree
for number in range(180, 360):
    if number % restDiv == 0:
        maps.append( number )
for number in range(0, 180):
    if number % restDiv == 0:
        maps.append( number )
##
# Resets the above code to only generate one map
maps = ['world']

# remove oceans
Z = basemap.maskoceans(X, Y, Z, resolution='h', grid=1.25)
print("drawing all")
for number in maps:

#for k, figsize, m in maps:
    if number == 'world':
        #Projection: merc / cyl
        k, figsize, m = ('world_projectionAzimutLondonTurbo', (20, 10), basemap.Basemap(projection='merc', llcrnrlat=-60,urcrnrlat=80,  llcrnrlon=-180,urcrnrlon=180,resolution='h'))

        width = 28000000; lon_0 = 0.1666; lat_0 = 51.4888#-5.239352519626899, 51.28175384234463
        m = basemap.Basemap(width=width,height=width,projection='aeqd',
                    lat_0=lat_0,lon_0=lon_0)
    else:
        k, figsize, m = f'rotation_vercel/rotate{number}', (20, 20), basemap.Basemap(projection='ortho',lat_0=15,lon_0=number-180,resolution='i')

    print('drawing', k)
    plt.figure(figsize=figsize)

    # draw coastlines, country boundaries, fill continents.
    #m.drawcoastlines(linewidth=0.25)
    #m.drawcountries(linewidth=0.25)

    # draw lon/lat grid lines every 30 degrees.
    #m.drawmeridians(np.arange(0,360,30))
    #m.drawparallels(np.arange(-90,90,30))

    # contour data over the map.
    # Scale colour: jet, viridis, turbo
    # https://matplotlib.org/stable/users/explain/colors/colormaps.html
    cf = m.contourf(X, Y, Z, 400, cmap=plt.get_cmap('turbo'), norm=plt.Normalize(vmin=vmin, vmax=vmax), latlon=True)
    cbar = m.colorbar(cf)
    #cbar.set_label('World Connectiviy Ratio: RTT(s) / (1 - ( ( 2 * distance(km) ) / c(km/s) ) )', rotation=270)

    plt.savefig(k + '.png', bbox_inches='tight')
    # Close to prevent memory leaks
    plt.close()
