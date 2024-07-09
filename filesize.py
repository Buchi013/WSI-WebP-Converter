import os #https://docs.python.org/3/library/os.html
import matplotlib.pyplot as plt #https://matplotlib.org/stable/
import numpy as np #https://numpy.org/doc/stable/

#group files labeled with same prefix SlideX where X is a number starting from 1 to num_slides from a given folder with their respective filesize in Megabyte
def group_data_byte(folder, num_slides):
    entries = [] #list of all grouped slides as dictionaries

    for i in range (1,num_slides+1):
        current_prefix = "Slide"+str(i)
        sizes = {}
        
        for f in os.listdir(folder):
            if(str(f).startswith(current_prefix+"_")):
                if("jp2k" in str(f)):
                    sizes[current_prefix+ " (Scanner) JPEG 2000 Q=70"] = os.path.getsize(os.path.join(folder,f))/(1024*1024)
                if("converted" in str(f) and "webp" in str(f)):
                    webp_string = str(f).split("webp")[1]
                    webp_quality = webp_string.split("_")[0]
                    sizes[current_prefix + " (Converter) WebP Q="+str(webp_quality)] = os.path.getsize(os.path.join(folder,f))/(1024*1024)
                if("converted" in str(f) and "jpeg" in str(f)):
                    jpeg_string = str(f).split("jpeg")[1]
                    jpeg_quality = jpeg_string.split("_")[0]
                    sizes[current_prefix + " (Converter) JPEG Q="+str(jpeg_quality)] = os.path.getsize(os.path.join(folder,f))/(1024*1024)
            if(str(f).startswith(current_prefix+".")):
                    sizes[current_prefix+" RAW"] = os.path.getsize(os.path.join(folder,f))/(1024*1024)
        
        entries.append(sizes)
    return entries

#similar to group_data_byte, but store the files sizes compared to their corresponding RAW file in percent
def group_data_percentage(folder, num_slides):
    entries = [] #list of all grouped slides as dictionaries

    for i in range (1,num_slides+1):
        current_prefix = "Slide"+str(i)
        sizes = {}

        raw_slide_size = 0

        for f in os.listdir(folder):
            if(str(f).startswith(current_prefix+".")):
                raw_slide_size = os.path.getsize(os.path.join(folder,f))
                sizes[str(f).split(".")[0]+" RAW"] = 100
        
        #add size compared to RAW file
        for f in os.listdir(folder):
            if(str(f).startswith(current_prefix+"_")):
                if("jp2k" in str(f)):
                    sizes[current_prefix+ " (Scanner) JPEG 2000 Q=70"] = os.path.getsize(os.path.join(folder,f))/(raw_slide_size)*100
                if("converted" in str(f) and "webp" in str(f)):
                    webp_string = str(f).split("webp")[1]
                    webp_quality = webp_string.split("_")[0]
                    sizes[current_prefix + " (Converter) WebP Q="+str(webp_quality)] = os.path.getsize(os.path.join(folder,f))/(raw_slide_size)*100
                if("converted" in str(f) and "jpeg" in str(f)):
                    jpeg_string = str(f).split("jpeg")[1]
                    jpeg_quality = jpeg_string.split("_")[0]
                    sizes[current_prefix + " (Converter) JPEG Q="+str(jpeg_quality)] = os.path.getsize(os.path.join(folder,f))/(raw_slide_size)*100
        
        entries.append(sizes)
    return entries

#Generates horizontal barplot comparing filesizes of different compression types and settings on a logarithmic scale, grouped by files
#barplot generation based on template generated by ChatGPT 3.5 https://chatgpt.com/
#https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html
def generate_plot(entries, data, fullsize):
    labels = []
    file_sizes = []
    filegroup_positions = []
    current_position = 0
    spacing = 1
    entry_limit = 3 #limit the number of entries displayed if fullsize=False
    entry_count = 0

    for file in entries:
        for filename, filesize in file.items():
            labels.append(filename)
            file_sizes.append(filesize)
            filegroup_positions.append(current_position)
            current_position = current_position+1
        current_position = current_position+spacing
        entry_count=entry_count+1
        if entry_count>=entry_limit and fullsize==False:
           break

    #https://matplotlib.org/stable/api/axes_api.html
    _ , ax = plt.subplots(layout="constrained")

    ax.barh(filegroup_positions, file_sizes, align='center', log=True)

    match(data):
        case "byte":
            ax.set_xlabel('Filesize (in MB)')
            ax.set_ylabel('WSI using different compression schemes/settings')
            ax.set_title('File Size Comparison')
            ax.set_yticks(filegroup_positions)
            ax.bar_label(ax.containers[0], label_type="center")
            ax.set_yticklabels(labels)
        case "percent":
            ax.set_xlabel('File Size relative to RAW size in %')
            ax.set_ylabel('WSI using different compression schemes/settings')
            ax.set_title('File Size % Comparison')
            ax.set_yticks(filegroup_positions)
            ax.bar_label(ax.containers[0], label_type="center")
            ax.set_yticklabels(labels)

    plt.show()

def main():
    #TODO Add the folder containing the testdata and number of test-files here, make sure you adhere to the naming scheme (output of converter.py) and that for every file there is at least the RAW file present
    #Naming scheme: RAW: Slide1.[tiff;svs;tif] ; WebP/JPEG (converted, Quality: 70): Slide1_webp70_converted.tiff / Slide1_jpeg70_converted.tiff
    path = "PATH/TO/TESTDATA/FOLDER"
    num_slides=10 #TODO add how many different groups of slides you are comparing
    
    entries_byte = group_data_byte(path,num_slides)
    generate_plot(entries_byte, "byte", False)
    
    entries_percentage = group_data_percentage(path,num_slides)
    generate_plot(entries_percentage, "percent", False)
    
    return

if __name__ == "__main__":
    main()