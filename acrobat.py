"""

  Runs the acrobat reader to either preview or print files
  usage:

    python acrobat.py filename.pdf

  Only known to work on MS Windows

"""

def import_err(s):
  sys.stderr.write(
  """ Error: [%s] Failed. You need to install this module. 
  (see http://docs.python.org/install/
  """\
  % ('win32api') )
  os._exit(-1)

import os
import sys

try:
  import win32api
except:
  import_err('win32api')

"""
You might have to go mining around for where your acrord is installed:
"""

acrobat  = os.path.normpath( "C:/Program Files/Adobe/Reader 11.0/Reader/AcroRd32.exe")
if (not os.path.exists(acrobat)):
  acrobat  = os.path.normpath("C:/Program Files/Adobe/Reader 10.0/Reader/AcroRd32.exe")
  if (not os.path.exists(acrobat)):
    acrobat  = os.path.normpath("C:/Program Files (x86)/Adobe/Reader 10.0/Reader/AcroRd32.exe")
    if (not os.path.exists(acrobat)):
      sys.stderr.write('can''t find acrobat\n')
      os._exit(1)


def run(file_name):
  """
  AcroRd32.exe <filename>

      /n - Launch a new instance of Reader even if one is already open
      /s - Don't show the splash screen
      /o - Don't show the open file dialog
      /h - Open as a minimized window
      /p <filename> - Open and go straight to the print dialog
      /t <filename> <printername> <drivername> <portname> - Print the file the specified printer.

  """

  cmd = acrobat +  ' /n /s /o ' + '"' + file_name + '"'

  try:
    exitcode = win32api.WinExec(cmd)

  except OSError as e:
    sys.stderr.write( "ERROR %s: %s\n" % (cmd, e.strerror))
    exit()


  if exitcode != 0:
    sys.stderr.write(cmd + ' ERROR: exit Code: ' + repr(exitcode) + ' there might be a problem. See above')
    exit()

#--------------------------------------------------------------------------------  
if __name__ == '__main__':
  """
  execution starts here
  """
  run(sys.argv[1])
