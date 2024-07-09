#input json logs containing deltaE values, mean -> create and save histogram for one file, comparing compressions
import numpy as np #https://numpy.org/doc/stable/
import os #https://docs.python.org/3/library/os.html
import matplotlib.pyplot as plt #https://matplotlib.org/stable/
import json #https://docs.python.org/3/library/json.html

#input_folder content: slides all derived from the same RAW file
#creates a histogramm for the given files, displays median as dashed line
def create_histogram(input_folder):
    
    #iterate over every file (compression scheme)
    #https://stackoverflow.com/questions/6871201/plot-two-histograms-on-single-chart
    bin = np.linspace(0,10,20)
    values = []
    labels = []
    medians = []
    colors = ["green","blue","red","orange"]

    for f in os.listdir(input_folder):
            if("converted" in str(f) and "webp" in str(f)):
                webp_string = str(f).split("webp")[1]
                webp_quality = webp_string.split("_")[0]
                with open(os.path.join(input_folder,f)) as file:
                    data = json.load(file)
                    #add values to histogramm
                    if "background_deltaE_values" in data:
                        values.append(data["background_deltaE_values"])
                        medians.append(data["background_deltaE_median"])
                    else:
                        values.append(data["deltaE_values"])
                        medians.append(data["deltaE_median"])
                labels.append("WebP Q="+webp_quality)    

            if("converted" in str(f) and "jpeg" in str(f)):
                jpeg_string = str(f).split("jpeg")[1]
                jpeg_quality = jpeg_string.split("_")[0]
                with open(os.path.join(input_folder,f)) as file:
                    data = json.load(file)
                    #add values to histogramm
                    if "background_deltaE_values" in data:
                        values.append(data["background_deltaE_values"])
                        medians.append(data["background_deltaE_median"])
                    else:
                        values.append(data["deltaE_values"])
                        medians.append(data["deltaE_median"])
                labels.append("JPEG Q="+jpeg_quality)    

    plt.hist(values, bin, label=labels, color=colors)
    for i in range(len(medians)):
        #add ymax to be able to differentiate median lines with (almost) same values
        plt.axvline(medians[i], ymax=1-(0.005*i), linestyle="dashed", color=colors[i], label=labels[i]+" Median: "+str(medians[i]))
    plt.legend(loc="upper right")
    plt.show()

#input: folder containing one folder each for every compression+Q combination json logs from DeltaE conversion
def create_boxplot(input_folder):
    values = []
    labels = []

    for folder in os.listdir(input_folder):
        folder_label=""
        file_values = []
        for file in os.listdir(os.path.join(input_folder,folder)):
            if(folder_label==""):
                if("converted" in str(file) and "webp" in str(file)):
                    webp_string = str(file).split("webp")[1]
                    webp_quality = webp_string.split("_")[0]
                    folder_label="WebP Q="+webp_quality
                if("converted" in str(file) and "jpeg" in str(file)):
                    jpeg_string = str(file).split("jpeg")[1]
                    jpeg_quality = jpeg_string.split("_")[0]
                    folder_label="JPEG Q="+jpeg_quality
            with open(os.path.join(os.path.join(input_folder,folder),file)) as file:
                    data = json.load(file)
                    if "background_deltaE_values" in data:
                        file_values.extend(data["background_deltaE_values"])
                    else:
                        file_values.extend(data["deltaE_values"])
        labels.append(folder_label)
        values.append(file_values)
        
    plt.boxplot(values, labels=labels)
    plt.show()
    return

def main():
    global logs_path
    script_path = os.path.dirname(os.path.abspath(__file__))
    logs_path = script_path+r"/Logs/"

    create_histogram("E:\Testdata\FINAL TESTDATA\Histogramm Struktur\Slide1")
    #create_boxplot("E:\Testdata\FINAL TESTDATA\Boxplot Struktur")

if __name__ == "__main__":
    main()