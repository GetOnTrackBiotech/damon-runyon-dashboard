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
    className="mb-4"
)

# Sidebar
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
    style={"position": "fixed", "top": "70px", "left": 0, "bottom": 0, "width": "250px", "padding": "20px", "background": "#f8f9fa"}
)

content = html.Div(id="page-content", style={"margin-left": "270px", "padding": "20px"})

# App Layout
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
        return publications_layout()
    elif pathname == '/funding':
        fig = px.bar(funding_df, x=funding_df.columns[0],
                     y='Total Federal Funding (NIH only) Dollars Secured (Post-Damon Runyon Award)',
                     title='Total NIH Funding by Scientist', color=funding_df.columns[0])
        return dbc.Container([html.H2("NIH Funding"), dcc.Graph(figure=fig)])
    else:
        total_funding = funding_df['Total Federal Funding (NIH only) Dollars Secured (Post-Damon Runyon Award)'].sum()
        total_awards = awards_df.shape[0]
        return dbc.Container([
            html.H2("Overview"),
            dbc.Row([
                kpi_card("Total NIH Funding", f"${total_funding:,.0f}"),
                kpi_card("Total Awards", f"{total_awards}", color="info")
            ])
        ])

# KPI Card Component
def kpi_card(title, value, color="primary"):
    return dbc.Col(dbc.Card(
        dbc.CardBody([
            html.H5(title, className="card-title"),
            html.H2(value)
        ]),
        className="shadow-sm rounded"
    ), width=3)

# Publications Page Layout
def publications_layout():
    return dbc.Container([
        html.H2("Publications Overview"),
        html.P("Explore publication productivity and impact across Damon Runyon scientists."),
        dcc.Dropdown(
            id='pubs-scientist-dropdown',
            options=[{'label': 'All Scientists', 'value': 'All'}] + 
                    [{'label': sci, 'value': sci} for sci in publications_df['Scientist Name']],
            value='All',
            style={'width': '50%', 'position': 'sticky', 'top': '80px', 'zIndex': 1000, 'margin-bottom': '20px'}
        ),
        dbc.Row([
            kpi_card("Total Publications", "", "primary"),
            kpi_card("Avg Pubs Per Year", "", "info"),
            kpi_card("% Pubs in Top 10%", "", "success"),
            kpi_card("Avg Weighted RCR", "", "warning")
        ], className="mb-4"),

        dbc.Accordion([
            dbc.AccordionItem([
                dcc.Graph(id='chart-top10')
            ], title="Count of Publications in Top 10%"),
            dbc.AccordionItem([
                dbc.Row([
                    dbc.Col(dcc.Graph(id='chart-pubs-year')),
                    dbc.Col(dcc.Graph(id='chart-total-pubs'))
                ])
            ], title="Productivity Metrics"),
            dbc.AccordionItem([
                dbc.Row([
                    dbc.Col(dcc.Graph(id='chart-weighted-rcr')),
                    dbc.Col(dcc.Graph(id
