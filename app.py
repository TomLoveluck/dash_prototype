import pandas as pd
import base64
import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from jupyter_dash import JupyterDash

# ------------------------------------------------------------------------------
# Import and clean data (importing csv into pandas)
df = pd.read_csv("data/intro_bees.csv")

states = df.State.unique()
years = df.Year.unique()
min_year = min(years)
max_year = max(years)

grouped_df = df.groupby(['State', 'ANSI', 'Affected by', 'Year', 'state_code'])[['Pct of Colonies Impacted']].mean()
grouped_df.loc[:, 'Pct of Colonies Impacted'] = grouped_df['Pct of Colonies Impacted'].round(2)
grouped_df = (
    grouped_df
    .sort_values(by=['Year', 'Affected by'])
    .reset_index()
    [['State', 'Year', 'Affected by', 'Pct of Colonies Impacted']]
)


# ------------------------------------------------------------------------------

# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa',
    'textAlign': 'center'
}

# the style arguments for the main content page.
CONTENT_STYLE = {
    'margin-left': '25%',
    'margin-right': '5%',
    'padding': '20px 10p'
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970'
}

CARD_TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#0074D9'
}

controls = dbc.FormGroup(
    [
        html.P('Intent', style={
            'textAlign': 'center'
        }),
        dcc.Dropdown(
            id='state_dropdown',
            options=[{
                'label': val,
                'value': val
            } for val in states
            ],
            value='Alabama'
        ),
        html.Br(),
        html.P('Time Period', style={
            'textAlign': 'center'
        }),
        dcc.RangeSlider(
            id='range_slider',
            min=min_year,
            max=max_year,
            value=[min_year, max_year]
        ),

        html.Div(id='output-container-range-slider'),

        html.Br(),
        html.Br(),
        dbc.Button(
            id='submit_button',
            n_clicks=0,
            children='Submit',
            color='primary',
            block=True
        ),
    ]
)

sidebar = html.Div(
    [
        html.Br(),
        html.H3('Search Parameters', style=TEXT_STYLE),
        html.Hr(),
        controls
    ],
    style=SIDEBAR_STYLE
)

content_row = dbc.Row(
    [
        dbc.Col(
            dash_table.DataTable(
                id='bee_data_table',
                columns=[{"name": i, "id": i, "deletable": False, "selectable": False, "hideable": False}
                         for i in grouped_df.columns],
                data=[],
                filter_action='none',
                sort_action="native",
                style_cell={'textAlign': 'center', 'font-family': 'sans-serif'},
                editable=False

            )
        )
    ]

)

content = html.Div(
    [
        html.H2('Transcript Review Tool', style=TEXT_STYLE),
        html.Hr(),
        content_row
    ],
    style=CONTENT_STYLE
)

app = JupyterDash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([sidebar, content])


@app.callback(
     Output(component_id='bee_data_table', component_property='data'),
     [Input(component_id='submit_button', component_property='n_clicks'),
      State(component_id='state_dropdown', component_property='value'),
      State(component_id='range_slider', component_property='value')]
)
def update_dash_table(n_clicks, state, date_range):
    dash_table_data = (
        grouped_df
        .loc[grouped_df["State"] == state]
        .loc[grouped_df["Year"] >= date_range[0]]
        .loc[grouped_df["Year"] <= date_range[1]]
        .to_dict('records')
    )
    return dash_table_data


@app.callback(
    dash.dependencies.Output('output-container-range-slider', 'children'),
    [dash.dependencies.Input('range_slider', 'value')])
def update_slideroutput(value):
    return 'You have selected {} to {} inclusive'.format(value[0], value[1])


if __name__ == '__main__':
    app.run_server()
