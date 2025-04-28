import dash
from dash import dcc, html, Input, Output
from dash_bootstrap_components import NavbarSimple, Nav, NavLink, NavItem, Card, CardBody, Row, Col, Accordion, AccordionItem
import pandas as pd
import plotly.express as px

# Initialize App with Lux Theme
app = dash.Dash(__name__, external_stylesheets=[dash.bootstrap_components.themes.LUX])
app.title = "Damon Runyon Dashboard | SOPHIA"

# Load Data
excel_file = 'assets/damon_runyon_data_CLEAN.xlsx'
funding_df = pd.read_excel(excel_file, sheet_name='NIH & Grant Funding Impact')
awards_df = pd.read_excel(excel_file, sheet_name='Awards & Recognitions')
publications_df = pd.read_excel(excel_file, sheet_name='Publications (ICite #)')

scientists = funding_df[funding_df.columns[0]].dropna().unique()

# --- Layout Components ---
header = NavbarSimple(
    brand="Damon Runyon Metrics Dashboard",
    brand_href="/",
    color="#4c00b0",
    dark=True,
    children=[NavItem(html.Span("Powered by SOPHIA", style={"color": "white"}) )]
)

sidebar = Nav(
    [
        NavLink("Overview", href="/", active="exact"),
        NavLink("NIH Funding", href="/funding", active="exact"),
        NavLink("Publications", href="/publications", active="exact"),
        NavLink("Publication Impact", href="/impact", active="exact"),
        NavLink("Companies & Career Timeline", href="/companies", active="exact"),
        NavLink("Entrepreneurship", href="/entrepreneurship", active="exact"),
        NavLink("Awards & Recognitions", href="/awards", active="exact"),
        NavLink("Scientist Drill-Down", href="/drilldown", active="exact"),
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
        return html.Div([
            html.H2("NIH Funding"),
            html.P("Overview of NIH funding secured by Damon Runyon scientists post-award."),
            dcc.Graph(figure=fig)
        ])
    
    elif pathname == '/publications':
        return html.Div([
            html.H2("Publications Overview"),
            html.P("Explore publication productivity and impact across Damon Runyon scientists."),
            dcc.Dropdown(
                id='pubs-scientist-dropdown',
                options=[{'label': 'All Scientists', 'value': 'All'}] + 
                        [{'label': sci, 'value': sci} for sci in publications_df['Scientist Name']],
                value='All',
                style={'width': '50%', 'margin-bottom': '20px', 'position': 'sticky', 'top': '80px', 'zIndex': 999}
            ),
            Row([
                Col(Card(CardBody([html.H5("Total Publications"), html.H3(id='total-pubs')]), color="primary", inverse=True, style={"border-radius": "10px", "box-shadow": "2px 2px 8px lightgrey"})),
                Col(Card(CardBody([html.H5("Avg Pubs Per Year"), html.H3(id='avg-pubs-year')]), color="info", inverse=True, style={"border-radius": "10px", "box-shadow": "2px 2px 8px lightgrey"})),
                Col(Card(CardBody([html.H5("% Pubs in Top 10%"), html.H3(id='top10-pubs')]), color="success", inverse=True, style={"border-radius": "10px", "box-shadow": "2px 2px 8px lightgrey"})),
                Col(Card(CardBody([html.H5("Avg Weighted RCR"), html.H3(id='avg-rcr')]), color="warning", inverse=True, style={"border-radius": "10px", "box-shadow": "2px 2px 8px lightgrey"})),
            ], className="mb-4"),
            Accordion([
                AccordionItem([
                    dcc.Graph(id='top10-chart')
                ], title="Publications in Top 10%"),
                AccordionItem([
                    Row([
                        Col(dcc.Graph(id='pubs-per-year-chart')),
                        Col(dcc.Graph(id='total-pubs-chart')),
                    ])
                ], title="Productivity Charts"),
                AccordionItem([
                    Row([
                        Col(dcc.Graph(id='weighted-rcr-chart')),
                        Col(dcc.Graph(id='mean-rcr-chart')),
                    ])
                ], title="RCR Metrics"),
                AccordionItem([
                    Row([
                        Col(dcc.Graph(id='avg-apt-chart')),
                        Col(dcc.Graph(id='cited-clin-chart')),
                    ])
                ], title="Additional Impact Metrics"),
            ], start_collapsed=True)
        ])

    elif pathname == '/impact':
        return html.Div([html.H2("Publication Impact"), html.P("Impact metrics and visuals coming soon...")])
    elif pathname == '/companies':
        return html.Div([html.H2("Companies & Career Timeline"), html.P("Career timelines and company data coming soon...")])
    elif pathname == '/entrepreneurship':
        return html.Div([html.H2("Entrepreneurship"), html.P("Startups, IPOs, patents, and more coming soon...")])
    elif pathname == '/awards':
        return html.Div([html.H2("Awards & Recognitions"), html.P("Awards data and highlights coming soon...")])
    elif pathname == '/drilldown':
        return html.Div([
            html.H2("Scientist Drill-Down"),
            dcc.Dropdown(options=[{'label': sci, 'value': sci} for sci in scientists],
                         id='scientist-dropdown', placeholder='Select a Scientist'),
            html.Div(id='scientist-output')
        ])
    else:
        total_funding = funding_df['Total Federal Funding (NIH only) Dollars Secured (Post-Damon Runyon Award)'].sum()
        total_awards = awards_df.shape[0]
        return html.Div([
            html.H2("Overview"),
            html.P("Summary of key metrics across all Damon Runyon scientists."),
            Row([
                Col(Card(CardBody([html.H4("Total NIH Funding"), html.H2(f"${total_funding:,.0f}")]), color="primary", inverse=True, style={"border-radius": "10px", "box-shadow": "2px 2px 8px lightgrey"})),
                Col(Card(CardBody([html.H4("Total Awards"), html.H2(f"{total_awards}")]), color="info", inverse=True, style={"border-radius": "10px", "box-shadow": "2px 2px 8px lightgrey"})),
            ])
        ])

# --- Scientist Drill-Down Callback ---
@app.callback(Output('scientist-output', 'children'),
              Input('scientist-dropdown', 'value'))
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
     Output('top10-chart', 'figure'),
     Output('pubs-per-year-chart', 'figure'),
     Output('total-pubs-chart', 'figure'),
     Output('weighted-rcr-chart', 'figure'),
     Output('mean-rcr-chart', 'figure'),
     Output('avg-apt-chart', 'figure'),
     Output('cited-clin-chart', 'figure')],
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

    charts = {
        'top10-chart': px.bar(df, x='Scientist Name', y='Count of Pubs in top 10%', title='Publications in Top 10%'),
        'pubs-per-year-chart': px.bar(df, x='Scientist Name', y='Pubs Per Year', title='Publications Per Year'),
        'total-pubs-chart': px.bar(df, x='Scientist Name', y='Total Pubs', title='Total Publications'),
        'weighted-rcr-chart': px.bar(df, x='Scientist Name', y='Weighted RCR', title='Weighted RCR'),
        'mean-rcr-chart': px.bar(df, x='Scientist Name', y='Mean RCR', title='Mean RCR'),
        'avg-apt-chart': px.bar(df, x='Scientist Name', y='Avg APT', title='Average APT'),
        'cited-clin-chart': px.bar(df, x='Scientist Name', y='Cited by Clin', title='Cited by Clinical Articles')
    }

    return total_pubs, avg_pubs_year, top10_pct, avg_rcr, charts['top10-chart'], charts['pubs-per-year-chart'], charts['total-pubs-chart'], charts['weighted-rcr-chart'], charts['mean-rcr-chart'], charts['avg-apt-chart'], charts['cited-clin-chart']

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
