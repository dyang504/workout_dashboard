import dash
import dash_table
from dash_table.Format import Format, Scheme, Symbol
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from sqlalchemy import create_engine
import pandas as pd

# Model Code
conn = create_engine("sqlite:///./train_items.db")


def fetch_data(q, conn):
    return pd.read_sql(sql=q, con=conn)


q = '''SELECT "日期",
 sum("次")AS "合计次数"
FROM train_record
GROUP BY "日期"
ORDER BY "日期" '''

sport_name_query = '''SELECT "运动名称",
 sum("次")AS "合计次数"
FROM train_record
WHERE "次" > 0
GROUP BY "运动名称"
ORDER BY sum("次")DESC '''

df = fetch_data(q, conn)
total_by_sports_name = fetch_data(sport_name_query, conn)

table_query = '''SELECT "运动名称",
 count("运动名称") / count(DISTINCT "日期")AS "Average_Sets",
sum("次")AS "合计次数",
AVG("重量")AS "平均重量(单位：KG)"
FROM train_record
WHERE "次" > 0
GROUP BY "运动名称"
ORDER BY sum("次")DESC '''

table_df = fetch_data(table_query, conn)

pie_query = '''SELECT "运动名称",
 count("运动名称")AS "Total_Sets"
FROM train_record
WHERE "次" > 0
GROUP BY "运动名称"
ORDER BY count("运动名称")DESC
'''

pie_df = fetch_data(pie_query, conn)

## View
color_scheme = {
    'white': "#F1EEF6",
    "black": '#1E152A',
    'green': '#8CFFBA',
    'dark_grey': '#373E49',
    'grey': '#9099AB',
    'red': '#FF5A33'
}
external_stylesheets = ['https://unpkg.com/purecss@1.0.0/build/pure-min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def generate_fact(dataframe, column_name, unit):
    return html.Div([
        html.Span(column_name),
        html.Span(children=f': {sum(df[column_name])}'),
        html.Span(f'{ unit}')
    ])


def generate_graph(dataframe):
    return dcc.Graph(id='example-graph',
                     figure={
                         'data': [{
                             'x': dataframe["日期"].tolist(),
                             'y': dataframe["合计次数"].tolist(),
                             'type': 'line',
                             'name': '次数累计',
                             'marker': {
                                 'color': color_scheme['green']
                             }
                         }],
                         'layout': {
                             'plot_bgcolor': color_scheme['black'],
                             'paper_bgcolor': color_scheme['black'],
                             'autosize': False,
                             'title': 'Total Repeats Trending',
                             'font': {
                                 'color': color_scheme['white']
                             },
                             'height': 300,
                             'width': '80%',
                             'xaxis': {
                                 'title': 'Workout Date',
                                 'showgrid': False,
                                 'showline': True,
                                 'linewidth': 3,
                                 'linecolor': color_scheme['grey'],
                                 'tickformat': '%d %b %Y'
                             },
                             'yaxis': {
                                 'title': 'Repeat X Sets',
                                 'showgrid': False,
                                 'showline': True,
                                 'linewidth': 3,
                                 'linecolor': color_scheme['grey']
                             },
                             'hovermode': 'closest'
                         }
                     })


def generate_bar_graph(dataframe):
    return dcc.Graph(id='sports_potion',
                     figure={
                         'data': [{
                             'x': dataframe['运动名称'].tolist(),
                             'y': dataframe['合计次数'].tolist(),
                             'type': 'bar',
                             'width': 0.55,
                             'marker': {
                                 'color': color_scheme['green']
                             }
                         }],
                         'layout': {
                            #  'autosize': False,
                             'title': 'Total Repeats of Each Sports',
                             'font': {
                                 'color': color_scheme['white']
                             },
                             'plot_bgcolor': color_scheme['black'],
                             'paper_bgcolor': color_scheme['black'],
                             'xaxis': {
                                 'title': '运动名称',
                                 'tickfont': {
                                     'size': 8
                                 },
                                 'showgrid': False,
                                 'linewidth': 3,
                                 'linecolor': color_scheme['grey']
                             },
                             'yaxis': {
                                 'title': '重复次数',
                                 'linewidth': 3,
                                 'linecolor': color_scheme['grey'],
                                 'tickfont': {
                                     'size': 10
                                 },
                                 'showgrid': False,
                                 'showline': True
                             },
                             'height': 300,
                             'width': 600,
                             'autosize': True,
                             'bargap': 0.1,
                             'hovermode': 'closest'
                         }
                     })


def generate_table(dataframe):
    return dash_table.DataTable(
        id='table',
        columns=[{
            'name': '运动名称',
            'id': '运动名称',
            'type': 'text'
        }, {
            'name': 'Average_Sets',
            'id': 'Average_Sets',
            'type': 'numeric',
            'format': Format(precision=0, scheme=Scheme.fixed)
        }, {
            'name': '合计次数',
            'id': '合计次数',
            'type': 'numeric',
            'format': Format(precision=0, scheme=Scheme.fixed)
        }, {
            'name': '平均重量(单位：KG)',
            'id': '平均重量(单位：KG)',
            'type': 'numeric',
            'format': Format(precision=0, scheme=Scheme.fixed)
        }],
        data=dataframe.to_dict('records'),
        n_fixed_rows=1,  # style_as_list_view = True, 
        sorting=True,
        pagination_mode='fe',
        pagination_settings={
            "current_page": 0,
            "page_size": 7
        },
        style_table={
            'maxHeight': 300,
            # 'overflowY': 'scroll'
        },
        style_cell={

            # 'textAlign': 'right',
            'backgroundColor': color_scheme['black'],
            'color': color_scheme['white']
        })


base_chart = {
    "values": [40, 10, 10, 10, 10, 10, 10],
    "labels": ["-", "0", "1", "2", "3", "4", "5+"],
    "domain": {
        "x": [0, .48]
    },
    "marker": {
        "colors": [
            color_scheme['black'],
            color_scheme['black'],
            color_scheme['black'],
            color_scheme['black'],
            color_scheme['black'],
            color_scheme['black'],
            color_scheme['black'],
            # 'rgb(255, 255, 255)',
            # 'rgb(255, 255, 255)',
            # 'rgb(255, 255, 255)',
            # 'rgb(255, 255, 255)',
            # 'rgb(255, 255, 255)',
            # 'rgb(255, 255, 255)',
            # 'rgb(255, 255, 255)'
        ],
        "line": {
            "width": 1
        }
    },
    "name": "Gauge",
    "hole": .4,
    "type": "pie",
    "direction": "clockwise",
    "rotation": 108,
    "showlegend": False,
    "hoverinfo": "none",
    "textinfo": "label",
    "textposition": "outside"
}

meter_chart = {
    "values": [50, 10, 10, 10, 10, 10],
    "labels": ['', "Very Low", "Low", "Med", "High", "Very High"],
    "marker": {
        'colors': [
            color_scheme['black'],
            '#DEF4E7',
            '#A9D3BA',
            '#8CFFBA',
            '#57ED93',
            '#1EE86E'  # 'rgb(255, 255, 255)',
            # 'rgb(232,226,202)',
            # 'rgb(226,210,172)',
            # 'rgb(223,189,139)',
            # 'rgb(223,162,103)',
            # 'rgb(226,126,64)'
        ]
    },
    "domain": {
        "x": [0, 0.48]
    },
    "name": "Gauge",
    "hole": .3,
    "type": "pie",
    "direction": "clockwise",
    "rotation": 90,
    "showlegend": False,
    "textinfo": "label",
    "textposition": "inside",
    "hoverinfo": "none"
}

layout = {
    'plot_bgcolor':
    color_scheme['black'],
    'paper_bgcolor':
    color_scheme['black'],
    'height':
    350,
    'width':
    500,
    'font': {
        'color': color_scheme['white']
    },
    'xaxis': {
        'showticklabels': False,
        'showgrid': False,
        'zeroline': False
    },
    'yaxis': {
        'showticklabels': False,
        'showgrid': False,
        'zeroline': False
    },
    'shapes': [{
        'type': 'path',
        'path': 'M 0.235 0.5 L 0.24 0.65 L 0.245 0.5 Z',
        'fillcolor': color_scheme['red'],
        'line': {
            'width': 0.5
        },
        'xref': 'paper',
        'yref': 'paper'
    }],
    'annotations': [{
        'xref': 'paper',
        'yref': 'paper',
        'x': 0.23,
        'y': 0.45,
        'text': '3',
        'showarrow': False
    }]
}


def generate_pie():  # we don 't want the boundary now
    base_chart['marker']['line']['width'] = 0
    return dcc.Graph(id='pie',
                     figure={
                         "data": [base_chart, meter_chart],
                         "layout": layout
                     })


app.layout = html.Div(
    children=[
        html.H2(children='Overall Workout Trend',
                style={
                    'color': color_scheme['green'],
                    'paddingTop': 20
                }),
        # generate_fact(df, "次", '次'),
        # generate_fact(df, "重量", 'KG'),
        html.Div([
            html.Div(generate_table(table_df), className='pure-u-1-2'),
            html.Div(generate_pie(), className='pure-u-1-2')
        ],
                 className='pure-g'),
        html.Div(generate_graph(df), className='pure-u-1-2'),
        html.Div(generate_bar_graph(total_by_sports_name),
                 className='pure-u-1-2')
    ],
    style={
        'backgroundColor': color_scheme['black'],
        'margin': 0,
        'hegith': '100%'
    })

if __name__ == '__main__':
    app.run_server(debug=True)
# we don 't want the boundary now
# base_chart['marker']['line']['width'] = 0
