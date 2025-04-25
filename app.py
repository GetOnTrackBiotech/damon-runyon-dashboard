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
publications_df = pd.read_excel(excel_file, sheet_name='Publications (ICite #)')

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

# Content Area
content = html.Div(id="page-content", style={"margin-left": "270px", "padding": "20px"})

# App Layout
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
    if pathname == '/funding':
        fig = px.bar(funding_df, 
                     x=funding_df.columns[0], 
                     y='Total Federal Funding (NIH only) Dollars Secured (Post-Damon Runyon Award)',
                     title='Total NIH Funding by Scientist', 
                     color=funding_df.columns[0])
        return dbc.Container([
            html.H2("NIH Funding"),
            dcc.Graph(figure=fig)
        ])
    
    elif pathname == '/publications':
        return dbc.Container([
            html.H2("Publications Overview"),
            dcc.Dropdown(
                id='pubs-scientist-dropdown',
                options=[{'label': 'All Scientists', 'value': 'All'}] + 
                        [{'label': sci, 'value': sci} for sci in publications_df['Scientist Name']],
                value='All',
                style={'width': '50%', 'margin-bottom': '20px'}
            ),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("Total Publications"),
                    html.H3(id='total-pubs')
                ]), color="primary", inverse=True)),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("Avg Pubs Per Year"),
                    html.H3(id='avg-pubs-year')
                ]), color="info", inverse=True)),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("% Pubs in Top 10%"),
                    html.H3(id='top10-pubs')
                ]), color="success", inverse=True)),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("Avg Weighted RCR"),
                    html.H3(id='avg-rcr')
                ]), color="warning", inverse=True)),
            ], className="mb-4"),
            dcc.Graph(id='pubs-chart')
        ])

    elif pathname == '/impact':
        return dbc.Container([
            html.H2("Publication Impact"),
            html.P("Impact metrics and visuals coming soon...")
        ])
    elif pathname == '/companies':
        return dbc.Container([
            html.H2("Companies & Career Timeline"),
            html.P("Career timelines and company data coming soon...")
        ])
    elif pathname == '/entrepreneurship':
        return dbc.Container([
            html.H2("Entrepreneurship"),
            html.P("Startups, IPOs, patents, and more coming soon...")
        ])
    elif pathname == '/awards':
        return dbc.Container([
            html.H2("Awards & Recognitions"),
            html.P("Awards data and highlights coming soon...")
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
        total_funding = funding_df['Total Federal Funding (NIH only) Dollars Secured (Post-Damon Runyon Award)'].sum()
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

# --- Scientist Drill-Down Callback ---

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
        html.P(f"Total NIH Funding: ${funding_row['Total Federal Funding (NIH only) Dollars Secured (Post-Damon Runyon Award)'].values[0]:,.0f}"),
        html.P(f"Awards: {', '.join(awards) if awards else 'None'}")
    ])

# --- Publications Section Callback ---

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
if df['% of pubs in Top 10%'].dtype == 'O':  # 'O' = object = string
    pct_values = df['% of pubs in Top 10%'].str.replace('%','').astype(float)
else:
    pct_values = df['% of pubs in Top 10%']

top10_pct = f"{round(pct_values.mean(), 1)}%"

    avg_rcr = round(df['Weighted RCR'].mean(), 2)
    
    fig = px.bar(df, x='Scientist Name', y='Pubs Per Year', color='Scientist Name',
                 title='Publications Per Year')
    
    return total_pubs, avg_pubs_year, top10_pct, avg_rcr, fig

# --- Run App ---

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
