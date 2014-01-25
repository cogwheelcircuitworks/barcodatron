"""

kitlabels - print labels with barcodes and graphics on regular and label printers

Zebra Printer Notes:
  Under printing preferences, set label size under page setup - For 3.5 x 1 labels, you 
  would use New.. to initially create it. Other settings: Orientation: portrait.
  In acrobat, under file->print>properties to actual size, portrait.

"""

# easy_install reportlab
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.graphics.barcode import code128, code39, qr
# Image requires Pil : http://effbot.org/downloads/PIL-1.1.7.win32-py2.7.exe
from reportlab.platypus import SimpleDocTemplate, Image
from reportlab.pdfbase.pdfmetrics import stringWidth
from pprint import pprint
import getopt
import sys
import os
import subprocess
import shlex
import re
import textwrap
import win32api
import time


import string
import random




# http://sourceforge.net/projects/pywin32/files/pywin32/Build%20214/pywin32-214.win32-py2.7.exe/download 
# ours

xwidth = yheight  = 0

gl_verbose = 0
mode = 't'
gl_filename = ''
  
gl_printer= 'acrobat'
#gl_printer= 'Zebra UPS 2844'
#gl_printer= 'Zebra 450 CTP'
gl_printer= 'zebra'

flip = False

barwidth = .0120*inch

acrobat  = os.path.normpath( "C:/Program Files/Adobe/Reader 11.0/Reader/AcroRd32.exe")
if (not os.path.exists(acrobat)):
  acrobat  = os.path.normpath("C:/Program Files/Adobe/Reader 10.0/Reader/AcroRd32.exe")
  if (not os.path.exists(acrobat)):
    acrobat  = os.path.normpath("C:/Program Files (x86)/Adobe/Reader 10.0/Reader/AcroRd32.exe")
    if (not os.path.exists(acrobat)):
      sys.stderr.write('can''t find acrobat\n')
      os._exit(1)

def genranstr():
  lst = [random.choice(string.ascii_letters + string.digits) for n in xrange(4)]
  str = ''.join(lst)
  return str

def v(m):
  global gl_verbose
  if (gl_verbose):
    pstderr(m)

def pstderr(m):
  sys.stderr.write(m + '\n')

def cutmark(canvas,x,y,xpol,ypol):
    v('------')
    cutlen = 10
    canvas.line(x, y, x+cutlen*xpol, y)
    v('cutmark() x,y,xe,ye %f %f %f %f' % (x, y, x+cutlen*xpol, y))
    canvas.line(x, y, x        , y+cutlen*ypol)
    v('cutmark() x,y,xe,ye %f %f %f %f' % (x, y, x        , y+cutlen*ypol))

def genkitlabel(canvas,xa,ya,xw,yh,contentlist,test=0,paper_size_no=0):
    """
    """
    v('[------genkitlabel()')
    x = xa
    y = ya
    m = .05*inch
    h = yh # calc height
    h -= m*2 # height - margin
    w = xw # calc width
    w -= m*2 # width - margin


    v('genkitlabel() ------')
    v('genkitlabel() xa,ya,xw,yh: %f %f %f %f' % (xa,ya,xw,yh))
    v('genkitlabel() m h w : %f %f %f' % ( m, h, w))

    xo = yo = m # origin
    canvas.setLineWidth(.01*inch)
    canvas.setStrokeColorRGB(.75,.75,.75)

    global xwidth
    if (not (xwidth/inch <= 3.50)):
      cutmark(canvas,x,y,1,1)
      cutmark(canvas,x+xw,y+yh,-1,-1)
      cutmark(canvas,x,y+yh,1,-1)
      cutmark(canvas,x+xw,y,-1,1)
  


    didlogo = False

    yloc = y + h 

    image_size = 1.2*inch
    logo_yloc = yloc-image_size+.2*inch

    yrel = 0

    for line in contentlist:
      if (line == '..' or line == '.'):
        flip = False
        break
      v('genkitlabel(): line:%s' %(line))
      token = line.split()
      if len(token) <=  0:
        continue

      dowhat = token[0].upper()

      #---
      global flip
      if (dowhat == 'FLIP'):
        flip = True

      elif (dowhat == 'LOGO'):
        v('LOGO')
        if (len(token) == 1):
          # no arg print logo
          if (paper_size_no == 3):
            image_size = 1*inch
            canvas.drawImage('logo512x512.png', x+m-.75*inch,logo_yloc, image_size, image_size, preserveAspectRatio=True)
          else:
            canvas.drawImage('logo512x512.png', x+m+.1*inch+2.4*inch,logo_yloc, image_size, image_size, preserveAspectRatio=True)
        else:
          # print arg
          arg = token[1]
          if (len(arg) == 1):
            # character. make it big
            if flip:
              # They said 'LOGO X', so we draw big fat X where the logo should be
              canvas.saveState()
              canvas.translate(x+m+.3*inch,logo_yloc+1*inch)
              canvas.scale(-1,-1)

              canvas.setFont('Helvetica-Bold',70) 
              canvas.drawString(0,0,token[1])

              canvas.restoreState()
            else:
              # They said 'LOGO X', so we draw big fat X where the logo should be
              canvas.setFont('Helvetica-Bold',70) 
              canvas.drawString(x+m-.45*inch,logo_yloc+.2*inch,token[1])
          else:
            # Multiple characters 
            if flip:
              # They said 'LOGO X', so we draw big fat X where the logo should be
              canvas.saveState()
              canvas.translate(x+m+.3*inch,logo_yloc+1*inch)
              canvas.scale(-1,-1)

              canvas.setFont('Helvetica-Bold',20) 
              canvas.drawString(.5*inch,.55*inch,arg[0])
              canvas.drawString(.5*inch,.30*inch,arg[1])
              canvas.drawString(.5*inch,.05*inch,arg[2])

              canvas.restoreState()
            else:
              # They said 'LOGO X', so we draw big fat X where the logo should be
              canvas.setFont('Helvetica-Bold',20) 
              canvas.drawString(x+m-.45*inch,logo_yloc+.80*inch,arg[0])
              canvas.drawString(x+m-.45*inch,logo_yloc+.55*inch,arg[1])
              canvas.drawString(x+m-.45*inch,logo_yloc+.30*inch,arg[2])


      #---
      elif (dowhat == 'BARCODE'):
          yloc = render_barcode(canvas, x,yloc, token[1], ' '.join(token[2:]))
          v('genkitlabel(): yloc now: %f' % (yloc))


      #---
      elif (dowhat == 'KEYVAL'):
        v('KEYVAL Width : ')
        yloc = render_key_and_value(canvas, x+m+.350*inch, yloc, token[1], ' '.join(token[2:]))
        #yinc = .150*inch
      ##
      ##

    v('genkitlabel() --- line:' + line)

    return line


def render_key_and_value(canvas,x,y,lhs,rhs,wraplen=40):
  """
  render a keyword:value pair. Keyword will be in bold
  """
  global xwidth
  global yheight

  yinc = .125*inch

  fontsize = 10
  v('render_key_and_value(): xwidth:%f yheight:%f ' % (xwidth,yheight))
  
  # little labels get special treatment
  if (xwidth/inch <= 3.50):
    v('render_key_and_value(): fixing wraplen for small labels')
    wraplen = 25
    fontsize = 9
    if flip:
      yinc = -.105*inch
    else:
      yinc = .105*inch

  lhs += ': '
  width = stringWidth(lhs,'Helvetica-Bold',fontsize)
  width *= 1.2
  if (width < .75*inch):
    width = .75*inch

  # draw keyword

  canvas.setFont('Helvetica-Bold',fontsize) 

  if flip:
    canvas.saveState()
    canvas.translate(x+2.45*inch,y+.25*inch)
    canvas.scale(-1,-1)

    canvas.drawString(0, 0, lhs.upper())

    canvas.restoreState()

  else:
    canvas.drawString(x, y, lhs.upper())

  # draw value

  canvas.setFont('Helvetica',fontsize) 
    
  yrel = 0
  lines = 0
  v('render_key_and_value(): y+yrel: %f' %(y+ yrel))

  text_line_list = textwrap.wrap(rhs,wraplen)
  for line in text_line_list:
    if flip:
      canvas.saveState()
      canvas.translate(x+width+1.00*inch, y+yrel+.25*inch)
      canvas.scale(-1,-1)

      canvas.drawString(0,0, line)

      canvas.restoreState()
    else:
      canvas.drawString(x+width, y+yrel, line)

    yrel -= yinc
    lines += 1
    if ((yheight/inch <= 1.25) and (lines == 3)):
      break

  yrel -= yinc/2
  return y+yrel


def render_barcode(canvas,x,y,key,value):
    global barwidth
    global xwidth

    yrel = y
    v('render_barcode() --------------')
    v('render_barcode(): yrel: %f' % (yrel))

    if ((xwidth/inch <= 3.50)):
      barwidth = .0125*inch

    barcode = code128.Code128( value=key + ':' + value, quiet=1, barWidth = barwidth, barHeight =.20*inch )

    if flip:
      barcode.drawOn(canvas, x+(.525*inch), yrel - .750*inch)
    else:
      barcode.drawOn(canvas, x+(.125*inch), yrel - .250*inch)

    yrel -= .400*inch
    v('render_barcode(): yrel: %f' % (yrel))

    # barcode plain text
    if flip:
      render_key_and_value(canvas, x+(.400*inch), yrel - .25*inch, key , value)
    else:
      render_key_and_value(canvas, x+(.400*inch), yrel, key , value)
    #canvas.drawString(x+(.400*inch), yrel, bar_code_arg)

    yrel -= .140*inch
    v('render_barcode(): returning y %f' % (yrel))

    return yrel

#--------------------------------------------------------------------------- 
def tgetl(paper_size_no):
  """
  get test line of input
  """
  if (paper_size_no == 0 or paper_size_no == 1 ): # 8.5 x 11 sheets n-up or 4 x 6 labels 1-up
    lines = tgetl.testlines_paper_size_0.split('\n')
    v('tgetl(): getting test lines regular')
  elif (paper_size_no == -1): 
    v('tgetl(-1) getting input from var label_content')
    lines = tgetl.label_content.split('\n')
  else:
    v('tgetl(): getting test lines little labels')
    lines = tgetl.testlines_little_labels.split('\n')
    pprint(lines)

  if tgetl.ctr > len(lines)-1:
    retval = lines[len(lines)-1]
  else:
    retval = lines[tgetl.ctr]

  v('tgetl(): ctr:[%d] retval:[%s]' % (tgetl.ctr, retval))
  tgetl.ctr += 1

  v('tgetl(): returning [%s]' %(retval))
  return retval


tgetl.ctr = 0

tgetl.label_content = '' # from the user

tgetl.testlines_little_labels = """
LOGO SBA
BARCODE TPN 750
KEYVAL QTY 25
KEYVAL DESC DIODE RECT SUPER FAST 400V 1A SMB 
.
FLIP
LOGO DEF
BARCODE TPN 750
KEYVAL QTY 25
KEYVAL DESC DIODE RECT SUPER FAST 400V 1A SMB 
.
..
"""

tgetl.testlines_little_labelsx = """
logo K
barcode TPN 783
keyval QTY 1500
keyval DESC  CAPACITOR TANT 4.7UF 20V 20% SMD
.
flip
logo K
barcode SBJOB tif952
keyval OWNER foo@bar.com
.
..
"""

tgetl.testlines_paper_size_0 = """
logo
barcode SBJOB miku9922
barcode SBPN 998
keyval QTY 10
keyval DESCR This is a bunch of things that are all identical we hope
keyval REFS R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 
.
logo
barcode SBJOB xyzy1234
barcode SBPN 999
keyval FOO bar
keyval GOO Schmoo
keyval DOO Shoobee Doobee Doobee Doobee Doobee do la the fcc and other authorities have developed this system to keep you informed in case of an emergency
.
logo
barcode SBJOB miku9922
barcode SBPN 998
keyval QTY 10
keyval DESCR This is a bunch of things that are all identical we hope
keyval REFS R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 
.
logo
barcode SBJOB miku9922
barcode SBPN 998
keyval QTY 10
keyval DESCR This is a bunch of things that are all identical we hope
keyval REFS R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 
.
logo
barcode SBJOB miku9922
barcode SBPN 998
keyval QTY 10
keyval DESCR This is a bunch of things that are all identical we hope
keyval REFS R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 
.
logo
barcode SBJOB miku9922
barcode SBPN 998
keyval QTY 10
keyval DESCR This is a bunch of things that are all identical we hope
keyval REFS R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 
.
logo
barcode SBJOB miku9922
barcode SBPN 998
keyval QTY 10
keyval DESCR This is a bunch of things that are all identical we hope
keyval REFS R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 
.
logo
barcode SBJOB miku9922
barcode SBPN 998
keyval QTY 10
keyval DESCR This is a bunch of things that are all identical we hope
keyval REFS R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 
.
logo
barcode SBJOB miku9922
barcode SBPN 998
keyval QTY 10
keyval DESCR This is a bunch of things that are all identical we hope
keyval REFS R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 
.
logo
barcode SBJOB miku9922
barcode SBPN 998
keyval QTY 10
keyval DESCR This is a bunch of things that are all identical we hope
keyval REFS R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 
.
logo
barcode SBJOB miku9922
barcode SBPN 998
keyval QTY 10
keyval DESCR This is a bunch of things that are all identical we hope
keyval REFS R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 
.
logo
barcode SBJOB miku9922
barcode SBPN 998
keyval QTY 10
keyval DESCR This is a bunch of things that are all identical we hope
keyval REFS R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 
.
logo
barcode SBJOB miku9922
barcode SBPN 998
keyval QTY 10
keyval DESCR This is a bunch of things that are all identical we hope
keyval REFS R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 
.
logo
barcode SBJOB miku9922
barcode SBPN 998
keyval QTY 10
keyval DESCR This is a bunch of things that are all identical we hope
keyval REFS R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 
.
logo
barcode SBJOB miku9922
barcode SBPN 998
keyval QTY 10
keyval DESCR This is a bunch of things that are all identical we hope
keyval REFS R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 R1 
.
..
"""
#--------------------------------------------------------------------------- 

def get_labels_worth_of_input_from_stdin():
  out = []
  while(True):
    l = sys.stdin.readline().strip()
    v('get_labels_worth_of_input_from_stdin([%s])' % (l) )

    if re.match('\.',l):
      out.append(l)
      break

    if re.match('\.\.',l):
      out.append(l)
      break

    if not len(l):
      break

    out.append(l)

  v('get_labels_worth_of_input_from_stdin():' + '|'.join(out))
  return out


def get_labels_worth_of_input_from_data(paper_size_no):
  out = []
  ctr = 0
  while(True):
    l = tgetl(paper_size_no)
    ctr += 1
    if ctr > 16:
      pstderr('get_labels_worth_of_input_from_data(): runaway')
      os._exit(-1)

    v('get_labels_worth_of_input_from_data(): l: ' + l)
    if re.match('\.',l):
      out.append(l)
      break

    out.append(l)

  v('get_labels_worth_of_input_from_stdin():' + '|'.join(out))
  return out

    
def genlabeldone(canvas):
  finish_up(canvas)
  return



def canvas_init(filename_arg, pagesize=letter,bottomup=1,verbosity=1):
  filename = filename_arg
  pdf_file_wpath = filename
  c = canvas.Canvas(filename,pagesize=pagesize,bottomup=bottomup,verbosity=verbosity)
  v('filename:[%s]  page size:[%s] bottomup[%s] verbosity[%d]'% (filename, pagesize, bottomup, verbosity)) 
  c.setFont("Helvetica",9)
  return c

def genlabels(test=0,paper_size_no=0,printer='acrobat',verbose=0,label_content='stdin',fold=False,file_name=''):
  global xwidth
  global yheight

  global gl_printer
  gl_printer = printer


  global gl_filename
  gl_filename = os.path.normpath( 'kitlabels' + str(os.getpid()) + genranstr() + '.pdf' )

  if (file_name != ''):
    gl_filename = file_name

  global gl_verbose
  gl_verbose = verbose

  if test == 2:
    pstderr('Running old gentestlabels()')
    gentestlabels()
    return

  pstderr('-h for help')

  yfix = 0 # needed when printer prefs set to 4x6 and printing labels smaller than same 
  
  #--
  if (paper_size_no == 0):
    # ascertain edges
    pstderr('genlabels() paper_size: letter')
    (xwidth, yheight) = letter
    canvas = canvas_init(gl_filename,pagesize=letter,bottomup=1,verbosity=1)
    margin = .3*inch
    xorg = yorg = margin

  #--
  elif (paper_size_no == 1):
    pstderr('genlabels() paper_size: 4 x 6 label')
    margin = .0*inch
    (xwidth , yheight) = (4*inch,6*inch)
    canvas = canvas_init(gl_filename,pagesize=(4*inch,6*inch),bottomup=1,verbosity=1)
    xorg = yorg = margin

  #--
  elif (paper_size_no == 2):
    pstderr('genlabels() paper_size: 2.25 x .125 label')
    margin = .0*inch
    (xwidth , yheight) = (2.25*inch,1.25*inch)
    canvas = canvas_init(gl_filename,pagesize=(4*inch,6*inch),bottomup=1,verbosity=1)
    yfix = 4.75*inch # fudge factor to get little label to top of 6" space  (which is what the label printer driver is set to
    xorg = yorg = margin
    xorg += .80*inch
  
  #--
  elif (paper_size_no == 3):
    pstderr('genlabels() paper_size: 3.50 x 1.0 label')
    margin = .0*inch
    (xwidth , yheight) = (3.50*inch,1.00*inch)
    canvas = canvas_init(gl_filename,pagesize=(4*inch,6*inch),bottomup=1,verbosity=1)
    yfix = 5*inch
    xorg = yorg = margin
    xorg += .55*inch
  
  #--
  else:
    pstderr('unknown paper size: ' + paper_size)
    exit()

  v('genlabels(): xwidth: %f' % (xwidth/inch))

  xwidth -= margin*2
  yheight -= margin*2


  canvas.setStrokeColorRGB(.33,.33,.33)
  canvas.setFont('Helvetica',10)

  if (paper_size_no == 0):
    yrows = 3
    xcols = 2
  else:
    yrows = 1
    xcols = 1

  ystep = yheight/yrows
  xstep = xwidth/xcols

  v('xystep,ystep: %f %f' % (xstep,ystep) )

  x = xorg

  i = 0

  page = 0

  if (label_content != 'stdin'):
    tgetl.label_content = label_content

  tgetl.ctr = 0
  while(True):
    if (page != 0):
      canvas.showPage()

    y = yheight-ystep+margin

    v('y: %f yh: %f marg: %f' % (y,yheight,margin)) 

    for yrowcount in reversed(range(yrows)):
      for xcolcount in reversed(range(xcols)):

        if (test):
          labelcontentlist = get_labels_worth_of_input_from_data(paper_size_no)
        else:
          if (label_content == 'stdin'):
            pstderr('Reading input from stdin')
            labelcontentlist = get_labels_worth_of_input_from_stdin()
          else:
            labelcontentlist = get_labels_worth_of_input_from_data(-1)

        if (labelcontentlist[0] == '..'):
          genlabeldone(canvas)
          return

        v('labelcontentlist[0]: [%s]' % (labelcontentlist[0]))
        v('genkitlabel(x=%f,y=%f,xstep=%f,ystep=%f)' % (x, y,xstep,ystep))

        flip = False
        last_line = genkitlabel(canvas    , x , y+yfix, xstep, ystep, labelcontentlist, 0, paper_size_no)

        if (last_line == '..'):
          genlabeldone(canvas)
          return

        x += xstep

      x = xorg
      y -= ystep
    page += 1


def gentestlabels():
  # ascertain edges
  global gl_printer
  (xwidth, yheight) = letter
  margin = .3*inch
  xwidth -= margin*2
  yheight -= margin*2
  xorg = yorg = margin


  canvas = canvas_init('kitlabels.pdf',pagesize=letter,bottomup=1,verbosity=1)

  canvas.setStrokeColorRGB(.33,.33,.33)
  canvas.setFont('Helvetica',10)

  yrows = 3
  xcols = 2

  ystep = yheight/yrows
  xstep = xwidth/xcols

  v('xystep: %f %f' % (xstep,ystep) )

  x = xorg

  i = 0
  pages = 2

  for page in range(pages):
    if (page != 0):
      canvas.showPage()

    y = yheight-ystep+margin
    for yrowcount in reversed(range(yrows)):
      for xcolcount in reversed(range(xcols)):

        genkitlabel(canvas, x,y,xstep,ystep,'',test=1)
        i += 1
        x += xstep

      x = xorg
      y -= ystep

  finish_up(canvas)
  exit()

def exit():
  os._exit(0)

    
def usage():
  help = """


OPTIONS:

    -t [ 0 = no test, 1 = test 1, 2 = test 2 ]
    -v [ 0 = no verbose, 1 = verbose ]
    -s [ 0 = 8.5 x 11 paper, 1 = 4 x 6 labels, 2 = 2.25 x 1.25 labels 3 = 3.5 x 1 ]
    -p [ <printer name>, acrobat = send to previewer ]

EXAMPLES:

  Print 2 sheets of test labels on 8.5 x 11 paper to the acrobat reader:

     python kitlabels.py -s 0 -t 1 -p acrobat -v 1

  Print 1 4x6 test label: 

     python kitlabels.py -s 1 -t 1 -p acrobat -v 1

  Print 1 2.25 x 1.25 test label: 

     python kitlabels.py -s 2 -t 1 -p acrobat -v 1


NOTES:

  Takes input on stdin of the format:
  
  First token is one of [logo,barcode,keyval] 

  LOGO w/no arg renders logo512x512.png 
  LOGO C renders the a very large character C in its place
  BARCODE f1 f2 renders a barcode consisting of f1:f2, then renders 'f1:f2' underneath the barcode in plain text 
  KEYVAL f1 f2 f3 fn renders 'f1:' in bold, followed by 'f2 f3 fn', wrapping text lines if necessary

  See tgetl.testlines in source code for example input

"""
  sys.stderr.write(help)
  return

def DoCmd(cmd,ignore_exit_code=1):
  " Execute command cmd. exit on fail. Otherwise, return exit code Colorized messages"
  v('command[' + cmd + ']')

  try:
    exitcode = win32api.WinExec(cmd)
    #exitcode = subprocess.call(shlex.split(cmd),shell=True)

  except OSError as e:
    sys.stderr.write( "ERROR %s: %s\n" % (cmd, e.strerror))
    exit()


  if ignore_exit_code == 0 and exitcode != 0:
    sys.stderr.write(cmd + ' ERROR: exit Code: ' + repr(exitcode) + ' there might be a problem. See above')
    exit()
  
  return exitcode

  """
  try: 
    win32api.WinExec(cmd)
  except: 
    pstderr('something bad happened when trying to exec ' + cmd)
  """
 

def finish_up(c):
  global gl_printer
  global acrobat
  global gl_filename

  #c.showPage()
  c.save()

  pstderr('finish_up() printer:[%s]' % (gl_printer))

  pdf_file_wpath = os.path.join(os.getcwd(), gl_filename)

  """
  AcroRd32.exe <filename>

      /n - Launch a new instance of Reader even if one is already open
      /s - Don't show the splash screen
      /o - Don't show the open file dialog
      /h - Open as a minimized window
      /p <filename> - Open and go straight to the print dialog
      /t <filename> <printername> <drivername> <portname> - Print the file the specified printer.

  """

  pstderr('1')

  if gl_printer == '':
    sys.stderr.write( "File:[%s] Written\n" % (filename))
  elif gl_printer == 'acrobat':
    pstderr('2')
    cmd = acrobat +  ' /n /s /o ' + '"' + pdf_file_wpath  + '"'
    v('calling: [' + cmd + ']')
    DoCmd(cmd)
  else:
    pstderr('3')
    cmd = acrobat +  ' /h /n /s /o /t ' + ' "' + pdf_file_wpath  + '" ' + gl_printer
    v('calling: [' + cmd + ']')
    DoCmd(cmd)
    usage()

  flip = False
  return

#--------------------------------------------------------------------------------  
if __name__ == '__main__':
  """
  execution starts here
  """
  try:
    options, arguments = getopt.getopt(sys.argv[1:], 't:p:s:v:f:h')

  except getopt.GetoptError as err:
    pstderr(str(err))
    usage()
    sys.exit(1)

  opt_test = 0
  opt_paper_size_no = 0
  opt_printer = gl_printer
  opt_verbose = False
  opt_filename = ''

  for opt,arg in options:
    if opt in ('-t'):
      opt_test = int(arg)
    elif opt in ('-v'):
      opt_verbose = True
      v('verbose on')
    elif opt in ('-s'):
      opt_paper_size_no = int(arg)
    elif opt in ('-p'):
      opt_printer = arg
    elif opt in ('-f'):
      opt_filename = arg
    elif opt in ('-h'):
      usage()
      exit()


  genlabels(          test = opt_test,
            paper_size_no  = opt_paper_size_no,
            printer        = opt_printer,
            verbose        = opt_verbose,
            file_name      = opt_filename
            )


  exit()
