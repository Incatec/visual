version = ('5.12', 'release')

# Copyright David Scherer and others, see license.txt

import sys as _sys
visual = _sys.modules['visual']

# This is called (visual._fix_symbols()) from modules in the package
# that (unfortunately) must "from visual import *" because clients expect
# to be able to import them _instead_ of visual.  This prevents them from
# binding symbols to other _modules_, which may overwrite symbols imported
# directly from those modules.  (yuck!)
def _fix_symbols( modg ):
    for sym in ( 'controls','factorial','ui' ):
        if modg.has_key(sym):
            del modg[sym]
    all = set(modg.keys()) & set(globals().keys())
    return list(all)

# The following manipulations of math and numpy functions is a workaround
# for the problem that in going from Numeric to numpy, the return by numpy
# from e.g. sqrt is numpy.float64, not float, which is not recognized as
# matching float in the operator overloading machinery, including Boost.
# This means is that right multiplication scalar*vector is not caught
# and the result is returned as numpy.ndarray instead of vector, which
# can be a big performance hit in vector calculations.

# There is an advantage to this workaround: sqrt(scalar) is much faster
# this way than when using the numpy sqrt, and there is little penalty
# for the numpy sqrt(array).

import math as _math
import numpy as _numpy
# TODO: be selective instead of importing * from these:
from math import *
from numpy import *

for ufunc in ('ceil','cos','cosh','exp','fabs','floor','fmod','frexp',
              'ldexp','log','log10','modf','sin','sinh','sqrt',
              'tan','tanh'):
    def _uf(x,
            numpy = getattr(_numpy,ufunc),
            math = getattr(_math,ufunc),
            mathtypes = (float,int,long)):
        if type(x) in mathtypes: return math(x)
        return numpy(x)
    globals()[ufunc] = _uf

for ufunc in ('hypot',):
    def _uf(x,y,
            numpy = getattr(_numpy,ufunc),
            math = getattr(_math,ufunc),
            mathtypes = (float,int,long)):
        if type(x) in mathtypes and type(y) in mathtypes: return math(x,y)
        return numpy(x,y)
    globals()[ufunc] = _uf

import crayola as color
import cvisual
cvisual.init_numpy()
from cvisual import (vector, mag, mag2, norm, cross, rotate, comp, proj,
                     diff_angle, rate)
from visual.primitives import (arrow, cylinder, cone, sphere, box, ring, label,
                               frame, pyramid, ellipsoid, curve, faces, convex, helix,
                               points, distant_light, local_light)
from visual.ui import display
import materials

# Undo side effect of from... import * that puts modules in package namespace
del ui, crayola, primitives

if 1:
    # Names defined for backward compatibility with Visual 3:
    import sys, time
    true = True
    false = False
    crayola = color
    from cvisual import vector_array, scalar_array

# Allow cvisual itself to load files from the visual package - used by GTK
#   driver to load glade data files
import os.path as _os_path
cvisual._set_dataroot( _os_path.split( __file__ )[0] + _os_path.sep)

# The following ensures that __waitclose will be run
# when we reach the end of the program,
# to permit viewing and navigating the scene.
import atexit as _atexit
_atexit.register(cvisual.waitclose)

import site_settings

# Construct the default display object.
scene = display()
