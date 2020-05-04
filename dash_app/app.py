#https://medium.com/@pentacent/nginx-and-lets-encrypt-with-docker-in-less-than-5-minutes-b4b8a60d3a71
from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from config import config_app
from layout import app_layout, make_header, make_main,make_footer
#from plots import bar_plot, scatter_plot, cnt_plot
from functions import generate_plot,load_data,data2dropdown,save_data,get_regions_options,set_regions_options
import json
import urllib

from concurrent.futures import ThreadPoolExecutor
from sys import platform
import os
import time
from datetime import datetime

from style import colors,default_style_country,default_style_area,default_column_style,default_norm_style


import sys
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(stream=sys.stderr))
logger.setLevel(logging.DEBUG)

debug_flag = False

server = Flask(__name__)

app = dash.Dash(name='Bootstrap_docker_app',
                server=server)#,
                #static_folder='static',
                #csrf_protect=False)

# Add css, js, container div with id='page-content' and location with id='url'
app = config_app(app, debug=debug_flag)

# Generate app layoute with 3 div elements: page-header, page-main, page-footer.
# Content of each div is a function input
app.layout = app_layout(header=make_header(),main=make_main(),footer=make_footer())


# Start new thread to check if files changed and save them
if platform == "darwin":
    data_dir = os.path.join('Data','COVID-MAC')
else:
    data_dir = os.path.normpath("/var/lib/dash/data")

#counter = 0
all_data_dict = {}
filesize_dict = {}


# number of seconds between re-calculating the data
UPDADE_INTERVAL = 600
def get_new_data_every(period=UPDADE_INTERVAL):
    """Update the data every 'period' seconds"""
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        app.server.logger.info("Attempting to refresh data at: {}".format(current_time))

        save_data(data_dir, filesize_dict,app)
        load_data(all_data_dict,filesize_dict,app)

        app.server.logger.info("Done")
        time.sleep(period)
# Run the function in another thread
executor = ThreadPoolExecutor(max_workers=1)
executor.submit(get_new_data_every)


out1 = [Output('page-main', 'children'),
               Output('tabs', 'value'),
        Output('javascript', 'run')]

out2 = [Output('page-main', 'children')]

@app.callback(out1,#,Output('country_dropdown', 'value')
              [Input('url', 'pathname')],
              [State('country_dropdown', 'options')])
def routing(pathname,country_opt):
    """Very basic router

    This callback function will read the current url
    and based on pathname value will populate the children of the page-main

    Returns:
        html.Div
    """
    app.server.logger.info(pathname)
    app.title = "COVID19 - dashboard"

    rv = make_main()

    #save_data(data_dir, filesize_dict,app,False)
    #load_data(all_data_dict, filesize_dict,app)

    # if pathname == '/bar':
    #     rv = make_main(bar_plot)
    # elif pathname == '/scatter':
    #     rv = make_main(scatter_plot)
    # else:
    #     rv = make_main({'layout': {'title': 'empty plot: click on a Bar or Scatter link'}})

    js_script = '''
                fix_input();
                function fix_input(){
                var x = document.getElementsByTagName('input');
                var i;
                for (i = 0; i < x.length; i++) {
                  x[i].setAttribute('autocomplete', 'off');
                }
                //console.log("Complete");
                
                //alert('hello');
                }
                '''

    return rv,'health',js_script#,country_opt[0]['value']

# @server.route("/")
# def MyDashApp():
#     app.title = "Title"
#     print('HERE')
#     return app.index()


@app.callback([Output('bar_graph', 'figure'),
               Output('loading-submit-cnt1','children'),
               Output('messages','children')],
              [Input('btn_refresh', 'n_clicks')],
              [State('sel_reg_dropdown', 'data'),
               State('aggragation_radio', 'value'),
               State('log_radio', 'value'),
               ])
def update_plot(n_clicks,sel_reg_dropdown,aggr_in,log_in):
    if n_clicks==0 or not sel_reg_dropdown:
        raise PreventUpdate

    rv,messages = generate_plot(all_data_dict,sel_reg_dropdown,aggr_in,log_in)
    ret_div = html.Div(messages)
    return rv,'done',ret_div



@app.callback([Output('area_dropdown', 'options'),
               Output('area_dropdown', 'value'),
               Output('loading-submit-cnt2','children')],
               [Input('area_type_dropdown', 'value')],
               [State('country_dropdown', 'value'),
                State('tabs', 'value')])
def load_data_callback(area_type,country_in,tabs):
    area_drp = []
    if country_in:
        if tabs == 'health' and len(country_in) == 1 and country_in[0] in all_data_dict and area_type:
            area_drp = data2dropdown(country_in[0], area_type, all_data_dict)
    return area_drp,[], 'done'


@app.callback([Output('area_type_dropdown', 'options'),
               Output('area_type_dropdown', 'value'),
               Output('area_type_dropdown', 'disabled'),
               Output('area_dropdown', 'disabled'),
               Output('area_type_dropdown', 'placeholder'),
               Output('area_dropdown', 'placeholder')],
               [Input('country_dropdown', 'value')],
              [State('tabs', 'value')])
def show_area_type_drp(country_in,tabs):
    disabled_type = True
    disabled_area = True
    placeholder_type = ''
    placeholder_area = ''
    area_type = []
    if country_in:
        if tabs=='health' and len(country_in)==1:
            disabled_type = False
            disabled_area = False
            placeholder_type = 'Area type'
            placeholder_area = 'Area'
        if tabs=='health' and len(country_in)==1 and country_in[0] in all_data_dict:
            area_type_list = all_data_dict[country_in[0]].keys()
            area_type = [{'label': cur_opt, 'value': cur_opt} for cur_opt in area_type_list]

    return area_type,None,disabled_type,disabled_area,placeholder_type,placeholder_area



@app.callback([Output('columns_dropdown', 'options'),
               Output('norm_dropdown', 'options'),
               Output('columns_dropdown', 'value'),
               Output('norm_dropdown', 'value'),
               ],
               [Input('area_type_dropdown', 'value')],
              [State('country_dropdown', 'value'),
               State('tabs', 'value')]
              )
def update_col_options(area_type,country_in,tabs):

    col_drp = []
    norm_drp = []
    new_col_val = None
    new_norm_val = None

    if tabs=='health' and country_in:
        if len(country_in) == 1:
            if area_type:
                cur_dict = all_data_dict[country_in[0]][area_type]
                col_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in cur_dict['options']]
                norm_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in cur_dict['norm']]
        else:
            col_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in all_data_dict['health_opts']]
            norm_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in all_data_dict['health_opts']]

    if tabs == 'response' and country_in:
        cols = all_data_dict['Response_Oxford']['col_names']
        col_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in cols]

    return col_drp,norm_drp,new_col_val,new_norm_val



@app.callback(Output('sel_reg_dropdown','data'),
               [Input('btn_add', 'n_clicks')],
               [State('area_type_dropdown', 'value'),
                State('area_dropdown', 'value'),
                State('sel_reg_dropdown', 'data'),
                State('country_dropdown', 'value'),
                State('tabs', 'value'),
                State('tabs_mob', 'value'),
                State('columns_dropdown', 'value'),
                State('norm_dropdown', 'value'),
                ])
def add_region(n_clicks,area_type_st,area_st,table_st,country_in,tabs,tabs_mob,columns_dropdown,norm_dropdown):

    if n_clicks == 0 or not columns_dropdown:
        raise PreventUpdate

    if not table_st:
        table_st = []

    if tabs == 'mobility':
        tabs_str = '{} - {}'.format(tabs,tabs_mob)
    else:
        tabs_str = tabs

    if not norm_dropdown:
        norm_dropdown = ''

    new_rows = []
    if tabs == 'health':
        if len(country_in)==1:
            for cur_area in area_st:
                for cur_col in columns_dropdown:
                    new_row = {'Tab': tabs_str,
                               'Data': country_in[0],
                               'Area': cur_area,
                               'Area type': area_type_st,
                               'Variable':cur_col,
                               'Denominator':norm_dropdown}#,
                               #'Lin/Log':log_radio,
                               #'Var/Cum':aggragation_radio}
                    new_rows.append(new_row)
        else:
            for cur_area in country_in:
                for cur_col in columns_dropdown:
                    new_row = {'Tab': tabs_str,
                               'Data': cur_area,
                               'Area': cur_area,
                               'Area type': 'Country',
                               'Variable':cur_col,
                               'Denominator':norm_dropdown}#,
                               #'Lin/Log':log_radio,
                               #'Var/Cum':aggragation_radio}
                    new_rows.append(new_row)

    elif tabs == 'response':
        for cur_area in country_in:
            for cur_col in columns_dropdown:
                new_row = {'Tab': tabs_str,
                           'Data': cur_area,
                           'Area': cur_area,
                           'Area type': 'Country',
                           'Variable':cur_col,
                           'Denominator':norm_dropdown}#,
                           #'Lin/Log':log_radio,
                           #'Var/Cum':aggragation_radio}
                new_rows.append(new_row)


    for cur_i,cur_row2 in enumerate(table_st):
        cur_row2['Legend']=cur_i+1

    for cur_row1 in new_rows:
        exist_flag = False
        for cur_row2 in table_st:
            if all(item in cur_row2.items() for item in cur_row1.items()):
                exist_flag=True
                break
        if exist_flag==False:
            cur_row1['Legend']=len(table_st)+1
            cur_row1['Visible (on/off)'] = 'on'
            table_st.append(cur_row1)

    return table_st


@app.callback(Output('tabs_mob_div_id', 'style'),
              [Input('tabs', 'value')])
def tab1_render(tab):
    if tab == 'mobility':
        ret_style = {'display': 'block'}
    else:
        ret_style = {'display': 'none'}
    return ret_style



@app.callback([Output('country_dropdown', 'options'),
               Output('country_dropdown', 'multi'),
               Output('country_div_id', 'style'),
               Output('area_div_id', 'style'),
               Output('country_dropdown', 'placeholder'),
               Output('country_dropdown', 'value'),
               Output('columns_div_id', 'style'),
               Output('norm_div_id', 'style')
               ],
              [Input('tabs', 'value')])
def update_content(tab):
    #global counter
    #app.server.logger.info(counter)

    multi = False
    countries_drp=[]

    style_country = default_style_country.copy()
    style_area = default_style_area.copy()
    column_style = default_column_style.copy()
    norm_style = default_norm_style.copy()

    placeholder='Select countries (multiple allowed)'

    if tab == 'mobility':
        pass
    elif tab == 'health':
        multi = True
        if 'Response_Oxford' in all_data_dict:
            countries = all_data_dict['Response_Oxford']['countries']
            countries_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in countries]
    elif tab == 'response':
        multi = True
        #style_country['width'] = '100%'
        column_style['width'] = '100%'
        #style_area = {'display': 'none'}
        norm_style = {'display': 'none'}
        #placeholder = 'Select countries (multiple allowed)'
        if 'Response_Oxford' in all_data_dict:
            countries = all_data_dict['Response_Oxford']['countries']
            countries_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in countries]

    #counter+=1
    return countries_drp,multi,style_country,style_area,placeholder,None,column_style,norm_style


@app.callback([Output('aggragation_radio', 'value'),
               Output('aggragation_radio', 'style')],
              [Input('log_radio', 'value')],
              [State('aggragation_radio', 'value')])
def aggr_render(log_in,aggr_in):
    if log_in == 'lin':
        return aggr_in,{'display':'block'}
    else:
        return 'cum',{'pointer-events':'none','opacity':'0.5'}

if __name__ == '__main__':
    app.run_server(debug=debug_flag)













