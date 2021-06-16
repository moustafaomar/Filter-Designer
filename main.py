from logging import Filter
from math import atan
import numpy as np
from bokeh.plotting import figure, Column,Row
from bokeh.models import PointDrawTool, ColumnDataSource,Button,Div
from bokeh.models.widgets import RadioButtonGroup
from bokeh.layouts import *
from bokeh.io import curdoc
from bokeh.events import DoubleTap
from scipy.signal import zpk2tf, freqz
import numpy as np
from bokeh.models import Dropdown,RadioGroup
## State variables
filter = None
apply = False
state=0
multiplee=[]
conj = 0
## Figures setup
p = figure(x_range=(-2,2), y_range=(-2,2), tools=[],
           title='Task 5',plot_width=270, plot_height=400)
p2 = figure(x_range=(-2,2), y_range=(-2,2), tools=[],
           title='Filter Designer',plot_width=270, plot_height=400)
PPhase=figure(x_range=(0,3.14), y_range=(-3.14,3.14), tools=[],
           title='Phase',plot_width=270, plot_height=400)
FilterPhase=figure(x_range=(0,3.14), y_range=(-3.14,3.14), tools=[],
title='Filter Phase',plot_width=270, plot_height=400)
PMagnitude=figure(x_range=(0,3.14), y_range=(0,10), tools=[],
           title='Magnitude',plot_width=270, plot_height=400)
## Draw unit circles
p.circle(0,0,radius=1,fill_color=None,line_color='OliveDrab')
p2.circle(0,0,radius=1,fill_color=None,line_color='OliveDrab')
## Initialize column data sources
source = ColumnDataSource({
    'x': [], 'y': [], 'marker': []
})
conjsource = ColumnDataSource({
    'x': [], 'y': [], 'marker': []
})
filtersource = ColumnDataSource({
    'x': [], 'y': [], 'marker': []
})
source2= ColumnDataSource({
    'w':[], 'h':[]
})
source3= ColumnDataSource({
    'w':[], 'p':[]
})
filterp=ColumnDataSource({
    'w':[], 'p':[]
})
## Initialize main zero,pole arrays
Zero=[]
Pole=[]

## Default filters definition
x1=[[0.25,0.5,1],0.5,0.2,0.75]
y1=[[0.25,0.5,1],0.2,0.75]
x2=[[2,1.75,1.5],3,4,5]
y2=[[2,1.75,1.5],3,4,5]

filterzero1x=[0.25,0.5,1]
filterzero1y=[0.25,0.5,1]
filterzero2x=[0.5,0.2,0.75]
filterzero2y=[0.5,0.2,0.75]

filterpole1x=[2,1.75,1.5]
filterpole1y=[2,1.75,1.5]
filterpole2x=[1.25,1.4,1.7]
filterpole2y=[1.25,1.4,1.7]
filterpoles=[[-1.85+1.85*1j,1.75+1.75*1j,-1.5-1.5*1j],[-1.25-1.25*1j,1.4+1.4*1j,1.7-1.7*1j],[-1.32-1.32*1j,1.45-1.45*1j,2+1*1j]]
filterzeros=[]
## Custom filter arrays
customzero_list=[]
custompoles_list=[]
## UI controls
dropdown = RadioButtonGroup(labels=['Zero', 'Pole'], active=0)
dropdown2 = RadioButtonGroup(labels=['No conjugate', 'Conjugate'], active=0)
button = Button(label='Reset')
menu = [("Filter 1", "0"), ("Filter 2", "1"), ("Filter 3", "2")]
bt = Button(label='Apply')
btr = Button(label='Reset filter')
btf = Button(label='Add to filters')
LABELS = ["Single","Multiple"]
checkbox_group = RadioGroup(labels=LABELS, active=0,max_width=70)
dropdown5 = Dropdown(label="Filters picker", button_type="warning", menu=menu)
## UI renderers
renderer = p.scatter(x='x', y='y',marker='marker', source=source,size=15)
renderer2 = p.scatter(x='x', y='y',marker='marker', source=conjsource,size=15)
renderer3 = p2.scatter(x='x', y='y',marker='marker', source=filtersource,size=15)
## Magnitude and phase plots
PMagnitude.line(x='w',y='h',source=source2)
PPhase.line(x='w',y='p',source=source3)
FilterPhase.line(x='w',y='p',source=filterp)
draw_tool = PointDrawTool(renderers=[renderer,renderer2],add=False)
p.add_tools(draw_tool)
p.toolbar.active_tap = draw_tool
draw_tool2 = PointDrawTool(renderers=[renderer3],add=False)
p2.add_tools(draw_tool2)
p2.toolbar.active_tap = draw_tool2

def customzeros(poles):
    xcustomzeros=[]
    ycustomzeros=[]
    fmarker = []
    for element in poles:
         x=element/((np.real(element))**2+(np.imag(element))**2)   
         xcustomzero=np.real(x)
         ycustomzero=np.imag(x)
         xcustomzeros.append(xcustomzero)
         ycustomzeros.append(ycustomzero)
         customzero_list.append(x)
         fmarker.append('circle')
    filtersource.stream({
    'x': xcustomzeros, 'y': ycustomzeros, 'marker': fmarker})
    return customzero_list
def addtofilters():
    global filterpoles,filterzeros,menu,dropdown5,filter
    custom_filter()
    menu.append(("Filter {}".format(len(menu)+1),"{}".format(len(menu))))
    dropdown5.menu=menu
def updatefilter(attr, old, new):
    pass
filtersource.on_change('data',updatefilter)

def  custom_filter():
    global custompoles_list,customzero_list,filterzeros,filterpoles
    for i in range(len(filtersource.data['x'])):
        if filtersource.data['marker'][i] == 'asterisk':
            custompoles_list.append(filtersource.data['x'][i]+filtersource.data['y'][i]*1j)
    filterpoles+=[custompoles_list]
    customzeros(custompoles_list)

def UpdateConj():
    global conj,conjsource,p,draw_tool
    conj = dropdown2.active
    if conj == 0:
        conjsource.data = {'x': [], 'y': [], 'marker': []}
    else:
        generate_conj()
marker = 'circle'
def UpdateMode():
    global marker
    marker = dropdown.active
    if marker == 0:
        marker = 'circle'
    else:
        marker = 'asterisk'
def callback(event):
    source.stream({
    'x': [event.x], 'y': [event.y], 'marker': [marker]
    })
def DrawFilter(event):
    filtersource.stream({
    'x': [event.x], 'y': [event.y], 'marker': ['asterisk']
    })
    custom_filter()
def reset():
    source.data = {'x': [], 'y': [], 'marker': []}
    source2.data= {'w':[],'h':[]}
    source3.data={'w':[],'p':[]}
    conjsource.data = {'x': [], 'y': [], 'marker': []}
    Z_p()
def generate_conj():
    global conj
    if conj:
        conjsource.data = {'x':[],'marker':[],'y':[]}
        for i in range(len(source.data['y'])):
            conjsource.stream({'x':[source.data['x'][i]],'marker':[source.data['marker'][i]],'y':[source.data['y'][i]*-1]})
def update(attr, old, new):
    generate_conj()
    Z_p()
    if not apply:
        return
    allpass()
source.on_change('data',update)

def Z_p():
    global Zero,Pole
    Zero = []
    Pole = []
    for i in range(len(source.data['x'])):
        if source.data and source.data['marker'][i]=='circle':
            Zero.append(source.data['x'][i]+source.data['y'][i]*1j)
        elif source.data:
            Pole.append(source.data['x'][i]+source.data['y'][i]*1j)
    CalcMagnitude()
    
def CalcMagnitude():
    source2.data={
    'w': [], 'h': []
    }
    source3.data={
        'w':[], 'p':[]
        }

    num, den=zpk2tf(Zero,Pole,1)
    w,h=freqz(num,den,worN=10000)
    mag=np.sqrt(h.real**2+h.imag**2)
    phase=np.arctan(h.imag/h.real)
    if len(source.data['x'])==0:
        mag=[]
        w=[]
        phase=[]
        source2.data={'w': [], 'h': [] }
        source3.data={'w':[], 'p':[]}

    source2.stream({
    'w': w, 'h': mag
    })
    source3.stream({
        'w':w, 'p':phase
    })

def calmagfl(index):
    num, den=zpk2tf(filterzeros,filterpoles[index],1)
    w,h=freqz(num,den,worN=10000)
    mag=np.sqrt(h.real**2+h.imag**2)

def phasefilter():
    global filterp
    filterp.data={
        'w':[], 'p':[]
        }
    print(filterzeros)
    test = filterzeros
    if state == 1:
        test = []
        for idx in multiplee:
            test+=setzeros(filterpoles,int(idx))
        print(test)
    num, den=zpk2tf(test,filterpoles[int(filter)],1)
    w,h=freqz(num,den,worN=10000)
   
    phase=np.arctan(h.imag/h.real)
    if len(filtersource.data['x'])==0:
        w=[]
        phase=[]
        filterp.data={'w':[], 'p':[]}

    filterp.stream({
        'w':w, 'p':phase
    })

def phasecalc():
    
    source3.data={
        'w':[], 'p':[]
        }

    num, den=zpk2tf(Zero,Pole,1)
    w,h=freqz(num,den,worN=10000)
   
    phase=np.arctan(h.imag/h.real)
    if len(source.data['x'])==0:
        mag=[]
        w=[]
        phase=[]
        source2.data={'w': [], 'h': [] }
        source3.data={'w':[], 'p':[]}

    source3.stream({
        'w':w, 'p':phase
    })
    
def setzeros(poles,filternum):
    global filterzeros
    if(state==0):
        
        filterzeros=[]
        for element in poles[filternum]:
            x=element/((np.real(element))**2+(np.imag(element))**2)
            filterzeros.append(x)
    else:
        
        filterzeros=[]
        for i in range(len(poles)):
            if str(i) in multiplee:
                for element in poles[i]:
                   x=element/((np.real(element))**2+(np.imag(element))**2)
                   filterzeros.append(x)
    return filterzeros
def checkbox(event):
    global state
    state=event

def valueUp(event):
    global filter
    
    filter = event.item

    allpass()

def status():
    global multiplee
    x=int(filter)
    if state==1:
        multiplee.append(filter)



def allpass():
    filtersource.data = {'x':[],'y':[],'marker':[]}
    
    status()
    xpoles=[]
    ypoles=[]
    xzeros=[]
    yzeros=[]
    try:
        index=int(filter)
    except:
        return

    markers = []
    filterzeros=setzeros(filterpoles,index)
    calmagfl(index)
    for element in filterzeros:
       x1=np.real(element)
       y1=np.imag(element)
       xzeros.append(x1)
       yzeros.append(y1)
       Zero.append(element)
       markers.append('circle')

    if(state==0):

      
     for element in filterpoles[index]:
         x2=np.real(element)
         y2=np.imag(element)
         xpoles.append(x2)
         ypoles.append(y2)
         Pole.append(element)
         markers.append('asterisk')
     xscale = xzeros+xpoles
     yscale = yzeros+ypoles
    elif(state==1):
        for i in range(len(filterpoles)):
            if str(i) in multiplee:
                for element in filterpoles[i]:
      
                  x2=np.real(element)
                  y2=np.imag(element)
                  xpoles.append(x2)
                  ypoles.append(y2)
                  Pole.append(element)
                  markers.append('asterisk')
        xscale = xzeros+xpoles
        yscale = yzeros+ypoles
  
    if apply:
        phasecalc()
    filtersource.stream({
    'x': xscale, 'y': yscale, 'marker': markers
    })
    phasefilter()
def apply_filter():
    global apply
    apply = True
    allpass()
def reset_filter():
    global custompoles_list,customzero_list
    filtersource.data={'x':[],'y':[],'marker':[]}
    filterp.data = {'w':[],'p':[]}
    custompoles_list = []
    customzero_list = []
## Control hooks
p.on_event(DoubleTap, callback)
p2.on_event(DoubleTap, DrawFilter)
button.on_click(reset)
dropdown.on_change('active', lambda attr, old, new: UpdateMode())
dropdown2.on_change('active', lambda attr, old, new: UpdateConj())
dropdown5.on_click(valueUp)
checkbox_group.on_click(checkbox)
bt.on_click(apply_filter)
btr.on_click(reset_filter)
btf.on_click(addtofilters)
mytext =Div(text="""<h3>To add a zero/pole double click the plotter. <br> To delete a zero/pole click the zero/pole to select then click backspace. <br> To move a zero/pole drag it to the position where you would like it to be.</h3>""")
layout=Column(Row(dropdown,dropdown2,button),Row(dropdown5,bt,btr,checkbox_group,btf),Row(p,PMagnitude,PPhase,p2,FilterPhase),mytext)
curdoc().add_root(layout)
