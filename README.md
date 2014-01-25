BARCODATRON

Run a local web server which accepts barcodes read in by a bar code scanner.

Based on the bar code, it will either pass request up to the server to get data or
intercept certain commands in order to print labels 
on special label printers 'n such.

Runs on the python-based Flask web microframework 

http://flask.pocoo.org/

In addition it requires Twitter Boostrap 3

http://pythonhosted.org/Flask-Bootstrap/


INSTALLATION

Just overlay this on top of your flask directory structure and you should be good to go.

barcode_list.pdf is a file of sample barcodes. Print it out and Aim your scanner at it.

You can regenerate it with barcode_list.py



RUNNING

Start the server with http_barcodes.py then browse to http://localhost/


When you first try to run it, you will inveitably need to do install some of the many python libraries that tis calls. Follow the standard procedures for installing Python libraries.






