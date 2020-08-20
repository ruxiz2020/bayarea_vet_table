import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, ClientsideFunction

import numpy as np
import pandas as pd
import datetime
from datetime import datetime as dt
import pathlib

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}],
)

server = app.server
app.config.suppress_callback_exceptions = True

# Path
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

# prepare data
#
df_city = pd.read_csv(DATA_PATH.joinpath("bay-area-city.csv"))
city_list = df_city["city_name"].unique()

breed_list = ['Cat', 'Dog', 'Bird', 'Rodent', 'Rabbit', 'Snake', "Other"]

df_review = pd.read_csv(DATA_PATH.joinpath("vet_review.csv"))
print(df_review.to_dict(orient='records'))
params = df_review.columns


def generate_control_card():
    """

    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.H5("Bayarea Veterinary Review Sheet"),
            html.H3("Welcome to the Bayarea Veterinary Review Sheet"),
            html.Div(
                id="intro",
                children="Feel free to explore or update Bayarea veterinary review data sheet. "
                "The data and app are maintained by Bayarea PetClub.",
            ),
            html.Br(),
            html.H6("Add A New Review"),
            html.P("Enter Animal Hospital Name:"),
            dcc.Input(
                id="hospital-name",
                placeholder='Animal Hospital Name',
                type='text',
                value=''
            ),
            html.P("Enter Doctor Name:"),
            dcc.Input(
                id="doctor-name",
                placeholder='Doctor Name',
                type='text',
                value=''
            ),
            html.P("Select City:"),
            dcc.Dropdown(
                id="city-select",
                options=[{"label": i, "value": i} for i in city_list],
                value=city_list[0],
            ),
            html.P("Select Pet Breed:"),
            dcc.Dropdown(
                id="breed-select",
                options=[{"label": i, "value": i} for i in breed_list],
                value=breed_list[0],
            ),
            html.P("Enter Disease:"),
            dcc.Input(
                id="disease-name",
                placeholder='Enter Disease',
                type='text',
                value=''
            ),
            html.P("Select Rating:"),
            dcc.Dropdown(
                id="rating-select",
                options=[
                    {"label": "1: Bad", "value": "1"},
                    {"label": "2: Below Expectation", "value": "2"},
                    {"label": "3: Met Expectation", "value": "3"},
                    {"label": "4: Beyond Expectation", "value": "4"},
                    {"label": "5: Excellent", "value": "5"},
                ],
                value="3",
            ),
            html.P("Enter Detailed Comments:"),
            dcc.Textarea(
                id='detail-comments',
                placeholder='How did you feel about the service?',
                style={'width': '100%', 'height': 200},
            ),
            html.Br(),
            html.Div(
                id="reset-btn-outer",
                children=html.Button(
                    id="reset-btn", children="Submit", n_clicks=0),
            ),
        ],
    )


app.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.A(
                    html.Button("Bayarea PetClub", id="learn-more-button"),
                    href="https://ruxiz2020.github.io/petclub/",
                ),
                html.Img(src=app.get_asset_url("pets.jpg")),

            ],
        ),
        # Left column
        html.Div(
            id="left-column",
            className="four columns",
            children=[generate_control_card()],
        ),
        # Right column
        html.Div(
            id="right-column",
            className="eight columns pkcalc-data-table",
            children=[
                # Patient Volume Heatmap
                html.Div([
                    dash_table.DataTable(
                        id='review_table',
                        style_cell={
                            'whiteSpace': 'normal',
                            'height': 'auto',  # wrapped text in column
                            'textAlign': 'left',
                            'overflowY': 'auto',
                            'overflowX': 'auto',
                            'fontSize': 12,
                            'font-family': 'sans-serif',
                        },
                        style_data={
                            'maxHeight': '30px',
                            # 'width': '150px', 'minWidth': '150px', 'maxWidth': '200px',
                            # 'textOverflow': 'ellipsis',
                        },
                        # style header
                        style_header={
                            'fontWeight': 'bold',
                            'fontSize': 15,
                            'color': 'white',
                            'backgroundColor': '#357EC7',
                        },
                        style_data_conditional=[
                            {
                                # stripped rows
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(248, 248, 248)'
                            },
                            {
                                # highlight one row
                                'if': {'row_index': 4},
                                "backgroundColor": "#3D9970",
                                'color': 'white'
                            }
                        ],
                        columns=(
                            [{'id': p, 'name': p} for p in params]
                        ),
                        data=df_review.to_dict(orient='records'),
                        editable=True,
                        # filter_action='native',
                    ),
                    # dcc.Graph(id='table-editing-simple-output')
                ]
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("wait_time_table", "children"),
    [
        Input("date-picker-select", "start_date"),
        Input("date-picker-select", "end_date"),
        Input("clinic-select", "value"),
        Input("admit-select", "value"),
        Input("patient_volume_hm", "clickData"),
        Input("reset-btn", "n_clicks"),
    ]
)
def update_table(start, end, clinic, admit_type, heatmap_click, reset_click, *args):

    return


# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)
