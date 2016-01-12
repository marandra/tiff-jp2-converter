tiff-jp2-converter
==================

Python converter from TIFF to JPEG2000, using external libraries

Description
-----------
Converts TIFF images to JP2 images, and also generates JP2 thumbnails.
It uses \ **glymur** module (python wrapper to the **openjpeg** library)
to write JP2 images. Can convert images from a directory or individualy.
Generates thumbnails of the images.

Copying of metadata possible but not implemented at the moment.

Usage
-----
Set internally the image location. Receives list of TIFF images to
convert.

Dependencies
------------
-  **openjpeg** library for reading and writing images in jpeg2000
   format
-  **skimage.io** for tiff reading
-  tifffile drive (in python or as a shared library in C)
-  **glymur** bindings for python to openjpeg libraries
-  **libxmp** module for parsing, manipulating, and serializing XMP
   (Extensible Metadata Platform) data. http://www.spacetelescope.org/static/projects/python-xmp-toolkit/docs/reference.html
-  **exempi**  is an implementation of XMP. Version 2.x is based on Adobe XMP SDK \ http://libopenraw.freedesktop.org/wiki/Exempi/
-  **uuid** UUID objects according to RFC 4122 https://docs.python.org/2/library/uuid.html

Performance
-----------
Execution time for 100 images in a directory is about **100s**

Validation
----------
Original TIFF and converted JP2 images are read using Matlab's imread().
The difference between both bitmaps is null.

>> imagetiff = imread
('b0bCDME-0007\_wN09\_s4\_z1\_t1\_cDAPI\_u001.tif');

>> imagejp2 =
imread ('b0bCDME-0007\_wN09\_s4\_z1\_t1\_cDAPI\_u001.jp2');

>> isequal(imagetiff, imagejp2) ans = 1 >> %interpretation: 1=equal,
0=non-equal

(Metadata reading/writing yet to be implemented)

