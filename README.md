# image-processing
A collection of image processing programs I've created for my own usage. All programs require Python and Pillow. Some programs require NumPy also

### gif_resize
A simple program to resize a batch of gifs to a square without stretching or squeezing. It scales evenly, and then pads the remainder with transparency. By default, it scales to 512x512px using Nearest-Neighbour interpolation. However, this is all easily changed in the variables near the top. 

Input gifs should be place in a folder named "input_gifs" in the same directory. Output gifs will be output to a folder named "output_gifs". 

### gif_resize_gui
A GUI version of the above file. It also includes the ability to select specific files rather than an entire directory, or to choose multiple directories. Through the GUI, you can select the Resampling method, the output directory and the output size.

### kuwahara
Applies the Kuwahara filter to an image. This gives images a "painterly" look. The size of the window (equivalently, the size of the "brushstrokes") can be changed using the variable n. Requires NumPy
