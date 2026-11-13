#Raunaq Foridi 2026
#An implementation of the Kuwahara filter

import numpy as np
from PIL import Image

image = Image.open("input.jpg").convert("RGB")
pixels = np.array(image)
height, width, channels = pixels.shape

value = np.max(pixels,axis=2).astype(np.float64)
output= np.zeros((height,width,3),dtype=np.uint8)

#Region sizes
n = 3

def get_region(x, y, width, height, dx=1, dy=1):
    x1 = x if dx == 1 else x - width + 1
    y1 = y if dy == 1 else y - height + 1

    x2 = x1 + width
    y2 = y1 + height

    x1 = np.clip(x1, 0, value.shape[1])
    x2 = np.clip(x2, 0, value.shape[1])

    y1 = np.clip(y1, 0, value.shape[0])
    y2 = np.clip(y2, 0, value.shape[0])

    return [x1,y1,x2,y2]

#Doing the full calculation for each pixel is slow
#Instead, use integral images (padded by 1)

S = np.pad(value, ((1,0),(1,0))).cumsum(0).cumsum(1)
S2 = np.pad(value**2, ((1,0),(1,0))).cumsum(0).cumsum(1)

#And an RGB integral for the mean
RGB = np.pad(pixels, ((1,0),(1,0),(0,0))).cumsum(0).cumsum(1)

def rect_sum(im, x1,y1,x2,y2):
    return im[y2,x2] - im[y1,x2] - im[y2,x1] + im[y1,x1]

def region_std(region):
    
    x1,y1,x2,y2 = region
    
    count = (y2-y1)*(x2-x1)

    total = rect_sum(S,x1,y1,x2,y2)
    total2= rect_sum(S2,x1,y1,x2,y2)

    mean = total/count
    variance= total2/count - mean**2

    #return np.sqrt(max(0,variance))
    #we only need magnitude, so we can actually just use variance

    return variance

def region_mean(region):

    x1,y1,x2,y2 = region
    
    count = (y2-y1)*(x2-x1)
    total = rect_sum(RGB,x1,y1,x2,y2)
    mean = total/count
    return mean

#iterate over all pixels
for y in range(height):
    for x in range(0,width):

        
        #define the regions
        regions = [
            get_region(x,y,n,n,-1,-1),     # A B
            get_region(x,y,n,n,1,-1),      # C D
            get_region(x,y,n,n,-1,1),
            get_region(x,y,n,n,1,1),
        ]

        #region = min(regions, key= lambda r: np.std(value[r[1]:r[3],r[0]:r[2]]))
        region = min(regions, key = region_std)
        
        #colour = np.mean(pixels[region[1]:region[3],region[0]:region[2]], axis=(0,1))
        colour = region_mean(region)

        output[y,x] = colour



Image.fromarray(output).save("output.png")
print("done")

        
        

        
