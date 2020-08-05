import gdal
import sys
import ogr, osr
import os

# Open dataset
dataset = gdal.Open('test0.TIF', gdal.GA_Update)

print(dataset.GetMetadata())

# Get Raster band
gdal.UseExceptions()

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
        print("Nodata ", nodataval)
        print("Scale ", src_band.GetScale())
        print("Unit type ", src_band.GetUnitType())
        print("ColorTable ", src_band.GetColorTable())
except RuntimeError as e:
    print("Exception ", e)

# Close dataset
dataset = None