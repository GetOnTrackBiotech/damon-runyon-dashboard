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

# --- Layout Components ---
header = dbc.NavbarSimple(
    brand="Damon Runyon Metrics Dashboard",
    brand_href="/",
    color="#4c00b0",
    dark=True,
    children=[dbc.NavItem(html.Span("Powered by SOPHIA", style={"color": "white"}) )]
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
    style={"position": "fixed", "top": "70px", "left": 0, "bottom": 0, "width": "250px", "padding": "20px", "background-color": "#f8f9fa"}
)

content = html.Div(id="page-content", style={"margin-left": "270px", "padding": "20px"})

app.layout = html.Div([
    dcc.Location(id="url"),
    header,
    sidebar,
    content
])

# --- Page Routing Callback ---
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/funding':
        fig = px.bar(funding_df, 
                     x=funding_df.columns[0], 
                     y='Total Federal Funding (NIH only) Dollars Secured (Post-Damon Runyon Award)',
                     title='Total NIH Funding by Scientist', 
                     color=funding_df.columns[0])
        return dbc.Container([html.H2("NIH Funding"), dcc.Graph(figure=fig, className="shadow-sm rounded")])
    
    elif pathname == '/publications':
        return dbc.Container([
            html.H2("Publications Overview"),
            html.P("Explore publication productivity and impact across Damon Runyon scientists."),
            dcc.Dropdown(
                id='pubs-scientist-dropdown',
                options=[{'label': 'All Scientists', 'value': 'All'}] + 
                        [{'label': sci, 'value': sci} for sci in publications_df['Scientist Name']],
                value='All',
                style={'width': '50%', 'margin-bottom': '20px'}
            ),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([html.H5("Total Publications"), html.H3(id='total-pubs')]), 
                                 color="primary", inverse=True, className="shadow-sm rounded")),
                dbc.Col(dbc.Card(dbc.CardBody([html.H5("Avg Pubs Per Year"), html.H3(id='avg-pubs-year')]), 
                                 color="info", inverse=True, className="shadow-sm rounded")),
                dbc.Col(dbc.Card(dbc.CardBody([html.H5("% Pubs in Top 10%"), html.H3(id='top10-pubs')]), 
                                 color="success", inverse=True, className="shadow-sm rounded")),
                dbc.Col(dbc.Card(dbc.CardBody([html.H5("Avg Weighted RCR"), html.H3(id='avg-rcr')]), 
                                 color="warning", inverse=True, className="shadow-sm rounded")),
            ], className="mb-4"),
            dcc.Graph(id='top10-chart', className="shadow-sm rounded"),
            dbc.Row([
                dbc.Col(dcc.Graph(id='pubs-per-year-chart', className="shadow-sm rounded")),
                dbc.Col(dcc.Graph(id='total-pubs-chart', className="shadow-sm rounded")),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id='weighted-rcr-chart', className="shadow-sm rounded")),
                dbc.Col(dcc.Graph(id='mean-rcr-chart', className="shadow-sm rounded")),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id='avg-apt-chart', className="shadow-sm rounded")),
                dbc.Col(dcc.Graph(id='cited-clin-chart', className="shadow-sm rounded")),
            ])
        ])

    else:
        total_funding = funding_df['Total Federal Funding (NIH only) Dollars Secured (Post-Damon Runyon Award)'].sum()
        total_awards = awards_df.shape[0]
        return dbc.Container([
            html.H2("Overview"),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([html.H4("Total NIH Funding"), html.H2(f"${total_funding:,.0f}")]), 
                                 color="primary", inverse=True, className="shadow-sm rounded")),
                dbc.Col(dbc.Card(dbc.CardBody([html.H4("Total Awards"), html.H2(f"{total_awards}")]), 
                                 color="info", inverse=True, className="shadow-sm rounded")),
            ])
        ])

# --- Keep Existing Callbacks Below ---
# (No changes needed for logic)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
