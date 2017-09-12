from visual import *

__all__ = visual._fix_symbols( globals() ) + [
    'controls','button','toggle','slider','menu']

# Bruce Sherwood, March 2002
# Import this module to create buttons, toggle switches, sliders, and pull-down menus.
# See test routine at end of this module for an example of how to use controls.

lastcontrols = None # the most recently created controls window
gray = (0.7, 0.7, 0.7)
darkgray = (0.5, 0.5, 0.5)

class controls: # make a special window for buttons, sliders, and pull-down menus
    def __init__(self, x=0, y=0, width=300, height=320, range=100,
                 title=None, foreground=None, background=None):
        global lastcontrols
        lastcontrols = self
        currentdisplay = display.get_selected()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.range = range
        self.title = title
        if title is None:
            title = 'Controls'
        if foreground is None:
            foreground = color.white
        if background is None:
            background = color.black
        self.foreground = foreground
        self.background = background
        self.display = display(title=title, x=x, y=y, range=range,
                width=width, height=height, fov=0.4,
                foreground=foreground, background=background,
                userzoom=0, userspin=0)
        self.display.lights=[distant_light(direction=(0,0,1),color=color.white)]
        self.focus = None
        self.lastpos = None
        self.controllist = []
        currentdisplay.select()

    def addcontrol(self, control):
        self.controllist.append(control)

    def interact(self):
        if self.display.mouse.events: 
            m = self.display.mouse.getevent()
            if m.press == 'left' and m.pick:
                picked = m.pick
                if self.focus: # have been moving over menu with mouse up
                    picked = self.focus
                for control in self.controllist:
                    if control.active is picked:
                        self.focus = control
                        control.highlight(m.pos)
            elif m.release == 'left':
                focus = self.focus
                self.focus = None # menu may reset self.focus for "sticky" menu
                if focus:
                    focus.unhighlight(m.pos)
        elif self.focus: # if dragging a control
            pos = self.display.mouse.pos
            if pos != self.lastpos:
                self.focus.update(pos)
                self.lastpos = pos

class ctrl(object): # common aspects of buttons, sliders, and menus
    # Note: ctrl is a subclass of "object" in order to be a new-type class which
    # permits use of the new "property" feature exploited by buttons and sliders.
    def __init__(self, args):
        if args.has_key('controls'):
            self.controls = args['controls']
        elif lastcontrols is None:
            self.controls = controls()
        else:
            self.controls = lastcontrols
        self.controls.addcontrol(self)
        self.pos = vector(0,0)
        self.action = None
        if args.has_key('pos'):
            self.pos = vector(args['pos'])
        if args.has_key('value'):
            self.value = args['value']
        if args.has_key('action'):
            self.action = args['action']
            
    def highlight(self, pos):
        pass
        
    def unhighlight(self, pos):
        pass

    def update(self, pos):
        pass
        
    def execute(self):
        if self.action:
            self.action()

class button(ctrl):
    def __init__(self, **args):
        self.type = 'button'
        self.value = 0
        ctrl.__init__(self, args)
        width = height = 40
        bcolor = gray
        edge = darkgray
        self.__text = ''
        if args.has_key('width'):
            width = args['width']
        if args.has_key('height'):
            height = args['height']
        if args.has_key('text'):
            self.__text = args['text']
        if args.has_key('color'):
            bcolor = args['color']
        disp = self.controls.display
        framewidth = width/10.
        self.thick = 2.*framewidth
        self.box1 = box(display=disp, pos=self.pos+vector(0,height/2.-framewidth/2.,0),
                       size=(width,framewidth,self.thick), color=edge)
        self.box2 = box(display=disp, pos=self.pos+vector(-width/2.+framewidth/2.,0,0),
                       size=(framewidth,height,self.thick), color=edge)
        self.box3 = box(display=disp, pos=self.pos+vector(width/2.-framewidth/2.,0,0),
                       size=(framewidth,height,self.thick), color=edge)
        self.box4 = box(display=disp, pos=self.pos+vector(0,-height/2.+framewidth/2.,0),
                       size=(width,framewidth,self.thick), color=edge)
        self.button = box(display=disp, pos=self.pos+vector(0,0,self.thick/2.+1.),
                       size=(width-2.*framewidth,height-2.*framewidth,self.thick), color=bcolor)
        self.label = label(display=disp, pos=self.button.pos, color=color.black,
                           text=self.__text, line=0, box=0, opacity=0)
        self.active = self.button

    def gettext(self):
        return self.label.text

    def settext(self, text):
        self.label.text = text

    text = property(gettext, settext) # establishes special getattr/setattr handling

    def highlight(self, pos):
        self.button.pos.z -= self.thick
        self.label.pos.z -= self.thick
        self.value = 1
        
    def unhighlight(self, pos):
        self.button.pos.z += self.thick
        self.label.pos.z += self.thick
        self.value = 0
        self.execute()

class toggle(ctrl):
    def __init__(self, **args):
        self.type = 'toggle'
        self.__value = 0
        ctrl.__init__(self, args)
        width = height = 20
        self.angle = pi/6. # max rotation of toggle
        bcolor = gray
        edge = darkgray
        self.__text0 = ''
        self.__text1 = ''
        if args.has_key('width'):
            width = args['width']
        if args.has_key('height'):
            height = args['height']
        if args.has_key('text0'):
            self.__text0 = args['text0']
        if args.has_key('text1'):
            self.__text1 = args['text1']
        if args.has_key('color'):
            bcolor = args['color']
        if args.has_key('value'):
            self.__value = args['value']
        diskthick = width/4.
        diskradius = height/2.
        ballradius = 0.6*diskradius
        self.rodlength = 1.2*diskradius+ballradius
        disp = self.controls.display
        self.frame = frame(display=disp, pos=self.pos, axis=(1,0,0))
        self.back = box(display=disp, frame=self.frame, pos=(0,0,0),
                        size=(width,height,0.3*diskradius), color=darkgray)
        self.disk1 = cylinder(display=disp, frame=self.frame, pos=(-diskthick,0,0),
                              axis=(-diskthick,0), radius=diskradius, color=gray)
        self.disk2 = cylinder(display=disp, frame=self.frame, pos=(diskthick,0,0),
                              axis=(diskthick,0), radius=diskradius, color=gray)
        self.rod = cylinder(display=disp, frame=self.frame, pos=(0,0,0),
                              axis=(0,0,self.rodlength), radius=width/8., color=gray)
        self.ball = sphere(display=disp, frame=self.frame, pos=(0,0,self.rodlength),
                              radius=ballradius, color=gray)
        self.label0 = label(display=disp, frame=self.frame, pos=(0,-1.0*height), text=self.__text0,
                           line=0, box=0, opacity=0)
        self.label1 = label(display=disp, frame=self.frame, pos=(0,1.0*height), text=self.__text1,
                           line=0, box=0, opacity=0)
        self.settoggle(self.__value)
        self.active = self.ball

    def settoggle(self, val):
        self.__value = val
        if val == 1:
            newpos = self.rodlength*vector(0,sin(self.angle), cos(self.angle))
        else:
            newpos = self.rodlength*vector(0,-sin(self.angle), cos(self.angle))
        self.rod.axis = newpos
        self.ball.pos = newpos
             
    def getvalue(self):
        return self.__value

    def setvalue(self, val):
        self.settoggle(val)
        self.__value = val

    value = property(getvalue, setvalue) # establishes special getattr/setattr handling

    def gettext0(self):
        return self.label0.text

    def settext0(self, text):
        self.label0.text = text

    text0 = property(gettext0, settext0) # establishes special getattr/setattr handling

    def gettext1(self):
        return self.label1.text

    def settext1(self, text):
        self.label1.text = text

    text1 = property(gettext1, settext1) # establishes special getattr/setattr handling
        
    def unhighlight(self, pos):
        if self.controls.display.mouse.pick is self.active:
            self.__value = not(self.__value)
            self.settoggle(self.__value)
            self.execute()

class slider(ctrl):
    def __init__(self, **args):
        self.type = 'slider'
        self.__value = 0
        ctrl.__init__(self, args)
        self.length = 100.
        width = 10.
        shaftcolor = darkgray
        scolor = gray
        self.min = 0.
        self.max = 100.
        self.axis = vector(1,0,0)
        if args.has_key('axis'):
            self.axis = vector(args['axis'])
            self.length = mag(self.axis)
            self.axis = norm(self.axis)
        if args.has_key('length'):
            self.length = args['length']
        if args.has_key('width'):
            width = args['width']
        if args.has_key('min'):
            self.min = args['min']
            if self.__value == 0:
                self.__value = self.min
        if args.has_key('max'):
            self.max = args['max']
        if args.has_key('color'):
            scolor = args['color']
        disp = self.controls.display
        self.shaft = box(display=disp, 
                       pos=self.pos+self.axis*self.length/2., axis=self.axis,
                       size=(self.length,0.5*width,0.5*width), color=shaftcolor)
        self.indicator = box(display=disp,
                       pos=self.pos+self.axis*self.__value*self.length/(self.max-self.min),
                       axis=self.axis,
                       size=(width,width,width), color=scolor)
        self.active = self.indicator

    def getvalue(self):
        return self.__value

    def setvalue(self, val):
        self.update(self.pos+self.axis*val*self.length/(self.max-self.min))
        self.__value = val

    value = property(getvalue, setvalue) # establishes special getattr/setattr handling

    def update(self, pos):
        val = dot((pos-self.pos),self.axis)*(self.max-self.min)/self.length
        if val < self.min:
            val = self.min
        elif val > self.max:
            val = self.max
        if val != self.__value:
            self.indicator.pos = self.pos+self.axis*val*self.length/(self.max-self.min)
            self.__value = val
            self.execute()

class menu(ctrl):
    def __init__(self, **args):
        self.type = 'menu'
        ctrl.__init__(self, args)
        self.items = []
        self.width = self.height = 40
        self.text = 'Menu'
        self.__value = None
        self.color = gray
        self.nitem = 0
        self.open = 0 # true if menu display open in the window
        self.action = 1 # dummy placeholder; what is driven is menu.execute()
        if args.has_key('width'):
            self.width = args['width']
        if args.has_key('height'):
            self.height = args['height']
        if args.has_key('text'):
            self.text = args['text']
        if args.has_key('color'):
            self.color = args['color']
        self.thick = 0.2*self.width
        disp = self.controls.display
        self.active = box(display=disp, pos=self.pos+vector(0,0,self.thick),
                       size=(self.width,self.height,self.thick), color=self.color)
        self.label = label(display=disp, pos=self.active.pos, color=color.black,
                           text=self.text, line=0, box=0, opacity=0)

    def getvalue(self):
        return self.__value

    value = property(getvalue, None) # establishes special getattr/setattr handling

    def inmenu(self, pos): # return item number (0-N) where mouse is, or -1
        # note that item is 0 if mouse is in menu title
        if self.pos.x-self.width/2. < pos.x < self.pos.x+self.width/2.:
            nitem = int((self.pos.y+self.height/2.-pos.y)/self.height)
            if 0 <= nitem <= len(self.items):
                return(nitem)
            else:
                return(-1)
        return(-1)
        
    def highlight(self, pos): # mouse down: open the menu, displaying the menu items
        self.nitem = self.inmenu(pos)
        if self.open: # "sticky" menu already open
            if self.nitem > 0:
                self.update(pos)
            else:
                self.unhighlight(pos)
                self.open = 0
            return
        pos = self.pos-vector(0,self.height,0)
        self.boxes = []
        self.highlightedbox = None
        disp = self.controls.display
        for item in self.items:
            self.boxes.append( (box(display=disp, pos=pos+vector(0,0,self.thick),
                       size=(self.width,self.height,self.thick), color=self.color),
                       label(display=disp, pos=pos+vector(0,0,self.thick), color=color.black,
                       text=item[0], line=0, box=0, opacity=0)) )
            pos = pos-vector(0,self.height,0)

    def unhighlight(self, pos): # mouse up: close the menu; selected item will be executed
        self.nitem = self.inmenu(pos)
        if self.nitem == 0 and not self.open: # don't close if mouse up in menu title
            self.controls.focus = self # restore menu to be in focus
            self.open = 1
            return
        for box in self.boxes:
            box[0].visible = 0
            box[1].visible = 0
        self.boxes = []
        self.open = 0
        self.execute()
            
    def update(self, pos): # highlight an individual item during drag
        self.nitem = self.inmenu(pos)
        if self.nitem > 0:
            if self.highlightedbox is not None:
                self.highlightedbox.color = gray
            if self.items[self.nitem-1][1]: # if there is an associated action
                self.highlightedbox = self.boxes[self.nitem-1][0]
                self.highlightedbox.color = darkgray
        else:
            if self.highlightedbox is not None:
                self.highlightedbox.color = gray
            self.highlightedbox = None

    def execute(self):
        if self.nitem > 0:
            self.__value = self.items[self.nitem-1][0]
            action = self.items[self.nitem-1][1]
            if action:
                action()

if __name__ == '__main__': # for testing the module

# Create "call-back" routines, routines that are called by the interact
# machinery when certain mouse events happen:

    def setdir(direction): # called on button up events
        cube.dir = direction

    def togglecubecolor(): # called on toggle switch flips
        if t1.value:
            cube.color = color.cyan
        else:
            cube.color = color.red

    def cubecolor(value): # called on a menu choice
        cube.color = value
        if cube.color == color.red:
            t1.value = 0 # make toggle switch setting consistent with menu choice
        else:
            t1.value = 1
        
    def setrate(obj): # called on slider drag events
        cuberate(obj.value) # value is min-max slider position
        if obj is s1:
            s2.value = s1.value # demonstrate coupling of the two sliders
        else:
            s1.value = s2.value

    def cuberate(value):
        cube.dtheta = 2*value*pi/1e4

    w = 350
    display(x=w, y=0, width=w, height=w, range=1.5, forward=-vector(0,1,1), newzoom=1)
    cube = box(color=color.red)

# In establishing the controls window, range=60 means what it usually means:
# (0,0) is in the center of the window, and (60,60) is the lower right corner.
# If range is not specified, the default is 100.
    c = controls(x=0, y=0, width=w, height=w, range=60)

# Buttons have a "text" attribute (the button label) which can be read and set.
# Toggles have "text0" and "text1" attributes which can be read and set.
# Toggles and sliders have a "value" attribute (0/1, or location of indicator) which can be read and set.

# The pos attribute for buttons, toggles, and menus is the center of the control (like "box").
# The pos attribute for sliders is at one end, and axis points to the other end (like "cylinder").

# By default a control is created in the most recently created "controls" window, but you
# can change this by specifying "controls=..." when creating a button, toggle, slider, or menu.

# The Python construct "lambda: setdir(-1)" below passes the location of the setdir function
# to the interact machinery, which call the setdir function when an action
# is to be taken. This scheme ensures that the execution of the function takes place
# in the appropriate namespace context in the case of importing the controls module.

    bl = button(pos=(-30,30), height=30, width=40, text='Left', action=lambda: setdir(-1))
    br = button(pos=(30,30), height=30, width=40, text='Right', action=lambda: setdir(1))
    s1 = slider(pos=(-15,-40), width=7, length=70, axis=(1,0.7,0), action=lambda: setrate(s1))
    s2 = slider(pos=(-30,-50), width=7, length=50, axis=(0,1,0), action=lambda: setrate(s2))
    t1 = toggle(pos=(40,-30), width=10, height=10, text0='Red', text1='Cyan', action=lambda: togglecubecolor())
    m1 = menu(pos=(0,0,0), height=7, width=25, text='Options')

# After creating the menu heading, add menu items:
    m1.items.append(('Left', lambda: setdir(-1))) # specify menu item title and action to perform
    m1.items.append(('Right', lambda: setdir(1)))
    m1.items.append(('---------',None)) # a dummy separator
    m1.items.append(('Red', lambda: cubecolor(color.red)))
    m1.items.append(('Cyan', lambda: cubecolor(color.cyan)))

    s1.value = 70 # update the slider
    setrate(s1) # set the rotation rate of the cube
    setdir(-1) # set the rotation direction of the cube

    while 1:
        rate(100)
        c.interact() # check for events, drive actions; must be executed repeatedly in a loop
        cube.rotate(axis=(0,1,0), angle=cube.dir*cube.dtheta)
       
