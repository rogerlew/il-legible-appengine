# -*- coding: utf-8 -*-
"""
Models the size, resolution, and physical location of a single video display
unit for standing users. In conjunction with standing distance graphical
determines recommended font character sizes for compliance with NUREG-0700
and ISO 9241-3.

Author: Roger Lew
        roger.lew@inl.gov

Last modified: 5/11/2015

Version: 1.1
"""

import math
import numpy as np
from numpy import pi

import base64
from io import BytesIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot as plt

plt.rc('font', family='serif')
purple = '#663399'
dkgreen = '#006400'
dkgray = '#555555'
teal = '#69acaf'
                 
class Display:
    """
    defines display parameters and phsyical location
    horizontal and vertical resolution must both be specified
    
    two of the following must be specified to determine the screen geometry:
        width, height, diagonal, and aspect ratio
        (assumes width, height, and diagonal are in inches)
        
    one of the following must be specified to determine the vertical physical
    location of the display:
        bottom (floor to bottom of screen), top (floor to top of screen)
    """
    def __init__(self, hor_res, ver_res, 
                 width=None, height=None, diagonal=None, aspect_ratio=None,
                 bottom=None, top=None, tilt=0):
                     
        if (width is not None and height is not None):
            diagonal = math.sqrt(width**2 + height**2)
            
        if (width is not None and diagonal is not None):
            height = math.sqrt(diagonal**2 - width**2)
            
        if (height is not None and diagonal is not None):
            width = math.sqrt(diagonal**2 - height**2)
            
        if (aspect_ratio is None):
            if (None in [height, width, diagonal]):
                raise Exception("Cannot determine screen geometry")
                
            aspect_ratio = width/height
            
        if (aspect_ratio is not None and height is not None):
            width = aspect_ratio * height
            diagonal = math.sqrt(width**2 + height**2)
            
        if (aspect_ratio is not None and width is not None):
            height = 1.0 / aspect_ratio * width
            diagonal = math.sqrt(width**2 + height**2)
            
        if (aspect_ratio is not None and diagonal is not None):
            # w^2 + h^2 = d^2
            # a = w/h -> w = ah
            # (ah)^2 + h^2 = d^2 -> wolfram alpha solve for h...
            # h must be > 0...
            # h = d / sqrt(a^2 + 1)
            height = diagonal / math.sqrt(aspect_ratio**2 + 1)
            width = math.sqrt(diagonal**2 - height**2)
        
        pix_aspect_ratio = float(hor_res) / float(ver_res)
        if (round(aspect_ratio,3) != round(pix_aspect_ratio, 3)):
            raise Exception("Pixels are not square")
        
        dot_pitch = height / ver_res
        
        if (bottom is not None):
            top = bottom + height
        elif (top is not None):
            bottom = top - height
        else:
            raise Exception("Vertical location not defined")
        
        center = bottom + height / 2.0
        
        self.hor_res = hor_res
        self.ver_res = ver_res
        self.width = width
        self.height = height
        self.diagonal = diagonal
        self.aspect_ratio = aspect_ratio
        self.dot_pitch = dot_pitch
        self.bottom = bottom
        self.top = top
        self.center = center
        self.tilt = tilt
            
    def moa(self, x, font_size):
        """
        calculates arcsize in minutes of viewing angle as a function of
        viewing distance (x) and font size (font_size)
        """
        return np.arctan(self.cs(font_size)/x)*(180/pi)*60.0
        
    def cs(self, font_size, units='in'):
        """
        calculates the physical size of the given font size based on the
        display's dot pitch
        
        if units=='mm' the physical size is returned in millimeters
        """
        if units == 'mm':
            return font_size * self.dot_pitch * 25.4
        
        return font_size * self.dot_pitch
            
    def __str__(self):
        return '%0.1f" diagonal, %ix%i, %0.5f" dot pitch'\
               %(self.diagonal, self.hor_res, self.ver_res, self.dot_pitch)
        
    def desc(self):        
        return '%0.1fdiag,%ix%i,%0.5fdp'\
               %(self.diagonal, self.hor_res, self.ver_res, self.dot_pitch)

class Person:
    """
    represents the height and standing distance of a person
    provides some convenience functionality for determining eyeheight and
    SI string formatting.
    """
    def __init__(self, height, sitting=False):
        """
        height is the person's height in inches
        distance is the horizontal distance of the person from the display
        in inches
        """
        
        # anthropormetry from 
        # http://ergotmc.gtri.gatech.edu/dgt/Design_Guidelines/hndch703.htm
        # averaging male and female measurements
        self.eyeheight_stature = (64.7/68.3 + 60.3/62.9) / 2.0
        self.popliteal_stature = (17.3/68.3 + 15.7/62.9) / 2.0
        self.eyeheightsitting_stature = (31.3/68.3 + 29.3/62.9) / 2.0        
        self.height = height
        if sitting:
            self.eyeheight = height * self.popliteal_stature + \
                             height * self.eyeheightsitting_stature
        else:
            self.eyeheight = height * self.eyeheight_stature
            
        self.sitting = sitting
        
    def __str__(self):
        h = self.height
        ft = int(math.floor(h/12.0))
        iN = int(round(h)%12.0)
        
        return '%i\'%i"'%(ft, iN)

def isfloat(x):
    try:
        float(x)
    except:
        return False
    
    return True

def _viewing_distance(display, z_distance, p):
    dymin = math.sqrt((p.eyeheight - display.bottom)**2 + (z_distance - 3.4)**2)
    dymax = math.sqrt((p.eyeheight - display.top)**2 + (z_distance - 3.4)**2)
    return max(dymin, dymax) # take the most conservative distance

viewing_distance = np.vectorize(_viewing_distance)

def erfcc2(x):
    """Complementary error function."""
    z = np.abs(x)
    t = 1.0 / (1.0 + 0.5*z)
    r = t * np.exp(-z*z-1.26551223+t*(1.00002368+t*(0.37409196+
    	t*(0.09678418+t*(-0.18628806+t*(0.27886807+
    	t*(-1.13520398+t*(1.48851587+t*(-0.82215223+
    	t*0.17087277)))))))))
	
    mask = x < 0.0
    r[mask] = 2.0 - r[mask]
    return r

erfcc = np.vectorize(math.erfc)

sqrt2 = math.sqrt(2.0)
sqrt2pi = math.sqrt(2.0 * pi)
def ncdf(x):
    global sqrt2
    return 1.0 - 0.5 * erfcc( x / sqrt2)
	
def normcdf(x, mu, sigma):
    global sqrt2
    t = x - mu
    y = 0.5 * erfcc( -t / ( sigma * sqrt2))
    return np.clip(y, 0.0, 1.0)

def normpdf(x, mean, sd):
    v = sd ** 2.0
    u = math.sqrt(2 * pi * v)
    y = np.exp(-(x - mean) ** 2.0 / (2.0 * v))
    return y / u
    
def normpdf2(x, mu, sigma):
    global sqrt2pi
    u = (x - mu) / abs(sigma)
    y = (1.0 / (sqrt2pi * abs(sigma))) * np.exp( -u * u / 2.0)
    return y

def plot(display, z_distance=None, pop=50, sitting=False,
         font_sizes=None, 
         fname=None, isopleth_label_xpos=None, show_inset=False, 
         guideline=16, save_as_pdf=False):
    """
    Creates a figure depicting viewing angle in MOA as a function of
    viewing distance, and font size. Font size is dependent on the
    physical size and resolution of the provided display parameter.
    The viewing distance is a function of the standing distance and
    heights of the population in the people parameter.
    
    display should be a Display instance
    people should be a list of Person instances
    
    To make things look pretty x axis limits should be divisible by 4 and y 
    axis limits should be divisible by 5.
    """
    
    if font_sizes is None:
            
        font_sizes=[10, 12, 14, 16, 18]

        if display.hor_res >= 2560:
            font_sizes = [14, 16, 18, 20, 24]

        if display.hor_res >= 3840:
            font_sizes = [18, 20, 24, 28, 32]


    if (z_distance is None):
        heights = []
    else: 
        heights = [60, 62, 64, 66, 68, 70, 72, 74, 76]
        
    people = [Person(h, sitting=sitting) for h in heights]

    # Specify some plotting parameters
    N = 1000 # x axis discretization parameter
        
    # array of heights between 55" and 80" for distribution plots
    hts = np.linspace(50, 85, N)

    pct_m = pop * 0.01
    pct_f = 1.0 - pct_m
    
    mu_m, sd_m = 68.6, 2.74
    pdf_m = pct_m * normpdf(hts, mu_m, sd_m)
    cdf_m = normcdf(hts, mu_m, sd_m)

    mu_f, sd_f = 64.25, 2.58
    pdf_f = pct_f * normpdf(hts, mu_f, sd_f)
    cdf_f = normcdf(hts, mu_f, sd_f)
    
    pdf_pop = pdf_m + pdf_f
                
    # specify the viewing distance parameters for plot in inches
    xmin = 16
    xmax = 36
    x = np.linspace(xmin, xmax, N)
    
    # specify the arc size parameters for plot in inches
    ymin = 10
    ymax = 30
    y1 = np.zeros(N)

    ymax_pdf = 0.15
    
    # create and setup the figure
    plt.figure(figsize=(12,14))
    plt.subplots_adjust(top=0.77, right=0.89, left=0.08, bottom=0.25)
    fig_aspect = (0.89 - 0.08) / (0.76 - 0.10)

    # if the x position of the isopleth labels is defined find it
    # here so we don't have to find the index for each font size
    indx = np.argmin(np.abs(isopleth_label_xpos - x))
    
    # draw the font size isopleths
    for (i, font_size) in enumerate(font_sizes[::-1]):
        y2 = display.moa(x, font_size)
        plt.fill_between(x, y1, y2, facecolor='gray', alpha=0.25)
        
        # label the isopleths
        if isopleth_label_xpos is None:
            indx = int(0.58 * N - i * 0.028 * N)
            
        rise = y2[indx+20] - y2[indx]
        rise /= ymax - ymin
        run = x[indx+20] - x[indx]
        run /= xmax - xmin
        run *= fig_aspect
        slope = math.atan(rise/run) * (180.0/pi)
        
        plt.text(x[indx] - 0.2, y2[indx] - 0.2, '%i Pt'%font_size,
                 ha='left', va='bottom', 
                 rotation=slope, color=dkgray)
            
        # create the font size table in the top right corner
        ypos = 32 + i * 0.75
        plt.text(30.5, ypos, '%i Pt'%font_size)
        plt.text(32.0, ypos, '%0.3f"'%display.cs(font_size))
        plt.text(33.75, ypos, '%0.2f mm'%display.cs(font_size, units='mm'))
        
    # set the x and y limits, specify the ticks and turn on the grid
    plt.xlim([xmin, xmax])
    plt.ylim([ymin, ymax])

    yticks = np.linspace(ymin, ymax, int((ymax - ymin) / 1.0 + 1.0))
    plt.yticks(yticks)#, [('','%i'%t)[t%5==0] for t in yticks])

    xticks = np.linspace(xmin, xmax, int((xmax - xmin) / 2.0 + 1.0))
    plt.xticks(xticks)#, [('','%i'%t)[t%4==0] for t in xticks])
    plt.grid(which='both')
    
    # provide MOA guideline references
##    plt.axhline(14.0, c=dkgreen)    
##    plt.text(xmax + 0.2, 14.0, 'Hugo (2009)', 
##             ha='left', va='center', color=dkgreen)
    plt.axhline(guideline, c=dkgreen)
    if (guideline == 16.0):
        plt.text(xmax + 0.2, 16.0, 'NUREG-0700', 
                 ha='left', va='center', color=dkgreen)
    plt.text(36.2, 21.0, '"$Acceptable$"', 
             rotation = 45, ha='left', va='bottom', color=dkgreen)
    plt.text(36.2, 11.0, '"$Unacceptable$"', 
             rotation = 45, ha='left', va='bottom', color=dkgreen)
    
    # label the axes
    plt.ylabel('Viewing Angle (MOA)')
    plt.xlabel('Viewing Distance (in)')
    
    # show the contribution of height variability        
    for p in people:
        d = viewing_distance(display, z_distance, p)
        
        plt.axvline(d, c=purple, ls='-.')
        plt.text(d - 0.3, ymax + 0.2, str(p), color=purple, 
                 rotation=45, ha='left', va='bottom')
        
    # provide the model parameters in the top left
    xpos = xmin + 0.1
    plt.text(xpos, 36.75, 'Model Assumptions', fontsize=16)
    plt.text(xpos, 36.00, str(display))
    plt.text(xpos, 35.25, 'Bottom of Screen Height: %0.1f"'%display.bottom)
    plt.text(xpos, 34.50, 'Vertical Tilt: %0.1f$^{\circ}$'%display.tilt)
    if len(people) > 0:
        w = display.width       
        fov = math.atan(w/2.0/z_distance) * (180.0/pi) * 2.0
        plt.text(xpos, 33.75, 'z Distance: %0.1f" (%i$^{\circ}$ FOV)'\
                              %(z_distance, fov))
        plt.text(xpos, 33.00, 'Posture: %s'\
                              %('Standing', 'Sitting')[sitting])
        plt.text(xpos, 32.25, 
                 'Population: %i%% Male'%pop)
##        plt.text(xpos, 7.6,
##                 r'Population Model: '
##                 r'$\frac{1}{\omega\pi} e^{-\frac{(x-\xi)^2}{2\omega^2}} '
##                 r'\int_{-\infty}^{\alpha\left(\frac{x-\xi}{\omega}\right)}'
##                 r'e^{-\frac{t^2}{2}}\ dt$, $\mathrm{where}$ '
##                 r'$\xi = %0.1f$, $\omega = %0.1f$, $\alpha = %0.02f$, '
##                 r'(50th Percentile = %0.1f")'
##                 %(pop_mu, pop_sd, pop_skew, pop_median))

    if show_inset:
        # Vertical Distance / View Angle plot inset
        ppl = [Person(h, sitting=sitting) for h in hts]
        ehts = np.array([p.eyeheight for p in ppl])
        
        ax = plt.axes([0.45, 0.84, 0.12*(4.0/3.0), 0.12])
        plt.fill_between(hts, y1, pdf_f,
                         facecolor='#000000', linewidth=0, alpha=0.07)
        plt.fill_between(hts, y1, pdf_m,
                         facecolor='#000000', linewidth=0, alpha=0.07)
        plt.plot(hts, pdf_pop, c='#999999', ls=':')
        distances = (ehts - display.center + 30) / 60.0 * ymax_pdf
        plt.plot(hts, distances, color=purple)
        plt.ylim([0.0, ymax_pdf])
        plt.yticks(np.linspace(0, ymax_pdf, 5),
                   ['-30"','-15"', '0"', '15"', '30"'])
        for tl in ax.get_yticklabels():
            tl.set_color(purple)
            tl.set_fontsize(11)
        
        ax2 = ax.twinx()
        angles = np.arctan((ehts - display.center) / z_distance) 
        angles *= (180.0 / pi) 
        angles -= display.tilt
        plt.plot(hts, angles, color=teal)
        plt.xlim([51,82])
        xticks = np.linspace(54, 78, 5)
        plt.xticks(xticks, ['' for t in xticks])
        for tl in xticks:
##            plt.axvline(tl, c='k', ls=':')
            plt.text(tl+1, -62, str(Person(tl, 0)), 
                     rotation=45, ha='right', va='top', fontsize=11)
        plt.ylim([-60, 60])
        yticks = np.linspace(-60, 60, 9)
        plt.yticks(yticks, ['%i$^{\circ}$'%t for t in yticks])
        plt.axhline(0, color='k', ls=':')
        for tl in ax2.get_yticklabels():
            tl.set_color(teal)
            tl.set_fontsize(11)

##        plt.grid()
    
        plt.text(69.5, 76, 'Vertical Distance', 
                 color=purple, ha='right', va='bottom', fontsize=11)
        plt.text(70.5, 76, '/', ha='center', va='bottom', fontsize=11)
        plt.text(71.5, 73, 'View Angle', 
                 color=teal, ha='left', va='bottom', fontsize=11)
                 
    # Distribution adherence analysis
    ehts = np.array([Person(h).eyeheight for h in hts])
    for i in range(min(5,len(font_sizes))):
        fs = font_sizes[i]
        
        ax = plt.axes([0.08 + i*0.166, 0.07, 0.11*(4.0/3.0), 0.11])
        plt.fill_between(hts, y1, pdf_f,
                         facecolor='#000000', linewidth=0, alpha=0.07)
        plt.fill_between(hts, y1, pdf_m,
                         facecolor='#000000', linewidth=0, alpha=0.07)
        plt.plot(hts, pdf_pop, c='#999999', ls=':')
        plt.ylim([0.0, ymax_pdf])
        plt.yticks([])
        plt.xlim([51,82])
        plt.xticks([])
        plt.title('%i Pt'%fs, fontsize=11)

        h = display.dot_pitch * fs
        d2bs = np.sqrt((ehts - display.bottom)**2 + (z_distance - 3.4)**2)
        d2ts = np.sqrt((ehts - display.top)**2 + (z_distance - 3.4)**2)

        Qy = np.array([(display.top, display.bottom)[d2b>d2t] for (d2b, d2t) in zip(d2bs, d2ts)])
        Py = np.array([(display.top-h, display.bottom+h)[d2b>d2t] for (d2b, d2t) in zip(d2bs, d2ts)])

        q = np.sqrt((z_distance - 3.4)**2 + (Qy - ehts)**2)
        p = np.sqrt((z_distance - 3.4)**2 + (Py - ehts)**2)
        moas = np.arccos((q**2 + p**2 - h**2)/(2*q*p)) * (180.0/pi) * 60.0
#        moas = np.arctan(h/q) * (180.0/pi) * 60.0
        
        Imoas = [j for (j,m) in enumerate(moas) if m > guideline]
        f_pct_L, f_pct_u, = 0.0, 0.0
        m_pct_L, m_pct_u, = 0.0, 0.0
        i0, iend = 0,0
        if len(Imoas) > 0:
            i0 = Imoas[0]
            iend = Imoas[-1]
            plt.fill_between(hts[i0:iend], y1[i0:iend], pdf_f[i0:iend],
                             facecolor=dkgreen, linewidth=0, alpha=0.3)
            plt.fill_between(hts[i0:iend], y1[i0:iend], pdf_m[i0:iend],
                             facecolor=dkgreen, linewidth=0, alpha=0.3)
            f_pct_L = cdf_f[i0]
            f_pct_u = cdf_f[iend]
            
            m_pct_L = cdf_m[i0]
            m_pct_u = cdf_m[iend]

        f_pct_t = f_pct_u - f_pct_L
        m_pct_t = m_pct_u - m_pct_L
        pop_pct_t = pct_m * m_pct_t + pct_f * f_pct_t
        
        _str = lambda r : ('%0.1f'%(r*100), '< 0.1')[r < 0.001 and r > 0.0]

        plt.text(52, -0.03, 'F:', horizontalalignment='left', verticalalignment='top')
        plt.text(52, -0.05, 'M:', horizontalalignment='left', verticalalignment='top')
        
        plt.text(62, -0.01, 'L', horizontalalignment='right', verticalalignment='top')
        plt.text(62, -0.03, '%0.1f'%(f_pct_L*100), horizontalalignment='right', verticalalignment='top')
        plt.text(62, -0.05, '%0.1f'%(m_pct_L*100), horizontalalignment='right', verticalalignment='top', fontdict=dict(color='#666666'))
        
        plt.text(71, -0.01, 'U', horizontalalignment='right', verticalalignment='top')
        plt.text(71, -0.03, '%0.1f'%(f_pct_u*100), horizontalalignment='right', verticalalignment='top', fontdict=dict(color='#666666'))
        plt.text(71, -0.05, '%0.1f'%(m_pct_u*100), horizontalalignment='right', verticalalignment='top')
        
        plt.text(83.8, -0.01, 'T %', horizontalalignment='right', verticalalignment='top')
        plt.text(80, -0.03, _str(f_pct_t), horizontalalignment='right', verticalalignment='top', fontdict=dict(color='#666666'))
        plt.text(80, -0.05, _str(m_pct_t), horizontalalignment='right', verticalalignment='top', fontdict=dict(color='#666666'))
        plt.text(80, -0.07, _str(pop_pct_t), horizontalalignment='right', verticalalignment='top')
    

    rv = BytesIO()

    plt.savefig(rv, format=("png", "pdf")[save_as_pdf])
    plt.clf()
    rv.seek(0)
    

    return rv 
   