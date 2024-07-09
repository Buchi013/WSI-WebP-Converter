import cv2 #https://github.com/opencv/opencv-python
import numpy as np #https://numpy.org/doc/stable/
import colormath, colormath.color_conversions, colormath.color_diff, colormath.color_objects #https://github.com/gtaylor/python-colormath/tree/master
import random
import matplotlib.pyplot as plt #https://matplotlib.org/stable/
import json #https://docs.python.org/3/library/json.html
import os #https://docs.python.org/3/library/os.html
from tiffslide import TiffSlide #https://github.com/Bayer-Group/tiffslide

#https://stackoverflow.com/questions/76147221/trying-to-fix-a-numpy-asscalar-deprecation-issue (deprecation fix für colormath)
def patch_asscalar(a):
    return a.item()
setattr(np, "asscalar", patch_asscalar)

#TODO Add your Openslide Binaries Path here
OPENSLIDE_PATH = os.getcwd()+"/openslide-bin-4.0.0.3-webp-windows-x64/bin"
if hasattr(os, 'add_dll_directory'):
    with os.add_dll_directory(OPENSLIDE_PATH):
        import openslide as osl

logs_path = ""

#Input: path to reference image (RAW), comparsion_folder: folder with converter results from reference image, patch_size: Delta E calculation for patch_size x patch_size samples
#tissue: do you want to calculate Delta E for background or for tissue, num_patches: how many patches DeltaE is calculated for
def deltaE(reference, comparison_folder, patch_size, tissue, num_patches):
    
    patch_coordinates = []

    #mask creation based on low-resolution level 3 of reference (RAW) image
    reference_image = TiffSlide(reference)
    width, height = reference_image.level_dimensions[3]
    reference_thumbnail_asarray = np.asarray(reference_image.read_region((0,0),3,(width,height)))
    #plt.imshow(reference_thumbnail_asarray, interpolation="nearest")
    #plt.show()

    #convert to HSV color space for image segmentation https://www.kaggle.com/code/sanikamal/image-segmentation-using-color-spaces
    hsv_reference = cv2.cvtColor(reference_thumbnail_asarray, cv2.COLOR_RGB2HSV)
    
    #HSV thresholding
    lower_bound = np.array([0,15,15])
    upper_bound = np.array([255,255,255])
    kernel = np.ones((3,3), np.uint8)

    #https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html
    blurred_reference = cv2.GaussianBlur(hsv_reference,(5,5),0)

    #close/fill mask
    mask = cv2.inRange(blurred_reference, lower_bound, upper_bound) 
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    #tissue_mask = cv2.bitwise_and(reference_thumbnail_asarray,reference_thumbnail_asarray,mask=mask) 
    #plt.imshow(tissue_mask, interpolation='nearest')
    #plt.show()

    #find num_patches reference patches and store coordinates
    for i in range(num_patches):
        patch_x, patch_y = find_patch(mask,patch_size,tissue)
        
        #adjust positions for base image
        patch_x=(patch_x*32)
        patch_y=(patch_y*32)

        patch_coordinates.append((patch_x,patch_y))

    #iterate over every file in the comparison folder and calculate deltaE
    for f in os.listdir(comparison_folder):
        
        values = []
        #load and compare all patches with patch_coordinates
        for (patch_x,patch_y) in patch_coordinates:
            reference_patch_image = TiffSlide(reference)
            reference_patch_asarray = np.asarray(reference_patch_image.read_region((patch_y,patch_x),0,(patch_size*32,patch_size*32)))
            #plt.imshow(reference_patch_asarray, interpolation='nearest')
            #plt.show()
            #del reference_patch_image
            
            comparison_image = osl.open_slide(os.path.join(comparison_folder,f))
            comparison_patch = comparison_image.read_region((patch_y,patch_x),0,(patch_size*32,patch_size*32))
            comparison_patch_asarray = np.asarray(comparison_patch)
            #plt.imshow(comparison_patch, interpolation='nearest')
            #plt.show()
            #del comparison_image

            #calculate comparison, store deltaE values
            output = np.empty((patch_size*32,patch_size*32))

            #Calculate Delta E CMC for selected patch
            for x in range(patch_size*32):
                for y in range(patch_size*32):
                    ref_r,ref_b,ref_g= reference_patch_asarray[x,y]
                    ref_pixel = colormath.color_objects.AdobeRGBColor(ref_r,ref_b,ref_g,is_upscaled=True)
                    ref_pixel_lab = colormath.color_conversions.convert_color(ref_pixel, colormath.color_objects.LabColor)
                    comp_r,comp_b,comp_g,_ = comparison_patch_asarray[x,y]
                    comp_pixel = colormath.color_objects.AdobeRGBColor(comp_r,comp_b,comp_g,is_upscaled=True)
                    comp_pixel_lab = colormath.color_conversions.convert_color(comp_pixel, colormath.color_objects.LabColor)
                    output[x,y] = colormath.color_diff.delta_e_cmc(ref_pixel_lab,comp_pixel_lab)
                    values.append(output[x,y])

        #save mean, median, deltaE_values to json
        if(tissue):
            stats = {
                "deltaE_mean": np.mean(values),
                "deltaE_median": np.median(values),
                "deltaE_values": values,     
                }
        else:
            stats = {
                "background_deltaE_mean": np.mean(values),
                "background_deltaE_values": values,
                }
        with open(logs_path+os.path.basename(f).split(".")[0]+"_deltaE.json","w") as out_file:
            json.dump(stats, out_file, ensure_ascii= False, indent=4) 
        
    return

#tissue=False -> find background patch
def find_patch(mask, patch_size, tissue):
    height, width = mask.shape

    while(True):
        x = random.randint(0, height - patch_size)
        y = random.randint(0, width - patch_size)

        patch = mask[x:x+patch_size, y:y+patch_size]

        if(tissue):
            if np.all(patch==255):
                return (x,y)
        else:
            if np.all(patch==0):
                return (x,y)

def main():
    global logs_path
    script_path = os.path.dirname(os.path.abspath(__file__))
    logs_path = script_path+r"/Logs/"

    #TODO add your reference file and comparison folder here
    deltaE("PATH/TO/REFERENCE FILE", "PATH/TO/COMPARISON FOLDER", 15, True, 3)
    return

if __name__ == "__main__":
    main()