import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Initialize app with LUXE theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = "Damon Runyon Dashboard | SOPHIA"

# Load Data
excel_file = 'assets/damon_runyon_data_CLEAN.xlsx'
funding_df = pd.read_excel(excel_file, sheet_name='NIH & Grant Funding Impact')
publications_df = pd.read_excel(excel_file, sheet_name='Publications (ICite #)')

# Sidebar Layout
sidebar = dbc.Nav(
    [
        dbc.NavLink("NIH Funding", href="/funding", active="exact"),
        dbc.NavLink("Publications", href="/publications", active="exact"),
        dbc.NavLink("Publication Impact", href="/impact", active="exact"),
        dbc.NavLink("Companies & Entrepreneurship", href="/companies", active="exact"),
        dbc.NavLink("Awards & Recognitions", href="/awards", active="exact"),
        dbc.NavLink("Scientist Drill-Down", href="/drilldown", active="exact"),
    ],
    vertical=True,
    pills=True,
    style={"padding": "20px"}
)

# Content Area
content = html.Div(id="page-content", style={"padding": "20px"})

# App Layout
app.layout = html.Div([
    dcc.Location(id="url"),
    dbc.Row([
        dbc.Col(sidebar, width=2),
        dbc.Col(content, width=10)
    ])
])
# Page Routing Callback
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/funding':
        total_funding = funding_df['Total Federal Funding (NIH only) Dollars Secured (Post-Damon Runyon Award)'].sum()
        fig = px.bar(funding_df, 
                     x=funding_df.columns[0], 
                     y='Total Federal Funding (NIH only) Dollars Secured (Post-Damon Runyon Award)',
                     title='Total NIH Funding by Scientist')
        return html.Div([
            html.H2("NIH Funding Overview"),
            html.P("This section highlights total NIH funding secured post-Damon Runyon awards."),
            dbc.Card([
                dbc.CardBody([
                    html.H4("Total NIH Funding Secured"),
                    html.H2(f"${total_funding:,.0f}")
                ])
            ], color="primary", inverse=True, style={"width": "300px", "margin-bottom": "20px"}),
            dcc.Graph(figure=fig)
        ])
    
    elif pathname == '/publications':
        return html.Div([
            html.H2("Publications Overview"),
            html.P("Explore publication productivity across scientists. Filter by individual scientists below."),
            dcc.Dropdown(
                id='pubs-scientist-dropdown',
                options=[{'label': 'All Scientists', 'value': 'All'}] + 
                        [{'label': sci, 'value': sci} for sci in publications_df['Scientist Name'].unique()],
                value='All',
                style={'width': '50%', 'margin-bottom': '20px'}
            ),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("Total Publications"),
                    html.H3(id='total-pubs')
                ]), color="info", inverse=True)),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("Avg Pubs Per Year"),
                    html.H3(id='avg-pubs-year')
                ]), color="secondary", inverse=True)),
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
        return html.Div([
            html.H2("Publication Impact"),
            html.P("Detailed impact metrics will be displayed here soon."),
        ])

    elif pathname == '/companies':
        return html.Div([
            html.H2("Companies & Entrepreneurship"),
            html.P("Startup activity, IPOs, and company affiliations will appear here."),
        ])

    elif pathname == '/awards':
        return html.Div([
            html.H2("Awards & Recognitions"),
            html.P("Major prizes and honors awarded to scientists will be listed here."),
        ])

    elif pathname == '/drilldown':
        return html.Div([
            html.H2("Scientist Drill-Down"),
            html.P("Select a scientist for detailed career metrics."),
            dcc.Dropdown(
                options=[{'label': sci, 'value': sci} for sci in funding_df[funding_df.columns[0]].unique()],
                id='scientist-dropdown',
                placeholder='Select a Scientist'
            ),
            html.Div(id='scientist-output')
        ])
    else:
        return html.Div([
            html.H2("Welcome to the Damon Runyon Dashboard"),
            html.P("Select a section from the sidebar to begin.")
        ])
# Scientist Drill-Down Callback
@app.callback(
    Output('scientist-output', 'children'),
    Input('scientist-dropdown', 'value')
)
def update_scientist_info(selected_scientist):
    if not selected_scientist:
        return ""
    funding_row = funding_df[funding_df[funding_df.columns[0]] == selected_scientist]
    awards = awards_df[awards_df['Scientist Name'] == selected_scientist]['Awards'].tolist()
    return dbc.Card([
        dbc.CardBody([
            html.H4(f"Details for {selected_scientist}"),
            html.P(f"Total NIH Funding: ${funding_row['Total Federal Funding (NIH only) Dollars Secured (Post-Damon Runyon Award)'].values[0]:,.0f}"),
            html.P(f"Awards: {', '.join(awards) if awards else 'No notable awards listed.'}")
        ])
    ], style={"margin-top": "20px"})

# Publications Metrics Callback
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
                 title='Publications Per Year')
    
    return total_pubs, avg_pubs_year, top10_pct, avg_rcr, fig

# Run Server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
