import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import numpy as np
import pandas as pd
import datetime
from datetime import datetime as dt
import pathlib
from io import StringIO
import boto3

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
#print(df_review.to_dict(orient='records'))
params = df_review.columns
table_city_list = df_review["city"].unique()



def write_csv_to_s3(df, outfilename="test.csv"):

    bucket = "bayarea-vet-review"
    region_name = "us-west-1"
    aws_access_key_id = "AKIARXCEGLG32O4BXR4G"
    aws_secret_access_key = "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"
    s3 = boto3.client("s3",\
                  region_name=region_name,\
                  aws_access_key_id=aws_access_key_id,\
                  aws_secret_access_key=aws_secret_access_key)
    csv_buf = StringIO()
    df.to_csv(csv_buf, header=True, index=False, encoding='UTF_8')
    csv_buf.seek(0)
    s3.put_object(Bucket=bucket, Body=csv_buf.getvalue(), Key='vet_reviews/' + outfilename)


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
                id="submit-btn-outer",
                children=[
                html.Button(id="submit-btn", children="Submit", n_clicks=0),
                html.Button(id="reset-btn", children="Reset", n_clicks=0),
                html.Div(id="btn-status", style=dict(height='500px',overflow='auto')),
                ],
            style={'marginTop':20, 'marginLeft':20}),
        ],
    )


app.layout = html.Div(
    id="app-container",
    children=[
        #html.Div(id='intermediate-value', style={'display': 'none'}),
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
                html.Br(),
                html.H6("Veterinary reviews"),
                html.P("You can: "),
                html.P("    1. Fill out and submit the form to add a row or,"),
                html.P(
                    "    2. Click on the X on each row to delete a row from the table."),

                html.Div([

                    dash_table.DataTable(
                        id='review_table',
                        style_cell={
                            'whiteSpace': 'normal',
                            # 'height': 'auto',  # wrapped text in column
                            'textAlign': 'left',
                            'overflowY': 'auto',
                            'overflowX': 'auto',
                            'fontSize': 12,
                            'font-family': 'sans-serif',
                            'minWidth': '40px',
                            'maxHeight': '100px',
                            'padding': '8px',
                        },
                        style_data={
                            'maxHeight': '100px',
                            # 'width': '150px', 'minWidth': '150px', 'maxWidth': '200px',
                            # 'textOverflow': 'ellipsis',
                        },
                        style_table={
                            'maxHeight': '100%',
                            'width': '100%',
                            'maxWidth': '200%',
                            'margin': '8px',
                        },
                        # style header
                        style_header={
                            'fontWeight': 'bold',
                            'fontSize': 13,
                            'color': 'white',
                            'backgroundColor': '#357EC7',
                            'textAlign': 'center',
                        },
                        style_data_conditional=[
                            {
                                'if': {'column_id': 'comment'},
                                'width': '260px',
                            },
                            {
                                'if': {'column_id': 'hospital'},
                                'width': '22px',
                            },
                            {
                                'if': {'column_id': 'doctor'},
                                'width': '22px',
                            },
                            {
                                'if': {'column_id': 'city'},
                                'width': '15px',
                            },
                            {
                                'if': {'column_id': 'breed'},
                                'width': '10px',
                            },
                            {
                                'if': {'column_id': 'rating'},
                                'width': '10px',
                            },
                            {
                                'if': {'column_id': 'disease'},
                                'width': '20px',
                            },
                            {
                                # stripped rows
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(248, 248, 248)'
                            },
                            {
                                'if': {
                                    # comparing columns to each other
                                    'filter_query': '{rating} = 5',
                                    'column_id': 'hospital'
                                },
                                'backgroundColor': '#006400',
                                'color': 'white',
                            },
                            {
                                'if': {
                                    # comparing columns to each other
                                    'filter_query': '{rating} = 4',
                                    'column_id': 'hospital'
                                },
                                'backgroundColor': '#228B22',
                            },
                            {
                                'if': {
                                    # comparing columns to each other
                                    'filter_query': '{rating} = 2',
                                    'column_id': 'hospital'
                                },
                                'backgroundColor': '#9ACD32',
                            },
                            {
                                'if': {
                                    # comparing columns to each other
                                    'filter_query': '{rating} = 3',
                                    'column_id': 'hospital'
                                },
                                'backgroundColor': '#556B2F',
                                'color': 'white',
                            },
                            {
                                'if': {
                                    # comparing columns to each other
                                    'filter_query': '{rating} = 1',
                                    'column_id': 'hospital'
                                },
                                'backgroundColor': '#000000',
                                'color': 'white',
                            },
                        ],
                        columns=(
                            [{'id': p, 'name': p} for p in params]
                        ),
                        data=df_review.to_dict(orient='records'),
                        fixed_rows={'headers': True, 'data': 0},
                        editable=False,
                        filter_action='native',
                        sort_action='native',
                        sort_mode='multi',
                        # page_action='native',
                        # page_size=10,
                        # virtualization=True, # this returns error
                        page_action='none',
                        # row_selectable="multi",
                        row_deletable=True,
                    ),
                    html.Div(id='output-table'),
                    html.Br(),

                    #html.Div(children=[
                    #    html.A("Download CSV", href="/download_excel/",
                    #           id='download-link',
                    #           download="bay_vet_reviews.csv",
                    #           target="_blank"),
                    #], ),
                ],
                ),
            ],

        ), # end of right-column
    ],

)

# for adding a row
@app.callback(
    Output("submit-btn", "n_clicks"),
    [
        Input("reset-btn", "n_clicks"),
    ]
)
def reset_submit(reset_click):

    if reset_click > 0:
        return 0
    else:
        return 0



@app.callback(
    [Output('review_table', 'data'),
    Output('btn-status', 'children'),],
    [
        Input("hospital-name", "value"),
        Input("doctor-name", "value"),
        Input("city-select", "value"),
        Input("breed-select", "value"),
        Input("disease-name", "value"),
        Input("rating-select", "value"),
        Input("detail-comments", "value"),
        Input("submit-btn", "n_clicks"),
    ]
)
def update_table(hospital, doctor, city, breed,
                 disease, rating, comment, submit_click):

    df_review = pd.read_csv(DATA_PATH.joinpath("vet_review.csv"))

    if submit_click >= 1:
        dict_new_review = {}
        dict_new_review['hospital'] = hospital
        dict_new_review['doctor'] = doctor
        dict_new_review['city'] = city
        dict_new_review['breed'] = breed
        dict_new_review['disease'] = disease
        dict_new_review['rating'] = rating
        dict_new_review['comment'] = comment

        df_review = df_review.append(dict_new_review, ignore_index=True)

        df_review.to_csv(DATA_PATH.joinpath("vet_review.csv"), index=False)
        now = datetime.datetime.now()
        write_csv_to_s3(df_review, outfilename=now.strftime("%Y_%b_%d_%A_%I_%M_%S") + "vet_review.csv")

        return [df_review.to_dict(orient='records'), "Form submitted succesfully"]

    else:
        return [df_review.to_dict(orient='records'), None]



# for deleting a row
@app.callback(Output('output-table', 'children'),
              [Input('review_table', 'data_previous')],
              [State('review_table', 'data')])
def show_removed_rows(previous, current):
    if previous is None:
        dash.exceptions.PreventUpdate()
    else:
        # archive previous
        now = datetime.datetime.now()
        #pd.DataFrame(previous).to_csv(DATA_PATH.joinpath(now.strftime("%Y_%b_%d_%A_%I_%M_%S_%f") + "vet_review.csv.gz"),
        #                              index=False, compression="gzip")
        write_csv_to_s3(pd.DataFrame(previous),
                        outfilename=now.strftime("%Y_%b_%d_%A_%I_%M_%S") + "vet_review.csv")
        # archive current
        pd.DataFrame(current).to_csv(
            DATA_PATH.joinpath("vet_review.csv"), index=False)
        write_csv_to_s3(pd.DataFrame(current),
                outfilename=now.strftime("%Y_%b_%d_%A_%I_%M_%S") + "vet_review.csv")
        return [f'Just removed {row}' for row in previous if row not in current]



@app.callback(
    Output('download-link', 'href'),
    [Input('download-link', 'children')])
def generate_csv(filter_value):
    import urllib

    df_review = pd.read_csv(DATA_PATH.joinpath("vet_review.csv"))
    csv_string = df_review.to_csv(index=False, encoding='utf-8') # not working with chinese characters
    csv_string = "data:text/csv;charset=utf-8," + \
        urllib.parse.quote(csv_string)
    return csv_string

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)
