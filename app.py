import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Use Bootstrap Theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Damon Runyon Dashboard | SOPHIA"

# Load Data from Cleaned Excel
excel_file = 'assets/damon_runyon_data_CLEAN.xlsx'
funding_df = pd.read_excel(excel_file, sheet_name='NIH & Grant Funding Impact')
awards_df = pd.read_excel(excel_file, sheet_name='Awards & Recognitions')
scientists = funding_df[funding_df.columns[0]].dropna().unique()

# --- Layout Components ---

# Header / Banner
header = dbc.NavbarSimple(
    brand="Damon Runyon Metrics Dashboard",
    brand_href="/",
    color="#4c00b0",
    dark=True,
    children=[
        dbc.NavItem(html.Span("Powered by SOPHIA", style={"color": "white", "margin-right": "15px"})),
    ]
)

# Sidebar Navigation
sidebar = dbc.Nav(
    [
        dbc.NavLink("Overview", href="/", active="exact"),
        dbc.NavLink("NIH Funding", href="/funding", active="exact"),
        dbc.NavLink("Scientist Drill-Down", href="/drilldown", active="exact"),
    ],
    vertical=True,
    pills=True,
    style={"position": "fixed", "top": "70px", "left": 0, "bottom": 0, "width": "200px", "padding": "20px", "background-color": "#f8f9fa"}
)

# Content Area
content = html.Div(id="page-content", style={"margin-left": "220px", "padding": "20px"})

# App Layout
app.layout = html.Div([
    dcc.Location(id="url"),
    header,
    sidebar,
    content
])

# --- Page Callbacks ---

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/funding':
        fig = px.bar(funding_df, x=funding_df.columns[0], y='Total Federal Funding (NIH only) Dollars Secured',
                     title='Total NIH Funding by Scientist', color=funding_df.columns[0])
        return dbc.Container([
            html.H2("NIH Funding"),
            dcc.Graph(figure=fig)
        ])
    elif pathname == '/drilldown':
        return dbc.Container([
            html.H2("Scientist Drill-Down"),
            dcc.Dropdown(options=[{'label': sci, 'value': sci} for sci in scientists],
                         id='scientist-dropdown',
                         placeholder='Select a Scientist'),
            html.Div(id='scientist-output')
        ])
    else:
        total_funding = funding_df['Total Federal Funding (NIH only) Dollars Secured'].sum()
        total_awards = awards_df.shape[0]
        return dbc.Container([
            html.H2("Overview"),
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H4("Total NIH Funding", className="card-title"),
                        html.H2(f"${total_funding:,.0f}")
                    ])
                ], color="primary", inverse=True)),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H4("Total Awards", className="card-title"),
                        html.H2(f"{total_awards}")
                    ])
                ], color="info", inverse=True)),
            ])
        ])

@app.callback(
    Output('scientist-output', 'children'),
    Input('scientist-dropdown', 'value')
)
def update_scientist_info(selected_scientist):
    if not selected_scientist:
        return ""
    funding_row = funding_df[funding_df[funding_df.columns[0]] == selected_scientist]
    awards = awards_df[awards_df['Scientist Name'] == selected_scientist]['Awards'].tolist()
    return html.Div([
        html.H4(f"Details for {selected_scientist}"),
        html.P(f"Total NIH Funding: ${funding_row['Total Federal Funding (NIH only) Dollars Secured'].values[0]:,.0f}"),
        html.P(f"Awards: {', '.join(awards) if awards else 'None'}")
    ])

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
