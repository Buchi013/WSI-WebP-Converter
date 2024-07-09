import os #https://docs.python.org/3/library/os.html
import tempfile as tf #https://docs.python.org/3/library/tempfile.html
import argparse #https://docs.python.org/3/library/argparse.html
import pyvips #https://pypi.org/project/pyvips/
import timeit #https://docs.python.org/3/library/timeit.html
import tifftools #https://pypi.org/project/tifftools/
import json #https://docs.python.org/3/library/json.html

#https://openslide.org/api/python/
#TODO Add your Openslide Binaries Path here:
OPENSLIDE_PATH = os.getcwd()+"/openslide-bin-4.0.0.3-webp-windows-x64/bin"
if hasattr(os, 'add_dll_directory'):
    with os.add_dll_directory(OPENSLIDE_PATH):
        import openslide as osl

input_path = ""
output_path = ""
logs_path = ""
script_path = ""
compression_types = ['jpeg','webp'] #supported compression schemes
tile_width = 240
tile_height = 240
jpeg_quality = 91 #TODO choose jpeg Q setting
webp_quality = 91 #TODO choose webp Q setting

def process_path(path, compression, lossless):
    if os.path.isfile(path):
        #create temporary directory for splitting/stitching and convert the input file
        with tf.TemporaryDirectory(dir=script_path) as temp_dir:
            convert_file(path, temp_dir, compression, lossless)
        return 
    for p in os.listdir(path):
        process_path(os.path.join(path, p), compression, lossless)
    return

def convert_file(filepath, temp_dir, compression, lossless):
    """Converts an input file in SVS/TIFF/TIF format to a svs-like bigTIFF-file with specified compression type, logging conversion time

    Args:
        filepath (string): path of file to be converted
        temp_dir (string): path of temporary directory for intermediate image storage
        compression (string): compression type to use
        lossless (bool): currently unused, use lossless modes if True
    """
    
    print("Converting {} with {}-compression".format(filepath, compression))
    starttime = timeit.default_timer()

    #Open base picture for image pyramid creation with pyvips (level 0)
    image_l0 = pyvips.Image.tiffload(filepath, access='sequential', page=0)
    input_filename = os.path.basename(filepath).split(".")[0]
    
    #Building full pyramid (until the entire level fits in one tile of tile_width x tile_height) with downsample factor 2
    pyramid_filepath = temp_dir + "/" + input_filename + "_" + compression + ".tiff"
    match(compression):
        case "webp":
            image_l0.tiffsave(pyramid_filepath, compression="webp", Q=webp_quality, tile=True, lossless=lossless, bigtiff=True, pyramid=True, tile_width=tile_width, tile_height=tile_height)
        case "jpeg":
            image_l0.tiffsave(pyramid_filepath, compression="jpeg", Q=jpeg_quality, tile=True, lossless=lossless, bigtiff=True, pyramid=True, tile_width=tile_width, tile_height=tile_height)
        case "lzw":
            image_l0.tiffsave(pyramid_filepath, compression="lzw", tile=True, lossless=lossless, bigtiff=True, pyramid=True, tile_width=tile_width, tile_height=tile_height)
        
    #read number of levels + ImageDescription
    input_slide = osl.open_slide(filepath)
    input_slide_level_count = input_slide.level_count
    image_description = input_slide.properties.get('tiff.ImageDescription')

    #Split Input file (to later extract thumbnail, macro, label)
    splitpath_prefix = temp_dir+"/" #temporary directory
    input_split_prefix = splitpath_prefix + input_filename + "_split"
    tifftools.tiff_split(filepath, prefix = input_split_prefix,overwrite=True)

    #split compressed full image pyramid
    compressed_prefix = splitpath_prefix + input_filename + "_" + compression + "_split"
    tifftools.tiff_split(pyramid_filepath, prefix=splitpath_prefix + input_filename + "_" + compression + "_split", overwrite=True)

    #Load and convert thumbnail, store in temporary folder
    image_l1 = pyvips.Image.tiffload(filepath, access='random', page=1) #access type sequential
    image_l1.tiffsave(splitpath_prefix + input_filename + "_" + compression + "_thumbnail.tiff", compression = compression, tile=False, bigtiff=True, pyramid=False)

    #Collect tiffs to build complete compressed file:
    level_list = []
    level_list.append(compressed_prefix+"aaa.tif") #Base image
    level_list.append(splitpath_prefix + input_filename + "_" + compression + "_thumbnail.tiff") #thumbnail

    #tifftools.tiff_split saves split images as prefixaaa.tif (level 0), prefixaab.tif (level 1), ...
    #we append every second image level to mimic scanner behaviour since libvips uses downsample factor 2, desired (scanner) downsample factor is 4 expcept for the lowest resolution level (downsample factor 2)
    #assumes downsample factors 4-4-....-4-2
    letter = "c";
    for i in range(1, input_slide_level_count-1):
        level_list.append(compressed_prefix+"aa"+letter+".tif")
        letter = chr(ord(letter[0])+2)
    letter = chr(ord(letter[0])-1)
    level_list.append(compressed_prefix+"aa"+letter+".tif")
    
    level_list.append(input_split_prefix+"aa"+chr(ord("a"[0])+input_slide_level_count+1)+".tif") #label
    level_list.append(input_split_prefix+"aa"+chr(ord("a"[0])+input_slide_level_count+2)+".tif") #macro

    #Concatenate the collected tiff files
    match(compression):
        case "webp":
            compressed_complete_path = output_path+"/"+input_filename+"_"+compression+str(webp_quality)+"_converted.tiff"
        case "jpeg":
            compressed_complete_path = output_path+"/"+input_filename+"_"+compression+str(jpeg_quality)+"_converted.tiff"
        case "lzw":
            compressed_complete_path = output_path+"/"+input_filename+"_"+compression+"_converted.tiff"
    tifftools.tiff_concat(level_list, output=compressed_complete_path, overwrite=True)

    #We keep the original ImageDescription of Level 0 for transparency but append a compression property
    match(compression):
        case "webp":
            tifftools.tiff_set(compressed_complete_path, overwrite=True, setlist=[('ImageDescription', image_description+"|Compression="+compression+" Q="+str(webp_quality))])
        case "jpeg":
            tifftools.tiff_set(compressed_complete_path, overwrite=True, setlist=[('ImageDescription', image_description+"|Compression="+compression+" Q="+str(jpeg_quality))])
        case "lzw":
            tifftools.tiff_set(compressed_complete_path, overwrite=True, setlist=[('ImageDescription', image_description+"|Compression="+compression)])
    
    conversion_time = timeit.default_timer() - starttime
    print("Conversion took {}s".format(conversion_time))
    
    stats = {"conversion_time_in_s": conversion_time}
    with open(logs_path+os.path.basename(compressed_complete_path).split(".")[0]+"_stats.json","w") as out_file:
            json.dump(stats, out_file, ensure_ascii= False, indent=4) 
    return

def main():
    global input_path, output_path, tile_height, tile_width, logs_path, script_path
    
    parser = argparse.ArgumentParser(description='Convert aperio svs/tiff/tif files to webp/jpeg-compressed svs-like bigTiff')
    parser.add_argument('-i', '--input', help='a path to a file/directory to be processed', dest='input', nargs=1, metavar='INPUT', type=str)
    parser.add_argument('-o', '--out', help='output directory', nargs=1, dest='output', metavar='DEST', type=str)
    parser.add_argument('-tw', help='tile width (default: 240)', nargs=1, metavar='WIDTH', dest='tw', default=256, type=int)
    parser.add_argument('-th', help='tile height (default: 240)', nargs=1, metavar='HEIGHT', dest='th', default=256, type=int)
    parser.add_argument('-c', help='compression type (default: webp, options: webp, jpeg, all)', dest='compression', metavar='COMP', type=str)
    
    args = parser.parse_args()

    script_path = os.path.dirname(os.path.abspath(__file__))
    logs_path = script_path+r"/Logs/"
    
    #input handling
    input_path = script_path+"/Input" if args.input == None else args.input[0]
    output_path = script_path+"/Output" if args.output == None else args.output[0]
    compression = 'webp' if args.compression == None else args.compression
    tile_height = args.th
    tile_width = args.tw
    
    #process input path based on compression settings
    if(compression in compression_types):
        process_path(input_path, compression, False)
    else:
        if(compression=="all"):
            for c in compression_types:
                process_path(input_path, c, False)
        else:
            print("Compression type not supported")
    return

if __name__ == "__main__":
    main()