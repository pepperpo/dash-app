import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from style import colors


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
        style={'backgroundColor': colors['background'],'width': '10%', 'display': 'inline-block', 'vertical-align': 'middle'},
        children=[
            dcc.Dropdown(
                id='country_dropdown',
                placeholder="Country",
                options=[{'label': country, 'value': country} for country in countries],
                clearable=False,
                value=countries[0]
            ),

        ])


    radio_div = html.Div(
        style={'backgroundColor': colors['background'],
               'display': 'inline-block','float':'right','margin-top':'10px','margin-right':'10px'},
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
               'display': 'inline-block', 'float': 'right', 'margin-top': '10px','margin-right':'50px'},
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
                placeholder="Region (leave empty for national data; it can be selected independently of province)",
                multi=True,
            ),
        ])

    province_drp_div = html.Div(
        style={'backgroundColor': colors['background'], 'width': '100%','margin-top': '5px'},
        children=[
            dcc.Dropdown(
                id='province_dropdown',
                placeholder="Province (leave empty for national data; it can be selected independently of region)",
                multi=True,
            ),
        ])

    columns_div = html.Div(
        style={'backgroundColor': colors['background'], 'width': '100%','margin-top': '5px'},
        children=[
            dcc.Dropdown(
                id='columns_dropdown',
                placeholder="Select options to plot... (leave empty to select all)",
                multi=True,
            ),
        ])

    norm_div = html.Div(
        style={'backgroundColor': colors['background'],
               'vertical-align': 'middle', 'display': 'inline-block', 'width': '20%'},
        children=[
            dcc.Dropdown(
                id='norm_dropdown',
                placeholder="Denominator",
            ),
        ])


    loading_div = html.Div(
        style={'backgroundColor': colors['background'], 'width': '3%', 'display': 'inline-block',
               'vertical-align': 'middle','height':'50px'},
        children=[
            dbc.Spinner(
                id="loading-submit",
                children=[html.Div([html.Div(id="loading-submit-cnt1", style={'display': 'none'})]),
                          html.Div([html.Div(id="loading-submit-cnt2", style={'display': 'none'})]),
                          html.Div([html.Div(id="loading-submit-cnt3", style={'display': 'none'})])],
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

    denom_div = html.Div(
        style={'backgroundColor': colors['background'],
               'vertical-align': 'middle', 'display': 'inline-block', 'width': '100%','margin-top':'5px'},
        children=[
            norm_div,
            html.Div(children="(use Denominator to plot a percentage with respect to one of the variables)",
                     style={'vertical-align': 'middle', 'display': 'inline-block','margin-left':'5px'}),
            radio_div,
            radio_log_div
        ])

    '''
    radio_cont_div = html.Div(
        style={'backgroundColor': colors['background'],
               'vertical-align': 'middle', 'display': 'inline-block', 'width': '100%', 'margin-top': '5px'},
        children=[
            radio_div,
            html.Div(children="(select Variation to show the day-to-day variation, else Cumulative)",
                     style={'vertical-align': 'middle', 'display': 'inline-block', 'margin-left': '5px'}),
        ])
    '''


    """Returns a div"""
    rv = html.Div(
        style={'backgroundColor': colors['background']},
        children=[
            controls_div,
            region_drp_div,
            province_drp_div,
            columns_div,
            denom_div,
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
                #figure=plot,
            )
        ]
    )
    return rv


def make_footer():
    """Returns a div with a plot"""
    rv = html.Div(
        style={'backgroundColor': colors['background']},
        children=[
            html.P('Data source - Notes:'),
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

