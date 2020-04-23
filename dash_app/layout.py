import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from style import colors
import plotly.graph_objects as go


def app_layout(header=None, main=None, footer=None):
    """Returns app layout with the following elements:
        app-layout: main div, should not be a target of an ouput callback
        page-content: container div, target for an ouput callback
        url: Location, target of an input callback
    """
    rv = html.Div(
        id='app-layout',
        children=[
            dcc.Location(id='url', refresh=False),
            dcc.Store(id='dash-session', storage_type='memory'),
            html.Div(id='page-content',
                className = 'container-fluid',
                children=[
                    html.Div(header, id='page-header'),
                    html.Div(main, id='page-main'),
                    html.Div(footer, id='page-footer')
                ]
            )
        ]
    )
    return rv


def make_header():
    """Returns a div with a header"""
    rv = html.Nav(
        className='navbar navbar-expand-md navbar-light bg-light',
        children = [
            # Title on the left
            html.Span(html.A("COVID19 - dashboard",
                             href='/',
                             className='navbar-brand'),
                      className='navbar-brand mr-auto w-50'),
            # Links on the right
            html.Ul(
                children = [
                    # html.Li(html.A('Bar',
                    #            href='/bar',
                    #            className='nav-link lead'
                    #         ),
                    #         className = 'nav-item'),
                    # html.Li(html.A('Scatter',
                    #            href='/scatter',
                    #            className='nav-link lead'
                    #         ),
                    #         className = 'nav-item'),
                ],
                className = 'nav navbar-nav ml-auto w-100 justify-content-end'
            ),
        ])
    return rv


def make_control_panel():
    from constants import countries
    country_div = html.Div(
        style={'backgroundColor': colors['background'],'width': '25%', 'display': 'inline-block', 'vertical-align': 'middle'},
        children=[
            dcc.Dropdown(
                id='country_dropdown',
                placeholder="Country",
                options=[{'label': country, 'value': country} for country in countries],
                clearable=False,
            ),

        ])


    radio_div = html.Div(
        style={'backgroundColor': colors['background'],
               'display': 'inline-block','float':'left','margin-left':'10px'},
        children=[ dcc.RadioItems(
                id='aggragation_radio',
                options=[
                    {'label': ' Variation', 'value': 'var'},
                    {'label': ' Cumulative', 'value': 'tot'},
                ],
                value='var',
                labelStyle={
                'display': 'block',
                'margin-top': '-10px'}
            ),
        ])

    radio_log_div = html.Div(
        style={'backgroundColor': colors['background'],
               'display': 'inline-block', 'float': 'left','margin-left':'20px'},
        children=[dcc.RadioItems(
            id='log_radio',
            options=[
                {'label': ' Linear', 'value': 'linear'},
                {'label': ' Logarithm', 'value': 'log'},
            ],
            value='linear',
            labelStyle={
                'display': 'block',
                'margin-top': '-10px'}
        ),
        ])


    region_drp_div = html.Div(
        style={'backgroundColor': colors['background'], 'width': '100%'},
        children=[
            dcc.Dropdown(
                id='region_dropdown',
                placeholder="Country / Region / State / Prefecture",
                multi=True,
            ),
        ])

    province_drp_div = html.Div(
        style={'backgroundColor': colors['background'], 'width': '100%','margin-top': '5px'},
        children=[
            dcc.Dropdown(
                id='province_dropdown',
                placeholder="Province / County",
                multi=True,
            ),
        ])


    subregions_div = html.Div(
        style={'backgroundColor': colors['background'], 'width': '47%','float':'left'},
        children=[
            region_drp_div,
            province_drp_div
        ])

    add_btn_div = html.Div(
        className='button-subregions',
        style={'backgroundColor': colors['background'],'width': '4%','height':'100%'},
        children=[
            html.Button('>', className='mybutton', id='btn_add',
                        style={'border': 'none', 'color': 'white', 'borderRadius': '5px','height':'100%','width': '100%'})
        ])

    sel_subreg_div = html.Div(
        style={'backgroundColor': colors['background'], 'width': '47%','float':'left','margin-left':'6%'},
        children=[
            dcc.Dropdown(
                id='sel_reg_dropdown',
                placeholder="Only items in this box are plotted",
                multi=True,
                style={'min-height': '75px'}
            ),
        ])

    regionsel_div = html.Div(
        className='container-subregions',
        style={'backgroundColor': colors['background'], 'width': '100%','float':'left'},
        children=[
            subregions_div,
            add_btn_div,
            sel_subreg_div
        ])


    columns_div = html.Div(
        style={'backgroundColor': colors['background'], 'width': '100%','float':'left'},
        children=[
            dcc.Dropdown(
                id='columns_dropdown',
                placeholder="Select variables to plot",
                value=['deaths','total_positive'],
                multi=True,
            ),
        ])

    norm_div = html.Div(
        style={'backgroundColor': colors['background'],
               'vertical-align': 'middle', 'display': 'inline-block', 'width': '100%','margin-top':'5px'},
        children=[
            dcc.Dropdown(
                id='norm_dropdown',
                placeholder="Denominator (use to plot percent)",
            ),
        ])


    loading_div = html.Div(
        style={'backgroundColor': colors['background'], 'width': '3%', 'display': 'inline-block',
               'vertical-align': 'middle','height':'50px'},
        children=[
            dbc.Spinner(
                id="loading-submit",
                children=[html.Div([html.Div(id="loading-submit-cnt1", style={'display': 'none'})]),
                          html.Div([html.Div(id="loading-submit-cnt2", style={'display': 'none'})])],
                size="sm",
                color="primary",
            ),
        ])


    controls_div = html.Div(
        style={'backgroundColor': colors['background'], 'width': '100%', 'display': 'inline-block',
               'vertical-align': 'middle'},
        children=[
            country_div,
            loading_div,
        ])

    radio_all_div = html.Div(
        style={'backgroundColor': colors['background'],
               'vertical-align': 'middle', 'display': 'inline-block', 'width': '100%','margin-top':'15px'},
        children=[
            radio_div,
            radio_log_div
        ])

    health_div = html.Div(
        style={'backgroundColor': colors['background'],
               'vertical-align': 'middle', 'float':'left', 'width': '38%','borderRadius': '5px','border':'1px solid gray','padding':'5px','padding-top':'0px'},
        children=[
            html.Div(children=['Health stats'],style={'float':'left','margin-top':'-14px','background':'white','margin-bottom':'5px','padding-left':'5px','padding-right':'5px','padding-top':'0px','padding-bottom':'0px'}),
            columns_div,
            norm_div,
            radio_all_div
        ])


    gov_div = html.Div(
        style={'backgroundColor': colors['background'], 'width': '30%', 'float': 'left', 'margin-left': '1%'},
        children=[
            dcc.Dropdown(
                id='gov_dropdown',
                placeholder="Government response",
                multi=True,
                style={'min-height': '160px'}
            ),
        ])

    mob_div = html.Div(
        style={'backgroundColor': colors['background'], 'width': '30%', 'float': 'left', 'margin-left': '1%'},
        children=[
            dcc.Dropdown(
                id='mob_dropdown',
                placeholder="Mobility (Google/Apple)",
                multi=True,
                style={'min-height': '160px'}
            ),
        ])



    var_sel_div = html.Div(
        style={'backgroundColor': colors['background'],
               'vertical-align': 'middle', 'display': 'inline-block', 'width': '100%', 'margin-top': '15px'},
        children=[
            health_div,
            gov_div,
            mob_div
        ])


    refresh_btn_div = html.Div(
        style={'backgroundColor': colors['background'],
               'vertical-align': 'middle', 'display': 'inline-block', 'width': '100%', 'margin-top': '5px','margin-bottom':'10px'},
        children=[
            html.Button('Refresh graph', className='mybutton', id='btn_refresh', style={'border': 'none', 'color': 'white','borderRadius': '5px','float':'left'}),
            html.Div(children=['(messages and errors below the graph)'],style={'float':'left','margin-left':'10px'})
        ])


    """Returns a div"""
    rv = html.Div(
        style={'backgroundColor': colors['background']},
        children=[
            controls_div,
            regionsel_div,
            var_sel_div,
            refresh_btn_div,
            ]
    )
    return rv


def make_main(plot=html.Div()):
    """Returns a div with a plot"""
    rv = html.Div(
        style={'backgroundColor': colors['background']},
        children=[
            make_control_panel(),
            dcc.Graph(
                id='bar_graph',
                figure=go.Figure({'layout':{'margin':{'t': 0}}})),

            html.Div(
                style={'background':'#DCDCDC','border-top-left-radius':'5px','border-top-right-radius':'5px','padding-left':'5px'},
                children=['Messages and errors:']
            ),
            html.Div(
                id='messages',
                style={'background': '#F8F8F8','min-height':'50px','border-bottom-left-radius':'5px','border-bottom-right-radius':'5px','padding-left':'5px'},
                children=['']
            )
        ]
    )
    return rv


def make_footer():
    """Returns a div with a plot"""
    rv = html.Div(
        style={'backgroundColor': colors['background'],'margin-top':'20px'},
        children=[
            'Data source - Notes:',
            html.P(['Italy: ',
                    html.A('https://github.com/pcm-dpc/COVID-19', href='https://github.com/pcm-dpc/COVID-19', target="_blank"),
                    ' - Notes: data of Provinces only contain total_cases'])
        ]
    )
    return rv

# def make_main(plot=html.Div()):
#     """Returns a div with a plot"""
#     rv = html.Div(
#         style={'backgroundColor': colors['background']},
#         children=[
#             dcc.Graph(
#                 id='fig',
#                 figure=plot
#             )
#         ]
#     )
#     return rv

