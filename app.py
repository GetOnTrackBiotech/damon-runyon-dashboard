from dash import dash_table
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Initialize App with LUX Bootstrap Theme
app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.LUX,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
])
app.title = "Damon Runyon Dashboard | SOPHIA"

# Load Data
excel_file = 'assets/damon_runyon_data_CLEAN.xlsx'
funding_df = pd.read_excel(excel_file, sheet_name='NIH & Grant Funding Impact')
awards_df = pd.read_excel(excel_file, sheet_name='Awards & Recognitions')
publications_df = pd.read_excel(excel_file, sheet_name='Publications (ICite #)')
publications_impact_df = pd.read_excel(excel_file, sheet_name='Publications Impact')

scientists = funding_df[funding_df.columns[0]].dropna().unique()

# --- Layout Components ---
header = dbc.NavbarSimple(
    brand="Damon Runyon Metrics Dashboard",
    brand_href="/",
    color="#4c00b0",
    dark=True,
    children=[dbc.NavItem(html.Span("Powered by SOPHIA", style={"color": "white"}))]
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
    style={"position": "fixed", "top": "70px", "left": 0, "bottom": 0,
           "width": "250px", "padding": "20px", "background-color": "#f8f9fa"}
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
        return dbc.Container([html.H2("NIH Funding"), dcc.Graph(figure=fig)])

    elif pathname == '/publications':
        return dbc.Container([
            html.H2("Publications Overview"),
            html.P("Explore publication productivity and impact across Damon Runyon scientists."),
            dcc.Dropdown(
                id='pubs-scientist-dropdown',
                options=[{'label': 'All Scientists', 'value': 'All'}] +
                        [{'label': sci, 'value': sci} for sci in publications_df['Scientist Name']],
                value='All',
                style={'width': '50%', 'margin-bottom': '20px', 'position': 'sticky', 'top': '70px', 'zIndex': 1000}
            ),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5(["Total Publications ",
                             html.I(className="bi bi-info-circle-fill", id="tooltip-total-pubs", style={"cursor": "pointer"})]),
                    html.H3(id='total-pubs')
                ]), color="primary", inverse=True)),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5(["Avg Pubs Per Year ",
                             html.I(className="bi bi-info-circle-fill", id="tooltip-avg-pubs-year", style={"cursor": "pointer"})]),
                    html.H3(id='avg-pubs-year')
                ]), color="info", inverse=True)),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5(["% Pubs in Top 10% ",
                             html.I(className="bi bi-info-circle-fill", id="tooltip-top10", style={"cursor": "pointer"})]),
                    html.H3(id='top10-pubs')
                ]), color="success", inverse=True)),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5(["Avg Weighted RCR ",
                             html.I(className="bi bi-info-circle-fill", id="tooltip-avg-rcr", style={"cursor": "pointer"})]),
                    html.H3(id='avg-rcr')
                ]), color="warning", inverse=True)),
            ], className="mb-4"),

            dcc.Graph(id='top10-chart'),

            dbc.Accordion([
                dbc.AccordionItem([
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='pubs-per-year-chart')),
                        dbc.Col(dcc.Graph(id='total-pubs-chart')),
                    ])
                ], title="Productivity Metrics"),

                dbc.AccordionItem([
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='weighted-rcr-chart')),
                        dbc.Col(dcc.Graph(id='mean-rcr-chart')),
                    ])
                ], title="Citation Impact"),

                dbc.AccordionItem([
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='avg-apt-chart')),
                        dbc.Col(dcc.Graph(id='cited-clin-chart')),
                    ])
                ], title="Translational Reach"),
            ], start_collapsed=True),

            dbc.Tooltip("Total number of publications by the selected scientist(s).", target="tooltip-total-pubs", placement="top"),
            dbc.Tooltip("Average number of publications per year.", target="tooltip-avg-pubs-year", placement="top"),
            dbc.Tooltip("Percentage of publications ranked in the top 10% by citations.", target="tooltip-top10", placement="top"),
            dbc.Tooltip("Average weighted Relative Citation Ratio, indicating citation impact.", target="tooltip-avg-rcr", placement="top"),
        ])
# --- Page Routing Callback (continued) ---
    elif pathname == '/impact':
        return dbc.Container([
            html.H2("Publications Impact"),
            html.P("Analyzing the impact factors of top publications post-Damon Runyon award."),

            dcc.Dropdown(
                id='impact-scientist-dropdown',
                options=[{'label': 'All Scientists', 'value': 'All'}] + 
                        [{'label': sci, 'value': sci} for sci in publications_impact_df['Scientist'].unique()],
                value='All',
                style={'width': '50%', 'margin-bottom': '20px', 'position': 'sticky', 'top': '70px', 'zIndex': 1000}
            ),
            
            html.Div([
                html.Label("Minimum Impact Factor:", style={"margin-bottom": "5px"}),
                dcc.Slider(
                    id='if-threshold-slider',
                    min=0, max=100, step=1, value=10,
                    marks={i: str(i) for i in range(0, 101, 10)},
                    tooltip={"placement": "bottom", "always_visible": False}
                )
            ], style={'margin-bottom': '30px'}),

            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5(["Avg Impact Factor ",
                             html.I(className="bi bi-info-circle-fill", id="tooltip-avg-impact", style={"cursor": "pointer"})]),
                    html.H3(id='avg-impact')
                ]), color="primary", inverse=True))
            ], className="mb-4"),

        # Stacked layout with wrapped y-axis titles
            dbc.Card([
                dbc.CardBody([
                    html.H4("Top 10 Publications by Impact Factor", className="card-title"),
                    dcc.Graph(id='avg-impact-chart')
                ])
            ], className="mb-4"),

            html.Hr(),

            dbc.Card([
                dbc.CardBody([
                    html.H4("Impact Factor vs. Total Citations", className="card-title"),
                    dcc.Graph(id='scatter-impact-chart')
                ])
            ], className="mb-4"),

            dbc.Accordion([
                dbc.AccordionItem([
                    html.Div(id='impact-table')
                ], title="View Detailed Top Publications"),
            ], start_collapsed=True),

        # Tooltips
        dbc.Tooltip("Average journal impact factor for top 5 post-award publications.", target="tooltip-avg-impact", placement="top"),
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
            dcc.Dropdown(
                options=[{'label': sci, 'value': sci} for sci in scientists],
                id='scientist-dropdown',
                placeholder='Select a Scientist'
            ),
            html.Div(id='scientist-output')
        ])

    else:
        total_funding = funding_df['Total Federal Funding (NIH only) Dollars Secured (Post-Damon Runyon Award)'].sum()
        total_awards = awards_df.shape[0]
        return dbc.Container([
            html.H2("Overview"),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4("Total NIH Funding"),
                    html.H2(f"${total_funding:,.0f}")
                ]), color="primary", inverse=True)),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4("Total Awards"),
                    html.H2(f"{total_awards}")
                ]), color="info", inverse=True)),
            ])
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
        df = publications_impact_df[publications_impact_df['Scientist Name'] == selected_scientist]

    total_pubs = df['Total Pubs'].sum()
    avg_pubs_year = round(df['Pubs Per Year'].mean(), 2)

    if df['% of pubs in Top 10%'].dtype == 'O':
        pct_values = df['% of pubs in Top 10%'].str.replace('%', '').astype(float)
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

    return (total_pubs, avg_pubs_year, top10_pct, avg_rcr,
            charts['top10-chart'], charts['pubs-per-year-chart'],
            charts['total-pubs-chart'], charts['weighted-rcr-chart'],
            charts['mean-rcr-chart'], charts['avg-apt-chart'],
            charts['cited-clin-chart'])

# --- Publications Impact Section Callback ---
# Add this inside your `update_impact_section` callback to upgrade the impact section as discussed
# Replace the current body of update_impact_section with this:
scientist_colors = {
    "Omar Abdel-Wahab, MD": "#636EFA",
    "Catherine J. Wu, MD": "#EF553B",
    "Nathanael S. Gray, PhD": "#00CC96",
    "Feng Zhang, PhD": "#AB63FA"
}

@app.callback(
    [Output('avg-impact', 'children'),
     Output('avg-impact-chart', 'figure'),
     Output('scatter-impact-chart', 'figure'),
     Output('impact-table', 'children')],
    [Input('impact-scientist-dropdown', 'value'),
     Input('if-threshold-slider', 'value')]
)
def update_impact_section(selected_scientist, if_threshold):
    if selected_scientist == 'All':
        df = publications_impact_df.dropna(subset=["Scientist", "Impact Factor", "Total Citations"])
    else:
        df = publications_impact_df[(publications_impact_df['Scientist'] == selected_scientist)]

    # Apply the Impact Factor threshold to ALL filtered data
    df = df[df['Impact Factor'] >= if_threshold]

    # Add the Impact Badge column to ALL data
    def get_badge(row):
        badges = []
        if row['Impact Factor'] > 25:
            badges.append('🔥 High IF')
        if row['Total Citations'] > 500:
            badges.append('📈 Highly Cited')
        return " | ".join(badges)

    df['Impact Badge'] = df.apply(get_badge, axis=1)

    # KPI Metrics
    total_pubs = len(df)
    avg_if = round(df['Impact Factor'].mean(), 2)
    most_cited_row = df.loc[df['Total Citations'].idxmax()]
    most_cited_count = int(most_cited_row['Total Citations'])

    # Bar Chart: Top 10 by Impact Factor
    # Top 10 Publications by Impact Factor with Rank Labels
    top10_df = df.sort_values(by='Impact Factor', ascending=False).head(10).copy()
    rank_emojis = ['🥇 1', '🥈 2', '🥉 3'] + [f"{i+1}" for i in range(3, 10)]
    top10_df['Rank Label'] = rank_emojis

    bar_fig = px.bar(
        top10_df,
        x='Impact Factor',
        y='Rank Label',
        color='Scientist',
        orientation='h',
        title='Top 10 Publications by Impact Factor',
        hover_data=['Title', 'Journal', 'Total Citations']
    )

    # Adjust the layout AFTER the figure is created
    bar_fig.update_yaxes(tickangle=0)
    bar_fig.update_layout(
        height=600,
        margin=dict(l=300, r=20, t=60, b=40),
        yaxis=dict(
            tickfont=dict(size=11),
            automargin=True
        )
    )
    # Scatter Plot: Impact Factor vs Citations
    scatter_fig = px.scatter(
        df,
        x='Impact Factor',
        y='Total Citations',
        color='Scientist',
        hover_data=['Title', 'Journal'],
        title='Impact Factor vs. Total Citations'
    )

    # Interactive Table
    table = dash_table.DataTable(
    data=df[['Scientist', 'Title', 'Journal', 'Impact Factor', 'Total Citations', 'Impact Badge']].to_dict('records'),
    columns=[
        {"name": "Scientist", "id": "Scientist"},
        {"name": "Title", "id": "Title"},
        {"name": "Journal", "id": "Journal"},
        {"name": "Impact Factor", "id": "Impact Factor"},
        {"name": "Total Citations", "id": "Total Citations"},
        {"name": "Impact Badge", "id": "Impact Badge"}
    ],
    style_table={'overflowX': 'auto'},
    style_cell={
        'textAlign': 'left',
        'padding': '5px',
        'minWidth': '100px',
        'whiteSpace': 'normal'
    },
    style_header={
        'backgroundColor': '#4c00b0',
        'color': 'white',
        'fontWeight': 'bold'
    },
    style_data_conditional=[
        {
            'if': {'filter_query': f'{{Scientist}} = "{sci}"'},
            'backgroundColor': color,
            'color': 'white'
        } for sci, color in scientist_colors.items()
    ],
    page_size=10
)
    kpi_display = f"Total Pubs: {total_pubs} | Avg IF: {avg_if} | Most Cited: {most_cited_count}"
    return kpi_display, bar_fig, scatter_fig, table

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
