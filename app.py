import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Load Data
excel_file = 'assets/damon_runyon_data.xlsx'
funding_df = pd.read_excel(excel_file, sheet_name='NIH & Grant Funding Impact', header=4)

awards_df = pd.read_excel(excel_file, sheet_name='Awards & Recognitions')

scientists = funding_df[funding_df.columns[0]].dropna().unique()

# Initialize App
app = dash.Dash(__name__)
app.title = "Damon Runyon Metrics Dashboard"

# Sidebar Style
sidebar = html.Div(
    [
        html.H2("Menu", style={'color': '#4c00b0'}),
        dcc.Link('Overview', href='/', style={'display': 'block', 'margin': '10px 0'}),
        dcc.Link('NIH Funding', href='/funding', style={'display': 'block', 'margin': '10px 0'}),
        dcc.Link('Scientist Drill-Down', href='/drilldown', style={'display': 'block', 'margin': '10px 0'}),
    ],
    style={'width': '20%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '20px'}
)

# Content Placeholder
content = html.Div(id='page-content', style={'width': '75%', 'display': 'inline-block', 'padding': '20px'})

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    sidebar,
    content
])
# Define Pages
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/funding':
        fig = px.bar(funding_df, x='Scientist Name', y='Total Federal Funding (NIH only) Dollars Secured', 
                     title='Total NIH Funding by Scientist', color='Scientist Name')
        return html.Div([
            html.H3('NIH Funding Overview', style={'color': '#4c00b0'}),
            dcc.Graph(figure=fig),
            html.A('View Data', href='/assets/damon_runyon_data.xlsx', target='_blank')
        ])
    elif pathname == '/drilldown':
        return html.Div([
            html.H3('Scientist Drill-Down', style={'color': '#4c00b0'}),
            dcc.Dropdown(options=[{'label': sci, 'value': sci} for sci in scientists],
                         id='scientist-dropdown',
                         placeholder='Select a Scientist'),
            html.Div(id='scientist-output')
        ])
    else:
        total_funding = funding_df['Total Federal Funding (NIH only) Dollars Secured'].sum()
        total_awards = awards_df.shape[0]
        return html.Div([
            html.H3('Overview', style={'color': '#4c00b0'}),
            html.P(f"Total NIH Funding Secured: ${total_funding:,.0f}"),
            html.P(f"Total Awards & Recognitions: {total_awards}")
        ])

# Drill-Down Callback
@app.callback(
    Output('scientist-output', 'children'),
    Input('scientist-dropdown', 'value')
)
def update_scientist_info(selected_scientist):
    if not selected_scientist:
        return ""
    funding_row = funding_df[funding_df['Scientist Name'] == selected_scientist]
    awards = awards_df[awards_df['Scientist Name'] == selected_scientist]['Awards'].tolist()
    return html.Div([
        html.H4(f"Details for {selected_scientist}"),
        html.P(f"Total NIH Funding: ${funding_row['Total Federal Funding (NIH only) Dollars Secured'].values[0]:,.0f}"),
        html.P(f"Awards: {', '.join(awards) if awards else 'None'}")
    ])

if __name__ == '__main__':
   app.run(debug=False, host='0.0.0.0', port=10000)

