import colorsys

black = (0,0,0)
white = (1,1,1)

red = (1,0,0)
green = (0,1,0)
blue = (0,0,1)

yellow = (1,1,0)
cyan = (0,1,1)
magenta = (1,0,1)

orange = (1,0.6,0)

def gray(luminance):
  return (luminance,luminance,luminance)

def rgb_to_hsv(T):
  if len(T) > 3:
    T = T[:3]
  return apply(colorsys.rgb_to_hsv,T)

def hsv_to_rgb(T):
  if len(T) > 3:
    T = T[:3]
  return apply(colorsys.hsv_to_rgb,T)

