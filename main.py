import random
import StringIO
 
from flask import Flask, request, make_response

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
 
from flask import Flask
app = Flask(__name__)
app.config['DEBUG'] = True

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

import textLegibility

@app.route('/')
def form():
    """Return a friendly HTTP greeting."""
    return '''
	<style type="text/css">


/* All form elements are within the definition list for this example */
dl {
	font:normal 12pt/15pt Helvetica;
    width: 500pt;
}
dt {
   
    width: 200pt;
    padding: 0 0 0 0;
}
dd {

    width: 120pt;
    margin: 0;
    padding: 0 0 16pt 0;
}


/* The hint to Hide and Show */
.hint {
	font:normal 10pt Helvetica;
   	display: none;
    position: absolute;
    left: 200pt;
    width: 200pt;
    margin-top: -18pt;
    border: 1pt solid #c93;
    padding: 10pt 12pt;
    /* to fix IE6, I can't just declare a background-color,
    I must do a bg image, too!  So I'm duplicating the pointer.gif
    image, and positioning it so that it doesn't show up
    within the box */
    background: #ffc url(pointer.gif) no-repeat -10pt 5pt;
}

/* The pointer image is hadded by using another span */
.hint .hint-pointer {
    position: absolute;
    left: -10pt;
    top: 5pt;
    width: 10pt;
    height: 19pt;
    background: url(pointer.gif) left top no-repeat;
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
</script>
<h1 style="font-family:Helvetica;">iLegible</h1>
<h2 style="font-family:Helvetica;">Text Legibility Analysis for Standing Workstations</h2>
<form action="/submit" method="post">
<h3>Display Specifications</h3>
<dl>
	<dt>
		<label for="xRes">Horizontal Resolution (pixels):</label>
	</dt>
	<dd>
		<input id="xRes" name="xRes" type="number" required="true" min="1" max="8192" step="1" value="1920"/>
		<span class="hint">Specify the horizontal resolution of the display.<span class="hint-pointer">&nbsp;</span></span>
	</dd>
	<dt>
		<label for="yRes">Vertical Resolution (pixels):</label>
	</dt>
	<dd>
		<input id="yRes" name="yRes" type="number" required="true" min="1" max="8192" step="1" value="1080"/>
		<span class="hint">Specify the vertical resolution of the display.<span class="hint-pointer">&nbsp;</span></span>
	</dd>
	<dt>
		<label for="diagonal">Diagonal Measurement (inches):</label>
	</dt>
	<dd>
		<input id="diagonal" name="diagonal" type="number" required="true" min="1" max="1000" step="any" value="23.9"/>
		<span class="hint">Specify the horizontal dimension of the display in decimal inches.<span class="hint-pointer">&nbsp;</span></span>
	</dd>
</dl>
<h3>Display Placement</h3>
<dl>
	<dt>
		<label for="vertical">Vertical Dimension:</label>
	</dt>
	<dd>
		<input id="vertical" name="vertical" type="number" required="true" min="0" max="240" step="any" value="51"/>
		<span class="hint">Specify the vertical distance from the floor to the bottom of the display in decimal inches.<span class="hint-pointer">&nbsp;</span></span>
	</dd>
	<dt>
		<label for="horizontal">Horizontal Dimension:</label>
	</dt>
	<dd>
		<input id="horizontal" name="horizontal" type="number" required="true" min="1" max="240" step="any" value="26"/>
		<span class="hint">Specify the horizontal distance from the front of the screen to the operator's eyepoint. If the operator is standing at a bench control board assume the eyepoint is 3 inches pass the front edge.<span class="hint-pointer">&nbsp;</span></span>
	</dd>
</dl>
<input type="submit" class="button" value="Submit" />
</form>
'''
 
@app.route('/submit', methods = ['POST'])
def submit():
    xRes = int(request.form['xRes'])
    yRes = int(request.form['yRes'])
    aspectRatio = float(xRes) / float(yRes)
    diagonal = float(request.form['diagonal'])
    horizontal = float(request.form['horizontal'])
    vertical = float(request.form['vertical'])
    
    display = textLegibility.Display(xRes, yRes, 
                                     diagonal=diagonal, 
                                     aspect_ratio=aspectRatio,
                                     bottom=vertical)
    rv = textLegibility.plot(display, z_distance=28.0, 
              isopleth_label_xpos=26.2, show_inset=True,
              font_sizes=[10, 12, 14, 16, 18], guideline=16)
            
    return """<img src="data:image/png;base64,%s"/>""" % rv.getvalue().encode("base64").strip()
    

@app.route('/plot.png')
def plot():

    display = textLegibility.Display(1920, 1080, 
                                     diagonal=23.9, 
                                     aspect_ratio=16.0/9.0,
                                     bottom=51.0)
    fig = textLegibility.plot(display, z_distance=28.0, 
              isopleth_label_xpos=26.2, show_inset=True,
              font_sizes=[10, 12, 14, 16, 18], guideline=16)
              
    canvas = FigureCanvas(fig)
    output = StringIO.StringIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response
	
@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
