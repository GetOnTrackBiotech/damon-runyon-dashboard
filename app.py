from dash import dash_table
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.LUX,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css",
    "https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"  
])

app.title = "Damon Runyon Dashboard | SOPHIA"

# Load Data
excel_file = 'assets/damon_runyon_data_CLEAN.xlsx'
funding_df = pd.read_excel(excel_file, sheet_name='NIH & Grant Funding Impact')
awards_df = pd.read_excel(excel_file, sheet_name='Awards & Recognitions')
publications_df = pd.read_excel(excel_file, sheet_name='Publications (ICite #)')
publications_impact_df = pd.read_excel(excel_file, sheet_name='Publications Impact')

scientists = funding_df[funding_df.columns[0]].dropna().unique()

# Load Overview-specific data
notable_df = pd.read_excel(excel_file, sheet_name="Companies Summary")[
    ["Scientist", "Current Academic Position", "Notable Awards", "High-Impact Publications (#)",
     "Total Funding Raised by Companies", "IPOs / Acquisitions"]
].dropna(how="all")

timeline_data = pd.read_excel(excel_file, sheet_name="NIH & Grant Funding Impact")[[
    "Scientist Name", "Award Start Date", "Time to First NIH Grant (Post-Damon Runyon Award)"
]].copy()

timeline_data["Award Start Date"] = pd.to_datetime(timeline_data["Award Start Date"], errors="coerce")
timeline_data["NIH Months"] = timeline_data["Time to First NIH Grant (Post-Damon Runyon Award)"].str.extract(r"(\d+)").astype(float)

import plotly.express as px
timeline_fig_overview = px.bar(
    timeline_data,
    x="NIH Months",
    y="Scientist Name",
    orientation="h",
    title="Time to First NIH Grant (Months)",
    labels={"NIH Months": "Months to First NIH Grant"},
    color="Scientist Name"
)
timeline_fig_overview.update_layout(height=500, margin=dict(l=100, r=40, t=50, b=50), showlegend=False)

# --- Layout Components ---
header = dbc.NavbarSimple(
    brand="Damon Runyon Metrics Dashboard",
    brand_href="/",
    color="#4c00b0",
    dark=True,
    children=[
        dbc.Switch(
            id="theme-toggle",
            label="🌙 Dark Mode",
            value=False,
            style={"marginRight": "20px", "color": "white"}
        ),
        dbc.NavItem(html.Span("Powered by SOPHIA", style={"color": "white"}))
    ]
)

sidebar = dbc.Nav(
    [
        dbc.NavLink("Overview", href="/", active="exact"),
        dbc.NavLink("Publications", href="/publications", active="exact"),
        dbc.NavLink("Publication Impact", href="/impact", active="exact"),
        dbc.NavLink("Companies & Career Timeline", href="/companies", active="exact"),
        dbc.NavLink("Awards & Recognitions", href="/awards", active="exact"),
    ],
    vertical=True,
    pills=True,
    style={"position": "fixed", "top": "70px", "left": 0, "bottom": 0,
           "width": "250px", "padding": "20px", "background-color": "#f8f9fa"}
)

content = html.Div(id="page-content", style={
    "margin-left": "270px",
    "padding": "20px",
    "overflowY": "auto",
    "height": "calc(100vh - 70px)"
})

app.layout = html.Div(
    id="main-wrapper",
    children=[
        dcc.Location(id="url"),
        header,
        sidebar,
        content
    ]
)

# --- Page Routing Callback ---
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/' or pathname == '':
        return dbc.Container([
            html.Div([
                # SECTION 1: Hero Banner
                html.Div([
                    html.H1("Impact Beyond Funding", style={"color": "#4c00b0", "fontWeight": "bold"}),
                    html.P("SOPHIA reveals the real-world reach of Damon Runyon scientists — from Damon Runyon Award to FDA breakthroughs.")
                ], style={"marginBottom": "40px"}),

                # SECTION 2 + 3 Combined: KPI Cards + Highlights Strip
                html.Div([
                    dbc.Row([
                        dbc.Col(dbc.Card(
                            dbc.CardBody([
                                html.Div([
                                    html.I(className="bi bi-award-fill", style={"fontSize": "28px", "color": "#4c00b0"}),
                                    html.H6("Received NIH Grants"),
                                    html.H2("100%"),
                                    html.Small("All funded within 3 years", className="text-muted")
                                ], className="text-center animate__animated animate__fadeInUp")
                            ]),
                            className="glass-card shadow-sm",
                            style={"height": "180px"}
                        ), md=3),

                        dbc.Col(dbc.Card(
                            dbc.CardBody([
                                html.Div([
                                    html.I(className="bi bi-building", style={"fontSize": "28px", "color": "#4c00b0"}),
                                    html.H6("Founded Companies"),
                                    html.H2("19"),
                                    html.Small("Biotech ventures launched", className="text-muted")
                                ], className="text-center animate__animated animate__fadeInUp")
                            ]),
                            className="glass-card shadow-sm",
                            style={"height": "180px"}
                        ), md=3),

                        dbc.Col(dbc.Card(
                            dbc.CardBody([
                                html.Div([
                                    html.I(className="bi bi-capsule", style={"fontSize": "28px", "color": "#4c00b0"}),
                                    html.H6("FDA-Linked Patents"),
                                    html.H2("1"),
                                    html.Small("With approved indication", className="text-muted")
                                ], className="text-center animate__animated animate__fadeInUp")
                            ]),
                            className="glass-card shadow-sm",
                            style={"height": "180px"}
                        ), md=3),

                        dbc.Col(dbc.Card(
                            dbc.CardBody([
                                html.Div([
                                    html.I(className="bi bi-person-badge-fill", style={"fontSize": "28px", "color": "#4c00b0"}),
                                    html.H6("Became PIs"),
                                    html.H2("100%"),
                                    html.Small("Now leading labs", className="text-muted")
                                ], className="text-center animate__animated animate__fadeInUp")
                            ]),
                            className="glass-card shadow-sm",
                            style={"height": "180px"}
                        ), md=3),
                    ], className="mb-2"),

                    dbc.Row([
                        dbc.Col(dbc.Card(dbc.CardBody([
                            html.Div([
                                html.H2("100%", style={"fontWeight": "bold", "color": "#4c00b0", "fontSize": "28px"}),
                                html.H6("with multiple NIH grants"),
                                html.Small("Most secured >1 grant post-award", className="text-muted")
                            ], className="d-flex flex-column align-items-center justify-content-center text-center")
                        ]), className="glass-card shadow-sm", style={"height": "180px"}), md=4),

                        dbc.Col(dbc.Card(dbc.CardBody([
                            html.Div([
                                html.H2("19", style={"fontWeight": "bold", "color": "#4c00b0", "fontSize": "28px"}),
                                html.H6("Companies Launched"),
                                html.Small("From drug dev to diagnostics", className="text-muted")
                            ], className="d-flex flex-column align-items-center justify-content-center text-center")
                        ]), className="glass-card shadow-sm", style={"height": "180px"}), md=4),

                        dbc.Col(dbc.Card(dbc.CardBody([
                            html.Div([
                                html.H2("1", style={"fontWeight": "bold", "color": "#4c00b0", "fontSize": "28px"}),
                                html.H6("FDA-Linked Patent"),
                                html.Small("Resulting in approved therapy", className="text-muted")
                            ], className="d-flex flex-column align-items-center justify-content-center text-center")
                        ]), className="glass-card shadow-sm", style={"height": "180px"}), md=4),
                    ], justify="center", className="mb-5"),
                ]),

                # SECTION 4: Timeline Chart
                html.Div([
                    dcc.Graph(figure=timeline_fig_overview)
                ], className="animate__animated animate__fadeInUp", style={"paddingTop": "30px", "paddingBottom": "40px"}),

                # SECTION 5: Notable Achievements
                html.H4("Notable Achievements"),
                dash_table.DataTable(
                    data=notable_df.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in notable_df.columns],
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "left", "padding": "6px"},
                    style_header={"fontWeight": "bold", "backgroundColor": "#f0f0f0"}
                )
            ], style={
                "padding": "40px",
                "background": "linear-gradient(180deg, #ffffff 0%, #f5f0ff 100%)"
            })
        ])

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
        companies_df = pd.read_excel(excel_file, sheet_name='Companies')
        summary_df = pd.read_excel(excel_file, sheet_name='Companies Summary')
        summary_df = summary_df.rename(columns={"Scientist Name": "Scientist"})

        return dbc.Container([
            html.H2("Companies & Career Timeline"),
            html.P("Explore company affiliations and career trajectories of Damon Runyon scientists."),

            dbc.Row([
                dbc.Col(dcc.Dropdown(
                    id="companies-scientist-dropdown",
                    options=[{"label": "All Scientists", "value": "All"}] +
                            [{"label": sci, "value": sci} for sci in sorted(companies_df['Scientist'].unique())],
                    value="All",
                    placeholder="Select a Scientist",
                    style={'margin-bottom': '10px'}
                ), width=6),

                dbc.Col(dcc.Dropdown(
                    id="color-by-dropdown",
                    options=[
                        {"label": "Company", "value": "Company"},
                        {"label": "Scientist", "value": "Scientist"},
                        {"label": "Role", "value": "Role"},
                        {"label": "Focus Area", "value": "Focus Area"}
                    ],
                    value="Company",
                    placeholder="Color By...",
                    style={'margin-bottom': '10px'}
                ), width=6),
            ], className="mb-4"),

            html.Div(id="companies-kpi-output"),
            html.Div(id="companies-gantt-output"),
            html.Div(id="companies-table-output")
        ])

    elif pathname == '/awards':
        # KPI Metrics
        total_awards = len(awards_df)
        most_awarded_scientist = awards_df['Scientist Name'].value_counts().idxmax()
        most_common_org = awards_df['Organization'].value_counts().idxmax()

        # Timeline Chart
        timeline_fig = px.scatter(
            awards_df,
            x="Year",
            y="Scientist Name",
            color="Organization",
            hover_data=["Awards", "Organization"],
            title="Awards & Recognitions Timeline"
        )
        timeline_fig.update_layout(height=500)
        
        # Bar Chart: Total Awards per Scientist
        award_counts = awards_df['Scientist Name'].value_counts().reset_index()
        award_counts.columns = ['Scientist Name', 'Award Count']

        bar_fig = px.bar(
            award_counts,
            x='Award Count',
            y='Scientist Name',
            orientation='h',
            title='Total Awards per Scientist',
            text='Award Count'
        )
        bar_fig.update_layout(height=500, margin=dict(l=100, r=20, t=60, b=40))

        return dbc.Container([
            html.H2("Awards & Recognitions"),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("Total Awards", className="card-title"),
                    html.P(f"{total_awards}", className="card-text")
                ]), style={"background-color": "#4c00b0", "color": "white", "border": "none", "height": "120px"})),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("Most Awarded Scientist", className="card-title"),
                    html.P(most_awarded_scientist, className="card-text")
                ]), style={"background-color": "#4c00b0", "color": "white", "border": "none", "height": "120px"})),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("Top Organization", className="card-title"),
                    html.P(most_common_org, className="card-text")
                ]), style={"background-color": "#4c00b0", "color": "white", "border": "none", "height": "120px"})),
            ], className="mb-4"),

            dcc.Dropdown(
                id='awards-scientist-dropdown',
                options=[{'label': 'All Scientists', 'value': 'all'}] + 
                        [{'label': s, 'value': s} for s in sorted(awards_df['Scientist Name'].unique())],
                value='all',
                placeholder="Filter by Scientist",
                style={'width': '50%', 'margin-bottom': '20px'}
            ),
            
            dcc.Graph(figure=bar_fig),
            html.Br(),
            dcc.Graph(id='awards-scatter', figure=timeline_fig),
            html.Br(),

            dash_table.DataTable(
                id='awards-table',
                columns=[{"name": i, "id": i} for i in awards_df.columns],
                data=awards_df.to_dict('records'),
                page_size=10,
                style_table={'overflowX': 'auto'},
                sort_action="native",
                filter_action="native",
                style_cell={'textAlign': 'left'}
            )
        ])
    
    else:
        return html.Div("404 Page Not Found")

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

    # Bar Chart: Top 10 by Impact Factor — ranked and labeled
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

    bar_fig.update_layout(
        height=550,
        width=1000,
        margin=dict(l=150, r=20, t=60, b=40),
        yaxis=dict(
            title="Rank (1 = Highest Impact Factor)",
            tickfont=dict(size=11),
            automargin=True
        )
    )

    bar_fig.add_annotation(
        text="Ranked by Impact Factor (1 = highest)",
        xref="paper", yref="paper",
        x=1, y=-0.2,
        showarrow=False,
        font=dict(size=12),
        align="right"
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

@app.callback(
    [Output('companies-kpi-output', 'children'),
     Output('companies-gantt-output', 'children'),
     Output('companies-table-output', 'children')],
    [Input('companies-scientist-dropdown', 'value'),
     Input('color-by-dropdown', 'value')]
)
def update_companies_section(selected_sci, color_by):
    companies_df = pd.read_excel(excel_file, sheet_name='Companies')
    summary_df = pd.read_excel(excel_file, sheet_name='Companies Summary')
    summary_df = summary_df.rename(columns={"Scientist Name": "Scientist"})

    # Clean & convert data
    companies_df = companies_df.dropna(subset=["Scientist", "Company", "Start Year", "End Year / Current"])
    companies_df["End Year"] = companies_df["End Year / Current"].replace("Current", pd.Timestamp.now().year)
    companies_df["Start Year"] = pd.to_numeric(companies_df["Start Year"], errors='coerce')
    companies_df["End Year"] = pd.to_numeric(companies_df["End Year"], errors='coerce')
    companies_df["Start Year"] = pd.to_datetime(companies_df["Start Year"], format="%Y", errors='coerce')
    companies_df["End Year"] = pd.to_datetime(companies_df["End Year"], format="%Y", errors='coerce')
    companies_df = companies_df.dropna(subset=["Start Year", "End Year"])

    # Filter
    if selected_sci == "All":
        filtered_df = companies_df.copy()
        filtered_summary = summary_df.copy()
        kpi = html.Div()  # No KPI cards
    else:
        filtered_df = companies_df[companies_df['Scientist'] == selected_sci]
        filtered_summary = summary_df[summary_df['Scientist'] == selected_sci]

        if filtered_summary.empty:
            kpi = html.Div("No data available.")
        else:
            row = filtered_summary.iloc[0]
            kpi = dbc.Row([
               dbc.Col(dbc.Card(
                   dbc.CardBody([
                       html.H6(html.Span("Companies Founded", title="Startups or co-founded companies"), className="card-title"),
                       html.H4(html.Span(f"{row['Companies Founded']}", title=f"{row['Companies Founded']}"))
               ]),
               style={'padding': '15px', 'textAlign': 'center', 'height': '120px'}
           ), width=3),

               dbc.Col(dbc.Card(
                   dbc.CardBody([
                       html.H6(html.Span("Advisory Roles", title="Board or scientific advisory roles"), className="card-title"),
                       html.H4(html.Span(f"{row['Advisory Roles']}", title=f"{row['Advisory Roles']}"))
               ]),
               style={'padding': '15px', 'textAlign': 'center', 'height': '120px'}
           ), width=3),

               dbc.Col(dbc.Card(
                   dbc.CardBody([
                       html.H6(html.Span("IPOs / Acquisitions", title="Public offerings or M&A outcomes"), className="card-title"),
                       html.H4(html.Span(f"{row['IPOs / Acquisitions']}", title=f"{row['IPOs / Acquisitions']}"))
               ]),
               style={'padding': '15px', 'textAlign': 'center', 'height': '120px'}
           ), width=3),

               dbc.Col(dbc.Card(
                   dbc.CardBody([
                       html.H6(html.Span("FDA-Linked Patents", title="Patents connected to FDA-approved products"), className="card-title"),
                       html.H4(html.Span(f"{row['FDA-Linked Patents']}", title=f"{row['FDA-Linked Patents']}"))
               ]),
               style={'padding': '15px', 'textAlign': 'center', 'height': '120px'}
           ), width=3),
       ], className="mb-4")

    # Gantt chart
    gantt_fig = px.timeline(
        filtered_df,
        x_start="Start Year",
        x_end="End Year",
        y="Company" if selected_sci != "All" else "Scientist",
        color=color_by,
        hover_data=["Scientist", "Company", "Role", "Focus Area"],
        title=f"Career Timeline for {'All Scientists' if selected_sci == 'All' else selected_sci}"
    )
    gantt_fig.update_yaxes(autorange="reversed")
    gantt_fig.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=40, b=40),
        xaxis_title="Year",
        yaxis_title=None
    )
    gantt = dcc.Graph(figure=gantt_fig)

    # Table
    if selected_sci == "All":
        table_data = summary_df[["Scientist", "Current Academic Position", "IPOs / Acquisitions",
                                 "Clinical Trials Linked", "FDA-Approved Patents"]]
    else:
        table_data = filtered_df[["Company", "Role", "Focus Area", "Start Year", "End Year"]]

    if "Start Year" in table_data.columns:
        table_data["Start Year"] = pd.to_datetime(table_data["Start Year"]).dt.year
    if "End Year" in table_data.columns:
        table_data["End Year"] = pd.to_datetime(table_data["End Year"]).dt.year

    table = dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in table_data.columns],
        data=table_data.to_dict("records"),
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={
            'backgroundColor': '#4c00b0',
            'color': 'white',
            'fontWeight': 'bold'
        },
        page_size=10
    )

    return kpi, gantt, table

@app.callback(
    Output('awards-scatter', 'figure'),
    Input('awards-scientist-dropdown', 'value')
)
def update_awards_scatter(scientist):
    if scientist and scientist != 'all':
        filtered_df = awards_df[awards_df['Scientist Name'] == scientist]
    else:
        filtered_df = awards_df

    fig = px.scatter(
        filtered_df,
        x="Year",
        y="Scientist Name",
        color="Organization",
        hover_data=["Awards", "Organization"],
        title="Awards & Recognitions Timeline"
    )
    fig.update_layout(
        height=500,
        showlegend=False
    )
    return fig
@app.callback(
    Output('awards-table', 'data'),
    Input('awards-scientist-dropdown', 'value')
)
def update_awards_table(scientist):
    if scientist and scientist != 'all':
        return awards_df[awards_df['Scientist Name'] == scientist].to_dict('records')
    return awards_df.to_dict('records')

@app.callback(
    Output("main-wrapper", "className"),
    Input("theme-toggle", "value")
)
def toggle_theme(dark_mode):
    return "dark-mode" if dark_mode else "light-mode"

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
