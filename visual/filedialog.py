from visual import *
import os 
from time import clock

def save_file(file_extensions=None, x=100, y=100, title="Save", mode='w', maxfiles=20):
    if maxfiles < 5: maxfiles = 5
    if mode[0] != 'w':
        raise ValueError, "To save a file, mode must start with 'w'."
    if file_extensions is not None:
        if isinstance(file_extensions, (list,tuple)):
            raise ValueError, "Only one file extension can be specified."
        file_extensions = [file_extensions]
    return filedialog(file_extensions=file_extensions,
                   x=x, y=y, title=title, mode=mode, maxfiles=maxfiles)

def get_file(file_extensions=None, x=100, y=100, title="Open", mode='rU', maxfiles=20):
    if maxfiles < 5: maxfiles = 5
    if mode[0] != 'r' and mode != 'U':
        raise ValueError, "To read a file, mode must start with 'r'."
    if file_extensions is not None:
        if not isinstance(file_extensions, (list,tuple)):
            file_extensions = [file_extensions]
    return filedialog(file_extensions=file_extensions,
                   x=x, y=y, title=title, mode=mode, maxfiles=maxfiles)

def filedialog(file_extensions=None, x=100, y=100, title="Open", mode='rU', maxfiles=20):
    # file_extensions is a list of types (reading) or a 1-element list (writing)
    writing =  not (mode[0] == 'r' or mode == 'U')
    filecolor = color.black
    dircolor = (0,0.5,0.5)
    selectcolor = (.7,1,1)
    inactivecolor = (0.8,0.8,0.8)
    activecolor = (0.6,0.6,0.6)
    winwidth = 300
    hitem = 20 # pixel height of each menu listing
    ctrls = 20 # button area
    hcanvas = hitem*(maxfiles+3)+ctrls # approx height without title bar
    currentdisplay = display.get_selected()
    menus = display(background=color.white, foreground=color.black, exit=0, range=100,
                       x=x, y=y, title=title, fov=0.001,
                       # allow 30 pixels for title bar
                       width=winwidth, height=30+hcanvas+ctrls)
    if menus.width >= hcanvas+ctrls:
        hmenu = 200.*hitem/menus.width
        ytop = 100.*hcanvas/menus.width-2*hmenu
        ybottom = ytop-maxfiles*hmenu
        ytopscroll = 100.*(hcanvas+ctrls)/menus.width
        ybottomscroll = -ytopscroll
        xmax = 100.
        xmin = -xmax
        scroll_edge = 87.
        okaypos = (20,ybottom-1.2*hmenu,0.1)
        cancelpos = (60,ybottom-1.2*hmenu,0.1)
        okaysize = (35,1.1*hmenu,0.1)
    else:
        hmenu = 200.*hitem/hcanvas
        ytop = 100.-2*hmenu
        ybottom = ytop-maxfiles*hmenu
        ytopscroll = 100.
        ybottomscroll = -ytopscroll
        xmax = 100.*menus.width/(hcanvas+ctrls)
        xmin = -xmax
        scroll_edge = xmax-14*menus.width/hcanvas
        okaypos = (20.*menus.width/hcanvas,ybottom-1.2*hmenu,0.1)
        cancelpos = (60.*menus.width/hcanvas,ybottom-1.2*hmenu,0.1)
        okaysize = (35.*menus.width/hcanvas,1.1*hmenu,0.1)
    okay = box(pos=okaypos, size=okaysize, color=inactivecolor)
    if writing:
        t = 'Save'
    else:
        t = 'Open'
    okaylabel = label(pos=okaypos, text=t, color=color.black, opacity=0, box=0)
    cancel = box(pos=cancelpos, size=okaysize, color=inactivecolor)
    label(pos=cancelpos, text='Cancel', color=color.black, opacity=0, box=0)
    go_up = box(pos=(cancel.pos.x,ytop+hmenu,0), size=okaysize, color=inactivecolor)
    go_up_arr = arrow(pos=(go_up.pos.x,go_up.pos.y-0.4*hmenu,0), axis=(0,0.9*hmenu,0),
          fixedwidth=1, shaftwidth=0.3*hmenu, color=(0.9,0,0))
    showdir = label(pos=(xmin+0.2*(xmax-scroll_edge),ytop+hmenu,0), text='',
                    color=dircolor, opacity=0, xoffset=1, box=0, line=0)
    if writing:
        # A bug in Visual 3 makes it necessary not to allow len(getname.text) < 1
        getname = label(pos=(xmin+0.5*(xmax-scroll_edge),okay.y,0), border = 2,
                        text='|', box=0, xoffset=1, line=0, opacity=0)
        z = 0.1
        curve(pos=[(getname.x,getname.y-0.5*hmenu,z), (getname.x,getname.y+0.5*hmenu,z),
                   (okay.x-1.2*0.5*okay.length,getname.y+0.5*hmenu,z), 
                   (okay.x-1.2*0.5*okay.length,getname.y-0.5*hmenu,z),
                   (getname.x,getname.y-0.5*hmenu,z)])

    labels = []
    for n in range(maxfiles):
        labels.append(label(pos=(xmin+0.5*(xmax-scroll_edge),ytop-n*hmenu),
                            text='', opacity=0, box=0,
                            xoffset=1, line=0))
        
    scrolltrack = box(pos=(0.5*(scroll_edge+xmax),0,0.02),
                      color=color.white, size=(xmax-scroll_edge,200,0.001), visible=0)
    scrollside = curve(pos=[(scroll_edge,100,.03),(scroll_edge,-100,.03)],
                       color=(0.8,0.8,0.8), visible=0)
    scroll = box(pos=(0.5*(scroll_edge+xmax),0,0.04), offset=vector(0,0,0),
                 color=inactivecolor, size=((xmax-scroll_edge+1),0,0.1), visible=0)
    
    shade = box(pos=(0,0,0), color=(.95,.95,.95), size=(200,hmenu,0.01), visible=0)
    select = box(pos=(0,0,0.01), color=selectcolor, size=(200,hmenu,0.01), visible=0)
    clicktime = -1

    while menus.visible:
        shade.visible = 0
        select.visible = 0
        highlighted = None
        selected = None
        changedir = False
        drag = False
        topmenu = 0
        showdir.text = os.path.split(os.getcwd())[-1]
        allfiles = os.listdir(os.curdir)
        files = []
        for f in allfiles:
            is_a_dir = os.path.isdir(f)
            if is_a_dir or (file_extensions is None):
                files.append([f,is_a_dir,False]) # file name, whether a directory, whether selected
            else:
                period = f.rfind('.')
                if period:
                    if f[period:] in file_extensions:
                        files.append([f,is_a_dir,False])
        Nfiles = len(files)
        need_to_scroll = (Nfiles > maxfiles)
        if need_to_scroll:
            Nfiles = maxfiles
            hscroll = (ytopscroll-ybottomscroll)*maxfiles/len(files)
            if hscroll < hmenu:
                hscroll = hmenu
            dy = (ytopscroll-ybottomscroll-hscroll)/(len(files)-maxfiles)
            scrolltrack.visible = 1
            scrollside.visible = 1
            scroll.y = ytopscroll-0.5*hscroll
            scroll.height = hscroll
            scroll.visible = 1
        else:
            scrolltrack.visible = 0
            scrollside.visible = 0
            scroll.visible = 0

        for n in labels:
            n.text = ''
        for n, f in enumerate(files[:Nfiles]):
            lcolor = filecolor
            if f[1]: lcolor = dircolor
            labels[n].text = f[0]
            labels[n].color = lcolor

        if writing:
            getname.text = '|'
            ending = '|'
        blink = clock()
        blinkon = True
        while menus.visible:
            rate(50)
            # A bug in Visual 3 makes it necessary not to allow len(getname.text) < 1
            if writing and clock()-blink > 0.5:
                blink = clock()
                blinkon = not blinkon
                if blinkon:
                    ending = '|'
                else:
                    ending = ' '
                if getname.text == '':
                    getname.text = ending
                elif getname.text == '|' or getname.text == ' ':
                    getname.text = ending
                elif getname.text[-1] == '|' or getname.text[-1] == ' ':
                    getname.text = getname.text[:-1]+ending 
                else:
                    getname.text += ending
            mpos = menus.mouse.pos
            if writing and menus.kb.keys: # event waiting to be processed?
                s = menus.kb.getkey() # get keyboard info; make sure string length never 0
                if s == '\n':
                    shade.visible = 0
                    select.visible = 0
                    ret = finish_save(getname.text, file_extensions, mode, menus, labels, currentdisplay)
                    if ret:
                        return ret
                    if highlighted: shade.visible = 1
                    if selected: select.visible = 1
                elif len(s) == 1 and s != '|':
                    if getname.text == '': # should never happen
                        getname.text = s+ending
                    elif getname.text[-1] == ending:
                        getname.text = getname.text[:-1]+s+ending
                    else:
                        getname.text = getname.text+s+ending # add new character
                elif s == 'backspace' or s == 'delete':
                    if getname.text == '': # should never happen
                        getname.text = ending
                    elif getname.text[-1] == ending:
                        getname.text = getname.text[:-2]+ending # erase character
                    else:
                        if len(getname.text) <= 1: # should never happen
                            getname.text = ending
                        else:
                            getname.text = getname.text[:-1]+ending # erase character
                elif s == 'shift+delete' or s == 'shift+backspace':
                    getname.text = ending # erase all text
            if menus.mouse.events:
                m = menus.mouse.getevent()
                mpos = m.pos
                nmenu = int((ytop+0.5*hmenu-mpos.y)/hmenu)
                if mpos.y > ytop+0.5*hmenu: nmenu = -1
                if drag and m.release == 'left':
                    drag = False
                elif need_to_scroll and m.pick == scroll:
                    scroll.color = dircolor
                    scroll.offset = scroll.y-mpos.y
                    drag = True
                elif m.click == 'left':

                    # Check for clicking go up or open or cancel
                    if m.pick == go_up or m.pick == go_up_arr:
                        os.chdir('../')
                        changedir = True
                        break
                    if m.pick == cancel:
                        return finish_get(None, mode, menus, currentdisplay)
                    elif m.pick == okay:
                        if writing and getname.text != '|':
                            shade.visible = 0
                            select.visible = 0
                            ret = finish_save(getname.text, file_extensions, mode, menus, labels, currentdisplay)
                            if ret:
                                return ret
                            if highlighted: shade.visible = 1
                            if selected: select.visible = 1
                        if selected is not None:
                            filename, is_a_dir, s = files[selected]
                            if is_a_dir:
                                os.chdir(filename)
                                changedir = True
                                break
                            elif not writing:
                                return finish_get(filename, mode, menus, currentdisplay)
                        
                    # Handle doubleclick on a name
                    clicktime = clock()-clicktime
                    if topmenu+nmenu == selected and clicktime < 0.5:
                        filename, is_a_dir, s = files[selected]
                        if is_a_dir:
                            os.chdir(filename)
                            changedir = True
                            break
                        else:
                            if writing:
                                getname.text = filename+'|'
                            else:
                                return finish_get(filename, mode, menus, currentdisplay)
                        
                    # Handle singleclick on a name
                    if (0 <= nmenu <= Nfiles-1):
                        select.y = ytop-nmenu*hmenu
                        select.visible = 1
                        if selected:
                            files[selected][2] = False
                        selected = topmenu+nmenu
                        files[selected][2] = True
                        if writing:
                            if files[selected][1]:
                                okaylabel.text = 'Open'
                            else:
                                okaylabel.text = 'Save'
                        clicktime = clock()
                    elif selected:
                        select.visible = 0
                        files[selected][2] = False
                        selected = 0
                        if writing:
                            okaylabel.text = 'Save'
                        
            if drag:
                newy = mpos.y+scroll.offset
                if newy+0.5*hscroll >= ytopscroll:
                    scroll.y = ytopscroll-0.5*hscroll
                    scroll.offset = scroll.y-mpos.y
                elif newy-0.5*hscroll <= ybottomscroll:
                    scroll.y = ybottomscroll+0.5*hscroll
                    scroll.offset = scroll.y-mpos.y
                else:
                    scroll.y = newy
                newtopmenu = int((ytopscroll-0.5*hscroll-scroll.y)/dy)
                if newtopmenu != topmenu:
                    topmenu = newtopmenu
                    select.visible = 0
                    for n, lab in enumerate(labels):
                        lab.text = files[n+topmenu][0]
                        if files[n+topmenu][2]:
                            select.y = ytop-n*hmenu
                            select.visible = 1
                        elif files[n+topmenu][1]:
                            lab.color = dircolor
                        else:
                            lab.color = filecolor
            else:
                if need_to_scroll:
                    if menus.mouse.pick == scroll:
                        scroll.color = activecolor
                    else:
                        scroll.color = inactivecolor
                        
                if menus.mouse.pick == go_up or menus.mouse.pick == go_up_arr:
                    go_up.color = activecolor
                else:
                    go_up.color = inactivecolor
                    
                if menus.mouse.pick == cancel:
                    cancel.color = activecolor
                else:
                    cancel.color = inactivecolor
                    
                if menus.mouse.pick == okay:
                    okay.color = activecolor
                else:
                    okay.color = inactivecolor
                    
                if need_to_scroll and mpos.x >= scroll_edge:
                    shade.visible = 0
                    highlighted = None
                else:
                    nmenu = int((ytop+0.5*hmenu-mpos.y)/hmenu)
                    if mpos.y > ytop+0.5*hmenu: nmenu = -1
                    if mpos.y < ytop+0.5*hmenu-hmenu*Nfiles: nmenu = -1
                    if (0 <= nmenu <= Nfiles):
                        shade.y = ytop-nmenu*hmenu
                        shade.visible = 1
                        highlighted = nmenu
                    else:
                        shade.visible = 0
                        highlighted = None
        if changedir: continue
        break
    currentdisplay.select()
    return None

def finish_get(filename, mode, menus, currentdisplay):
    menus.visible = 0
    del menus
    currentdisplay.select()
    if filename is None:
        return None
    return open(str(filename), mode)

def finish_save(filename, file_extensions, mode, menus, labels, currentdisplay):
    if filename == '':
        return None
    if filename[-1] == '|' or filename[-1] == ' ':
        filename = filename[:-1]
    if filename == '':
        return None
    t = filename.split(".")
    ext = ''
    if len(t) > 0:
        ext = '.'+t[-1]
    elif t[0] == '':
        return None
    if file_extensions is not None:
        if ext != file_extensions[0]:
            filename += file_extensions[0]
    try:
        fd = open(str(filename), 'r') # see whether file already exists
    except:
        menus.visible = 0
        del menus
        currentdisplay.select()
        return open(str(filename), mode)
    fd.close()
    for a in labels:
        a.visible = 0
    inactivecolor = (0.8,0.8,0.8)
    activecolor = (0.6,0.6,0.6)
    templabel = label(pos=(0,15,0.3), text="%s already exists" % filename, box=0, opacity=0)
    overwrite = box(pos=(-30,-5,0.4), size=(50,15,.1), color=inactivecolor)
    overlabel = label(pos=overwrite.pos, text="Overwrite", box=0, opacity=0)
    cancel = box(pos=(30,-5,0.4), size=(50,15,.1), color=inactivecolor)
    cancellabel = label(pos=cancel.pos, text="Cancel", box=0, opacity=0)
    while menus.visible:
        rate(50)
        if menus.mouse.events:
            m = menus.mouse.getevent()
            if m.click == 'left':
                if m.pick == overwrite:
                    menus.visible = 0
                    del menus
                    currentdisplay.select()
                    return open(str(filename), mode)
                if m.pick == cancel:
                    templabel.visible = 0
                    overwrite.visible = 0
                    overlabel.visible = 0
                    cancel.visible = 0
                    cancellabel.visible = 0
                    del templabel
                    del overwrite
                    del overlabel
                    del cancel
                    del cancellabel
                    for a in labels:
                        a.visible = 1
                    return None
        if menus.mouse.pick == overwrite:
            overwrite.color = activecolor
        else:
            overwrite.color = inactivecolor
        if menus.mouse.pick == cancel:
            cancel.color = activecolor
        else:
            cancel.color = inactivecolor
    return None

# Test routines

##fd = save_file('.txt')
##if fd is None:
##    print 'Canceled'
##else:
##    print fd.name
##    fd.write("This is a test\nIt is only a test")
##    fd.close()

##fd = get_file()
##if fd is None:
##    print "Canceled"
##else:
##    print fd.name
##    data = fd.read()
##    print data



