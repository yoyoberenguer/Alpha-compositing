import pygame
import numpy
import timeit


def blend_texture_add(surface1_: pygame.Surface, surface2_: pygame.Surface,
                      set_alpha1_: float, set_alpha2_: float, mask_: bool) -> pygame.Surface:
    """

    :param surface1_: First layer texture
    :param surface2_: Second layer texture
    :param set_alpha1_: Alpha values for surface1
    :param set_alpha2_: Alpha values for surface2
    :param mask_: True | False, create a mask for black pixel
    :return: Return a pygame surface
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
    OutA = SrcA + DstA(1 - SrcA)
    outRGB = (SrcRGB x SrcA + DstRGB x DstA x (1 - SrcA) / ( SrcA + DstA(1 - SrcA))

    if pre-multiplied  alpha is used, the above equations are simplified to:
    outA = SrcA + DstA(1 - SrcA)
    outRGB = SrcRGB + DstRGB(1 - SrcA)

    Surface1 is png format with alpha transparency channel (image created with alpha channel)
    Compatible with 32 bit only
    """

    assert isinstance(surface1_, pygame.Surface), \
        'Expecting Surface for argument surface got %s ' % type(surface1_)
    assert isinstance(surface2_, pygame.Surface), \
        'Expecting Surface for argument surface2_ got %s ' % type(surface2_)
    assert isinstance(set_alpha1_, float), \
        'Expecting float for argument set_alpha1_ got %s ' % type(set_alpha1_)
    assert isinstance(set_alpha2_, float), \
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

    # Extract the surface1_ alpha channel and create a mask_ for (black pixel)
    alpha1_ = numpy.array(surface1_.get_view('a'), dtype=numpy.uint8).transpose(1, 0) / 255
    mask_alpha1 = alpha1_ <= 0

    # Create alpha channels alpha1 and alpha2
    alpha1 = numpy.full((w, h, 1), set_alpha1_).transpose(1, 0, 2)
    alpha2 = numpy.full((w, h, 1), set_alpha2_).transpose(1, 0, 2)

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
    new[:, :, 3] = numpy.add(alpha1[0], alpha2[0] * (1 - alpha1[0]))
    # -------------------  pre-multiplied -------------------
    """
    # ------------------- non pre-multiplied -------------------
    # Formula to apply to each pixels:
    # outRGB = (SrcRGB x SrcA + DstRGB x DstA x (1 - SrcA) / ( SrcA + DstA(1 - SrcA))
    # OutA = SrcA + DstA(1 - SrcA)
    rgb1 = (numpy.array(buffer1, dtype=numpy.uint8).transpose(1, 0, 2) / 255) * alpha1
    rgb2 = (numpy.array(buffer2, dtype=numpy.uint8).transpose(1, 0, 2) / 255) * alpha2
    new[:, :, 3] = alpha1[0] + alpha2[0] * (1 - alpha1[0])
    new[:, :, :3] = rgb1 * alpha1 + rgb2 * alpha2 * (1 - alpha1) / (alpha1 + alpha2 * (1 - alpha1))
    # ------------------- non pre-multiplied -------------------
    """

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

    # Blend textures (surface1 with 31% opacity and surface2 full opacity.
    # If mask is true, a mask for black pixel will be generated and full transparency will be
    # applied to surface1 black pixels when blending surface1 & surface2.
    texture = blend_texture_add(surface1, surface2, 150 / 255, 255 / 255, mask_=True)

    pygame.image.save(texture, 'Assets\\Blend.png')

    N = 1
    print('Time per iteration: %s ' %
          (timeit.timeit("blend_texture_add(surface1, surface2, 80 / 255, 255 / 255, mask_=False)",
          "from __main__ import blend_texture_add, surface1, surface2", number=N)/N))

    i = 255
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        texture = blend_texture_add(surface1, surface2, i / 255, 255 / 255, mask_=False)
        i -= 1
        if i == 0:
            i = 255

        screen.blit(background, (0, 0))
        screen.blit(texture, (0, 0))
        pygame.display.flip()
