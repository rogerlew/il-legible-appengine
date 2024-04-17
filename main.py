"""
Copyright (c) 2015-Now, Roger Lew
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
  * Redistributions in binary form must reproduce the above
    copyright notice, this list of conditions and the following
    disclaimer in the documentation and/or other materials provided
    with the distribution.
  * Neither the name of the organizations affiliated with the
    contributors or the names of its contributors themselves may be
    used to endorse or promote products derived from this software
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

import base64
from datetime import datetime
 
from flask import Flask, request, make_response, send_file, render_template

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
 
from flask import Flask

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

import textLegibility

@app.route('/')
def main_response(xRes='1920', yRes='1080', diagonal='23.9', 
                  vertical='51', horizontal='26'):
    
    return render_template("main.html", 
                           xRes=xRes, yRes=yRes,
                           diagonal=diagonal, vertical=vertical,
                           horizontal=horizontal, 
                           submitcontent='Run Analysis',
                           data=None, rv=None)

@app.route('/doc')
def doc_response():
    return render_template("doc.html")

@app.route('/about')
def about_response():
    return render_template("about.html")

@app.route('/legal')
def legal_response():
    return render_template("legal.html")
    
# stuff to handle pdf generation
def get_utc_timestamp():
    utc = datetime.now()
    return (utc - datetime(1970, 1, 1)).total_seconds()
    
def serialize(xRes, yRes, diagonal, vertical, horizontal):
    # This offers very rudimentary obfuscation. 
    # Chances are if you got here trying to break it you
    # are more than capable of using the TextLegibility
    # module to do whatever it is that you want to do.
    # Please don't reverse engineer this to provide persistent 
    # hotlinks. The free bandwidth provided by appengine is
    # very limited.
    timestamp = get_utc_timestamp() #- 24*60*60 -1
    s = "%f,%s,%s,%s,%s,%s" %(timestamp, xRes, yRes, diagonal, vertical, horizontal)
    return s #urlsafe_b64encode(s)
    
def deserialize(s):
#    uenc = s.decode('utf-8')
#    s2 = urlsafe_b64decode(uenc.encode("utf-8"))
    
    tokens = s.split(',')
    return ( float(tokens[0]), 
             int(tokens[1]), 
             int(tokens[2]), 
             float(tokens[3]), 
             float(tokens[4]), 
             float(tokens[5]) )
    
@app.route('/<path:path>.pdf')
def pdf(path):
    dt, xRes, yRes, diagonal, vertical, horizontal = deserialize(path)
    aspect_ratio = float(xRes) / float(yRes)
    
    display = textLegibility.Display(xRes, yRes, 
                                     diagonal=diagonal, 
                                     aspect_ratio=aspect_ratio,
                                     bottom=vertical)
         
    data = serialize(xRes, yRes, diagonal, vertical, horizontal)
    
    rv = textLegibility.plot(display, z_distance=28.0, 
             isopleth_label_xpos=26.2, show_inset=True,
             font_sizes=[10, 12, 14, 16, 18], guideline=16, 
             save_as_pdf=True)

    return send_file(rv,
                     attachment_filename=f'il-legible_{data}.pdf',
                     as_attachment=True)
                     
    
@app.route('/submit', methods=['GET'])
def submit_response():
    xRes = request.form.get('xRes', '1920')
    yRes = request.form.get('yRes', '1080')
    diagonal = request.form.get('diagonal', '23.9')
    vertical = request.form.get('vertical', '51')
    horizontal = request.form.get('horizontal', '26')
    
    data = serialize(xRes, yRes, diagonal, vertical, horizontal)
    
    xRes = int(xRes)
    yRes = int(yRes)
    diagonal = float(diagonal)
    vertical = float(vertical)
    horizontal = float(horizontal)
    aspect_ratio = float(xRes) / float(yRes)
    
    display = textLegibility.Display(xRes, yRes, 
                                     diagonal=diagonal, 
                                     aspect_ratio=aspect_ratio,
                                     bottom=vertical)
    
    rv = textLegibility.plot(display, z_distance=28.0, 
             isopleth_label_xpos=26.2, show_inset=True,
             font_sizes=[10, 12, 14, 16, 18], guideline=16)
    
    rv_data = base64.b64encode(rv.read()).decode('utf-8')

    return render_template("main.html",
                           xRes=xRes, yRes=yRes,
                           diagonal=diagonal, vertical=vertical,
                           horizontal=horizontal, 
                           submitcontent='Rerun Analysis',
                           data=data,
                           rv_data=rv_data)

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404


if __name__ == "__main__":
    app.run(debug=True)
