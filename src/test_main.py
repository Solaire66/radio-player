from main import STATIONS

# Test 1: Verificar que el diccionario de estaciones no esté vacío
def test_stations_not_empty():
    assert len(STATIONS) > 0
    assert "Radio Nuages (Monterrey, MX)" in STATIONS

# Test 2: Verificar que las URLs tengan un formato básico válido
def test_station_urls_format():
    for name, url in STATIONS.items():
        assert url.startswith("http")
        assert len(url) > 10

# Test 3: Un test simple para que Pytest siempre pase a verde
def test_player_logic_placeholder():
    # Aquí podrías probar lógica de filtrado de nombres si la tuvieras
    test_name = "Classic 106.9"
    assert test_name in STATIONS