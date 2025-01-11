import dash
import dash_leaflet as dl
from dash import html
import geopandas as gpd

gdf_low_res = gpd.read_file('kontur_population_20231101_r4.gpkg')

# Zakładamy, że dane są w GeoDataFrame gdf_low_res
gdf = gdf_low_res[gdf_low_res['population'] > 100].copy()

# Konwertujemy GeoDataFrame na GeoJSON
geojson_data = gdf.to_json()

app = dash.Dash(__name__)

# Warstwa GeoJSON z danymi
geojson_layer = dl.GeoJSON(
    data=gdf.__geo_interface__,  # Używamy GeoJSON z GeoDataFrame
    id="geojson",
    zoomToBounds=True
)

# Layout aplikacji
app.layout = html.Div([
    html.H1("Mapa Heksagonalna Populacji"),
    dl.Map([
        dl.TileLayer(),  # Warstwa bazowa (OpenStreetMap)
        geojson_layer   # Dodanie GeoJSON
    ], style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
])

# Uruchomienie aplikacji
if __name__ == '__main__':
    app.run_server(debug=True)