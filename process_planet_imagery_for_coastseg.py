from osgeo import gdal, osr
import osgeo.gdalnumeric as gdn
import geopandas as gpd
import numpy as np
from PIL import Image
import os
import glob
import shutil
from shutil import copyfile
import matplotlib.pyplot as plt
import argparse

def format_planet_downloads(in_folder,
                            out_folder):
    """
    Organizes downloaded Planet geotiffs into CoastSeg format
    data
        PS
            ms
            udm2
            meta
    inputs:
    in_folder (str): path to where the images got downloaded to
    out_folder (str): path to coastseg/data/site/PS
    """
    ms_geotiffs = glob.glob(in_folder + '/*AnalyticMS_clip.tif')
    udm2_geotiffs = glob.glob(in_folder + '/*udm2_clip.tif')
    meta_xmls = glob.glob(in_folder + '/*metadata_clip.xml')

    ps_dir = os.path.join(out_folder, 'PS')
    ms_dir = os.path.join(out_folder, 'PS', 'ms')
    udm2_dir = os.path.join(out_folder, 'PS', 'udm2')
    meta_dir = os.path.join(out_folder, 'PS', 'meta')
    new_dirs = [ps_dir, ms_dir, udm2_dir, meta_dir]
    for d in new_dirs:
        try:
            os.mkdir(d)
        except:
            pass

    for i in range(len(ms_geotiffs)):
        ##get ms, udm2 files
        ms = ms_geotiffs[i]
        udm2 = udm2_geotiffs[i]

        ##get metadata
        src = gdal.Open(ms)
        proj = osr.SpatialReference(wkt=src.GetProjection())
        epsg = proj.GetAttrValue('AUTHORITY',1)
        width, height = src.RasterXSize, src.RasterYSize
        
        ##get basenames
        ms_basename = os.path.basename(ms)
        ms_no_ext = os.path.splitext(ms_basename)[0]
        udm2_basename = os.path.basename(udm2)

        ##make new paths
        new_ms = os.path.join(ms_dir, ms_basename)
        new_udm2 = os.path.join(udm2_dir, udm2_basename)
        new_meta = os.path.join(meta_dir, ms_no_ext+'.txt')

        ##copy to new paths
        shutil.copyfile(ms, new_ms)
        shutil.copyfile(udm2, new_udm2)

        ##write metadata to txt file
        meta_file = open(new_meta, "w")
        lines = ['filename\t'+ms_basename+'\n',
                 'epsg\t'+epsg+'\n',
                 'im_width\t'+str(width)+'\n',
                 'im_height\t'+str(height)+'\n']
        meta_file.writelines(lines)
        meta_file.close()
    
    ##delete original download folder
    #shutil.rmtree(os.path.dirname(in_folder))
    return ms_dir
                            
def make_planet_jpgs(planet_folder, jpg_folder):
    """
    Converts Planet ms imagery to rgb jpeg and nir jpeg
    inputs:
    planet_folder (str): path to coastseg/data/site/PS/ms
    jpg_folder (str): path to coastseg/data/site/jpg_files
    """
    preprocessed_folder = os.path.join(jpg_folder, 'preprocessed')
    RGB_folder = os.path.join(jpg_folder, 'preprocessed', 'RGB')
    NIR_folder = os.path.join(jpg_folder, 'preprocessed', 'NIR')
    dirs = [jpg_folder, preprocessed_folder, RGB_folder, NIR_folder]
    for d in dirs:
        try:
            os.mkdir(d)
        except:
            pass
    
    ##loop over all ms geotiffs in PS folder
    for tif in glob.glob(planet_folder + '/*.tif'):
        ##making new names and paths for out images, YYYY-MM-DD-hh-mm-ss_RGB_PS.jpg
        name = os.path.splitext(os.path.basename(tif))[0]
        year = name[0:4]
        month = name[4:6]
        day = name[6:8]
        hour = name[9:11]
        minute = name[11:13]
        second = name[13:15]
        date = year + '-' + month + '-' + day + '-' + hour + '-' + minute + '-' + second
        name_RGB = date + '_RGB_PS.jpg'
        name_NIR = date + '_NIR_PS.jpg'
        out_RGB = os.path.join(RGB_folder, name_RGB)
        out_NIR = os.path.join(NIR_folder, name_NIR)
        

        ##open tif and separate NIR from RGB
        raster = gdal.Open(tif)
        bands = [raster.GetRasterBand(i) for i in range(1, raster.RasterCount+1)]
        arr = np.array([gdn.BandReadAsArray(band) for band in bands]).astype('float32')
        arr = np.transpose(arr, [1,2,0])

        blue = arr[:,:,0]
        green = arr[:,:,1]
        red = arr[:,:,2]
        nir_arr = arr[:,:,3]
        
        def rescale(arr):
            arr_min = arr.min()
            arr_max = arr.max()
            return (arr - arr_min) / (arr_max - arr_min)

        arr = 255.0 * rescale(arr)

        rgb_arr = np.array([red,green,blue])
        rgb_arr = np.transpose(rgb_arr, [1,2,0])
        rgb_arr = 255.0*rescale(rgb_arr)

        nir_arr = 255.0*rescale(nir_arr)

        rgb_img = Image.fromarray(rgb_arr.astype('uint8'), 'RGB')
        nir_img = Image.fromarray(nir_arr.astype('uint8')).convert('L')

        rgb_img.save(out_RGB)
        nir_img.save(out_NIR)

        ##clean up
        raster = None
        rgb_arr = None
        nir_arr = None
        rgb_img = None
        nir_img = None

        return jpg_folder


        
