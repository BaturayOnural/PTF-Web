import dash
from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
import dash_html_components as html


app = dash.Dash(__name__)

app.layout = html.Div([
    
    html.Div([
        dcc.Input(
            id='adding-rows-name',
            placeholder='Enter a column name...',
            value='',
            style={'padding': 10}
        ),
        html.Button('Add Column', id='adding-rows-button', n_clicks=0)
    ], style={'height': 50}),

    html.Div(
        id='table-div',
           children=[

    ], style={'display': 'inline-block'}),

    dash_table.DataTable(
        id='adding-rows-table',
        columns=[{
            'name': 'Column {}'.format(i),
            'id': 'column-{}'.format(i),
            'deletable': True,
            'renamable': True
        } for i in range(1, 5)],
        data=[
            {'column-{}'.format(i): (j + (i-1)*5) for i in range(1, 5)}
            for j in range(5)
        ],
        editable=True,
        row_deletable=True
    ),

    html.Button('Add Row', id='editing-rows-button', n_clicks=0),

    
])


@app.callback(
    Output('adding-rows-table', 'data'),
    [Input('editing-rows-button', 'n_clicks')],
    [State('adding-rows-table', 'data'),
     State('adding-rows-table', 'columns')])
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@app.callback(
    Output('adding-rows-table', 'data'),
    [Input('editing-rows-button', 'n_clicks')],
    [State('adding-rows-table', 'data'),
     State('adding-rows-table', 'columns')])
def add_row(n_clicks, rows, columns):
    return dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict("rows"),
    style_header={'backgroundColor': 'rgb(30, 30, 30)'},
    style_cell={
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': 'white'
    },

)


@app.callback(
    Output('adding-rows-table', 'columns'),
    [Input('adding-rows-button', 'n_clicks')],
    [State('adding-rows-name', 'value'),
     State('adding-rows-table', 'columns')])
def update_columns(n_clicks, value, existing_columns):
    if n_clicks > 0:
        existing_columns.append({
            'id': value, 'name': value,
            'renamable': True, 'deletable': True
        })
    return existing_columns





if __name__ == '__main__':
    app.run_server(debug=True)