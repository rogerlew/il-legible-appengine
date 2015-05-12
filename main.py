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

import random
import StringIO
from base64 import urlsafe_b64encode, urlsafe_b64decode
from datetime import datetime
 
from flask import Flask, request, make_response, send_file

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
 
from flask import Flask

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

import textLegibility


# I know there are better more sophisticated templating methods, but this is my
# first flask project and I don't really have the time at this point to figure
# all of that out. So I went with a more manual approach for this small scope
# project.

header = """
<style type="text/css">
p, label {
	font-family: Helvetica;
	font-size: 14pt;
}

.hangingindent {
  padding-left: 1em ;
  text-indent: -1em ;
} 

h2, h3 {
	font-family: Helvetica;
    font-weight: bold;
}

h3 {
    font-size: 15pt;
    margin: 0 0 -4pt 0;
}

div.header {
    background-color: #888888;
    padding: 0.2em 2em 0.2em 2em;
    width: 100%; 
    overflow: hidden;
}

div.footer {
	color: #fff;
    text-align=center;
    height:3em;
    background-color: #888888;
    width: 100%; 
}

div.footercontent {
	font-family: Helvetica;
    position: relative;
    width: 40em;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}

div.title {   
	font-family: 'Times New Roman', serif;
	font-weight: 800;
	color: #fff;
	font-size: 42px;
    width: 30%; 
    float: left;
}

div.navigation { 
	font-size: 16pt;
	font-family: Helvetica;
	color: #fff;
    height: 2.5em;
    margin-left: 40%;
    text-align: right;
    padding: 0 2em 0 0;
}

div.navcontent {
	font-family: Helvetica;
    position: relative;
    top: 50%;
    transform: translateY(-50%);
}

div.maincontent {
    width: 90%;
    max-width: 800pt;
    margin: 0 auto;
}
div.pcontent {
    max-width: 600pt;
}

dl {
	font:normal 12pt/15pt Helvetica;
    width: 500pt;
}
dt {
   
    width: 300pt;
    padding: 0 0 0 0;
}
dd {
    width: 100pt;
    margin: 0;
    padding: 0 0 16pt 0;
}

img.result {
    display: block;
    margin-left: auto;
    margin-right: auto 
}

a {
    text-decoration: none;
	color: #666;
}
a {
	font-family: Helvetica;
	font-size: 14pt;
    text-decoration: none;
	color: #666;
}

a.aheader {
	font-size: 16pt;
    text-decoration: none;
	color: #fff;
}
a.aheader:hover {
 	color: #fff;
}

a.afooter {
	font-size: 10pt;
    text-decoration: none;
	color: #fff;
}
a.afooter:hover {
 	color: #fff;
}

.hint {
	font:normal 12pt/15pt Helvetica;
   	display: none;
    position: absolute;
    margin-left: 12px;
    padding: 4pt 12pt;
    width: 200pt;
  	background: #ccc;
	border: 2px solid #888888;
    line-height = 15pt;
}
.hint:after, .hint:before {
	right: 100%;
	top: 50%;
	border: solid transparent;
	content: " ";
	height: 0;
	width: 0;
	position: absolute;
	pointer-events: none;
}

.hint:after {
	border-color: rgba(204, 204, 204, 0);
	border-right-color: #ccc;
    top: 8pt;
	border-width: 10px;
	margin-top: -10px;
}
.hint:before {
	border-color: rgba(136, 136, 136, 0);
	border-right-color: #888888;
	top: 8pt;
    border-width: 12px;
	margin-top: -12px;
}

</style>
<script type="text/javascript">
function addLoadEvent(func) {
  var oldonload = window.onload;
  if (typeof window.onload != 'function') {
    window.onload = func;
  } else {
    window.onload = function() {
      oldonload();
      func();
    }
  }
}

function prepareInputsForHints() {
	var inputs = document.getElementsByTagName("input");
	for (var i=0; i<inputs.length; i++){
		// test to see if the hint span exists first
		if (inputs[i].parentNode.getElementsByTagName("span")[0]) {
			// the span exists!  on focus, show the hint
			inputs[i].onfocus = function () {
				this.parentNode.getElementsByTagName("span")[0].style.display = "inline";
			}
			// when the cursor moves away from the field, hide the hint
			inputs[i].onblur = function () {
				this.parentNode.getElementsByTagName("span")[0].style.display = "none";
			}
		}
	}
	// repeat the same tests as above for selects
	var selects = document.getElementsByTagName("select");
	for (var k=0; k<selects.length; k++){
		if (selects[k].parentNode.getElementsByTagName("span")[0]) {
			selects[k].onfocus = function () {
				this.parentNode.getElementsByTagName("span")[0].style.display = "inline";
			}
			selects[k].onblur = function () {
				this.parentNode.getElementsByTagName("span")[0].style.display = "none";
			}
		}
	}
}
addLoadEvent(prepareInputsForHints);

(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

ga('create', 'UA-3873514-2', 'auto');
ga('send', 'pageview');
</script>
<div class="header">
    <div class="title">illegible</div>
    <div class="navigation">
        <div class="navcontent">
          <a class="aheader" {{tool}} href="/">tool</a> |
          <a class="aheader" {{doc}} href="/doc">doc</a> |
          <a class="aheader" {{about}} href="/about">about</a> |
          <a class="aheader" {{legal}} href="/legal">legal</a>
        </div>
    </div>
</div>
"""

main = """<div class="maincontent" >
<h2>Text Legibility Analysis for Standing Workstations</h2>
<form action="/submit" method="post">
<h3>Display Specifications</h3>
<dl>
    <dt>
        <label for="xRes">Horizontal Resolution (pixels):</label>
    </dt>
    <dd>
        <input id="xRes" 
               name="xRes" 
               type="number" 
               required="true" 
               min="1" 
               max="8192" 
               step="1" 
               value="{{xRes}}" 
               style="width:100pt;"/>
        <span class="hint">Specify the horizontal resolution of the display.</span>
    </dd>
    <dt>
        <label for="yRes">Vertical Resolution (pixels):</label>
    </dt>
    <dd>
        <input id="yRes" 
               name="yRes" 
               type="number" 
               required="true" 
               min="1" 
               max="8192" 
               step="1" 
               value="{{yRes}}" 
               style="width:100pt;"/>
        <span class="hint">Specify the vertical resolution of the display.</span>
    </dd>
    <dt>
        <label for="diagonal">Diagonal Measurement (inches):</label>
    </dt>
    <dd>
        <input id="diagonal" 
               name="diagonal" 
               type="number" 
               required="true" 
               min="1" 
               max="1000" 
               step="any" 
               value="{{diagonal}}" 
               style="width:100pt;"/>
        <span class="hint">Specify the horizontal dimension of the display in decimal inches.</span>
    </dd>
</dl>
<h3>Display Placement</h3>
<dl>
    <dt>
        <label for="vertical">Vertical Dimension(inches):</label>
    </dt>
    <dd>
        <input id="vertical" 
               name="vertical" 
               type="number" 
               required="true" 
               min="0" 
               max="240" 
               step="any" 
               value="{{vertical}}" 
               style="width:100pt;"/>
        <span class="hint">Specify the vertical distance from the floor to the bottom of the display in decimal inches.</span>
    </dd>
    <dt>
        <label for="horizontal">Horizontal Dimension(inches):</label>
    </dt>
    <dd>
        <input id="horizontal" 
               name="horizontal" 
               type="number" 
               required="true" 
               min="1" 
               max="240" 
               step="any" 
               value="{{horizontal}}" 
               style="width:100pt;"/>
        <span class="hint">Specify the horizontal distance from the front of the screen to the operator's eyepoint.</span>
    </dd><dt>
    </dt>
    <dd>
        <input type="submit" 
               class="button" 
               value="{{submitcontent}}"  
               style="width:180pt; height:36pt;font-size:18px;" 
               onClick="this.form.submit(); this.disabled=true; this.value='Please wait...'; ">
    </dd>
</dl>
</form>
</div>
"""

submit = """
<div class="maincontent">
    <a href="%s.pdf">Download Results as PDF</a>
    <br/><i>This link will expire after 24 hours.</i>
    <br/>&nbsp;
</div>"""

expired = """
<div class="maincontent">
<h2>Expired Link</h2>
    <div class="pcontent">
        <p>The link for the pdf you are attempting to download has expired. Please rerun your analysis to obtain a new
        download link.</p>
        <p><b><i>Why has my link expired?</i></b> PDF links are only active for a period of 24 hours to circumvent persistent 
        hotlinks.</p>
    </div>
</div>"""

doc = """
<div class="maincontent">
<h2>Documentation</h2>
    <div class="pcontent">
        <p>This tool is intended to aid qualified professionals in the assessment of the legibility of text presented on a 
        digital display for the purposes designing and and analysing human machine interfaces in accordance NUREG-0700
        and ISO 9241-3.</p>
        <p>Given a display (such as an LCD screen) of a known size and resolution at a fixed location this tool calculates
        how well different sized fonts presented on the display will accomodate users of varying statures. The tool models
        population height distributions for both sexes based on means and averages identified in MIL-STD 1472G.</p>
    </div>
    <h3>Interpreting the figure</h3>
    <div class="pcontent">
        <p>The assumptions of the model are provided in the top left corner.</p>
        <p>To the right of the models assumptions is a figure depicting the vertical distance from the user's eye to the 
        farthest vertical location on the screen (either the top or bottom) as a function of stature. View angle is depicted
        in teal. A view angle of zero indicates the center of the screen is perpendicular to the user's gaze. Negative view 
        angles indicate the user would be looking up at the screen, positive angles indicate the user would be looking 
        down.</p>
        <p>The table in the top right corner lists the font sizes used in the analysis and their cooresponding physical heights
        in inches and millimeters</p>
        <p>The main figure depicts viewing angle in minutes of arc (MOA) as a function of viewing distance in (inches) and font size.
        The isopleths indicate contours of constant font size. Viewing distance is a function of the display's placement, the 
        horizontal distance from the display to the user, and the user's stature. In the analysis all of these factors are 
        fixed except for stature so a monotonic relation exists between viewing distance and stature.</p>
        <p>The green horizontal line indicates the threshold for NUREG-0700 compliance. For a given viewing distance a font size 
        is compliant if it is above this line.</p>
        <p>The bottom figures depict how a given font will satisfy the potential population distribution of users. The probabliity 
        density functions for females and males are shaded in light gray. For each distribution the percentiles satisfied by the font
        size are shaded in green. The tables underneath each lists the lower (L) and upper (U) bounds as well as the total (T)
        percentage of the populations accomodated by the font size.</p>
    </div>
</div>
"""

about = """
<div class="maincontent">
<h2>About</h2>
    <div class="pcontent">
        <p>This tool is intended to aid qualified professionals in the assessment of the legibility of text presented on a 
        digital display for the purposes designing and and analysing human machine interfaces in accordance with NUREG-0700 
        and MIL-STD 1472G.</p>
    </div>
    <h3>Authors</h3>
    <div class="pcontent">
        <p>Roger Lew (rogerlew@inl.gov)<br/>Ronald L. Boring (ronald.boring@inl.gov)</p>
    </div>
    <h3>Source</h3>
    <div class="pcontent">
        <p>Source code for this tool is available under the 3-Clause BSD license and is available on github:</p>
        <a href="https://github.com/rogerlew/il-legible-appengine">https://github.com/rogerlew/il-legible-appengine</a>
    </div>
    <br/>
    <h3>Privacy</h3>
    <div class="pcontent">
        <p>Analyses are ran server-side using Google's appengine cloud platform. Form requests are sent unsecured as http post requests. 
        Your IP may be recorded for analytical purposes. The source code is available for users who require additional anonymity or
        would like to run automated analyses.</p>
    </div>
    <h3>Cite illegible</h3>
    <div class="pcontent">
        <p>If you find illegible useful. Please cite the following:</p>
        <p class="hangingindent">Lew, R., Boring R. (Unpublished Manuscript). A Tool for Assessing the Text Legibility of Digital Human 
        Machine Interfaces.</p>
    </div>
</div>
"""

legal = """
<div class="maincontent">
<h2>Legal Disclaimer</h2>
    <div class="pcontent">
        <p>This software is provided by the Copyright Holders and Contributors "as is" and any express or implied warranties, including, 
        but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. In no event 
        shall the Copyright Holder or Contributors be liable for any direct, indirect, incidental, special, examplary, or consequential 
        damages (including, but not limited to, procurement of subttitute goods or services; loss of use, data, or profits; or business 
        interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence 
        or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.</p>
    </div>
</div>
"""

footer = """
<div class="footer">
    <div class="footercontent">
        <span style="height:60px; vertical-align:middle; font-size:10pt;">
            Copyright &copy; <script>document.write(new Date().getFullYear());</script>. All rights reserved. 
            <a class="afooter" href="http://www4vip.inl.gov/research/human-system-simulation-laboratory/">
            Human Systems Simulation Laboratory.</a></span>
        <a href="https://inl.gov">
            <img style="height:22; width=40; vertical-align:middle;" 
            src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAWCAYAAACyjt6wAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyZpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMDE0IDc5LjE1Njc5NywgMjAxNC8wOC8yMC0wOTo1MzowMiAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTQgKFdpbmRvd3MpIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjA0NjAwMEZCRjdCMTExRTQ5NDJEQUY0NjVCNDI0MEE1IiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOjA0NjAwMEZDRjdCMTExRTQ5NDJEQUY0NjVCNDI0MEE1Ij4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6MDQ2MDAwRjlGN0IxMTFFNDk0MkRBRjQ2NUI0MjQwQTUiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6MDQ2MDAwRkFGN0IxMTFFNDk0MkRBRjQ2NUI0MjQwQTUiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz6KyHvqAAAC8ElEQVR42ryWS2gUQRCGZ5dkNyHGqBElqKg5RDA+EFHjySCoKASiYED0IAYD6kUvGoN4URHBgwgeFIMiPsCDj5sgPsD3C0nw7QY1QvCZxNUkJuvu+hf8A20xu9OzrCn46J7umpnq6qrqDqXTacdCZoLDIA4awTdnuEQMJDtBO+hL/yud6vm+8c5/J0QPHgGbQRd4Ar6AEKgA08Fkta7QcDmwAKwE70AVeJtB7wL1RPZ7zFdwUcl8GygefIR2no/eeLAWDIJjIAEiIAoKwWzwB6TAAHeiz4wk8Iv6EWM8pfQ8Y/Ap2JslDmrBe3AX3AMxjjeBOOjl/CdQD6pAC+dcOvjOPjX+2C8GZYvXgWfgBOjwWEMRY1DH4UhQyn4Z2xpwCdwx5hyjH1XjE/22OAyegwMgRmO0JNTzT7a/PXQ3sv2qxrsYBlPUeI9Nkog0g2rwA5QzXnKRMWAOF+uoWJNEHAr6wbDRrwPn6KGpGXRspI4G6TCJe4RQKoiBIuvBbvAatKgttZXlYJb6udsvVrqjwcIgBorsAQ1gEzgFekGbKhnZRBJlK+i2WEw3jV4CKm0NdJiJk5ipl8EunsVu9voZ2mDoZa3D4Dp4BRYzkawMdKWehfkss1aOw6OcG+HzbiRADnzkbknsL3MCJsA11q7tLCMvWS7a83yqDXHnJKEWBTGw3OhLCTkELvISsQ1c5ZzE6ps8GCohNRbU5lJCRD6DVWA+M1Y8uQOsBqcDfmswy+VETq7qghwMLGXRlZWeAUtZltwjUWK2BKwxHFCY4VvjwAajFJ0H/UzAm+KAXAxMGqeGK9PoxZNgArgFHrAe1hgGlnlc01qN5xvgA/vStoXzGORyQdhCDxxkLZT47aS3Z4CH4AWvZl6ix622uMRji3XyiMxl28rtrTSK7wrqRxnDRfTqdx6BxSxLA/yfhM0C8aKNgTHWqCRjqp/jt5kUCV463AyW7T1OA1J8p4cZ32wUfzdB4tQTmsAoxuYVicm/AgwAsp+ltvQrrbUAAAAASUVORK5CYII="/>
        </a>
    </div>
</div>
"""

def header_response(mask=[0, 0, 0, 0]):
    style = lambda b : ('', 'style="font-weight:bolder"')[b]
    return header.replace('{{tool}}', style(mask[0])) \
                 .replace('{{doc}}', style(mask[1])) \
                 .replace('{{about}}', style(mask[2])) \
                 .replace('{{legal}}', style(mask[3]))

@app.route('/')
def main_response(xRes='1920', yRes='1080', diagonal='23.9', 
                  vertical='51', horizontal='26'):
    s = header_response([1,0,0,0])
    
    s += main.replace('{{xRes}}', xRes) \
             .replace('{{yRes}}', yRes) \
             .replace('{{diagonal}}', diagonal) \
             .replace('{{vertical}}', vertical) \
             .replace('{{horizontal}}', horizontal) \
             .replace('{{submitcontent}}', 'Run Analysis')
             
    s += footer;
    return s;

@app.route('/doc')
def doc_response():
    s = header_response([0,1,0,0]) + doc + footer
    return s

@app.route('/about')
def about_response():
    s = header_response([0,0,1,0]) + about + footer
    return s

@app.route('/legal')
def legal_response():
    s = header_response([0,0,0,1]) + legal + footer
    return s 
    
# stuff to handle pdf generation
def get_utc_timestamp():
    utc = datetime.utcnow()
    return (utc - datetime(1970, 1, 1)).total_seconds()
    
def datetime_expired(timestamp, period=24*60*60):
    return get_utc_timestamp() - timestamp > period
    
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
    return urlsafe_b64encode(s)
    
def deserialize(s):
    uenc = unicode(s)
    s2 = urlsafe_b64decode(uenc.encode("utf-8"))
    
    tokens = s2.split(',')
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
    
    if datetime_expired(dt):
        return header_response() + expired + footer
 
 
    display = textLegibility.Display(xRes, yRes, 
                                     diagonal=diagonal, 
                                     aspect_ratio=aspect_ratio,
                                     bottom=vertical)
              
    rv = textLegibility.plot(display, z_distance=28.0, 
             isopleth_label_xpos=26.2, show_inset=True,
             font_sizes=[10, 12, 14, 16, 18], guideline=16, 
             save_as_pdf=True)
    rv.seek(0)

    return send_file(rv,
                     attachment_filename='il-legible analysis.pdf',
                     as_attachment=True)
                     
#    return str(d) + " " + str(datetime_expired(d['dt']))
    
@app.route('/submit', methods=['POST'])
def submit_response():
    s = header_response([1,0,0,0])
    
    xRes = request.form.get('xRes', '1920')
    yRes = request.form.get('yRes', '1080')
    diagonal = request.form.get('diagonal', '23.9')
    vertical = request.form.get('vertical', '51')
    horizontal = request.form.get('horizontal', '26')
    
    s += main.replace('{{xRes}}', xRes) \
             .replace('{{yRes}}', yRes) \
             .replace('{{diagonal}}', diagonal) \
             .replace('{{vertical}}', vertical) \
             .replace('{{horizontal}}', horizontal) \
             .replace('{{submitcontent}}', 'Rerun Analysis')

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
            
    s += """<img class="result" src="data:image/png;base64,%s"/>""" \
         % rv.getvalue().encode("base64").strip()

    s += submit % data
    
    s += footer;
    return s;
    
@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
