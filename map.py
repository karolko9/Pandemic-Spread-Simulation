from dash import Dash, dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px

app = Dash(__name__)

# Dane początkowe
data = pd.DataFrame({
    'city': ['Berlin', 'Paris', 'Madrid', 'Warsaw', 'Rome'],
    'latitude': [52.52, 48.86, 40.42, 52.23, 41.89],
    'longitude': [13.405, 2.352, -3.703, 21.012, 12.511],
    'population': [3769000, 2148000, 3266000, 1794000, 2873000]
})

# Layout aplikacji
app.layout = html.Div([
    # Przechowywanie widoku mapy
    dcc.Store(id='map-view-store', data={'center': {'lat': 50, 'lon': 10}, 'zoom': 1}),

    # Mapa
    dcc.Graph(
        id='map',
        style={'height': '100vh', 'width': '100%'},
        config={'scrollZoom': True},
    ),
    # Przycisk
    html.Button(
        'Aktualizuj',
        id='update-button',
        n_clicks=0,
        style={
            'position': 'fixed',
            'top': '20px',
            'right': '20px',
            'z-index': '1000',
            'padding': '10px 20px',
            'font-size': '16px',
            'background-color': '#007bff',
            'color': 'white',
            'border': 'none',
            'border-radius': '5px',
            'cursor': 'pointer'
        }
    )
])


# Callback do zapisywania widoku mapy
@app.callback(
    Output('map-view-store', 'data'),
    [Input('map', 'relayoutData')],
    [State('map-view-store', 'data')]
)
def save_map_view(relayout_data, current_view):
    if relayout_data:
        # Sprawdź, czy istnieją dane dotyczące centrum mapy
        if 'geo.center.lon' in relayout_data and 'geo.center.lat' in relayout_data:
            current_view['center'] = {
                'lat': relayout_data['geo.center.lat'],
                'lon': relayout_data['geo.center.lon']
            }
        # Sprawdź, czy istnieją dane dotyczące zoomu
        if 'geo.projection.scale' in relayout_data:
            current_view['zoom'] = relayout_data['geo.projection.scale']
    return current_view


# Callback do aktualizacji mapy
@app.callback(
    Output('map', 'figure'),
    [Input('update-button', 'n_clicks')],
    [State('map-view-store', 'data')]
)
def update_map(n_clicks, map_view):
    # Zwiększenie populacji
    data['population'] = data['population'] + n_clicks * 10000

    # Tworzenie figury z zachowaniem widoku
    fig = px.scatter_geo(
        data,
        lat='latitude',
        lon='longitude',
        text='city',
        size='population',
        title='Populacja miast w Europie (Dynamiczna)',
        projection='natural earth'
    )
    fig.update_geos(center=map_view['center'], projection_scale=map_view['zoom'])
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
