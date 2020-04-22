from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from config import config_app
from layout import app_layout, make_header, make_main,make_footer
#from plots import bar_plot, scatter_plot, cnt_plot
from functions import generate_plot,load_data,data2dropdown
import json

import sys
# import logging
# logger = logging.getLogger(__name__)
# logger.addHandler(logging.StreamHandler(stream=sys.stderr))
# logger.setLevel(logging.DEBUG)

debug_flag = True

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

all_data_dict = {}

@app.callback(Output('page-main', 'children'), [Input('url', 'pathname')])
def routing(pathname):
    """Very basic router

    This callback function will read the current url
    and based on pathname value will populate the children of the page-main

    Returns:
        html.Div
    """
    app.server.logger.info(pathname)
    app.title = "COVID19 - dashboard"

    rv = make_main()

    # if pathname == '/bar':
    #     rv = make_main(bar_plot)
    # elif pathname == '/scatter':
    #     rv = make_main(scatter_plot)
    # else:
    #     rv = make_main({'layout': {'title': 'empty plot: click on a Bar or Scatter link'}})

    return rv

# @server.route("/")
# def MyDashApp():
#     app.title = "Title"
#     print('HERE')
#     return app.index()


@app.callback([Output('bar_graph', 'figure'),
               Output('loading-submit-cnt1','children')],
              [Input('aggragation_radio', 'value'),
               Input('columns_dropdown', 'value'),
               Input('norm_dropdown', 'value'),
               Input('log_radio', 'value'),
               Input('region_dropdown', 'value'),
               Input('province_dropdown', 'value'),
               Input('loading-submit-cnt2', 'children')],
              [State('country_dropdown','value')])
def update_plot(aggr_in, col_in, norm_in, log_in, region_in, prov_in, update_done, country_in):
    print(aggr_in, col_in, norm_in, log_in, region_in, prov_in, update_done)
    if not update_done:
        raise PreventUpdate

    rv = generate_plot(all_data_dict[country_in],aggr_in,col_in,norm_in,log_in,region_in,prov_in)
    return rv,'done'

@app.callback([Output('region_dropdown', 'options'),
               Output('province_dropdown','options'),
               Output('loading-submit-cnt2','children')],
               [Input('country_dropdown', 'value')])
def load_data_callback(country_in):

    if not country_in:
        raise PreventUpdate

    load_data(country_in,all_data_dict)
    region_drp, province_drp = data2dropdown(country_in, all_data_dict)
    return region_drp, province_drp, 'done'



@app.callback([Output('columns_dropdown', 'options'),
               Output('norm_dropdown', 'options'),
               Output('loading-submit-cnt3','children'),
               Output('columns_dropdown', 'value'),
               Output('norm_dropdown', 'value'),
               ],
               [Input('region_dropdown', 'value'),
                Input('province_dropdown', 'value')],
              [State('columns_dropdown', 'value'),
               State('norm_dropdown', 'value'),
               State('country_dropdown','value')]
              )
def update_col_options(region_in,province_in,col_st,norm_st,country_in):

    if not (region_in or province_in):
        raise PreventUpdate

    col_drp = []
    norm_drp = []
    new_col_val = None
    new_norm_val = None

    cur_dict = all_data_dict[country_in]

    if province_in and not region_in:
        options = cur_dict['options_province']
        col_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in options]
    else:
        options = cur_dict['options_nation']
        col_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in options]
        norm_drp = [{'label': cur_opt, 'value': cur_opt} for cur_opt in options]

    if province_in:
        norm_drp = []

    if col_st:
        new_col_val = [value for value in options if value in col_st]
    if norm_st:
        new_norm_val = [value for value in options if value in norm_st]

    return col_drp,norm_drp,'done',new_col_val,new_norm_val



if __name__ == '__main__':
    app.run_server(debug=debug_flag)
