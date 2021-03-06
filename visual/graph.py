from __future__ import division
from visual import *

__all__ = visual._fix_symbols( globals() ) + [
            'gdisplay','gcurve','gdots','gvbars','ghbars','ghistogram']

# Visual 3 ten iterations 0.14 s each (labels for points)
# Visual 4 hundred iteractions 0.02 s each

# A graph package for plotting a curve, with labeled axes and autoscaling
# Bruce Sherwood, Carnegie Mellon University, begun April 2000

# minmax[xaxis][negaxis], minmax[yaxis][negaxis] refer to absolute values of minimum negative values;
# minmax[xaxis][posaxis], minmax[yaxis][posaxis] to maximum positive values.
# This graph package forces the origin (0,0) to be on screen, at the axes intersection.

grey = (0.7,0.7,0.7) # color of axes
tmajor = 10. # length of major tick marks in pixels
tminor = 5. # length of minor tick marks in pixels
border = 10. # border around graph
frac = 0.02 # fraction of range required before remaking axes
minorticks = 5 # number of minor tick intervals between major ticks
maxmajorticks = 3 # max number of major ticks (not including 0)
maxminorticks = (maxmajorticks+1)*minorticks # max number of minor ticks (4 between major ticks)
lastgdisplay = None # the most recently created gdisplay
gdotsize = 6.0 # diameter of gdot in pixels
dz = 0.01 # offset for plots relative to axes and labels
xaxis = 0
yaxis = 1
negaxis = 0
posaxis = 1
graphfont = ""
fontheight = -1 # font point size
charwidth = 12 # approximate character width
znormal = [0,0,1] # for faces
     
def labelnum(x): # determine what labels to show, in what format
    if x >= 0.: sign = 1.
    else: sign = -1.
    mantissa, exponent = modf(log10(abs(x)))
    number = 10.**mantissa
    if number < 1.:
        number = 10.*number
        exponent = exponent-1.
    if number >= 7.5: 
        number = 7.5
        marks = [2.5, 5.0, 7.5]
        extra = 1
    elif number >= 5.: 
        number = 5.
        marks = [2.5, 5.0]
        extra = 1
    elif number >= 4.:
        number = 4.
        marks = [2.0, 4.0]
        extra = 0
    elif number >= 3.:
        number = 3.
        marks = [1.0, 2.0, 3.0]
        extra = 0
    elif number >= 2.:
        number = 3.
        marks = [1.0, 2.0]
        extra = 0
    elif number >= 1.5:
        number = 1.5
        marks = [0.5, 1.0, 1.5]
        extra = 1
    else: 
        number = 1.
        marks = [0.5, 1.0]
        extra = 1
    if exponent > 0:
        digits = 0
    else:
        digits = int(-exponent)+extra
    if digits < 3. and exponent <= 3.:
        format = '%0.'+('%s' % digits)+'f'
    else:
        format = '%0.1E'
    return (sign*(array(marks)*10.**exponent)).tolist(), format

def cleaneformat(string): # convert 2.5E-006 to 2.5E-6; 2.5E+006 to 2.5E6
    index = string.find('E') 
    if index == -1: return string # not E format
    index = index+1
    if string[index] == '-':
        index = index+1
    elif string[index] == '+':
        string = string[:index]+string[index+1:]
    while index < len(string) and string[index] == '0':
        string = string[:index]+string[index+1:]
    if string[-1] == '-':
        string = string[:-1]
    if string[-1] == 'E':
        string = string[:-1]
    return string

class gdisplay:
    def __init__(self, x=0, y=0, width=800, height=400,
                 title=None, xtitle=None, ytitle=None,
                 xmax=None, xmin=None, ymax=None, ymin=None,
                 foreground=None, background=None):
        global lastgdisplay
        lastgdisplay = self
        currentdisplay = display.get_selected()
        if title is None:
            title = 'Graph'
        self.width = width
        self.height = height
        if foreground is not None:
            self.foreground = foreground
        else:
            self.foreground = color.white
        if background is not None:
            self.background = background
        else:
            self.background = color.black
        self.display = display(title=title, x=x, y=y,
                               width=self.width, height=self.height,
                               foreground=self.foreground, background=self.background,
                               fov=0.01, userspin=0, uniform=0,
                               lights=[], ambient=color.gray(0))
        distant_light(direction=(0,0,1), color=color.white)
        self.autoscale = [1, 1]
        self.title = [[xtitle, 0], [ytitle, 0]] # titles not displayed yet
        if xtitle is not None:
            self.xtitlewidth = len(xtitle)*charwidth
        else:
            self.xtitlewidth = 0
        if ytitle is not None:
            self.ytitlewidth = len(ytitle)*charwidth
        else:
            self.ytitlewidth = 0
        # For all axis-related quantities: [x axis 0 or y axis 1][neg axis 0 or pos axis 1]
        self.axis = [[None, None], [None, None]]
        self.zero = [None, None]
        self.lastlabel = [[0., 0.], [0., 0.]]
        self.format = [None, None]
        self.majormarks = [[None, None], [None, None]]
        self.lastminmax = [[0., 0.], [0., 0.]]
        self.minmax = [[0., 0.], [0., 0.]] # [x or y][negative 0 or positive 1]
        if xmax is not None:
            if xmax > 0:
                self.minmax[xaxis][posaxis] = abs(xmax)
                self.autoscale[xaxis] = 0
        if xmin is not None:
            if xmin < 0:
                self.minmax[xaxis][negaxis] = abs(xmin)
                self.autoscale[xaxis] = 0
        if ymax is not None:
            if ymax > 0:
                self.minmax[yaxis][posaxis] = abs(ymax)
                self.autoscale[yaxis] = 0
        if ymin is not None:
            if ymin < 0:
                self.minmax[yaxis][negaxis] = abs(ymin)
                self.autoscale[yaxis] = 0

        if self.minmax[xaxis][posaxis]+self.minmax[xaxis][negaxis] == 0:
            self.minmax[xaxis][posaxis] = self.lastminmax[xaxis][posaxis] = 1E-35
        if self.minmax[yaxis][posaxis]+self.minmax[yaxis][negaxis] == 0:
            self.minmax[yaxis][posaxis] = self.lastminmax[yaxis][posaxis] = 1E-35
        self.gscale = self.calculategscale()
        self.setcenter()

        self.minorticks = [ [ [], [] ], [ [],[] ] ] # all the minor ticks we'll ever use
        for axis in range(2):
            for axissign in range(2):
                for nn in range(maxminorticks):
                    if axis == xaxis:
                        self.minorticks[axis][axissign].append(label(display=self.display, yoffset=-tminor,
                            linecolor=grey, visible=0, box=0, opacity=0))
                    else:
                        self.minorticks[axis][axissign].append(label(display=self.display, xoffset=-tminor,
                            linecolor=grey, visible=0, box=0, opacity=0))

        self.majorticks = [ [ [], [] ], [ [],[] ] ] # all the major ticks we'll ever use
        for axis in range(2):
            for axissign in range(2):
                for nn in range(maxmajorticks):
                    if axis == xaxis:
                        self.majorticks[axis][axissign].append(label(display=self.display, yoffset=-tmajor, 
                            font=graphfont, text='', border=0, 
                            linecolor=grey, visible=0, box=0, opacity=0))
                    else:
                        self.majorticks[axis][axissign].append(label(display=self.display, xoffset=-tmajor, 
                            font=graphfont, text='', border=2,
                            linecolor=grey, visible=0, box=0, opacity=0))
                        
        for axis in range(2):
            for axissign in range(2):
                self.axisdisplay(axis, axissign)

        currentdisplay.select()

    def setcenter(self):
        if self.title[xaxis][1]:
            xright = self.title[xaxis][0].x+0.5*self.xtitlewidth*self.display.range[0]/self.width
        else:
            xright = self.minmax[xaxis][posaxis]
        xleft = self.minmax[xaxis][negaxis] # a positive number
        ytop = self.minmax[yaxis][posaxis]
        ybottom = self.minmax[yaxis][negaxis] # a positive number
        if (xleft==0):
            xleft += 3*tmajor/self.gscale[0]
        if (ybottom==0):
            ybottom += 3*tmajor/self.gscale[1]
        x = (xright-xleft)/2.0
        y = (ytop-ybottom)/2.0
        self.display.center = array([x,y,0])
        
    def calculategscale(self):
        if self.title[xaxis][1]:
            xright = self.title[xaxis][0].x+0.5*self.xtitlewidth*self.display.range[0]/self.width
        else:
            xright = self.minmax[xaxis][posaxis]
        xleft = self.minmax[xaxis][negaxis] # a positive number
        rangex = xleft+xright
        rangex += self.xtitlewidth*rangex/self.width
        ytop = self.minmax[yaxis][posaxis]
        ybottom = self.minmax[yaxis][negaxis] # a positive number
        rangey = ytop+ybottom
        if (xleft==0):
            rangex += 3*tmajor*rangex/self.width
        if (ybottom==0):
            rangey += 3*tmajor*rangey/self.height
        self.display.range = (0.55*rangex,0.55*rangey,0.1)
        return array([self.width/rangex,self.height/rangey,1.0])

    def setxyparams(self):
        global x0, y0
        if self.minmax[xaxis][posaxis] >= 0 and self.minmax[xaxis][negaxis] >= 0:
            x0 = 0.
        else:
            x0 = self.minmax[xaxis][negaxis]
        if self.minmax[yaxis][posaxis] >= 0 and self.minmax[yaxis][negaxis] >= 0:
            y0 = 0.
        else:
            y0 = self.minmax[yaxis][negaxis]
        
    def axisdisplay(self, axis, axissign):
        if self.minmax[axis][axissign] == 0.: return
        self.setxyparams()
        if axissign == posaxis: sign = 1.
        else: sign = -1.
        if self.axis[axis][axissign] is None: # new; no axis displayed up till now
            if axis == xaxis:
                axispos = array([(0,y0,0), (sign*self.minmax[axis][axissign],y0,0)])
                titlepos = array([self.minmax[axis][posaxis],y0,0])
            else:
                axispos = array([(x0,0,0), (x0,sign*self.minmax[axis][axissign],0)])          
                titlepos = array([x0,self.minmax[axis][posaxis],0])
            self.axis[axis][axissign] = curve(pos=axispos, color=grey, display=self.display)
            if (self.title[axis][0] is not None) and (not self.title[axis][1]):
                title = self.title[axis][0]
                self.title[axis][0] = label(display=self.display, pos=titlepos, text=title,
                            font=graphfont, xoffset=tminor, opacity=0, box=0, line=0)                    
                self.title[axis][1] = 1

            if self.minmax[axis][posaxis] >= self.minmax[axis][negaxis]:
                newmajormarks, format = labelnum(self.minmax[axis][posaxis])
            else:
                newmajormarks, format = labelnum(self.minmax[axis][negaxis])
            self.format[axis] = format
                
            if self.zero[axis] is None:
                if axis == xaxis:
                    self.zero[axis] = label(display=self.display, pos=(0,0,0), text='0',
                                color=self.foreground,
                                font=graphfont, height=fontheight, border=0,
                                yoffset=-tmajor, linecolor=grey, box=0, opacity=0)
                elif self.minmax[xaxis][negaxis] == 0:
                    self.zero[axis] = label(display=self.display, pos=(0,0,0), text='0',
                                color=self.foreground,
                                font=graphfont, height=fontheight, border=2,
                                xoffset=-tmajor, linecolor=grey, box=0, opacity=0)

            d1 = newmajormarks[0]
            d2 = d1/minorticks
            nminor = 0
            nmajor = 0
            marks = []
            for x1 in newmajormarks:
                if x1 > self.minmax[axis][axissign]: break # newmajormarks can refer to opposite half-axis
                marks.append(x1)
                obj = self.majorticks[axis][axissign][nmajor]
                obj.text = cleaneformat(self.format[axis] % (sign*x1))
                obj.color = self.foreground
                obj.visible = 1
                if axis == xaxis:
                    obj.pos = array([sign*x1,y0,0])
                    obj.yoffset = -tmajor 
                else:
                    obj.pos = array([x0,sign*x1,0])
                    obj.xoffset = -tmajor
                nmajor = nmajor+1

            nminor = 0
            for x2 in arange(0.+d2, self.minmax[axis][axissign]+1.01*d2, d2):
                if x2 > self.minmax[axis][axissign]+0.01*d2: break
                if x2 % d1 < d2/2.: continue # don't put minor tick where there is a major one
                obj = self.minorticks[axis][axissign][nminor]
                obj.visible = 1
                if axis == xaxis:
                    obj.pos = array([sign*x2,y0,0])
                else:
                    obj.pos = array([x0,sign*x2,0])
                nminor = nminor+1
                    
            if marks != []:
                self.majormarks[axis][axissign] = marks
                self.lastlabel[axis][axissign] = self.majormarks[axis][axissign][-1]
            else:
                self.lastlabel[axis][axissign] = 0

        else:
            # Don't show y=0 label if there is a negative-x axis
            if (self.zero[axis] is not None) and (axis == yaxis) and (self.minmax[xaxis][negaxis] != 0):
                    self.zero[axis].visible = 0
                    self.zero[axis] = None
                    
            # Extend axis, which has grown
            if axis == xaxis:
                self.axis[axis][axissign].pos = array([[0,0,0],[sign*self.minmax[axis][axissign], y0, 0]])
            else:
                self.axis[axis][axissign].pos = array([[0,0,0],[x0,sign*self.minmax[axis][axissign],0]])
                
            # Reposition xtitle (at right) or ytitle (at top)
            if self.title[axis][1] and axissign == posaxis:
                if axis == xaxis:
                    titlepos = array([self.minmax[axis][posaxis],y0,0])
                else:
                    titlepos = array([x0,self.minmax[axis][axissign],0])
                self.title[axis][0].pos = titlepos
                
            # See how many majormarks are now needed, and in what format
            if self.minmax[axis][posaxis] >= self.minmax[axis][negaxis]:
                newmajormarks, format = labelnum(self.minmax[axis][posaxis])
            else:
                newmajormarks, format = labelnum(self.minmax[axis][negaxis])

            if (self.majormarks[axis][axissign] is not None) and (len(self.majormarks[axis][axissign]) > 0):
                # this axis already has major tick marks/labels
                oldd1 = self.majormarks[axis][axissign][0]
            else:
                oldd1 = 0.
            oldd2 = oldd1/minorticks
            while newmajormarks[-1] > self.minmax[axis][axissign]:
                if len(newmajormarks) == 1: break
                del newmajormarks[-1]
            d1 = newmajormarks[0]
            d2 = d1/minorticks
                
            newformat = (format != self.format[axis])
            self.format[axis] = format
            needminor = (self.minmax[axis][axissign] >= self.lastlabel[axis][axissign]+d2) or (d2 != oldd2)
            needmajor = ((self.majormarks[axis][axissign] is None)
                        or (newmajormarks[-1] != self.majormarks[axis][axissign][-1]) or newformat)
                    
            if needmajor: # need new labels
                start = 0
                if (self.majormarks[axis][axissign] is None) or newformat or (d1 != oldd1):
                    marks = []
                else:
                    for num in newmajormarks:
                        if num > self.majormarks[axis][axissign][-1]:
                            start = num
                            break
                    marks = self.majormarks[axis][axissign]
                for nmajor in range(maxmajorticks):
                    x1 = (nmajor+1)*d1
                    obj = self.majorticks[axis][axissign][nmajor]
                    if x1 > self.minmax[axis][axissign]:
                        obj.visible = 0
                        continue
                    if x1 < start: continue
                    marks.append(x1)
                    obj.text = cleaneformat(self.format[axis] % (sign*x1))
                    obj.color = self.foreground
                    obj.visible = 1
                    if axis == xaxis:
                        obj.pos = array([sign*x1,y0,0])
                    else:
                        obj.pos = array([x0,sign*x1,0])

                if marks != []:
                    self.majormarks[axis][axissign] = marks
                        
            if needminor: # adjust minor tick marks
                nminor = 0
                for x2 in arange(0.+d2, self.minmax[axis][axissign]+1.01*d2, d2):
                    if x2 > self.minmax[axis][axissign]+0.01*d2: break
                    if x2 % d1 < d2/2.: continue # don't put minor tick where there is a major one
                    if (d2 != oldd2) or x2 > self.lastlabel[axis][axissign]-0.01*d2:
                        if axis == xaxis:
                            self.minorticks[axis][axissign][nminor].pos = array([sign*x2,y0,0])
                        else:
                            self.minorticks[axis][axissign][nminor].pos = array([x0,sign*x2,0])
                        self.minorticks[axis][axissign][nminor].visible = 1
                    nminor = nminor+1
                while nminor < maxminorticks:
                    self.minorticks[axis][axissign][nminor].visible = 0
                    nminor = nminor+1

            self.lastlabel[axis][axissign] = d2*int(self.minmax[axis][axissign]/d2)
                   
    def resize(self, x, y):
        redox = redoy = 0
        if self.autoscale[xaxis]:
            if x > self.lastminmax[xaxis][posaxis]:
                self.minmax[xaxis][posaxis] = x+frac*self.display.range[0]
                if (self.lastminmax[xaxis][posaxis] == 0 or
                        (self.minmax[xaxis][posaxis] >= self.lastminmax[xaxis][posaxis])):
                    redox = 1
            elif -x > self.lastminmax[xaxis][negaxis]:
                self.minmax[xaxis][negaxis] = -x-frac*self.display.range[0]
                if (self.lastminmax[xaxis][negaxis] == 0 or
                        (self.minmax[xaxis][negaxis] >= self.lastminmax[xaxis][negaxis])):
                    redox = 1
                    
        if self.autoscale[yaxis]:
            if y > self.lastminmax[yaxis][posaxis]:
                self.minmax[yaxis][posaxis] = y+frac*self.display.range[1]
                if (self.lastminmax[yaxis][posaxis] == 0 or
                        (self.minmax[yaxis][posaxis] >= self.lastminmax[yaxis][posaxis])):
                    redoy = 1
            elif -y > self.lastminmax[yaxis][negaxis]:
                self.minmax[yaxis][negaxis] = -y-frac*self.display.range[1]
                if (self.lastminmax[yaxis][negaxis] == 0 or
                        (self.minmax[yaxis][negaxis] >= self.lastminmax[yaxis][negaxis])):
                    redoy = 1

        if (redox or redoy):
            self.gscale = self.calculategscale()
            if redox:
                self.axisdisplay(xaxis,posaxis)
                self.lastminmax[xaxis][posaxis] = self.minmax[xaxis][posaxis]
                self.axisdisplay(xaxis,negaxis)
                self.lastminmax[xaxis][negaxis] = self.minmax[xaxis][negaxis]
            if redoy:
                self.axisdisplay(yaxis,posaxis)
                self.lastminmax[yaxis][posaxis] = self.minmax[yaxis][posaxis]
                self.axisdisplay(yaxis,negaxis)
                self.lastminmax[yaxis][negaxis] = self.minmax[yaxis][negaxis]
            self.setcenter()
                    
def getgdisplay():
    return gdisplay()

def constructorargs(obj,arguments):
    if arguments.has_key('gdisplay'):
        obj.gdisplay = arguments['gdisplay']
    else:
        if lastgdisplay is None:
            obj.gdisplay = getgdisplay()
        else:
            obj.gdisplay = lastgdisplay
    if arguments.has_key('delta'):
        obj.delta = arguments['delta']
    else:
        obj.delta = 1.
    if arguments.has_key('color'):
        obj.color = arguments['color']
    else:
        obj.color = obj.gdisplay.foreground
    if arguments.has_key('pos'):
        return arguments['pos']
    else:
        return None

def primitiveargs(obj,arguments):
        if arguments.has_key('color'):
            obj.color = arguments['color']
        if arguments.has_key('pos'):
            return arguments['pos']
        else:
            raise SyntaxError

class gcurve:
    def __init__(self, **args):
        pos = constructorargs(self,args)
        self.gcurve = curve(display=self.gdisplay.display, color=self.color)
        if pos is not None:
            for xy in pos:
                self.plot(pos=xy)

    def plot(self, **args):
        pos = primitiveargs(self,args)
        self.gdisplay.resize(pos[0], pos[1])
        self.gcurve.append(pos=(pos[0],pos[1],2*dz), color=self.color)
                    
class gdots:
    def __init__(self, **args):
        pos = constructorargs(self,args)
        self.size = 5
        if args.has_key('size'):
            self.size = args['size']
        self.shape = 'round'
        if args.has_key('shape'):
            self.shape = args['shape']
        # For now, restrict to single color
        self.dots = points(display=self.gdisplay.display, color=self.color,
                               size=self.size, shape=self.shape, size_units="pixels")
        if pos is not None:
            for p in pos:
                self.plot(pos=p)
        else:
            if type(self.color) is ndarray and c.shape[0] > 1:
                raise RuntimeError, "Cannot give an array of colors without giving pos."

    def plot(self, **args):
        if args.has_key('pos'):
            pos = array(args['pos'])
        else:
            raise RuntimeError, "Cannot plot without giving pos."
        c = self.color
        if args.has_key('color'):
            c = args['color']
        if pos.ndim == 1: # a single position
                self.gdisplay.resize(pos[0], pos[1])
                self.dots.append(pos=(pos[0],pos[1],2*dz), color=c) 
        else:
            for p in pos: # an array of positions
                self.gdisplay.resize(p[0], p[1])
                self.dots.append(pos=(p[0],p[1],2*dz), color=c) 

class gvbars:
    def __init__(self, **args):
        pos = constructorargs(self,args)
        self.vbars = faces(display=self.gdisplay.display,
                           pos=[(0,0,0),(0,0,0),(0,0,0)],
                           normal=znormal, color=self.color)
        if pos is not None:
            for xy in pos:
                self.plot(pos=xy)

    def makevbar(self, pos):
        x,y = pos[0],pos[1]
        if y < 0.0:
            ymin = y
            ymax = 0
        else:
            ymin = 0.0
            ymax = y
        d = self.delta/2.0
        return [(x-d,ymin,dz),(x+d,ymin,dz),(x-d,ymax,dz),
                (x-d,ymax,dz),(x+d,ymin,dz),(x+d,ymax,dz)]

    def plot(self, **args):
        pos = primitiveargs(self,args)
        self.gdisplay.resize(pos[0], pos[1])
        for pt in self.makevbar(pos):
            self.vbars.append(pos=(pt[0],pt[1],dz), normal=znormal)

class ghbars:
    def __init__(self, **args):
        pos = constructorargs(self,args)
        self.hbars = faces(display=self.gdisplay.display,
                           pos=[(0,0,0),(0,0,0),(0,0,0)],
                           normal=znormal, color=self.color)
        if pos is not None:
            for xy in pos:
                self.plot(pos=xy)

    def makehbar(self, pos):
        x,y = pos[0],pos[1]
        if x < 0.0:
            xmin = x
            xmax = 0
        else:
            xmin = 0.0
            xmax = x
        d = self.delta/2.0
        return [(xmin,y-d,dz),(xmax,y-d,dz),(xmin,y+d,dz),
                (xmin,y+d,dz),(xmax,y-d,dz),(xmax,y+d,dz)]

    def plot(self, **args):
        pos = primitiveargs(self,args)
        self.gdisplay.resize(pos[0], pos[1])
        for pt in self.makehbar(pos):
            self.hbars.append(pos=(pt[0],pt[1],dz), normal=znormal)

class ghistogram:
    def __init__(self, bins=None, accumulate=0, average=0,
                 delta=None, gdisplay=None, color=None):
        if gdisplay is None:
            if lastgdisplay is None:
                gdisplay = getgdisplay()
            else:
                gdisplay = lastgdisplay
        self.gdisplay = gdisplay
        self.bins = bins
        self.nhist = 0 # number of calls to plot routine
        self.accumulate = accumulate # add successive data sets
        self.average = average # display accumulated histogram divided by self.nhist
        if color is None:
            self.color = self.gdisplay.foreground
        else:
            self.color = color
        self.histaccum = zeros(len(bins))
        if delta is None:
            self.delta = (bins[1]-bins[0])
        else:
            self.delta = delta
        self.vbars = faces(display=self.gdisplay.display,
                           pos=[(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0)],
                           normal=znormal, color=self.color)
        self.gdisplay.resize(bins[0]-self.delta,1.0)
        self.gdisplay.resize(bins[-1]+self.delta,1.0)

    def makehistovbar(self, pos):
        x,y = pos[0],pos[1]
        d = 0.8*self.delta/2.0
        return [(x-d,0.0,dz),(x+d,0.0,dz),(x-d,y,dz),
                (x-d,y,dz),(x+d,0.0,dz),(x+d,y,dz)]

    def plot(self, data=None, accumulate=None, average=None, color=None):
        if color is None:
            color = self.color
        if accumulate is not None:
            self.accumulate = accumulate
        if average is not None:
            self.average = average
        if data is None: return
        n = searchsorted(sort(data), self.bins)
        n = concatenate([n, [len(data)]])
        histo = n[1:]-n[:-1]
        if self.accumulate:
            self.histaccum = self.histaccum+histo
        else:
            self.histaccum = histo
        self.nhist = self.nhist+1.
        ymax = max(self.histaccum)
        if ymax == 0.: ymax == 1.
        self.gdisplay.resize(self.bins[-1],ymax)
        for nbin in range(len(self.bins)):
            pos = [self.bins[0]+(nbin+0.5)*self.delta, self.histaccum[nbin]]
            if self.nhist == 1.:
                for pt in self.makehistovbar(pos):
                    self.vbars.append(pos=pt, normal=znormal)
            else:
                if self.accumulate and self.average: 
                    pos[1] /= self.nhist
                # (nbin+1) because self.vbars was initialized with one dummy bar
                self.vbars.pos[6*(nbin+1)+2][1] = pos[1]
                self.vbars.pos[6*(nbin+1)+3][1] = pos[1]
                self.vbars.pos[6*(nbin+1)+5][1] = pos[1]

if __name__ == '__main__':
    from time import clock
    # If xmax, xmin, ymax, or ymin specified, the related axis is not autoscaled
    # Can turn off autoscaling with
    #    oscillation.autoscale[0]=0 for x or oscillation.autoscale[1]=0 for y
    
    oscillation = gdisplay(title='Test Plotting', xtitle='Time', ytitle='Response',
                           x=0, y=0, width=800, height=400)

    funct1 = gcurve(color=color.cyan)
    funct2 = gvbars(color=color.red, delta=0.8)
    funct3 = gdots(color=color.yellow)

    print "start timing"
    tt = clock()
    for n in range(1):
        for t in arange(-30, 76, 1):
            funct1.plot(pos=(t, 5.0+5.0*cos(-0.2*t)*exp(0.015*t)) )
            funct2.plot(pos=(t, 2.0+5.0*cos(-0.1*t)*exp(0.015*t)) )
            funct3.plot(pos=(t, 5.0*cos(-0.03*t)*exp(0.015*t)) )
    tt = clock()-tt

    histo = gdisplay(title='Histogram', x=0, y=400, width=800,height=400)
    datalist1 = [5, 37, 12, 21, 25, 28, 8, 63, 52, 75, 7]
    data = ghistogram(bins=arange(-20, 80, 10), color=color.red)
    data.plot(data=datalist1)
    datalist2 = [7, 23, 25, 72, -15]
    data.plot(data=datalist2, accumulate=1)
    print '%0.1f sec' % tt


