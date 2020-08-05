import gdal
import sys
import ogr, osr
import os
import numpy as np


def array2raster(newRasterfn, array):
    cols = array.shape[1]
    rows = array.shape[0]

    driver = gdal.GetDriverByName('GTiff')
    gdal.SetConfigOption('GDAL_TIFF_INTERNAL_MASK', 'YES')
    ops = ["INTERLEAVE=BAND", "TILED=YES", "ALPHA=YES"]
    outRaster = driver.Create(newRasterfn, cols, rows, array.shape[2], gdal.GDT_Byte, ops)
    for band in range(outRaster.RasterCount):
        outband = outRaster.GetRasterBand(band + 1)
        outband.WriteArray(array[:, :, band])
        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromEPSG(4326)
        outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()
    del array


# Open dataset
dataset = gdal.Open('test0.TIF', gdal.GA_Update)

print(dataset.GetMetadata())

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
        stats = src_band.GetStatistics(True, True)
        print("Min \t{} Max\t{} Mean \t{} Stddev \t{}".format(*stats))
        # print("Nodata ", nodataval)
        # print("Scale ", src_band.GetScale())
        # print("Unit type ", src_band.GetUnitType())
        # print("ColorTable ", src_band.GetColorTable())


        src_band = src_band.ReadAsArray()
        src_band[src_band == nodataval] = 255

        if (band == 0):
            alpha = np.zeros_like(band)
            print(alpha.shape)
            output_image.append(alpha)

        output_image.append(src_band)
        del src_band

except RuntimeError as e:
    print("Exception ", e)

# Close dataset
dataset = None

# Write the output_image
output_image = np.stack(output_image, axis=2)
array2raster("test00.TIF", output_image)
