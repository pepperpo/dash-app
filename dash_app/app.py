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

from style import colors,default_style_country,default_style_area,default_column_style,default_norm_style,default_at_style,default_area_style


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
    data_dir = os.path.join('..','data','COVID-MAC')
else:
    data_dir = os.path.normpath("/var/lib/dash/data")

#counter = 0
all_data_dict = {}
#filesize_dict = {}


# number of seconds between re-calculating the data
UPDADE_INTERVAL = 600
def get_new_data_every(period=UPDADE_INTERVAL):
    """Update the data every 'period' seconds"""
    while True:
        now = datetime.now()
        current_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        app.server.logger.info("Attempting to refresh data at: {}".format(current_time))

        save_data(data_dir,app)
        load_data(all_data_dict,data_dir,app)

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

    #save_data(data_dir,app,True)
    #load_data(all_data_dict, data_dir,app)

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
               Output('loading-submit-cnt2','children'),
               Output('area_dropdown', 'disabled'),
               Output('columns_dropdown', 'disabled')],
               [Input('area_type_dropdown', 'value')],
               [State('country_dropdown', 'value'),
                State('tabs', 'value'),
                State('tabs_mob', 'value')])
def load_data_callback(area_type,country_in,tabs,tabs_mob):
    area_drp = []
    area_val = []
    disabled_area = True
    disabled_col = False
    if country_in:
        if tabs == 'health' and len(country_in) == 1 and country_in[0] in all_data_dict:
            if area_type:
                if area_type == 'Country':
                    area_drp = [{'label':country_in[0], 'value':country_in[0]}]
                    area_val = country_in
                else:
                    area_drp = data2dropdown(country_in[0], area_type, all_data_dict)
                    disabled_area = False
            else:
                disabled_col = True

        if tabs == 'mobility':
            if tabs_mob == 'google' and 'Mobility_Google' in all_data_dict \
                    and len(country_in) == 1 and country_in[0] in all_data_dict['Mobility_Google']['options'] \
                    and area_type and len(area_type) == 1:
                area_list = all_data_dict['Mobility_Google']['options'][country_in[0]][area_type[0]]
                if area_list:
                    disabled_area = False
                    area_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in area_list]

    return area_drp,area_val, 'done',disabled_area,disabled_col


@app.callback([Output('area_type_dropdown', 'options'),
               Output('area_type_dropdown', 'value'),
               Output('area_type_dropdown', 'disabled'),
               Output('area_type_dropdown', 'placeholder'),
               Output('area_dropdown', 'placeholder'),
               Output('area_type_dropdown', 'multi')],
               [Input('country_dropdown', 'value')],
              [State('tabs', 'value'),
               State('tabs_mob', 'value')])
def show_area_type_drp(country_in,tabs,tabs_mob):
    disabled_type = True
    #disabled_area = True
    placeholder_type = ''
    placeholder_area = ''
    multi_at_drop = False
    area_type = []

    if country_in:
        if tabs=='health' and len(country_in)==1:
            disabled_type = False
            #disabled_area = False
            placeholder_type = 'Area type'
            placeholder_area = 'Area'
            if country_in[0] in all_data_dict:
                area_type_list = all_data_dict[country_in[0]].keys()
                area_type = [{'label': cur_opt, 'value': cur_opt} for cur_opt in area_type_list]

        if tabs=='mobility':
            if tabs_mob=='google' and 'Mobility_Google' in all_data_dict \
                    and len(country_in)==1 and country_in[0] in all_data_dict['Mobility_Google']['options']:
                disabled_type = False
                multi_at_drop = True
                placeholder_type = 'Sub-region 1 (multiple allowed)'
                placeholder_area = 'Sub-region 2 (multiple allowed)'
                area_type_list = all_data_dict['Mobility_Google']['options'][country_in[0]].keys()
                if area_type_list:
                    area_type = [{'label': cur_opt, 'value': cur_opt} for cur_opt in area_type_list]

            if tabs_mob=='apple' and 'Mobility_Apple' in all_data_dict \
                    and country_in in all_data_dict['Mobility_Apple']['options']:
                disabled_type = False
                multi_at_drop = True
                placeholder_type = 'Region'
                area_type_list = all_data_dict['Mobility_Apple']['options'][country_in].keys()
                if area_type_list:
                    area_type = [{'label': cur_opt, 'value': cur_opt} for cur_opt in area_type_list]

    return area_type,None,disabled_type,placeholder_type,placeholder_area,multi_at_drop



@app.callback([Output('columns_dropdown', 'options'),
               Output('norm_dropdown', 'options'),
               Output('columns_dropdown', 'value'),
               Output('norm_dropdown', 'value'),
               Output('prev-tab', 'data'),
               ],
               [Input('area_type_dropdown', 'value')],
              [State('country_dropdown', 'value'),
               State('tabs', 'value'),
               State('tabs_mob', 'value'),
               State('prev-tab', 'data'),
               State('columns_dropdown', 'options'),
               State('columns_dropdown', 'value')
               ]
              )
def update_col_options(area_type,country_in,tabs,tabs_mob,prev_tab,col_opt,col_val):

    col_drp = []
    norm_drp = []
    new_col_val = None
    new_norm_val = None

    data = {'tab1':tabs,'tab2':tabs_mob}

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

    if tabs == 'mobility':
        if tabs_mob == 'google' and 'Mobility_Google' in all_data_dict:
            if prev_tab != data:
                cols = all_data_dict['Mobility_Google']['col_names']
                col_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in cols]
            else:
                col_drp = col_opt
                new_col_val = col_val

        if tabs_mob == 'apple' and 'Mobility_Apple' in all_data_dict \
                and country_in in all_data_dict['Mobility_Apple']['options'] \
                and area_type:
            cur_area_set = set()
            for cur_at in area_type:
                cur_area_list = all_data_dict['Mobility_Apple']['options'][country_in][cur_at]
                for cur_at in cur_area_list:
                    cur_area_set.add(cur_at)
            if cur_area_set:
                disabled_area = False
                col_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in cur_area_set]
                if col_val and cur_area_set.issuperset(col_val):
                    new_col_val = col_val

    return col_drp,norm_drp,new_col_val,new_norm_val,data



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

    if n_clicks == 0 or not columns_dropdown or not (area_type_st or area_st or country_in):
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
                               'Field 2': cur_area,
                               'Field 1': area_type_st,
                               'Variable':cur_col,
                               'Denominator':norm_dropdown}
                    new_rows.append(new_row)
        else:
            for cur_area in country_in:
                for cur_col in columns_dropdown:
                    new_row = {'Tab': tabs_str,
                               'Data': cur_area,
                               'Field 2': cur_area,
                               'Field 1': 'Country',
                               'Variable':cur_col,
                               'Denominator':norm_dropdown}
                    new_rows.append(new_row)

    elif tabs == 'response':
        for cur_area in country_in:
            for cur_col in columns_dropdown:
                new_row = {'Tab': tabs_str,
                           'Data': cur_area,
                           'Field 2': cur_area,
                           'Field 1': 'Country',
                           'Variable':cur_col,
                           'Denominator':norm_dropdown}
                new_rows.append(new_row)

    elif tabs == 'mobility':
        if tabs_mob == 'google':
            if area_st:
                for cur_area in area_st:
                    for cur_col in columns_dropdown:
                        new_row = {'Tab': tabs_str,
                                   'Data': country_in[0],
                                   'Field 2': cur_area,
                                   'Field 1': area_type_st[0],
                                   'Variable': cur_col,
                                   'Denominator': norm_dropdown}
                        new_rows.append(new_row)
            elif area_type_st:
                for cur_area in area_type_st:
                    for cur_col in columns_dropdown:
                        new_row = {'Tab': tabs_str,
                                   'Data': country_in[0],
                                   'Field 2': '',
                                   'Field 1': cur_area,
                                   'Variable': cur_col,
                                   'Denominator': norm_dropdown}
                        new_rows.append(new_row)

            elif country_in:
                for cur_area in country_in:
                    for cur_col in columns_dropdown:
                        new_row = {'Tab': tabs_str,
                                   'Data': cur_area,
                                   'Field 2': '',
                                   'Field 1': '',
                                   'Variable': cur_col,
                                   'Denominator': norm_dropdown}
                        new_rows.append(new_row)

        if tabs_mob == 'apple':
            if area_type_st:
                for cur_area in area_type_st:
                    for cur_col in columns_dropdown:
                        if cur_col in all_data_dict['Mobility_Apple']['options'][country_in][cur_area]:
                            new_row = {'Tab': tabs_str,
                                       'Data': country_in,
                                       'Field 2': '',
                                       'Field 1': cur_area,
                                       'Variable': cur_col,
                                       'Denominator': norm_dropdown}
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
            #cur_row1['Visible (on/off)'] = 'on'
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
               Output('norm_div_id', 'style'),
               Output('area_type_drp_div', 'style'),
               Output('area_drp_div', 'style'),
               ],
              [Input('tabs', 'value'),
               Input('tabs_mob', 'value')])
def update_content(tab,tabs_mob):
    #global counter
    #app.server.logger.info(counter)

    multi = False
    countries_drp=[]

    style_country = default_style_country.copy()
    style_area = default_style_area.copy()
    column_style = default_column_style.copy()
    norm_style = default_norm_style.copy()
    at_style = default_at_style.copy()
    area_style = default_area_style.copy()

    placeholder='Select countries (multiple allowed)'

    if tab == 'mobility':
        column_style['width'] = '100%'
        norm_style = {'display': 'none'}
        at_style['width'] = '50%'
        area_style['width'] = '49%'

        if tabs_mob == 'google' and 'Mobility_Google' in all_data_dict:
            multi = True
            countries = all_data_dict['Mobility_Google']['options'].keys()
            countries_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in countries]

        if tabs_mob == 'apple' and 'Mobility_Apple' in all_data_dict:
            multi = False
            geo_types = all_data_dict['Mobility_Apple']['options'].keys()
            countries_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in geo_types]
            placeholder = 'Geo type'

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
    return countries_drp,multi,style_country,style_area,placeholder,None,column_style,norm_style,at_style,area_style


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













