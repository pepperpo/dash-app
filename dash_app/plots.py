import plotly.graph_objs as go
import numpy as np
from style import colors


# define data declaratively as a dict
bar_plot =  {
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                    {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
                ],
                'layout': {
                    'title': "Bar Plot",
                    'images': [
                        {
                            'source':'/static/api_logo_pwrdBy_strava_horiz_light.png',
                            'xref':"paper",
                            'yref':"paper",
                            'x':1,
                            'y':1.05,
                            'sizex':0.2,
                            'sizey':0.2,
                            'xanchor':"right",
                            'yanchor':"bottom"
                    }],
                    'plot_bgcolor': colors['background'],
                    'paper_bgcolor': colors['background'],
                    'font': {
                        'color': colors['text']
                    }
                }
            }


# use a go object
scatter_plot =  {
                'data': [
                    go.Scatter({
                        'name': 'Sin(x)',
                        'x': np.arange(10),
                        'y': np.sin(np.arange(10))
                    })
                ],
                'layout': {
                    'title': 'Scatter Plot',
                    'images': [
                        {
                            'source':'/static/api_logo_pwrdBy_strava_horiz_light.png',
                            'xref':"paper",
                            'yref':"paper",
                            'x':1,
                            'y':1.05,
                            'sizex':0.2,
                            'sizey':0.2,
                            'xanchor':"right",
                            'yanchor':"bottom"
                    }],
                    'plot_bgcolor': colors['background'],
                    'paper_bgcolor': colors['background'],
                    'font': {
                        'color': colors['text']
                    }
                }
            }


# define data declaratively as a dict
cnt_plot =  {
                'data': [
                    {'z': [[10, 10.625, 12.5, 15.625, 20],
                           [5.625, 6.25, 8.125, 11.25, 15.625],
                           [2.5, 3.125, 5., 8.125, 12.5],
                           [0.625, 1.25, 3.125, 6.25, 10.625],
                           [0, 0.625, 2.5, 5.625, 10]], 'type': 'contour'},
                ],
                'layout': {
                    'title': "Contour",
                    'plot_bgcolor': colors['background'],
                    'paper_bgcolor': colors['background'],
                    'font': {
                        'color': colors['text']
                    }
                }
            }