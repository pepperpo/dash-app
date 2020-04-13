import dash_core_components as dcc
import dash_html_components as html
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
            html.Span(html.A("GPviz",
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
    rv_runs = html.Div(
        style={'backgroundColor': colors['background'],'width': '10%', 'display': 'inline-block', 'vertical-align': 'middle'},
        children=[
            html.Label("Runs"),
            dcc.Input(id="runA", type="number", placeholder="Run A"),
            dcc.Input(id="runB", type="number", placeholder="Run B"),
            ])

    rv_gp = html.Div(
        style={'backgroundColor': colors['background'], 'width': '20%', 'display': 'inline-block','margin-left':'5%',
               'vertical-align': 'middle'},
        children=[
            html.Label("Gaussian Process Params"),
            dcc.Input(id="ls_input", type="number", placeholder="Lengthscales"),
            dcc.Input(id="signa_input", type="number", placeholder="Sigma"),
        ])

    """Returns a div"""
    rv = html.Div(
        style={'backgroundColor': colors['background']},
        children=[
            rv_runs,
            rv_gp
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
                id='fig',
                figure=plot
            )
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

