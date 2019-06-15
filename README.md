# Alpha-compositing

## **Image alpha compositing**

### WIKIPEDIA

In computer graphics, alpha compositing is the process of combining an image with a background to create 
the appearance of partial or full transparency. It is often useful to render image elements in separate 
passes, and then combine the resulting multiple 2D images into a single, final image called the composite.

With straight alpha, the RGB components represent the color of the object or pixel, disregarding its opacity.

With premultiplied alpha, the RGB components represent the color of the object or pixel, adjusted for its 
opacity by multiplication. A more obvious advantage of this is that, in certain situations, it can save a 
subsequent multiplication (e.g. if the image is used many times during later compositing). However, the most 
significant advantages of using premultiplied alpha are for correctness and simplicity rather than 
performance: premultiplied alpha allows correct filtering and blending. In addition, premultiplied alpha 
allows regions of regular alpha blending and regions with additive blending mode to be encoded within the same image.

Alpha blending is the process of combining a translucent foreground color with a background color, 
thereby producing a new blended color. The degree of the foreground color's translucency may range from completely
transparent to completely opaque. If the foreground color is completely transparent, the blended color will be the
background color. Conversely, if it is completely opaque, the blended color will be the foreground color. 
The translucency can range between these extremes, in which case the blended color is computed as a weighted average
of the foreground and background colors.
Alpha blending is a convex combination of two colors allowing for transparency effects in computer graphics. 
The value of alpha in the color code ranges from 0.0 to 1.0, where 0.0 represents a fully transparent color,
and 1.0 represents a fully opaque color. 
This alpha value also corresponds to the ratio of "SRC over DST" in Porter and Duff equations.

The value of the resulting color is given by:

![alt text](https://github.com/yoyoberenguer/Alpha-compositing/blob/master/equation1.png) 

If the destination background is opaque, then dstA = 1, and if you enter it to the upper equation:

![alt text](https://github.com/yoyoberenguer/Alpha-compositing/blob/master/equation2.png)

The alpha component may be used to blend to red, green and blue components equally, as in 32-bit RGBA, or, alternatively, there may be three alpha values specified corresponding to each of the primary colors for spectral color filtering.
If premultiplied alpha is used, the above equations are simplified to:

![alt text](https://github.com/yoyoberenguer/Alpha-compositing/blob/master/equation3.png)

### Alpha blending example

**Partial opacity**  |  **Full opacity**   | **Blend mask is False**                                         
---------------------|---------------------|----------------------------------------------------------------------------------------
![alt_text](https://github.com/yoyoberenguer/Alpha-compositing/blob/master/Assets/foreground1.png) | ![alt_text](https://github.com/yoyoberenguer/Alpha-compositing/blob/master/Assets/background1.png) | ![alt_text] (https://github.com/yoyoberenguer/Alpha-compositing/blob/master/Assets/Blend_Troll.png)

### Blending texture example

texture = blend_texture_add(surface1, surface2, 150 / 255, 255 / 255, mask_=False)

**surface1 Partial opacity**  |  **surface2 Full opacity**               | **Blend mask is False** | **Blend mask is True** 
--------------------------|--------------------------------------|---------------------|--------------------
![alt_text](https://github.com/yoyoberenguer/Alpha-compositing/blob/master/Assets/Asteroid.png)  | ![alt_text](https://github.com/yoyoberenguer/Alpha-compositing/blob/master/Assets/Lava.png)   | ![alt_text](https://github.com/yoyoberenguer/Alpha-compositing/blob/master/Assets/Blend_no_mask.png) | ![alt_text](https://github.com/yoyoberenguer/Alpha-compositing/blob/master/Assets/Blend.png)


### Below, using a different mask alpha for surface1 

- New mask for surface1 with an inverted radial opacity.

![alt_text](https://github.com/yoyoberenguer/Alpha-compositing/blob/master/Mask1.png)

**surface1 Partial opacity**  |  **surface2 Full opacity**               | **Blend mask is True** 
--------------------------|--------------------------------------|---------------------
![alt_text](https://github.com/yoyoberenguer/Alpha-compositing/blob/master/Assets/Egg.png) | ![alt_text](https://github.com/yoyoberenguer/Alpha-compositing/blob/master/Assets/Humpty.jpg) | ![alt_text](https://github.com/yoyoberenguer/Alpha-compositing/blob/master/Assets/Blend_Humpty.png)
