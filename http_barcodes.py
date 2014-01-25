"""
http_barcodes.py

Run a local web server which accepts small batch barcodes 
Mostly passes request up to the real server to get data
It will also intercept certain commands in order to print labels 
on special label printers 'n such.

Start this and browse to http://localhost/

"""
from barcode_flask import * # creates app see barcode_flask/__init__.py
from kitlabels import *
from pprint import pprint
from sb_aj_query import *  # for asking the smallbatch web server ajax questions

# =--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=-- 
@app.route('/',methods=['GET', 'POST']) 
def barcode_form():
  """
  Called when the barcode form is either rendered or submitted
  """
  if request.method == 'GET':
    return render_template('form.html')

  elif request.method == 'POST':
    barcode_process(request.form['barcode'])
    return request.form['barcode'] + ' foo'

# =--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=-- 
@app.route('/ajax',methods=['POST'])
def barcode_ajax():
  """
  Called when the barcode form submitted
  """
  print('barcode_ajax() TOP =========================================================================')
  print('-------------------')
  pprint(request)
  print('-------------------')


  # form data is in request
  if 'action' in request.form: # HTTP POST data comes in request object
    action  = request.form['action'] # sb_get_job_info, sb_get_part_info, etc..
  else:
    return json_punt()

  if 'arg1' in request.form:
    a1 = request.form['arg1']
  else:
    a1 = ''

  if 'arg2' in request.form:
    a2 = request.form['arg2']
  else:
    a2 = ''

  if 'arg3' in request.form:
    a3 = request.form['arg3']
  else:
    a3 = ''

  if (action == 'sb_execute_local'):
    #
    # execute locally
    #
    if (ex_local(a1,a2,a3)):
      m = 'barcode_ajax(): execute local: OK'
      d = {'error':0,'as_data':m,'as_html':m}
      return jsonify(d)
    else:
      json_punt()
      return

  else:
    #
    # send it up to the main server
    #
    r  =  aj_query(query = action,arg1 = a1, arg2 = a2, arg3 = a3)

    print('-------------------')

    j = json.loads(r.text)
    pprint(json.dumps(j))

    print('-------------------')

    try:
      return jsonify(j)
    except:
      return json_punt()

# =--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=-- 
def json_punt():
  """
  generate json formatted error message barcode.js will understand and exit
  """
  m = 'barcode_ajax(): server didn''t return intelligible response'
  print m
  d = {'err':1,'as_data':m,'as_html':m}
  return jsonify(d)




# =--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=-- 
def ex_local(a1,a2,a3):
  cmd = a1
  labeldata = a2
  print 'ex_local(a1[%s] a2[%s] a3[%s])' % (a1,a2,a3)
  print file

  if (a1 == 'genlabelp'):
    which_printer = 'acrobat'
  else:
    which_printer  = 'zebra'

  kitlabels.genlabels(verbose=0, paper_size_no=3, label_content=labeldata, printer=which_printer)

  return True;

# =--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=-- 
if __name__ == "__main__":
  """
  execution starts here
  """
  app.run(port=80) # ,debug=True)
