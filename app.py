# Import Libraries
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Initialize App with LUX Theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = "Damon Runyon Dashboard | SOPHIA"

# Load Data
excel_file = 'assets/damon_runyon_data_CLEAN.xlsx'
funding_df = pd.read_excel(excel_file, sheet_name='NIH & Grant Funding Impact')
awards_df = pd.read_excel(excel_file, sheet_name='Awards & Recognitions')
publications_df = pd.read_excel(excel_file, sheet_name='Publications (ICite #)')

scientists = funding_df[funding_df.columns[0]].dropna().unique()

# Header
header = dbc.NavbarSimple(
    brand="Damon Runyon Metrics Dashboard",
    brand_href="/",
    color="#4c00b0",
    dark=True,
    children=[dbc.NavItem(html.Span("Powered by SOPHIA", style={"color": "white"}))]
)

# Sidebar
sidebar = dbc.Nav(
    [
        dbc.NavLink("Overview", href="/", active="exact"),
        dbc.NavLink("NIH Funding", href="/funding", active="exact"),
        dbc.NavLink("Publications", href="/publications", active="exact"),
        dbc.NavLink("Awards & Recognitions", href="/awards", active="exact"),
        dbc.NavLink("Scientist Drill-Down", href="/drilldown", active="exact"),
    ],
    vertical=True,
    pills=True,
    style={"position": "fixed", "top": "70px", "left": 0, "bottom": 0, "width": "250px", "padding": "20px", "background-color": "#f8f9fa"}
)

# Content
content = html.Div(id="page-content", style={"margin-left": "270px", "padding": "20px"})

# Layout
app.layout = html.Div([
    dcc.Location(id="url"),
    header,
    sidebar,
    content
])

# Page Routing
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/publications':
        return dbc.Container([
            html.H2("Publications Overview"),
            html.P("Explore publication productivity and impact metrics across Damon Runyon scientists."),
            dcc.Dropdown(
                id='pubs-scientist-dropdown',
                options=[{'label': 'All Scientists', 'value': 'All'}] + [{'label': sci, 'value': sci} for sci in publications_df['Scientist Name']],
                value='All',
                style={'width': '50%', 'margin-bottom': '20px', 'position': 'sticky', 'top': '80px', 'zIndex': 1000}
            ),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([html.H5("Total Publications"), html.H3(id='total-pubs')]), className="shadow-sm rounded")),
                dbc.Col(dbc.Card(dbc.CardBody([html.H5("Avg Pubs Per Year"), html.H3(id='avg-pubs-year')]), className="shadow-sm rounded")),
                dbc.Col(dbc.Card(dbc.CardBody([html.H5("% Pubs in Top 10%"), html.H3(id='top10-pubs')]), className="shadow-sm rounded")),
                dbc.Col(dbc.Card(dbc.CardBody([html.H5("Avg Weighted RCR"), html.H3(id='avg-rcr')]), className="shadow-sm rounded")),
            ], className="mb-4"),

            dbc.Accordion([
                dbc.AccordionItem([
                    dcc.Graph(id='chart-top10'),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='chart-pubs-year')),
                        dbc.Col(dcc.Graph(id='chart-total-pubs')),
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='chart-weighted-rcr')),
                        dbc.Col(dcc.Graph(id='chart-mean-rcr')),
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='chart-avg-apt')),
                        dbc.Col(dcc.Graph(id='chart-cited-clin')),
                    ])
                ], title="View Detailed Publication Metrics")
            ], start_collapsed=True)
        ])
    else:
        return dbc.Container([html.H2("Welcome to the Damon Runyon Dashboard"), html.P("Select a section from the sidebar to begin.")])

# Publications Callback
@app.callback(
    [Output('total-pubs', 'children'),
     Output('avg-pubs-year', 'children'),
     Output('top10-pubs', 'children'),
     Output('avg-rcr', 'children'),
     Output('chart-top10', 'figure'),
     Output('chart-pubs-year', 'figure'),
     Output('chart-total-pubs', 'figure'),
     Output('chart-weighted-rcr', 'figure'),
     Output('chart-mean-rcr', 'figure'),
     Output('chart-avg-apt', 'figure'),
     Output('chart-cited-clin', 'figure')],
    [Input('pubs-scientist-dropdown', 'value')]
)
def update_publications(selected_scientist):
    if selected_scientist == 'All':
        df = publications_df.copy()
    else:
        df = publications_df[publications_df['Scientist Name'] == selected_scientist]

    total_pubs = df['Total Pubs'].sum()
    avg_pubs_year = round(df['Pubs Per Year'].mean(), 2)
    pct_values = df['% of pubs in Top 10%']
    if pct_values.dtype == 'O':
        pct_values = pct_values.str.replace('%','').astype(float)
    top10_pct = f"{round(pct_values.mean(), 1)}%"
    avg_rcr = round(df['Weighted RCR'].mean(), 2)

    fig_top10 = px.bar(df, x='Scientist Name', y='% of pubs in Top 10%', title='Count of Publications in Top 10%')
    fig_pubs_year = px.bar(df, x='Scientist Name', y='Pubs Per Year', title='Publications Per Year')
    fig_total_pubs = px.bar(df, x='Scientist Name', y='Total Pubs', title='Total Publications')
    fig_weighted_rcr = px.bar(df, x='Scientist Name', y='Weighted RCR', title='Weighted RCR')
    fig_mean_rcr = px.bar(df, x='Scientist Name', y='Mean RCR', title='Mean RCR')
    fig_avg_apt = px.bar(df, x='Scientist Name', y='Avg APT', title='Average APT')
    fig_cited_clin = px.bar(df, x='Scientist Name', y='Cited by Clin Art', title='Cited by Clinical Articles')

    return total_pubs, avg_pubs_year, top10_pct, avg_rcr, fig_top10, fig_pubs_year, fig_total_pubs, fig_weighted_rcr, fig_mean_rcr, fig_avg_apt, fig_cited_clin

# Run Server
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
