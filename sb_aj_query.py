"""
 sb_aj_query.py

 Interfaces with a web server to obtain job/part information

 Can be called as a library function or from the command line

"""

from pprint import pprint
import kitlabels
import string,sys,os,getopt,json,requests
import re

#----------------  
# server constants
server_ajax_url = 'http://www.YOUR_SERVER.com/wp-admin/admin-ajax.php' # server's ajax api
server_auth_key = 'fake_query' #  replace w/an auth key your server checks for


# default query lookup values
opt_query = 'sb_get_sb_parts'
opt_lookup_val = '0'
opt_arg1 = ''
opt_arg2 = ''
opt_arg3 = ''

#----------------  
def usage():
  pstderr("""

  COMMAND LINE OPTIONS

      -q query_id 
      -l lookup_val

  EXAMPLES

  <no args> runs a default lookup

  Lookup part number 1

    -q sb_lookup_sba_pn -l 1

  Get all parts

    -q sb_get_sb_parts 

  Generate quote

    -q sb_execute -1 genquote -2 tif952

""")
  return

#----------------  
def aj_query(query,arg1,arg2,arg3):
  """
  library call interface
  """
  url = server_ajax_url 
  if (server_auth_key == 'fake_query'):
      pstderr('No Server Key. Faking Queries')
      if (query == 'sb_get_job_info'):
        return fake_sb_get_job_info()
      elif (query == 'sb_get_part_info'):
        return fake_sb_get_part_info()
      elif (query == 'sb_execute' and re.match('genlabel',arg1)):
        return fake_sb_execute()
      else:
        pstderr('%s: Thatt\'s one I don\'t know how to fake' % query)
        return ''
  
      
  params = {
    'action'        : query,
    'db_lookup_val' : arg1, # some take this as arg 1
    'arg1'          : arg1,
    'arg2'          : arg2,
    'arg3'          : arg3,
    'key'           : server_auth_key
  } 
  print('QUERY ----------')
  pprint(url)
  pprint(params)


  # make the request
  return requests.post(url,data=params)


#----------------  
def pstderr(m):
  sys.stderr.write(m + '\n')
  return

#----
def fake_sb_execute():
  """

  """
  class fake_response: 
    text = '{"as_data": "OK", "label_data": "LOGO CUS\\nBARCODE TPN 891\\nKEYVAL QTY 25\\nKEYVAL DESC _\\n.\\nFLIP\\nLOGO CUS\\nBARCODE SBJOB tif952\\nKEYVAL OWNER bob.coggeshall@gmail.com\\nKEYVAL BQTY 25\\n.\\n..\\n", "err": 0, "as_html": "<pre>LOGO CUS\\nBARCODE TPN 891\\nKEYVAL QTY 25\\nKEYVAL DESC _\\n.\\nFLIP\\nLOGO CUS\\nBARCODE SBJOB tif952\\nKEYVAL OWNER bob.coggeshall@gmail.com\\nKEYVAL BQTY 25\\n.\\n..\\n</pre>"}' 

  pprint (fake_response.text)

  return (fake_response)

#----
def fake_sb_get_part_info():
  """

  """
  class fake_response: 
    text = '{"as_data": {"TPN": "891", "REFS": "PCB1", "PACKAGE": "pcb", "VALUE": "pcb", "QTY": "25"}, "supplier": "C", "err": 0, "as_html": "<table class=\\"table table-striped table-condensed table-bordered\\" style=\\"width:66%;\\"><tr><td style=\\"text-align:right\\"><b>TPN</b></td><td>891</td></tr><tr><td style=\\"text-align:right\\"><b>QTY</b></td><td>25</td></tr><tr><td style=\\"text-align:right\\"><b>REFS</b></td><td>PCB1</td></tr><tr><td style=\\"text-align:right\\"><b>PACKAGE</b></td><td>pcb</td></tr><tr><td style=\\"text-align:right\\"><b>VALUE</b></td><td>pcb</td></tr></table>"}'

  pprint (fake_response.text)

  return (fake_response)

#----
def fake_sb_get_job_info():
  """

  """
  class fake_response: 
    text = '{"as_data": {"STATUS": "unsubmitted", "BOM COMPLETE": "YES", "DIMENSIONS": "127 x 127mm (5.00 x 5.00in)", "TOTAL PLACEMENTS PER BOARD": "77", "BOARD QUANTITY": "25", "AGE": "74d 21h 20m", "BOM FILE NAME": "NixieDrvrB3-3_SBA_BOM.csv", "TOTAL PART TYPES": "29", "DATE": "2013.11.1111:57 EST (Mon)", "Job ID": "tif952", "PANELIZED": "YES", "CUSTOMER-SUPPLIED PART TYPES": "6", "OWNER": "foo.bar@gmail.com", "TOTAL PLACEMENTS THIS ORDER": "1925", "PASTE FILE NAME": "NixieDrvrB3-3_SBA_PASTE.ger", "ASSEMBLER-SUPPLIED PART TYPES": "23"}, "err": 0, "as_html": "<table class=\\"table table-striped table-condensed table-bordered\\" style=\\"width:66%;\\"><tr><td style=\\"text-align:right\\" ><b>Job ID</b></td><td>tif952</td></tr><tr><td style=\\"text-align:right\\" ><b>STATUS</b></td><td>unsubmitted</td></tr><tr><td style=\\"text-align:right\\" ><b>BOM FILE NAME</b></td><td>NixieDrvrB3-3_SBA_BOM.csv</td></tr><tr><td style=\\"text-align:right\\" ><b>PASTE FILE NAME</b></td><td>NixieDrvrB3-3_SBA_PASTE.ger</td></tr><tr><td style=\\"text-align:right\\" ><b>OWNER</b></td><td>foo.bar@gmail.com</td></tr><tr><td style=\\"text-align:right\\" ><b>DATE</b></td><td>2013.11.11 11:57 EST (Mon)</td></tr><tr><td style=\\"text-align:right\\" ><b>AGE</b></td><td>74d 21h 20m</td></tr><tr><td style=\\"text-align:right\\" ><b>BOARD QUANTITY</b></td><td>25</td></tr><tr><td style=\\"text-align:right\\" ><b>PANELIZED</b></td><td>YES</td></tr><tr><td style=\\"text-align:right\\" ><b>DIMENSIONS</b></td><td>127 x 127mm (5.00 x 5.00in)</td></tr><tr><td style=\\"text-align:right\\" ><b>BOM COMPLETE</b></td><td>YES</td></tr><tr><td style=\\"text-align:right\\" ><b>CUSTOMER-SUPPLIED PART TYPES</b></td><td>6</td></tr><tr><td style=\\"text-align:right\\" ><b>ASSEMBLER-SUPPLIED PART TYPES</b></td><td>23</td></tr><tr><td style=\\"text-align:right\\" ><b>TOTAL PART TYPES</b></td><td>29</td></tr><tr><td style=\\"text-align:right\\" ><b>TOTAL PLACEMENTS PER BOARD</b></td><td>77</td></tr><tr><td style=\\"text-align:right\\" ><b>TOTAL PLACEMENTS THIS ORDER</b></td><td>1925</td></tr></table>"}'

  pprint (fake_response.text)

  return (fake_response)

# --------------
if __name__ == '__main__':
  """
  execution starts here
  """
  try:
    options, arguments = getopt.getopt(sys.argv[1:], 'q:l:1:2:')
# ----
  except getopt.GetoptError as err:
    pstderr(str(err))
    usage()
    sys.exit(1)

  for opt,arg in options:
    if opt in ('-q'):
      opt_query = arg
    if opt in ('-l'):
      opt_lookup_val = arg
    if opt in ('-1'):
      opt_arg1 = arg
    if opt in ('-2'):
      opt_arg2 = arg
    if opt in ('-3'):
      opt_arg3 = arg

        
  r = aj_query(opt_query,opt_arg1,opt_arg2,opt_arg3)
  print('RESPONSE ---------')
  j = json.loads(r.text)
  pprint(json.dumps(j))
  print('---------')
  os._exit(0)
