import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Damon Runyon Dashboard | SOPHIA"

# Load Data
excel_file = 'assets/damon_runyon_data_CLEAN.xlsx'
publications_df = pd.read_excel(excel_file, sheet_name='Publications (ICite #)')

# Scientist List
scientists = ['All'] + publications_df['Scientist Name'].dropna().unique().tolist()

# KPI Card Component
def kpi_card(title, id_value, color):
    return dbc.Col(dbc.Card(dbc.CardBody([
        html.H5(title),
        html.H3(id=id_value)
    ]), color=color, inverse=True))

# Accordion Section Component
def accordion_section(title, description, chart_id):
    return dbc.AccordionItem([
        html.P(description),
        dcc.Graph(id=chart_id)
    ], title=title)

# Layout
publications_layout = dbc.Container([
    html.H2("Publications Overview"),
    dcc.Dropdown(
        id='pubs-scientist-dropdown',
        options=[{'label': sci, 'value': sci} for sci in scientists],
        value='All',
        style={'width': '50%', 'margin-bottom': '20px'}
    ),
    dbc.Row([
        kpi_card("Total Publications", 'total-pubs', "primary"),
        kpi_card("Avg Pubs Per Year", 'avg-pubs-year', "info"),
        kpi_card("% Pubs in Top 10%", 'top10-pubs', "success"),
        kpi_card("Avg Weighted RCR", 'avg-rcr', "warning"),
    ], className="mb-4"),

    dbc.Accordion([
        accordion_section("Count of Publications in Top 10%", 
                          "This chart shows how many publications per scientist rank in the top 10% by citations.", 
                          'chart-top10-count'),

        accordion_section("Publications Per Year & Total Publications", 
                          "Annual publication trends alongside total output.", 
                          'chart-pubs-year-total'),

        accordion_section("Weighted RCR & Mean RCR", 
                          "Research Citation Ratios reflecting influence and impact.", 
                          'chart-rcr'),

        accordion_section("Average APT & Clinical Citations", 
                          "Average time to citation (APT) and frequency of clinical citations.", 
                          'chart-apt-clin'),
    ], start_collapsed=True)
])

# Callbacks
@app.callback(
    [Output('total-pubs', 'children'),
     Output('avg-pubs-year', 'children'),
     Output('top10-pubs', 'children'),
     Output('avg-rcr', 'children'),
     Output('chart-top10-count', 'figure'),
     Output('chart-pubs-year-total', 'figure'),
     Output('chart-rcr', 'figure'),
     Output('chart-apt-clin', 'figure')],
    [Input('pubs-scientist-dropdown', 'value')]
)
def update_publications(selected_scientist):
    if selected_scientist == 'All':
        df = publications_df.copy()
    else:
        df = publications_df[publications_df['Scientist Name'] == selected_scientist]

    total_pubs = int(df['Total Pubs'].sum())
    avg_pubs_year = round(df['Pubs Per Year'].mean(), 2)

    if df['% of pubs in Top 10%'].dtype == 'O':
        pct_values = df['% of pubs in Top 10%'].str.replace('%','').astype(float)
    else:
        pct_values = df['% of pubs in Top 10%']
    top10_pct = f"{round(pct_values.mean(), 1)}%"

    avg_rcr = round(df['Weighted RCR'].mean(), 2)

    # Charts
    fig_top10 = px.bar(df, x='Scientist Name', y='Count of Pubs in top 10%', color='Scientist Name', title='Top 10% Publications Count')

    fig_pubs = px.bar(df, x='Scientist Name', y=['Pubs Per Year', 'Total Pubs'], barmode='group', title='Publications Per Year & Total')

    fig_rcr = px.bar(df, x='Scientist Name', y=['Weighted RCR', 'Mean RCR'], barmode='group', title='RCR Metrics')

    fig_apt = px.bar(df, x='Scientist Name', y=['Avg APT', 'Cited by Clin'], barmode='group', title='APT & Clinical Citations')

    return total_pubs, avg_pubs_year, top10_pct, avg_rcr, fig_top10, fig_pubs, fig_rcr, fig_apt

# Run the app
if __name__ == '__main__':
    app.layout = publications_layout
    app.run(debug=False, host='0.0.0.0', port=10000)
