import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from style import colors
import plotly.graph_objects as go
import dash_table


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
    from constants import table_cols
    country_div = html.Div(
        style={'backgroundColor': colors['background'],'width': '30%', 'float':'left'},
        children=[
            dcc.Dropdown(
                id='country_dropdown',
                placeholder="Select dataset",
                #options=[{'label': country, 'value': country} for country in countries],
                clearable=False,
            ),

        ])

    area_type_drp_div = html.Div(
        style={'backgroundColor': colors['background'], 'width': '13%', 'float':'left'},
        children=[
            dcc.Dropdown(
                id='area_type_dropdown',
                placeholder="Select area type",
                clearable=False,
            ),
        ])

    area_drp_div = html.Div(
        style={'backgroundColor': colors['background'], 'width': '53%', 'float':'left','margin-left':'1%'},
        children=[
            dcc.Dropdown(
                id='area_dropdown',
                placeholder="Select area",
                multi=True,
            ),
        ])

    loading_div = html.Div(
        style={'backgroundColor': colors['background'], 'width': '3%', 'float':'left','height':'40px','margin-top':'-8px'},
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
        style={'backgroundColor': colors['background'], 'width': '100%', 'float':'left','margin-top':'10px'},
        children=[
            country_div,
            loading_div,
            area_type_drp_div,
            area_drp_div,
        ])


    radio_div = html.Div(
        style={'backgroundColor': colors['background'],
               'display': 'inline-block','float':'left','margin-left':'20px'},
        children=[ dcc.RadioItems(
                id='aggragation_radio',
                options=[
                    {'label': ' Daily increment', 'value': 'var'},
                    {'label': ' Cumulative', 'value': 'cum'},
                ],
                value='var',
                labelStyle={
                'display': 'block',
                'margin-top': '-10px'}
            ),
        ])

    radio_log_div = html.Div(
        style={'backgroundColor': colors['background'],
               'display': 'inline-block', 'float': 'left'},
        children=[dcc.RadioItems(
            id='log_radio',
            options=[
                {'label': ' Linear', 'value': 'lin'},
                {'label': ' Logarithm', 'value': 'log'},
            ],
            value='lin',
            labelStyle={
                'display': 'block',
                'margin-top': '-10px'}
        ),
        ])


    add_btn_div = html.Div(
            style={'backgroundColor': colors['background'],'width': '100%','float':'left','margin-top':'5px'},
            children=[
                html.Button('Add to table', className='mybutton', id='btn_add',
                            style={'float':'left','border': 'none', 'color': 'white', 'borderRadius': '5px','height':'100%','width': '10%'}),
                html.Div(children=['(to plot add variables to the table)'],
                         style={'float': 'left', 'margin-left': '10px'})
            ])

    # sel_subreg_div = html.Div(
    #     style={'backgroundColor': colors['background'], 'width': '89%','float':'left','margin-left':'1%','display':'none'},
    #     children=[
    #         dcc.Dropdown(
    #             id='sel_reg_dropdown',
    #             placeholder="Only items in this box are plotted",
    #             multi=True,
    #             style={'min-height': '75px'}
    #         ),
    #     ])

    table_div = html.Div(
        className='table_div',
        style={'backgroundColor': colors['background'], 'width': '100%', 'float': 'left','margin-top':'5px'},
        children=[
            dash_table.DataTable(
                id='sel_reg_dropdown',
                columns=[{
                    'name': '{}'.format(i),
                    'id': '{}'.format(i),
                    'deletable': False,
                    'renamable': False
                } for i in table_cols],
                #data=[
                #    {j: [''] for j in table_cols}
                #],
                editable=False,
                row_deletable=True
            ),
        ])

    columns_div = html.Div(
        style={'backgroundColor': colors['background'], 'width': '69%','float':'left'},
        children=[
            dcc.Dropdown(
                id='columns_dropdown',
                placeholder="Select variables to plot",
                multi=True,
            ),
        ])

    norm_div = html.Div(
        style={'backgroundColor': colors['background'],'float':'left','width':'30%','margin-left':'1%'},
        children=[
            dcc.Dropdown(
                id='norm_dropdown',
                placeholder="Denominator (optional)",
            ),
        ])




    radio_all_div = html.Div(
        style={'backgroundColor': colors['background'],'float':'left','margin-top':'10px','width':'20%','margin-bottom':'-10px'},
        children=[
            radio_log_div,
            radio_div,
        ])


    var_sel_div = html.Div(
        style={'backgroundColor': colors['background'],'float':'left','width':'100%','margin-top':'5px'},
        children=[
            columns_div,
            norm_div,
        ])


    refresh_btn_div = html.Div(
        style={'backgroundColor': colors['background'],
               'vertical-align': 'middle', 'display': 'inline-block', 'width': '100%', 'margin-top': '5px','margin-bottom':'10px'},
        children=[
            html.Button('Refresh graph', className='mybutton', id='btn_refresh', style={'border': 'none', 'color': 'white','borderRadius': '5px','float':'left','width':'10%'}),
            html.Div(children=['(messages and errors below the graph)'],style={'float':'left','margin-left':'10px'})
        ])

    tabs_styles = {
        'height': '44px'
    }
    tab_style = {
        'padding': '6px',
    }
    tab_selected_style = {
        'padding': '6px'
    }

    tabs = html.Div(id='tabs_div_id',children=[
        dcc.Tabs(id='tabs', value='health',
            children=[
            dcc.Tab(label='Health stats', value='health',style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='Government response', value='response',style=tab_style, selected_style=tab_selected_style,disabled=True),
            dcc.Tab(label='Mobility', value='mobility',style=tab_style, selected_style=tab_selected_style,disabled=True),
        ],style=tabs_styles)
    ])

    tabs_mobility = html.Div(id='tabs_mob_div_id', style={'display':'none'},children=[
        dcc.Tabs(id='tabs_mob', value='google',
                 children=[
                     dcc.Tab(label='Google', value='google',style=tab_style, selected_style=tab_selected_style),
                     dcc.Tab(label='Apple', value='apple',style=tab_style, selected_style=tab_selected_style),
                 ],style=tabs_styles)
    ])

    """Returns a div"""
    rv = html.Div(
        style={'backgroundColor': colors['background']},
        children=[
            tabs,
            tabs_mobility,
            controls_div,
            var_sel_div,
            add_btn_div,
            table_div,
            radio_all_div,
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
                style={'background':'#DCDCDC','border-top-left-radius':'5px','border-top-right-radius':'5px','padding-left':'5px','font-size': 'large'},
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
            html.Div(className='source_title',children=['Data source - Notes:']),
            html.Div(className='source_subtitle',children=['Health stats:']),
            html.Div(['Italy: ',
                    html.A('Dipartimento Protezione Civile Italiana', href='https://github.com/pcm-dpc/COVID-19', target="_blank"),
                    ' - Notes: data of Provinces only contain total_cases']),

            html.Div(['Other countries: ',
                    html.A('Oxford University - Coronavirus Government Response Tracker', href='https://www.bsg.ox.ac.uk/research/research-projects/coronavirus-government-response-tracker',
                           target="_blank")]),
            html.Div(className='source_subtitle', children=['Government responses:']),
            html.Div(['All countries: ',
                    html.A('Oxford University - Coronavirus Government Response Tracker',
                           href='https://www.bsg.ox.ac.uk/research/research-projects/coronavirus-government-response-tracker',
                           target="_blank")]),

            html.Div(className='source_subtitle', children=['Mobility:']),
            html.Div(['All countries: ',
                      html.A('Google - Community Mobility Reports',
                             href='https://www.google.com/covid19/mobility/',
                             target="_blank")]),
            html.Div(['All countries: ',
                      html.A('Apple - Mobility Trends Reports',
                             href='https://www.apple.com/covid19/mobility',
                             target="_blank")]),


            html.P('')
        ]
    )
    return rv

