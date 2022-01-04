Author: Siddharth Shah

The python files within this directory implement k-means clustering to partition
the pixel colors in an image into "N" clusters (sys.argv[2]) and saves the reformatted
image as a .PNG file to observe the clustered coloring.

The image URL can be inputted as sys.argv[3] 
"python kmeans.py 4 2021sshah.jpg"

The kmeans algorithm begins with random means and gradually corrects towards selecting
pixel colors that result in no changes between the clusters of closest-coloring pixels
upon immediate color correction to the means.