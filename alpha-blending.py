"""
This code comes with a MIT license.

Copyright (c) 2018 Yoann Berenguer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

Please acknowledge and give reference if using the source code for your project(s)
"""

"""
Alpha-Compositing python algorithm 
"""

__author__ = "Yoann Berenguer"
__copyright__ = "Copyright 2007"
__credits__ = ["Yoann Berenguer"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"
__status__ = "Demo"

import pygame
import numpy
import timeit


def alpha_blending(surface1_: pygame.Surface, surface2_: pygame.Surface) -> pygame.Surface:
    """
    Alpha blending algorithm

    :param surface1_: First layer texture (foreground)
    :param surface2_: Second layer texture (background)
    :return: Return a pygame surface (blend between surface1 & surface2)
    """

    """
    WIKIPEDIA
    Assuming that the pixel color is expressed using straight (non-premultiplied) RGBA tuples,
    a pixel value of (0, 0.7, 0, 0.5) implies a pixel that has 70% of the maximum green intensity
    and 50% opacity. If the color were fully green, its RGBA would be (0, 1, 0, 0.5).
    However, if this pixel uses premultiplied alpha, all of the RGB values (0, 0.7, 0)
    are multiplied by 0.5 and then the alpha is appended to the end to yield (0, 0.35, 0, 0.5).
    In this case, the 0.35 value for the G channel actually indicates 70% green intensity (with 50% opacity).
    Fully green would be encoded as (0, 0.5, 0, 0.5). For this reason, knowing whether a file uses straight
    or premultiplied alpha is essential to correctly process or composite it.


    Formula to apply to each pixels:
    OutA = SrcA + DstA x (1 - SrcA)
    outRGB = (SrcRGB x SrcA + DstRGB x DstA x (1 - SrcA) / ( SrcA + DstA(1 - SrcA))

    if pre-multiplied  alpha is used, the above equations are simplified to:
    outA = SrcA + DstA x (1 - SrcA)
    outRGB = SrcRGB + DstRGB x (1 - SrcA)
    
    If the destination background is opaque, then DSTA = 1 , and if you enter it to the upper equation:
    outA = 1
    outRGB = SrcRGB x SrcA + DstRGB x (1 - SrcA)

    Surface1 is png format with alpha transparency channel (image created with alpha channel)
    Compatible with 32 bit only
    """

    assert isinstance(surface1_, pygame.Surface), \
        'Expecting Surface for argument surface got %s ' % type(surface1_)
    assert isinstance(surface2_, pygame.Surface), \
        'Expecting Surface for argument surface2_ got %s ' % type(surface2_)

    # sizes
    w, h = surface1_.get_size()

    # Create a BufferProxy for surface1_ and 2
    # '3' returns a (surface-width, surface-height, 3) array of RGB color components.
    #  Each of the red, green, and blue components are unsigned bytes.
    # Only 24-bit and 32-bit surfaces are supported.
    # The color components must be in either RGB or BGR order within the pixel.
    buffer1 = surface1_.get_view('3')
    buffer2 = surface2_.get_view('3')

    # Extract RGB values (source -> rgb1, destination -> rgb2)
    rgb1 = (numpy.array(buffer1, dtype=numpy.uint8).transpose(1, 0, 2) / 255)
    rgb2 = (numpy.array(buffer2, dtype=numpy.uint8).transpose(1, 0, 2) / 255)

    # create the output array RGBA
    new = numpy.zeros((w, h, 4))

    # ---------------- background opaque ---------------------------
    # Extract the alpha channels from surface1 & surface2
    # alpha1 = (numpy.array(surface1_.get_view('a'), dtype=numpy.uint8).transpose(1, 0)).reshape(w, h, 1) / 255
    # alpha2 = (numpy.array(surface2_.get_view('a'), dtype=numpy.uint8).transpose(1, 0)).reshape(w, h, 1) / 255
    # new[:, :, 3] = 1  # outA
    # new[:, :, :3] = (rgb1 * alpha1 + rgb2 * alpha2 * (1 - alpha1))  # outRGB

    # ---------------- background partially transparent ------------
    # Extract the alpha channels from surface1 & surface2
    alpha1 = (numpy.array(surface1_.get_view('a'), dtype=numpy.uint8).transpose(1, 0)) / 255
    alpha2 = (numpy.array(surface2_.get_view('a'), dtype=numpy.uint8).transpose(1, 0)) / 255
    new[:, :, 3] = alpha1 + alpha2 * (1 - alpha1)
    alpha1 = alpha1.reshape(w, h, 1)
    alpha2 = alpha2.reshape(w, h, 1)
    new[:, :, :3] = (rgb1 * alpha1 + rgb2 * alpha2 * (1 - alpha1)) / (alpha1 + alpha2 * (1 - alpha1))

    # De-normalization
    new = numpy.multiply(new, 255)

    # Capping all the values over 255
    # numpy.putmask(new, new > 255, 255)

    return pygame.image.frombuffer(new.copy('C').astype(numpy.uint8),
                                   (w, h), 'RGBA')


def alpha_blending_1(surface1_: pygame.Surface, surface2_: pygame.Surface) -> pygame.Surface:
    """
    Same method than alpha_blending but much slower (looping over all pixels).

    :param surface1_: First layer texture (foreground)
    :param surface2_: Second layer texture (background)
    :return: Return a pygame surface (blend between surface1 & surface2)
    """

    assert isinstance(surface1_, pygame.Surface), \
        'Expecting Surface for argument surface got %s ' % type(surface1_)
    assert isinstance(surface2_, pygame.Surface), \
        'Expecting Surface for argument surface2_ got %s ' % type(surface2_)

    # sizes
    w, h = surface1_.get_size()

    # Create a BufferProxy for surface1_ and 2
    # '3' returns a (surface-width, surface-height, 3) array of RGB color components.
    #  Each of the red, green, and blue components are unsigned bytes.
    # Only 24-bit and 32-bit surfaces are supported.
    # The color components must be in either RGB or BGR order within the pixel.
    buffer1 = surface1_.get_view('3')
    buffer2 = surface2_.get_view('3')

    # Extract RGB values (source -> rgb1, destination -> rgb2)
    rgb1 = (numpy.array(buffer1, dtype=numpy.uint8).transpose(1, 0, 2) / 255)
    rgb2 = (numpy.array(buffer2, dtype=numpy.uint8).transpose(1, 0, 2) / 255)

    # create the output array RGBA
    new = numpy.zeros((w, h, 4))
    # Extract the alpha channels from surface1 & surface2
    alpha1 = (numpy.array(surface1_.get_view('a'), dtype=numpy.uint8).transpose(1, 0)).reshape(w, h, 1) / 255
    alpha2 = (numpy.array(surface2_.get_view('a'), dtype=numpy.uint8).transpose(1, 0)).reshape(w, h, 1) / 255

    """
    # -------------- background opaque--------------
    for i in range(w):
        for j in range(h):
            rgb = (rgb1[i][j] * alpha1[i][j] + rgb2[i][j] * (1 - alpha1[i][j]))
            new[i][j] = (*rgb, 1)  # (outRGB, outA=1)
    # --------------- background not opaque --------
    """

    for i in range(w):
        for j in range(h):
            alpha = alpha1[i][j] + alpha2[i][j] * (1 - alpha1[i][j])
            assert alpha > 0, 'Incorrect alpha value, Division by zero.'
            rgb = (rgb1[i][j] * alpha1[i][j] + rgb2[i][j] * alpha2[i][j] * (1 - alpha1[i][j])) / alpha
            new[i][j] = (*rgb, alpha)

            # De-normalization
    new = numpy.multiply(new, 255)

    return pygame.image.frombuffer(new.copy('C').astype(numpy.uint8),
                                   (w, h), 'RGBA')

if __name__ == '__main__':
    pygame.init()
    numpy.set_printoptions(threshold=numpy.nan)
    SIZE = (256, 256)
    screen = pygame.display.set_mode(SIZE, 0, 32)

    # background = pygame.image.load('Assets\\background.png').convert_alpha()
    # background = pygame.transform.smoothscale(background, SIZE)
    # screen.blit(background, (0, 0))

    # Firat layer texture (foreground)
    surface1 = pygame.image.load('Assets\\foreground1.png').convert_alpha()
    surface1 = pygame.transform.smoothscale(surface1, SIZE)

    # Second layer (background)
    surface2 = pygame.image.load('Assets\\background1.png').convert_alpha()
    surface2 = pygame.transform.smoothscale(surface2, SIZE)

    # Blend textures
    texture = alpha_blending(surface1, surface2)

    # Save the image
    pygame.image.save(texture, 'Assets\\Blend.png')
    """
    N = 1
    assert N != 0, 'N cannot be equal to <= 0'
    print('Time per iteration: %s ' %
          (timeit.timeit("alpha_blending(surface1, surface2)",
                         "from __main__ import alpha_blending, surface1, surface2", number=N) / N))

    print('Time per iteration: %s ' %
          (timeit.timeit("alpha_blending_1(surface1, surface2)",
                         "from __main__ import alpha_blending_1, surface1, surface2", number=N) / N))
    """
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        # Alpha Blending
        texture = alpha_blending(surface1, surface2)

        screen.blit(texture, (0, 0))
        pygame.display.flip()
