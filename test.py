import adpthr_py
from timeit import default_timer as timer
from osgeo import gdal
import numpy as np
# parameters for testing


#information of the module
print("adpthr_py version: ", adpthr_py.__version__)
print(dir(adpthr_py))
print("Note: the input raster only can be integer, float, or byte")
print("Note: only the first band is used")
#read input data
#get the spatial reference from gdal
def read_tiff_image(file_path):
    # Open the TIFF file
    dataset = gdal.Open(file_path, gdal.GA_ReadOnly)

    if dataset is None:
        print("Failed to open the TIFF file.")
        return None

    # Read the image data
    image = dataset.ReadAsArray()
    geo_transform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()

    # Close the dataset
    dataset = None

    return image,geo_transform,projection




#write output

def write_tiff(output_path, data, geo_transform, projection):
    # Get the dimensions of the data
    height, width = data.shape

    # Create a new GeoTIFF file
    driver = gdal.GetDriverByName("GTiff")
    output_dataset = driver.Create(output_path, width, height, 1, gdal.GDT_Byte)

    # Set the geotransform and projection
    output_dataset.SetGeoTransform(geo_transform)
    output_dataset.SetProjection(projection)

    # Write the data to the band
    output_band = output_dataset.GetRasterBand(1)
    output_band.WriteArray(data)

    # Close the dataset
    output_dataset = None

def main():
    # Specify the path to your TIFF image
    tiff_path = r"C:\Users\leiwang\workspace\images\sar_clp.tif"
    output_img = r"C:\Users\leiwang\workspace\images\segmented.tif"

    # Read the TIFF image using GDAL
    image,geo_transform,projection = read_tiff_image(tiff_path)
    # image is stretched to 0~255 to match the assumed value range by the cpp library
    #remove those nan and -9999 values
    mask = ~np.isnan(image) & (image != -9999)
    filtered = image[mask]
    minValue = np.min(filtered)
    maxValue = np.max(filtered)
    print(f"Strech the image from {minValue},{maxValue} to 0, 255")
    image[~mask] = minValue
    image_uint8 = (255 * ((image - minValue) / (maxValue- minValue))).astype(np.uint8)
    
    
    shape = image.shape
        
    dtpye = np.int16
    output = np.empty(shape,dtpye)

    #processing data
    start = timer()

    adpthr_py.AdaptiveThreshold(image_uint8,output,percent=100, region_size = 100, debug = False, smooth_his = True)
    end = timer()
    print("Time lapse: ",end - start, " seconds.") # Time in seconds, e.g. 5.38091952400282    
    print("Writing to ouptput")
    write_tiff(output_img, output, geo_transform, projection)
    dataset = gdal.Open(output_img,gdal.GA_Update)
    dataset.SetGeoTransform(geo_transform)
    dataset.SetProjection(projection)


if __name__ == "__main__":
    main()