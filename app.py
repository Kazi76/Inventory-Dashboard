import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
from datetime import datetime, timedelta
import dash.daq as daq  # For icons

# Sample Inventory Data (Hardcoded)
inventory = pd.DataFrame({
    "item": ["rice", "wheat", "pulses", "sugar"],
    "stock": [100, 150, 60, 40],
    "consumption_rate": [0.5, 0.7, 0.6, 0.2],
    "threshold": [20, 30, 10, 10],
    "last_replenished": [datetime.now()] * 4  # Replace None with current date
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
app = dash.Dash(__name__)
server = app.server  # Expose Flask server for Gunicorn compatibility
app.title = "Inventory Management Dashboard"

app.layout = html.Div([
    html.Div([
        html.H1("Inventory Management Dashboard", style={
            'textAlign': 'center', 'fontSize': '2.5em', 'color': '#ffffff', 'marginBottom': '20px',
            'fontFamily': 'Roboto, sans-serif', 'fontWeight': '700'}),
        dcc.Tabs([
            dcc.Tab(label="Forecast Ration", children=[
                html.Div([
                    html.P("Instructions: Enter values to forecast the stock required.", style={
                        'fontSize': '1em', 'color': '#ffffff', 'marginBottom': '20px'}),
                    html.Label("Number of Days:", style={'color': '#ffffff'}),
                    dcc.Input(id="forecast_days", type="number", min=1, value=7),
                    html.Label("Number of People:", style={'color': '#ffffff'}),
                    dcc.Input(id="forecast_people", type="number", min=1, value=10),
                    html.Button("Forecast", id="forecast_button", n_clicks=0),
                    html.Div(id="forecast_output", style={'marginTop': '20px'})
                ], style={'padding': '20px'})
            ]),
            dcc.Tab(label="Simulate Consumption", children=[
                html.Div([
                    html.P("Simulate stock consumption over time.", style={
                        'fontSize': '1em', 'color': '#ffffff'}),
                    html.Label("Number of People:", style={'color': '#ffffff'}),
                    dcc.Input(id="simulate_people", type="number", min=1, value=10),
                    html.Label("Number of Days:", style={'color': '#ffffff'}),
                    dcc.Input(id="simulate_days", type="number", min=1, value=7),
                    html.Button("Simulate", id="simulate_button", n_clicks=0),
                    html.Div(id="simulate_output", style={'marginTop': '20px'})
                ])
            ]),
            dcc.Tab(label="Forecast Depletion", children=[
                html.Div([
                    html.P("Forecast when your stock will be depleted.", style={
                        'fontSize': '1em', 'color': '#ffffff'}),
                    html.Button("Forecast Depletion", id="depletion_button", n_clicks=0),
                    html.Div(id="depletion_output", style={'marginTop': '20px'})
                ])
            ])
        ])
    ], style={'padding': '20px', 'backgroundColor': '#333333'})
])

@app.callback(
    Output("forecast_output", "children"),
    Input("forecast_button", "n_clicks"),
    State("forecast_days", "value"),
    State("forecast_people", "value")
)
def update_forecast(n_clicks, n_days, n_people):
    if n_clicks > 0 and n_days and n_people:
        forecast = forecast_ration(n_days, n_people)
        return html.Div([
            html.H4("Forecast Results:", style={'color': '#4CAF50'}),
            dash.dash_table.DataTable(
                data=forecast.to_dict("records"),
                columns=[{"name": i, "id": i} for i in forecast.columns]
            )
        ])

@app.callback(
    Output("simulate_output", "children"),
    Input("simulate_button", "n_clicks"),
    State("simulate_people", "value"),
    State("simulate_days", "value")
)
def update_simulation(n_clicks, n_people, n_days):
    if n_clicks > 0 and n_people and n_days:
        simulation = simulate_consumption(n_people, n_days)
        return html.Div([
            html.H4("Simulation Results:", style={'color': '#4CAF50'}),
            dash.dash_table.DataTable(
                data=simulation.to_dict("records"),
                columns=[{"name": i, "id": i} for i in simulation.columns]
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
            html.H4("Depletion Forecast:", style={'color': '#4CAF50'}),
            dash.dash_table.DataTable(
                data=depletion.to_dict("records"),
                columns=[{"name": i, "id": i} for i in depletion.columns]
            )
        ])

if __name__ == "__main__":
    app.run_server(debug=False)
