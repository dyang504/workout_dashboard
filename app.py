import dash
import dash_table
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import pandas as pd
from dash_table.Format import Format, Scheme
from sqlalchemy import create_engine

# TODO
# Unify the languages
# Clean up the code

##############
# Model Code #
##############

conn = create_engine("sqlite:///./train_items.db")


def fetch_data(q: str, conn) -> pd.DataFrame:
    '''
    parm: q - the SQL query
    parm: conn - the create engine variable
    '''
    return pd.read_sql(sql=q, con=conn)


def query_date(conn,hoverData):
    q = ''
    if hoverData:
        sport = hoverData['points'][0]['x']
        q = f'''SELECT "日期",
                    SUM("次")AS "合计次数"
                FROM train_record
                WHERE "运动名称" = "{sport}"
                GROUP BY "日期"
                ORDER BY "日期" '''
    else:
        q =  '''SELECT "日期",
                    SUM("次")AS "合计次数"
                FROM train_record
                GROUP BY "日期"
                ORDER BY "日期" '''
    return fetch_data(q, conn)


def query_sport_name(conn,hoverData):
    q=''
    if hoverData:
        sport_name = hoverData['points'][0]['x']
        q = f'''SELECT "运动名称",
                            sum("次")AS "合计次数"
                            FROM train_record
                            WHERE "次" > 0 AND "日期" = "{sport_name}"
                            GROUP BY "运动名称"
                            ORDER BY sum("次")DESC '''
    else:
        q = '''SELECT "运动名称",
                            sum("次")AS "合计次数"
                            FROM train_record
                            WHERE "次" > 0
                            GROUP BY "运动名称"
                            ORDER BY sum("次")DESC '''
    return fetch_data(q, conn)

table_query = '''
                SELECT "运动名称",
                count("运动名称") / count(DISTINCT "日期")AS "Average_Sets",
                sum("次")AS "合计次数",
                AVG("重量")AS "平均重量(单位：KG)"
                FROM train_record
                WHERE "次" > 0
                GROUP BY "运动名称"
                ORDER BY sum("次") DESC
                '''

table_df = fetch_data(table_query, conn)


def query_meter(conn, select_date):
    q= ''
    if select_date:
        date = select_date['points'][0]['x']
        q = f'''
        SELECT  AVG(Avg_Left_Weight/Avg_Repeats)  AS Intensity
        FROM (SELECT "运动名称",
                SUM("次") / count("日期") AS "Avg_Repeats",
                SUM("重量") / count("日期") AS "Avg_Left_Weight"
            FROM train_record
            WHERE "次" > 0 AND "重量" > 0 AND "日期" = "{date}"
            GROUP BY "运动名称"
            ORDER BY sum("次") DESC)
    '''
    else:
        q = '''
            SELECT  AVG(Avg_Left_Weight/Avg_Repeats)  AS Intensity
            FROM (SELECT "运动名称",
                    SUM("次") / count("日期") AS "Avg_Repeats",
                    SUM("重量") / count("日期") AS "Avg_Left_Weight"
                FROM train_record
                WHERE "次" > 0 AND "重量" > 0
                GROUP BY "运动名称"
                ORDER BY sum("次") DESC)
        '''
    dataframe = fetch_data(q, conn)
    return dataframe.at[0,'Intensity']


##########
#  View  #
##########

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

server = app.server

def generate_fact():
    days_query = 'SELECT COUNT(DISTINCT "日期") AS days FROM train_record'
    days = fetch_data(days_query,conn).at[0,"days"]
    return days


def generate_table(dataframe):
    return dash_table.DataTable(id='table',
                                columns=[{
                                    'name': '运动名称',
                                    'id': '运动名称',
                                    'type': 'text'
                                }, {
                                    'name':
                                    'Average_Sets',
                                    'id': 'Average_Sets',
                                    'type': 'numeric',
                                    'format':
                                    Format(precision=0, scheme=Scheme.fixed)
                                }, {
                                    'name':
                                    '合计次数',
                                    'id':
                                    '合计次数',
                                    'type':
                                    'numeric',
                                    'format':
                                    Format(precision=0, scheme=Scheme.fixed)
                                }, {
                                    'name':
                                    '平均重量(单位：KG)',
                                    'id':
                                    '平均重量(单位：KG)',
                                    'type':
                                    'numeric',
                                    'format':
                                    Format(precision=0, scheme=Scheme.fixed)
                                }],
                                data=dataframe.to_dict('records'),
                                style_as_list_view=True,
                                sorting=True,
                                style_table={
                                    'maxHeight': 300,
                                    'whiteSpace': 'normal',
                                    'textOverflow': 'ellipsis',
                                },
                                style_cell={
                                    'backgroundColor': color_scheme['black'],
                                    'color': color_scheme['white']
                                },
                                n_fixed_rows=1,
                                style_data_conditional=[{
                                    'if': {
                                        'column_id': '运动名称'
                                    },
                                    'width': '50px'
                                }, {
                                    'if': {
                                        'column_id': 'Average_Sets'
                                    },
                                    'width': '50px'
                                }, {
                                    'if': {
                                        'column_id': '合计次数'
                                    },
                                    'width': '100px'
                                }, {
                                    'if': {
                                        'column_id': '平均重量(单位：KG)'
                                    },
                                    'width': '80px'
                                }],
                                virtualization=True,
                                pagination_mode=False)


app.layout = html.Div(children=[
    html.H2(children='Workout Summary'),
    html.Div([
        html.Div(generate_table(table_df), className='pure-u-1-2'),
        html.Div(children=[
            daq.DarkThemeProvider(theme={
                'dark': False,
                'detail': color_scheme['white'],
                'primary': color_scheme['white'],
                'secondary': color_scheme['white']
            },
                                  children=daq.Gauge(
                                      id='work_out_intensity_gauge',
                                      min=0,
                                      max=5,
                                      color=color_scheme['green'])),
            html.Span(children=f"You've complete {generate_fact()} days workout.",
                      className='summary')
        ],
                 className='pure-u-1-2')
    ],
             className='pure-g'),
    html.Div(children=[
        html.Div(dcc.Graph(id='time_trend',figure={'layout':{'plot_bgcolor':color_scheme['black'],
                                      'paper_bgcolor':color_scheme['black']}}), className='pure-u-1-2'),
        html.Div(dcc.Graph(id='sports_potion_barplot',figure={'layout':{'plot_bgcolor':color_scheme['black'],
                                      'paper_bgcolor':color_scheme['black']}}), className='pure-u-1-2')
    ],
             className='pure-g')
])

# CallBacks


# Customerize the bar plot interaction
@app.callback(
    Output(component_id='sports_potion_barplot', component_property='figure'),
    [
        Input(component_id='table', component_property='data'),
        Input('time_trend', 'hoverData')
    ])
def generate_bar_graph(data, hoverData):
    dataframe = query_sport_name(conn, hoverData)
    return go.Figure(data=[
        go.Bar(x=dataframe['运动名称'].tolist(),
               y=dataframe['合计次数'].tolist(),
               width=0.55,
               marker={'color': color_scheme['green']})
    ],
                     layout=go.Layout(title='Total Repeats of Each Sports',
                                      font={'color': color_scheme['white']},
                                      plot_bgcolor=color_scheme['black'],
                                      paper_bgcolor=color_scheme['black'],
                                      xaxis={
                                          'title': '运动名称',
                                          'tickfont': {
                                              'size': 8
                                          },
                                          'showgrid': False,
                                          'linewidth': 3,
                                          'linecolor': color_scheme['grey']
                                      },
                                      yaxis={
                                          'title': '重复次数',
                                          'linewidth': 3,
                                          'linecolor': color_scheme['grey'],
                                          'tickfont': {
                                              'size': 10
                                          },
                                          'showgrid': False,
                                          'showline': True
                                      },
                                      height=400,
                                      autosize=True,
                                      bargap=0.1,
                                      hovermode='closest'))


@app.callback(
    Output(component_id='work_out_intensity_gauge',
           component_property='value'),
    [Input(component_id='time_trend', component_property='hoverData')])
def update_gauge(hoverData):  # we don 't want the boundary now
    return query_meter(conn, hoverData)


@app.callback(Output(component_id='time_trend', component_property='figure'), 
        [Input(component_id='sports_potion_barplot', component_property='hoverData')
])
def update_time_trend(hoverData):
    dataframe = query_date(conn,hoverData)
    return go.Figure(data=[
        go.Scatter({
            'x': dataframe["日期"].tolist(),
            'y': dataframe["合计次数"].tolist(),
            'type': 'line',
            'name': '次数累计',
            'marker': {
                'color': color_scheme['green']
            }
        })
    ],
                     layout=go.Layout({
                         'plot_bgcolor': color_scheme['black'],
                         'paper_bgcolor': color_scheme['black'],
                         'autosize': False,
                         'title': 'Total Repeats Trending',
                         'font': {
                             'color': color_scheme['white']
                         },
                         'height': 400,
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
                     }))


if __name__ == '__main__':
    app.run_server(debug=True)
