import csv
import matplotlib.pyplot as plt

from operator import itemgetter
from collections import defaultdict

import json
from pprint import pprint
import pdb
import numpy as np

def rgb2Hex(r,g,b):
    return '#{:02x}{:02x}{:02x}'.format(r,g,b)


def compresssingData(x, c, quan):
    # x: timestamp, y: fieldID, c: event
    interval = (max(x) - min(x))/quan
    interval_list = {}; val = {}; hex_color = {}
    percentile = 0
    count = 15 # weighted parameter for color
    val[percentile] = {}
    val[percentile]['r'] = 0
    val[percentile]['g'] = 0
    val[percentile]['b'] = 0
    val[percentile][c[0]] = 1
    interval_list[0] = [0]
    for i, t in enumerate(x):
        if (t <= (percentile+1)*interval+min(x) 
            and t > (percentile)*interval+min(x)
            and percentile <= quan):
            if i != 0:
                interval_list[percentile].append(i)
            else:
                interval_list[0] = [0]
            val[percentile][c[i]] += 1
        else:
            # counting value
            if percentile in val:
                #count = val[percentile]['r'] + val[percentile]['g'] + val[percentile]['b']
                cr = round(val[percentile]['r']*255/count)
                cg = round(val[percentile]['g']*255/count)
                cb = round(val[percentile]['b']*255/count)
                cr = 255 if cr > 255 else cr
                cg = 255 if cg > 255 else cg
                cb = 255 if cb > 255 else cb
                hex_color[percentile] = rgb2Hex(255-cr,255-cg,255-cb)
            # move on to next percentile
            while(t > (percentile+1)*interval+min(x)):
                percentile += 1
            if (t <= (percentile+1)*interval+min(x)
                and t > (percentile)*interval+min(x)
                and percentile <= quan):
                interval_list[percentile] = [i]
                val[percentile] = {}
                val[percentile]['r'] = 0
                val[percentile]['g'] = 0
                val[percentile]['b'] = 0
                val[percentile][c[i]] = 1
    if percentile in val:
        #count = val[percentile]['r'] + val[percentile]['g'] + val[percentile]['b']
        cr = round(val[percentile]['r']*255/count)
        cg = round(val[percentile]['g']*255/count)
        cb = round(val[percentile]['b']*255/count)
        cr = 255 if cr > 255 else cr
        cg = 255 if cg > 255 else cg
        cb = 255 if cb > 255 else cb
        hex_color[percentile] = rgb2Hex(255-cr,255-cg,255-cb)
    return list(hex_color.keys()), list(hex_color.values())

def plotTimeline(dataset, **kwargs):
    """
    Plots a timeline of events from different fieldIDs to visualize a relative
    sequence or density of events. Expects data in the form of:
        (timestamp, fieldID, event)
    Though this can be easily modified if needed. Expects sorted input.
    """
    id_range = range(kwargs['start_id'], kwargs['end_id']+1)
    quan = kwargs['quan']
    outpath = kwargs.pop('outpath', None)  # Save the figure as an SVG
    colors  = kwargs.pop('colors', {})     # Plot the colors for the series.
    series  = set(id_range)   # Figure out the unique series
    # Sort and index the series
    series  = sorted(list(series))

    # Bring the data into memory and sort
    # sort by timestamp
    #dataset = sorted(list(dataset), key=itemgetter(0))

    # Make a first pass over the data to determine number of series, etc.
    #for event, fieldID, _ in dataset:
    #    series.add(fieldID)
    #    if event not in colors:
    #        colors[event] = 'k'


    # Create the visualization
    x = []  # Scatterplot X values
    y = []  # Scatterplot Y Values
    c = []  # Scatterplot color values

    # Loop over the data a second time
    for event, fieldID, timestamp in dataset:
        x.append(timestamp)
        #y.append(series.index(fieldID))
        y.append(fieldID)
        c.append(colors[event])

    x,c = compresssingData(x,c,quan)
    x = [k - min(x) for k in x]
    plt.figure(figsize=(14,4))
    plt.title(kwargs.get('title', "Timeline Plot: {}".format(outpath)))
    plt.ylim((-1,len(series)))
    #plt.xlim((-1000, dataset[-1][0]+1000))
    plt.xlim(0, quan)
    plt.yticks(id_range, series)
    plt.scatter(x, 5*np.ones(len(x)), color=c, alpha=0.85, s=40)
    plt.xlabel('timestamp')
    plt.ylabel('fieldID')
    plt.legend(['red: press, blue: down, green: up'], loc='upper left')

    if outpath:
        plt.savefig(outpath, format='jpg', dpi=100)
        pass
        #return plt.savefig(outpath, format='jpg', dpi=1200)
    #plt.show()
    plt.close()
    #return plt

if __name__ == '__main__':
    colors = {12.0: 'r', 13.0: 'b', 14.0: 'g'}
    quan = 100; humanbot = 'bot'; start_id = -1; end_id = 10

    with open('{}.json'.format(humanbot), 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            reader = json.loads(line)
            reader = reader['keyboard']
            plotTimeline([
                (float(row[0]), row[1], row[2])
                for row in reader
            ], colors=colors, 
            outpath='{}_{:d}_15max/{}_{:03d}.jpg'.format(humanbot,quan,humanbot,i),
            start_id=start_id,
            end_id=end_id, 
            quan=quan)
            print('now at: {:d}'.format(i))
            #plt.show()
