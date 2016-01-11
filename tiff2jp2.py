#!/usr/bin/env python2.7

import skimage.io as io
import scipy.misc
import glymur
import time
from libxmp import XMPFiles
import uuid
import sys

def readtiff(fnt):
    #read bitmap from tiff
    bmpo = io.imread(fnt, plugin='tifffile')
    return bmpo

def writejp2(bmp, fjp2):
    #write bitmap to jp2 image 
    jp2 = glymur.Jp2k(fjp2, 'wb')
    jp2[:] = bmp
    return

def readmetadata(fname):
    #read metadata from tiff
    xf = XMPFiles()
    xf.open_file(file)
    xmp = xf.get_xmp()

def writemetadata(fname):
    #append metadata in uuid box
    xmp_uuid = uuid.UUID('be7acfcb-97a9-42e8-9c71-999491e3afac')
    box = glymur.jp2box.UUIDBox(xmp_uuid, str(xmp))
    jp2.append(box)

def resizebmp(bmpi, L):
    #resize bitmap (thumbnail)
    if bmpi.shape[0] > bmpi.shape[1]:
        i0 = int(L)
        i1 = int(L * bmpi.shape[1] / bmpi.shape[0])
    else:
        i0 = int(L * bmpi.shape[0] / bmpi.shape[1])
        i1 = int(L)
    bmpo = scipy.misc.imresize(bmpi, (i0, i1), interp='cubic')
    return bmpo

def tiff2jp2(fnt):
        fnj = fnt.split(".tif")[0]+".jp2"
        bmp = readtiff(fnt)
        writejp2(bmp, fnt.split(".")[0]+".jp2")

def tiff2jp2thumb(fnt, bmp, L):
        fnjt = fnt.split(".tif")[0]+"_thumb.jp2"
        bmpt = resizebmp(bmp, L)
        writejp2(bmpt, fnjt)


#################################################################
if __name__ == "__main__":

    start = time.time()
    nfiles = 0

    for fnt in sys.argv[1:]:

        fnj = "{}.jp2".format(fnt.split('.tif')[0])
    
        #read tiff bitmap
        bmp = readtiff(fnt)
        writejp2(bmp, fnj)
        bmpt = resizebmp(bmp, 200) 
        writejp2(bmpt, fnj+"_thumb")
       
        #read metadata from tiff
        #readmetadata(file)
    
        #append metadata in uuid box
        #writemetadata(fname)
    
        #resize bitmap (thumbnail)
        #savethumbnail()

        nfiles += 1

    end = time.time()

    print "Time:{:.0e}s Files:{} Time/Files:{:.1e}s/file".format(end-start, nfiles, (end-start)/nfiles)
