import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Initialize App with Superhero Theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])
app.title = "Damon Runyon Dashboard | SOPHIA"

# Load Data
excel_file = 'assets/damon_runyon_data_CLEAN.xlsx'
funding_df = pd.read_excel(excel_file, sheet_name='NIH & Grant Funding Impact')
awards_df = pd.read_excel(excel_file, sheet_name='Awards & Recognitions')
publications_df = pd.read_excel(excel_file, sheet_name='Publications (ICite #)')

scientists = funding_df[funding_df.columns[0]].dropna().unique()

# --- Layout Components ---

header = dbc.NavbarSimple(
    brand="Damon Runyon Metrics Dashboard",
    brand_href="/",
    color="#4c00b0",
    dark=True,
    className="mb-4"
)

sidebar = dbc.Nav(
    [
        dbc.NavLink("Overview", href="/", active="exact"),
        dbc.NavLink("NIH Funding", href="/funding", active="exact"),
        dbc.NavLink("Publications", href="/publications", active="exact"),
        dbc.NavLink("Publication Impact", href="/impact", active="exact"),
        dbc.NavLink("Companies & Career Timeline", href="/companies", active="exact"),
        dbc.NavLink("Entrepreneurship", href="/entrepreneurship", active="exact"),
        dbc.NavLink("Awards & Recognitions", href="/awards", active="exact"),
        dbc.NavLink("Scientist Drill-Down", href="/drilldown", active="exact"),
    ],
    vertical=True,
    pills=True,
    style={"position": "fixed", "top": "70px", "left": 0, "bottom": 0, "width": "250px", "padding": "20px", "background-color": "#2c3e50"}
)

content = html.Div(id="page-content", style={"margin-left": "270px", "padding": "20px"})

app.layout = html.Div([
    dcc.Location(id="url"),
    header,
    sidebar,
    content
])

# --- Page Navigation Callback ---

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/publications':
        return dbc.Container([
            html.H2("Publications Overview", className="text-primary"),
            html.P("Explore scientific productivity across Damon Runyon awardees. Use the dropdown to filter by individual scientists.",
                   className="text-light"),
            dcc.Dropdown(
                id='pubs-scientist-dropdown',
                options=[{'label': 'All Scientists', 'value': 'All'}] + 
                        [{'label': sci, 'value': sci} for sci in publications_df['Scientist Name']],
                value='All',
                style={'width': '50%', 'position': 'sticky', 'top': '80px', 'zIndex': 1000, 'margin-bottom': '20px'}
            ),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("Total Publications", className="card-title"),
                    html.H3(id='total-pubs')
                ]), className="mb-4 shadow rounded")),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("Avg Pubs Per Year", className="card-title"),
                    html.H3(id='avg-pubs-year')
                ]), className="mb-4 shadow rounded")),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("% Pubs in Top 10%", className="card-title"),
                    html.H3(id='top10-pubs')
                ]), className="mb-4 shadow rounded")),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("Avg Weighted RCR", className="card-title"),
                    html.H3(id='avg-rcr')
                ]), className="mb-4 shadow rounded")),
            ]),
            dcc.Graph(id='pubs-chart', className="shadow rounded")
        ])
    else:
        return dbc.Container([
            html.H2("Welcome to the Damon Runyon Dashboard", className="text-primary"),
            html.P("Use the sidebar to navigate through key metrics, funding data, publications, and career achievements.",
                   className="text-light")
        ])

# --- Publications Callback ---

@app.callback(
    [Output('total-pubs', 'children'),
     Output('avg-pubs-year', 'children'),
     Output('top10-pubs', 'children'),
     Output('avg-rcr', 'children'),
     Output('pubs-chart', 'figure')],
    [Input('pubs-scientist-dropdown', 'value')]
)
def update_publications_section(selected_scientist):
    if selected_scientist == 'All':
        df = publications_df.copy()
    else:
        df = publications_df[publications_df['Scientist Name'] == selected_scientist]
    
    total_pubs = df['Total Pubs'].sum()
    avg_pubs_year = round(df['Pubs Per Year'].mean(), 2)

    if df['% of pubs in Top 10%'].dtype == 'O':
        pct_values = df['% of pubs in Top 10%'].str.replace('%','').astype(float)
    else:
        pct_values = df['% of pubs in Top 10%']
    top10_pct = f"{round(pct_values.mean(), 1)}%"

    avg_rcr = round(df['Weighted RCR'].mean(), 2)
    
    fig = px.bar(df, x='Scientist Name', y='Pubs Per Year', color='Scientist Name',
                 title='Publications Per Year',
                 template='plotly_dark')
    
    return total_pubs, avg_pubs_year, top10_pct, avg_rcr, fig

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)



