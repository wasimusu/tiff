import gdal
import sys
import ogr, osr
import os
import numpy as np
import cv2


def mask_image(image, nodataval):
    # 0 for full transparency, 255 for fully opaque
    alpha = 0
    for i in range(3):
        layer = image[:, :, i]
        if i == 0:
            alpha = layer.copy()
            alpha[layer == nodataval] = 0
            alpha[layer != nodataval] = 255
        layer[layer == nodataval] = 255

    row, col, _ = image.shape
    row, col, _ = image.shape
    image = np.dstack((image, alpha))
    return image

def array2raster(newRasterfn, array):
    cols = array.shape[1]
    rows = array.shape[0]

    driver = gdal.GetDriverByName('GTiff')
    gdal.SetConfigOption('GDAL_TIFF_INTERNAL_MASK', 'YES')
    ops = ["COMPRESS=LZW", "INTERLEAVE=BAND", "TILED=YES", "ALPHA=YES"]
    outRaster = driver.Create(newRasterfn, cols, rows, array.shape[2], gdal.GDT_Byte, ops)
    print("Output band size ", outRaster.RasterCount)
    for band in range(outRaster.RasterCount):
        outband = outRaster.GetRasterBand(band + 1)
        outband.WriteArray(array[:, :, band])
        outband.FlushCache()
    del array


# Open dataset
dataset = gdal.Open('test0.TIF', gdal.GA_Update)

# Get Raster band
gdal.UseExceptions()

output_image = []
try:
    source_band = dataset.GetRasterBand(1)
    print("Raster bands ", dataset.RasterCount)
    for band in range(dataset.RasterCount):
        src_band = dataset.GetRasterBand(band + 1)
        if src_band is None:
            continue

        nodataval = src_band.GetNoDataValue()
        nodataval = 0 if nodataval is None else nodataval
        stats = src_band.GetStatistics(True, True)
        print("Min \t{} Max\t{} Mean \t{} Stddev \t{}".format(*stats))
        print("Nodata ", nodataval)

        src_band = src_band.ReadAsArray()
        # src_band[src_band == nodataval] = 255
        #
        # if (band == 0):
        #     ref_band = dataset.GetRasterBand(1).ReadAsArray()
        #     alpha = np.zeros_like(ref_band)
        #     alpha[ref_band == nodataval] = 255
        #     alpha[ref_band != nodataval] = 0
        #     output_image.append(alpha)

        output_image.append(src_band)
        del src_band

except RuntimeError as e:
    print("Exception ", e)

# Close dataset
dataset = None
# Write the output_image
output_image = np.stack(output_image, axis=2)
output_image = mask_image(output_image, nodataval)
array2raster("tested.TIF", output_image)
