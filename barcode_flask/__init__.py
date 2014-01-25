# http://pythonhosted.org/Flask-Bootstrap/

"""
barcode_flask/__init__.py

Starts up an instance of Flask (lightweight python http server)

  usage:

    from barcode_flash import *
    
    ...

    @app.route('/')
    def foo():
      return render_template('index.html') #


    ...

    app.run(port=80) # ,debug=True)
    

"""
from flask.ext.bootstrap import Bootstrap
from flask import Flask, render_template, request, url_for, jsonify

# http://stackoverflow.com/questions/18297041/im-not-able-to-import-flask-wtf-textfield-and-booleanfield
# http://wtforms.readthedocs.org/en/latest/ext.html#module-wtforms.ext.csrf

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['BOOTSTRAP_SERVE_LOCAL'] = True # don't get the .css an .js files from outside

Bootstrap(app) # bootstrapify

if __name__ == "__main__":
  app.run(port=80)
