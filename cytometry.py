'''
Do basic cytometry analysis

Use the ``bokeh serve`` command to run the example by executing:
    bokeh serve cytometry.py
at your command prompt. Then navigate to the URL
    http://localhost:5006/cytometry
in your browser.

File setup:
Get all the cytometry files you want to use and place them in the import
directory.

They will be converted to appropriate FCS files for reading.

In most cases this just copies files, but in the case of the CellQuest Pro,
it also removes the non-utf8 character \xaa from the header.
'''

import numpy as np
import fcs as fcsparser
import os

from bokeh.layouts import row, column
from bokeh.models import BoxSelectTool, LassoSelectTool, Spacer, Label
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, curdoc
from bokeh.layouts import widgetbox
from bokeh.models.widgets import Select, Button, PreText
# from importer import import_files
#
# import_files()

# Add/remove color channels here
colors = [u'FSC-H', u'SSC-H', u'FL1-H', u'FL2-H', u'FL3-H', u'FL1-A', u'FL1-W']

# The beautiful mess of global variables that tracks the state
params = {"file": "", "x": colors[0], "y": colors[0], "data": 0,
          "n_tot": 0, "n_sel": 0, "selected": []}


def fcs_files():
    files = []
    for f in os.listdir('import'):
        try:
            fcsparser.parse('import/' + f)
            files.append(f)
        except:
            pass
    return files


# create three normal population samples with different parameters
params["file"] = fcs_files()[0]
d = fcsparser.parse("import/" + params["file"])[-1]
params["data"] = d
xdata = np.array(params["data"][params["x"]])
ydata = np.array(params["data"][params["y"]])
params["n_tot"] = len(xdata)
hhist, hedges = np.histogram(xdata, bins=40)
hzeros = np.zeros(len(hedges)-1)

vhist, vedges = np.histogram(ydata, bins=40)
vzeros = np.zeros(len(vedges)-1)

print("Loading Data")
source = ColumnDataSource(data={"x": xdata, "y": ydata})
hsource = ColumnDataSource(data={"vright": vhist, "vbottom": vedges[:-1],
                                 "vtop": vedges[1:],
                                 "vselect": vzeros, "htop": hhist,
                                 "hleft": hedges[:-1], "hright": hedges[1:],
                                 "hselect": hzeros})
edges = {"hedges": hedges, "vedges": vedges}

TOOLS = "pan,wheel_zoom,box_select,lasso_select,reset"

# create the scatter plot
p = figure(tools=TOOLS, plot_width=600, plot_height=600, min_border=10,
           min_border_left=50, toolbar_location="above", x_axis_location=None,
           y_axis_location=None, title="Cytometry Measurements")
p.background_fill_color = "#fafafa"
p.select(BoxSelectTool).select_every_mousemove = False
p.select(LassoSelectTool).select_every_mousemove = False

r = p.scatter('x', 'y', source=source, size=3, color="#3A5785", alpha=0.6)

count = Label(x=100, y=40, x_units='screen', y_units='screen',
              text="0 / {}".format(params["n_tot"]), render_mode='css',
              background_fill_color='white', background_fill_alpha=0.5)
p.add_layout(count)
# create the horizontal histogram


LINE_ARGS = dict(color="#3A5785", line_color=None)

ph = figure(toolbar_location=None, plot_width=p.plot_width, plot_height=200,
            x_range=p.x_range, min_border=10,
            min_border_left=50, y_axis_location="right")
ph.xgrid.grid_line_color = None
ph.yaxis.major_label_orientation = np.pi/4
ph.background_fill_color = "#fafafa"


h0 = ph.quad(bottom=0, left="hleft", right="hright", top="htop",
             color="white", line_color="#3A5785", source=hsource)
hh1 = ph.quad(bottom=0, left="hleft", right="hright", top="hselect",
              alpha=0.5, source=hsource, **LINE_ARGS)

# create the vertical histogram
pv = figure(toolbar_location=None, plot_width=200, plot_height=p.plot_height,
            y_range=p.y_range, min_border=10,
            y_axis_location="right")
pv.ygrid.grid_line_color = None
pv.xaxis.major_label_orientation = np.pi/4
pv.background_fill_color = "#fafafa"

vh0 = pv.quad(left=0, bottom="vbottom", top="vtop", right="vright",
              color="white", line_color="#3A5785", source=hsource)
vh1 = pv.quad(left=0, bottom="vbottom", top="vtop", right="vselect",
              alpha=0.5, source=hsource, **LINE_ARGS)


print("Building Widgets")
file_selector = Select(title="File:", value="file", options=fcs_files())
x_selector = Select(title="X Sample:", value="x", options=colors)
y_selector = Select(title="Y Sample:", value="y", options=colors)
record_button = Button(label="Record", button_type="success")
stats = PreText(text='FILE N_SEL N_TOT\n', width=300)


def update_lasso(attr, old, new):
    params["selected"] = np.array(new['1d']['indices'])
    update_histos()
    update_annotation()
    return None


def update_histos():
    inds = params["selected"]
    if len(inds) == 0 or len(inds) == len(params["data"][params["x"]]):
        hhist1 = np.zeros(len(edges["hedges"] - 1))
        vhist1 = np.zeros(len(edges["vedges"] - 1))
    else:
        hhist1, _ = np.histogram(params["data"][params["x"]][inds],
                                 bins=edges["hedges"])
        vhist1, _ = np.histogram(params["data"][params["y"]][inds],
                                 bins=edges["vedges"])
    hsource.data["hselect"] = hhist1
    hsource.data["vselect"] = vhist1
    return None


def update_annotation():
    params["n_sel"] = len(params["selected"])
    count.text = "{0} / {1}".format(params["n_sel"], params["n_tot"])
    return None


def print_data():
    stats.text += "{} {} {}\n".format(params["file"], params["n_sel"],
                                      params["n_tot"])
    return None


def update_data():
    xdata = np.array(params["data"][params["x"]])
    ydata = np.array(params["data"][params["y"]])

    hhist, hedges = np.histogram(xdata, bins=40)
    hzeros = np.zeros(len(hedges)-1)

    vhist, vedges = np.histogram(ydata, bins=40)
    vzeros = np.zeros(len(vedges)-1)
    new_data = {"x": xdata, "y": ydata}
    h_data = {"vright": vhist, "vbottom": vedges[:-1], "vtop": vedges[1:],
              "vselect": vzeros, "htop": hhist,
              "hleft": hedges[:-1], "hright": hedges[1:], "hselect": hzeros}
    edges["vedges"] = vedges
    edges["hedges"] = hedges
    source.data = new_data
    hsource.data = h_data
    params["n_tot"] = len(xdata)

    update_histos()
    update_annotation()
    return None


def file_change(attr, old, new):
    params["selected"] = []
    params["file"] = new
    filename = "./import/" + params["file"]
    cytometry = fcsparser.parse(filename)
    params["data"] = cytometry[-1]
    update_data()
    return None


def x_change(attr, old, new):
    params["x"] = new
    update_data()
    return None


def y_change(attr, old, new):
    params["y"] = new
    update_data()
    return None

file_selector.on_change("value", file_change)
x_selector.on_change("value", x_change)
y_selector.on_change("value", y_change)
record_button.on_click(print_data)
r.data_source.on_change('selected', update_lasso)

widgets = widgetbox(file_selector, x_selector, y_selector, record_button,
                    stats, width=300)
layout = column(row(p, pv, widgets), row(ph, Spacer(width=500, height=200)))

curdoc().add_root(layout)
curdoc().title = "COUNTATRON 5000"

print("BOKEH GO!")
