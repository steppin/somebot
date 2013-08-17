#!/usr/bin/env python

from __future__ import division
import json
import sys
from PIL import Image, ImageDraw
# FIXME: wtf are you importing both StringIO.  Dummy.
import urllib, cStringIO
import StringIO


TILESIZE = 40


def usage():
    print 'Usage: {} PNG JSON [SPLATS]'.format(sys.argv[0])


#class TileReader():
    #"""Reads tiles..."""

    #def __init__(self, png):
        #self.png = png
        #tiles = Image.open('tiles.png')
        #speedpad = Image.open('speedpad.png')


class Map():
    """A preview generator for tagpro."""


    #tiles = TileReader('tiles.png')
    #speedpad = TileReader('speedpad.png')
    tiles = Image.open('tiles.png')
    speedpad = Image.open('speedpad.png')
    colormap = {
            'black': (0, 0, 0),
            'wall': (120, 120, 120),
            'tile': (212, 212, 212),
            'spike': (55, 55, 55),
            'button': (185, 122, 87),
            'powerup': (0, 255, 0),
            'gate': (0, 117, 0),
            'blueflag': (0, 0, 255),
            'redflag': (255, 0, 0),
            'speedpad': (255, 255, 0),
            'bomb': (255, 128, 0),
            'bluetile': (187, 184, 221),
            'redtile': (220, 186, 186)
    }



    def __init__(self, pngpath, jsonpath):
        if 'http' in pngpath:
            pfile = cStringIO.StringIO(urllib.urlopen(pngpath).read())
            png = Image.open(pfile)
        else:
            png = Image.open(pngpath)
        self.png = png
        self.pixels = png.load()

        if 'http' in jsonpath:
            jfile = urllib.urlopen(jsonpath)
            j = json.load(jfile)
        else:
            with open(jsonpath) as fp:
                j = json.load(fp)
        self.json = j



    def draw(self, (x, y), (i, j), tiles, preview, drawBackground=False, source=None):
        """draw square (x, y) from source on preview in spot (i, j)"""

        if drawBackground:
            im = tiles.crop((2 * TILESIZE, 2 * TILESIZE, 2 * TILESIZE + TILESIZE, 2 * TILESIZE + TILESIZE))
            preview.paste(im, (i * TILESIZE, j * TILESIZE))

        if not source:
            source = tiles

        x, y = x * TILESIZE, y * TILESIZE
        im = source.crop((x, y, x + TILESIZE, y + TILESIZE))
        preview.paste(im, (i * TILESIZE, j * TILESIZE), im)


    def _draw_tiles(self):
        speedpad = self.speedpad
        tiles = self.tiles
        preview = self.preview
        colormap = self.colormap
        pixels = self.pixels
        max_x, max_y = self.max_x, self.max_y
        draw = self.draw

        for i in range(max_x):
            for j in range(max_y):
                try:
                    color = pixels[i, j][:3]
                    if color == colormap['speedpad']:
                        a, b = 0, 0
                        draw((a, b), (i, j), tiles, preview, drawBackground=True, source=speedpad)
                    elif color == colormap['bomb']:
                        a, b = 6, 5
                        draw((a, b), (i, j), tiles, preview, drawBackground=True)
                    elif color == colormap['redtile']:
                        a, b = 3, 1
                        draw((a, b), (i, j), tiles, preview, drawBackground=True)
                    elif color == colormap['bluetile']:
                        a, b = 3, 2
                        draw((a, b), (i, j), tiles, preview, drawBackground=True)
                    elif color == colormap['spike']:
                        a, b = 2, 3
                        draw((a, b), (i, j), tiles, preview, drawBackground=True)
                    elif color == colormap['button']:
                        a, b = 2, 5
                        draw((a, b), (i, j), tiles, preview, drawBackground=True)
                    elif color == colormap['powerup']:
                        a, b = 7, 8
                        draw((a, b), (i, j), tiles, preview, drawBackground=True)
                    elif color == colormap['blueflag']:
                        a, b = 9, 0
                        draw((a, b), (i, j), tiles, preview, drawBackground=True)
                    elif color == colormap['redflag']:
                        a, b = 8, 0
                        draw((a, b), (i, j), tiles, preview, drawBackground=True)
                    elif color == colormap['tile']:
                        a, b = 2, 2
                        draw((a, b), (i, j), tiles, preview)
                except KeyError:
                    print "make this an error mkay"


    def _draw_splats(self, splats):
        im = self.preview
        with open(splats) as f:
            s = json.load(f)
        #draw = ImageDraw.Draw(self.preview)
        radius = 10
        opacity = 64
        color = {2: (0, 0, 255, opacity), 1: (255, 0, 0, opacity)}

        redsplats = Image.new("RGBA", (21, 21))
        c = ImageDraw.ImageDraw(redsplats, "RGBA")
        x, y = 10, 10
        c.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color[1])
        r, g, b, a = redsplats.split()
        redsplats = Image.merge("RGB", (r, g, b))
        redmask = Image.merge("L", (a,))

        bluesplats = Image.new("RGBA", (21, 21))
        c = ImageDraw.ImageDraw(bluesplats, "RGBA")
        x, y = 10, 10
        c.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color[2])
        r, g, b, a = bluesplats.split()
        bluesplats = Image.merge("RGB", (r, g, b))
        bluemask = Image.merge("L", (a,))

        for splat in s:
            (x, y) = (splat['x']-10, splat['y']-10)
            t = splat['t']
            if t == 1:
                im.paste(redsplats, (x, y), redmask)
            elif t == 2:
                im.paste(bluesplats, (x, y), bluemask)


    def _draw_rest(self):
        speedpad = self.speedpad
        tiles = self.tiles
        preview = self.preview
        colormap = self.colormap
        pixels = self.pixels
        max_x, max_y = self.max_x, self.max_y
        draw = self.draw
        png = self.png

        green = []
        try:
            for point, state in self.json['fields'].iteritems():
                if state['defaultState'] == 'on':
                    x, y = point.split(',')
                    green.append((int(x), int(y)))
        except KeyError:
            pass

        for i in range(max_x):
            for j in range(max_y):
                try:
                    color = pixels[i, j][:3]
                    if color == colormap['black']:
                        preview.paste((0, 0, 0, 255), (i * TILESIZE, j * TILESIZE, i * TILESIZE + TILESIZE, j * TILESIZE + TILESIZE))
                    elif color == colormap['wall']:
                        north, south, west, east = [False]*4
                        if j > 0:
                            north = pixels[i, j-1][:3] == colormap['wall']
                        if j < png.size[1] - 1:
                            south = pixels[i, j+1][:3] == colormap['wall']
                        if i > 0:
                            west = pixels[i-1, j][:3] == colormap['wall']
                        if i < png.size[0] - 1:
                            east = pixels[i+1, j][:3] == colormap['wall']
                        if north:
                            if south:
                                if east:
                                    if west:
                                        a, b = 4, 4
                                    else:
                                        a, b = 0, 4
                                else:
                                    if west:
                                        a, b = 7, 4
                                    else:
                                        a, b = 4, 2
                            else:
                                if east:
                                    if west:
                                        a, b = 4, 8
                                    else:
                                        a, b = 2, 8
                                else:
                                    if west:
                                        a, b = 6, 8
                                    else:
                                        a, b = 0, 6
                        else:
                            if south:
                                if east:
                                    if west:
                                        a, b = 4, 0
                                    else:
                                        a, b = 2, 0
                                else:
                                    if west:
                                        a, b = 6, 0
                                    else:
                                        a, b = 0, 2
                            else:
                                if east:
                                    if west:
                                        a, b = 2, 4
                                    else:
                                        a, b = 8, 6
                                else:
                                    if west:
                                        a, b = 9, 6
                                    else:
                                        a, b = 0, 0
                        draw((a, b), (i, j), tiles, preview)
                    elif color == colormap['speedpad']:
                        a, b = 0, 0
                        draw((a, b), (i, j), tiles, preview, drawBackground=False, source=speedpad)
                    elif color == colormap['bomb']:
                        a, b = 6, 5
                        draw((a, b), (i, j), tiles, preview, drawBackground=False)
                    elif color == colormap['spike']:
                        a, b = 2, 3
                        draw((a, b), (i, j), tiles, preview, drawBackground=False)
                    elif color == colormap['button']:
                        a, b = 2, 5
                        draw((a, b), (i, j), tiles, preview, drawBackground=False)
                    elif color == colormap['powerup']:
                        a, b = 7, 8
                        draw((a, b), (i, j), tiles, preview, drawBackground=False)
                    elif color == colormap['blueflag']:
                        a, b = 9, 0
                        draw((a, b), (i, j), tiles, preview, drawBackground=False)
                    elif color == colormap['redflag']:
                        a, b = 8, 0
                        draw((a, b), (i, j), tiles, preview, drawBackground=False)
                    elif color == colormap['gate']:
                        if (i, j) in green:
                            a, b = 10, 2
                        else:
                            a, b = 10, 1
                        draw((a, b), (i, j), tiles, preview)
                except KeyError:
                    print "make this an error mkay"



    def preview(self, splats=None):
        self.max_x, self.max_y = max_x, max_y = self.png.size
        self.preview = Image.new('RGBA', (max_x*TILESIZE, max_y*TILESIZE))

        self._draw_tiles()
        if splats:
            self._draw_splats(splats)
        self._draw_rest()

        #preview.resize((preview.size[0]//10, preview.size[1]//10)).save('temp.png')
        temp = StringIO.StringIO()
        self.preview.save(temp, 'PNG')
        return temp


def main():
    if len(sys.argv) < 3:
        usage()
        return 1

    pngpath = sys.argv[1]
    jsonpath = sys.argv[2]
    splats = sys.argv[3] if len(sys.argv) > 3 else None

    map_ = Map(pngpath, jsonpath)
    preview = map_.preview(splats=splats)

    print "saving..."
    with open('temp.png', 'w') as f:
        f.write(preview.getvalue())


if '__main__' == __name__:
    status = main()
    sys.exit(status)
