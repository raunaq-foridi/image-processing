# image-processing
A collection of image processing programs I've created for my own usage.

### gif_resize
A simple program to resize a batch of gifs to a square without stretching or squeezing. It scales evenly, and then pads the remainder with transparency. By default, it scales to 512x512px using Nearest-Neighbour interpolation. However, this is all easily changed in the variables near the top. 

Input gifs should be place in a folder named "input_gifs" in the same directory. Output gifs will be output to a folder named "output_gifs". 
