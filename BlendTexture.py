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


def blend_texture_add(surface1_: pygame.Surface, surface2_: pygame.Surface,
                      set_alpha1_: (float, numpy.ndarray),
                      set_alpha2_: (float, numpy.ndarray), mask_: bool = False) -> pygame.Surface:
    """

    :param surface1_: First layer texture
    :param surface2_: Second layer texture
    :param set_alpha1_: Alpha values for surface1 (can be a float or a numpy array)
    :param set_alpha2_: Alpha values for surface2 (can be a flaot or a numpy array)
    :param mask_: True | False, create a mask from surface1 (only black pixels)
    :return: Return a pygame surface (blend between surface1 & surface2)
    """

    assert isinstance(surface1_, pygame.Surface), \
        'Expecting Surface for argument surface got %s ' % type(surface1_)
    assert isinstance(surface2_, pygame.Surface), \
        'Expecting Surface for argument surface2_ got %s ' % type(surface2_)
    assert isinstance(set_alpha1_, (float, numpy.ndarray)), \
        'Expecting float or numpy.ndarray for argument set_alpha1_ got %s ' % type(set_alpha1_)
    assert isinstance(set_alpha2_, (float, numpy.ndarray)), \
        'Expecting float for argument set_alpha2_ got %s ' % type(set_alpha2_)

    # sizes
    w, h = surface1_.get_width(), surface1_.get_height()

    # Create a BufferProxy for surface1_ and 2
    # '3' returns a (surface-width, surface-height, 3) array of RGB color components.
    #  Each of the red, green, and blue components are unsigned bytes.
    # Only 24-bit and 32-bit surfaces are supported.
    # The color components must be in either RGB or BGR order within the pixel.
    buffer1 = surface1_.get_view('3')
    buffer2 = surface2_.get_view('3')

    # Extract the alpha channel from surface1 and create
    # a mask (array with black pixels flagged) alpha1_ <= 0
    if isinstance(mask_, bool):
        # Extract the surface1_ alpha channel and create a mask_ for (black pixel)
        alpha1_ = numpy.array(surface1_.get_view('a'), dtype=numpy.uint8).transpose(1, 0) / 255
        mask_alpha1 = alpha1_ <= 0

    if isinstance(set_alpha1_, float):
        # Create alpha channels alpha1 and alpha2
        alpha1 = numpy.full((w, h, 1), set_alpha1_).transpose(1, 0, 2)
    elif isinstance(set_alpha1_, numpy.ndarray):
        alpha1 = set_alpha1_

    if isinstance(set_alpha2_, float):
        # Create alpha channels alpha1 and alpha2
        alpha2 = numpy.full((w, h, 1), set_alpha2_).transpose(1, 0, 2)
    elif isinstance(set_alpha2_, numpy.ndarray):
        alpha2 = set_alpha2_

    # -------------------  pre-multiplied -------------------
    # 1) create arrays representing surface1_ and surface2_, swap row and column and normalize.
    # 2 ) pre - multiplied alphas
    rgb1 = (numpy.array(buffer1, dtype=numpy.uint8).transpose(1, 0, 2) / 255) * alpha1
    rgb2 = (numpy.array(buffer2, dtype=numpy.uint8).transpose(1, 0, 2) / 255) * alpha2

    # create the output array RGBA
    new = numpy.zeros((w, h, 4))

    # Calculations for RGB values -> outRGB = SrcRGB + DstRGB(1 - SrcA)
    new[:, :, :3] = numpy.add(rgb1, rgb2 * (1 - alpha1))
    # Calculation for alpha channel -> outA = SrcA + DstA(1 - SrcA)
    new[:, :, 3] = numpy.add(alpha1, alpha2 * (1 - alpha1)).reshape(w, h)
    # -------------------  pre-multiplied -------------------

    # De-normalization
    new = numpy.multiply(new, 255)

    # Capping all the values over 255
    numpy.putmask(new, new > 255, 255)

    # Apply the mask_ to the new surface
    if mask_:
        new[mask_alpha1] = 0
    return pygame.image.frombuffer(new.copy('C').astype(numpy.uint8),
                                   (w, h), 'RGBA')


if __name__ == '__main__':
    pygame.init()
    numpy.set_printoptions(threshold=numpy.nan)
    SIZE = (256, 256)
    screen = pygame.display.set_mode(SIZE, 0, 32)

    # Background picture
    background = pygame.image.load('Assets\\background.png')
    background = pygame.transform.scale(background, SIZE)
    screen.blit(background, (0, 0))

    # Firat layer texture
    surface1 = pygame.image.load('Assets\\Asteroid.png').convert_alpha()
    surface1 = pygame.transform.smoothscale(surface1, SIZE)

    # Second layer
    surface2 = pygame.image.load('Assets\\Lava.png').convert_alpha()
    surface2 = pygame.transform.smoothscale(surface2, SIZE)

    # gradient = numpy.linspace(0, 255, surface1.get_width())
    # surface1_mask = numpy.repeat(gradient[:, numpy.newaxis], [surface1.get_height()], 1).reshape((256, 256, 1)) / 255
    # surface1_mask.transpose(1, 0, 2)

    # Create an alpha channel from a the image radial1_inverted.png
    mask = pygame.image.load('Assets\\radial1_inverted.png').convert_alpha()
    mask = pygame.transform.smoothscale(mask, SIZE)
    surface1_mask = pygame.surfarray.array_alpha(mask)
    surface1_mask = surface1_mask.reshape((256, 256, 1)) / 255
    surface1_mask = 0.8

    """
    # Create alpha channel from the image radial1
    mask = pygame.image.load('Assets\\radial1.png').convert_alpha()
    mask = pygame.transform.smoothscale(mask, SIZE)
    surface2_mask = pygame.surfarray.array_alpha(mask)
    surface2_mask = surface2_mask.reshape((256, 256, 1)) / 255
    """
    surface2_mask = 1.0

    # Blend textures (surface1 with 31% opacity and surface2 full opacity.
    texture = blend_texture_add(surface1, surface2, surface1_mask, surface2_mask, mask_=True)

    # Save the image
    pygame.image.save(texture, 'Assets\\Blend.png')

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        # Create a transition effect between 2 layers
        # texture = blend_texture_add(surface1, surface2, i / 255, 255 / 255, mask_=True)

        # Blending
        texture = blend_texture_add(surface1, surface2, surface1_mask, surface2_mask, mask_=True)

        screen.blit(background, (0, 0))
        screen.blit(texture, (0, 0))
        pygame.display.flip()