import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
from datetime import datetime, timedelta
import dash_daq as daq  # For icons

# Sample Inventory Data (Hardcoded)
inventory = pd.DataFrame({
    "item": ["rice", "wheat", "pulses", "sugar"],
    "stock": [100, 150, 60, 40],
    "consumption_rate": [0.5, 0.7, 0.6, 0.2],
    "threshold": [20, 30, 10, 10],
    "last_replenished": [None, None, None, None]
})

# Function to forecast ration required for N days
def forecast_ration(n_days, n_people):
    inventory["required_ration"] = inventory["consumption_rate"] * n_days * n_people
    inventory["sufficient_stock"] = inventory["stock"] >= inventory["required_ration"]
    return inventory[["item", "stock", "required_ration", "sufficient_stock"]]

# Function to simulate consumption for N people over multiple days
def simulate_consumption(n_people, n_days):
    simulation_log = []
    for day in range(1, n_days + 1):
        day_log = {"day": day}
        for idx, row in inventory.iterrows():
            daily_consumption = row['consumption_rate'] * n_people
            adjusted_consumption = min(daily_consumption, row['stock'])
            inventory.at[idx, 'stock'] -= adjusted_consumption
            day_log[row['item']] = inventory.at[idx, 'stock']
        simulation_log.append(day_log)
        if any(inventory["stock"] <= 0):
            break
    return pd.DataFrame(simulation_log)

# Function to forecast depletion dates
def forecast_depletion():
    today = datetime.now()
    depletion_forecast = []
    for idx, row in inventory.iterrows():
        predicted_consumption = row['consumption_rate']
        depletion_time = row['stock'] / predicted_consumption if predicted_consumption else float('inf')
        depletion_date = today + timedelta(days=depletion_time)
        depletion_forecast.append({"item": row['item'], "depletion_date": depletion_date.strftime('%Y-%m-%d')})
    return pd.DataFrame(depletion_forecast)

# Dash App Layout and Callbacks
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Inventory Management Dashboard"

app.layout = html.Div([ 
    html.Div([
        html.H1("Inventory Management Dashboard", style={
            'textAlign': 'center', 'fontSize': '2.5em', 'color': '#ffffff', 'marginBottom': '20px',
            'fontFamily': 'Roboto, sans-serif', 'fontWeight': '700'}),
        dcc.Tabs([ 
            dcc.Tab(label="Forecast Ration", children=[ 
                html.Div([
                    html.Div("Instructions: This section allows you to forecast the amount of ration needed for N days and N people. Enter the values to view the required stock for each item.", style={
                        'fontSize': '1em', 'color': '#ffffff', 'marginBottom': '20px', 'fontFamily': 'Roboto, sans-serif'}),
                    html.Label("Number of Days:", style={'fontSize': '1em', 'color': '#ffffff', 'marginRight': '10px'}),
                    dcc.Input(id="forecast_days", type="number", min=1, value=7, style={
                        'width': '200px', 'padding': '10px', 'margin': '10px 0', 'border': '1px solid #ccc', 'borderRadius': '4px'}),
                    html.Label("Number of People:", style={'fontSize': '1em', 'color': '#ffffff', 'marginRight': '10px'}),
                    dcc.Input(id="forecast_people", type="number", min=1, value=10, style={
                        'width': '200px', 'padding': '10px', 'margin': '10px 0', 'border': '1px solid #ccc', 'borderRadius': '4px'}),
                    html.Button("Forecast", id="forecast_button", n_clicks=0, style={
                        'backgroundColor': '#4CAF50', 'color': 'white', 'border': 'none', 'padding': '12px 20px', 
                        'marginTop': '10px', 'borderRadius': '4px', 'cursor': 'pointer'}),
                    html.Div(id="forecast_output", style={'marginTop': '20px'})
                ], style={'padding': '20px', 'backgroundColor': '#2c2c2c'})
            ]),
            dcc.Tab(label="Simulate Consumption", children=[ 
                html.Div([
                    html.Div("Instructions: Simulate how the stock is consumed over multiple days for a specified number of people.", style={
                        'fontSize': '1em', 'color': '#ffffff', 'marginBottom': '20px', 'fontFamily': 'Roboto, sans-serif'}),
                    html.Label("Number of People:", style={'fontSize': '1em', 'color': '#ffffff', 'marginRight': '10px'}),
                    dcc.Input(id="simulate_people", type="number", min=1, value=10, style={
                        'width': '200px', 'padding': '10px', 'margin': '10px 0', 'border': '1px solid #ccc', 'borderRadius': '4px'}),
                    html.Label("Number of Days:", style={'fontSize': '1em', 'color': '#ffffff', 'marginRight': '10px'}),
                    dcc.Input(id="simulate_days", type="number", min=1, value=7, style={
                        'width': '200px', 'padding': '10px', 'margin': '10px 0', 'border': '1px solid #ccc', 'borderRadius': '4px'}),
                    html.Button("Simulate", id="simulate_button", n_clicks=0, style={
                        'backgroundColor': '#4CAF50', 'color': 'white', 'border': 'none', 'padding': '12px 20px', 
                        'marginTop': '10px', 'borderRadius': '4px', 'cursor': 'pointer'}),
                    html.Div(id="simulate_output", style={'marginTop': '20px'})
                ], style={'padding': '20px', 'backgroundColor': '#2c2c2c'})
            ]),
            dcc.Tab(label="Forecast Depletion", children=[ 
                html.Div([
                    html.Div("Instructions: This section uses historical consumption rates to predict when your stock will be depleted.", style={
                        'fontSize': '1em', 'color': '#ffffff', 'marginBottom': '20px', 'fontFamily': 'Roboto, sans-serif'}),
                    html.Button("Forecast Depletion", id="depletion_button", n_clicks=0, style={
                        'backgroundColor': '#4CAF50', 'color': 'white', 'border': 'none', 'padding': '12px 20px', 
                        'marginTop': '10px', 'borderRadius': '4px', 'cursor': 'pointer'}),
                    html.Div(id="depletion_output", style={'marginTop': '20px'})
                ], style={'padding': '20px', 'backgroundColor': '#2c2c2c'})
            ])
        ])
    ], style={
        'maxWidth': '1200px', 'margin': '20px auto', 'padding': '20px', 
        'backgroundColor': '#333333', 'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.1)', 'borderRadius': '8px'
    })
])

# Callbacks
@app.callback(
    Output("forecast_output", "children"),
    Input("forecast_button", "n_clicks"),
    State("forecast_days", "value"),
    State("forecast_people", "value")
)
def update_forecast(n_clicks, n_days, n_people):
    if n_clicks > 0:
        forecast = forecast_ration(n_days, n_people)
        return html.Div([
            html.H4("Forecast Results:", style={'fontSize': '1.2em', 'color': '#4CAF50', 'marginBottom': '10px'}),
            dash.dash_table.DataTable(
                data=forecast.to_dict("records"),
                columns=[{"name": i, "id": i} for i in forecast.columns],
                style_table={"overflowX": "auto", 'backgroundColor': '#f4f4f4', 'color': '#333'}
            )
        ])

@app.callback(
    Output("simulate_output", "children"),
    Input("simulate_button", "n_clicks"),
    State("simulate_people", "value"),
    State("simulate_days", "value")
)
def update_simulation(n_clicks, n_people, n_days):
    if n_clicks > 0:
        simulation = simulate_consumption(n_people, n_days)
        return html.Div([
            html.H4("Simulation Results:", style={'fontSize': '1.2em', 'color': '#4CAF50', 'marginBottom': '10px'}),
            dash.dash_table.DataTable(
                data=simulation.to_dict("records"),
                columns=[{"name": i, "id": i} for i in simulation.columns],
                style_table={"overflowX": "auto", 'backgroundColor': '#f4f4f4', 'color': '#333'}
            )
        ])

@app.callback(
    Output("depletion_output", "children"),
    Input("depletion_button", "n_clicks")
)
def update_depletion(n_clicks):
    if n_clicks > 0:
        depletion = forecast_depletion()
        return html.Div([
            html.H4("Depletion Forecast:", style={'fontSize': '1.2em', 'color': '#4CAF50', 'marginBottom': '10px'}),
            dash.dash_table.DataTable(
                data=depletion.to_dict("records"),
                columns=[{"name": i, "id": i} for i in depletion.columns],
                style_table={"overflowX": "auto", 'backgroundColor': '#f4f4f4', 'color': '#333'}
            )
        ])

if __name__ == "__main__":
    app.run_server(debug=True)
