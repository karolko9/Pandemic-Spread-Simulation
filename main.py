import networkx as nx
import pygame
import random
import cv2
import numpy as np

# Parametry okna pygame
WIDTH, HEIGHT = 800, 600
NODE_RADIUS = 10
EDGE_COLOR = (200, 200, 200)
NODE_COLOR = (84, 217, 61)
TEXT_COLOR = (255, 255, 255)
BACKGROUND_COLOR = (30, 30, 30)

RED_THRESHOLD = 217
GREEN_THRESHOLD = 61

TIME_STEP = 0.01  # Krok czasowy w symulacji
IMMUNE_TIME_THRESHOLD = 200  # Po jakim czasie ludzie tracą odporność

# Funkcja do generowania losowych współczynników SEIR
def random_seir_params():
    beta = random.uniform(0.1, 0.3)  # Współczynnik transmisji
    sigma = random.uniform(0.05, 0.2)  # Współczynnik inkubacji
    gamma = random.uniform(0.01, 0.1)  # Współczynnik wyzdrowienia
    delta = random.uniform(0.001, 0.05)  # Współczynnik umieralności
    return beta, sigma, gamma, delta

# Funkcja do generowania początkowych wartości SEIR
def random_seir():
    S = random.uniform(0.5, 0.7)
    E = random.uniform(0.0, 0.3)
    I = 1.0 - S - E
    R = 0
    D = 0  # Początkowo brak osób zmarłych
    immune_time = 0  # Czas utraty odporności
    return S, E, I, R, D, immune_time

# Tworzenie grafu
G = nx.Graph()

# Dodajemy wierzchołki
for i in range(10):
    pos = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
    seir = 1, 0, 0, 0, 0, 0  # Parametry SEIR + D + immune_time
    pop_size = random.uniform(500, 1000)
    seir_params = random_seir_params()
    G.add_node(i, pos=pos, seir=seir, pop_size=pop_size, seir_params=seir_params)

# Dodajemy krawędzie
for _ in range(15):
    u = random.choice(list(G.nodes))
    v = random.choice(list(G.nodes))
    if u != v:
        G.add_edge(u, v, infection_occurred=False)

# Wybieramy losowy wierzchołek, który będzie początkowo dotknięty chorobą
patient_zero = random.choice(list(G.nodes))
S, E, I, R, D, immune_time = 0.6, 0.2, 0.2, 0.0, 0.0, 0.0  # Inicjalizujemy tylko stan I i E
G.nodes[patient_zero]['seir'] = (S, E, I, R, D, immune_time)

# Funkcja rysowania grafu w pygame
# Funkcja rysowania grafu w pygame
def draw_graph(screen, graph):
    # Rysowanie krawędzi
    for edge in graph.edges:
        u, v = edge
        pos_u = graph.nodes[u]['pos']
        pos_v = graph.nodes[v]['pos']

        # Sprawdzamy, czy którykolwiek z wierzchołków ma zarażoną osobę (I > 0)
        S_u, E_u, I_u, R_u, D_u, immune_time_u = graph.nodes[u]['seir']
        S_v, E_v, I_v, R_v, D_v, immune_time_v = graph.nodes[v]['seir']

        # Jeśli którykolwiek wierzchołek ma osobę zarażoną, krawędź ma kolor żółty
        if I_u > 0 or I_v > 0:
            edge_color = (255, 255, 0)  # Kolor żółty
        else:
            edge_color = EDGE_COLOR  # Domyślny kolor krawędzi

        if G.get_edge_data(u, v)['infection_occurred']:
            edge_color = (255, 0, 0)

        pygame.draw.line(screen, edge_color, pos_u, pos_v, 2)

    # Rysowanie wierzchołków
    for node in graph.nodes:
        pos = graph.nodes[node]['pos']

        # Pobranie wartości SEIR dla wierzchołka
        pop_size = graph.nodes[node]['pop_size']
        seir = graph.nodes[node]['seir']
        S, E, I, R, D, immune_time = tuple([int(p * pop_size) for p in seir])

        # Obliczanie sumy zarażonych, martwych i wyzdrowiałych
        total_infected = I + D + R
        max_possible = pop_size  # Maksymalna liczba osób w wierzchołku

        # Obliczamy stopień czerwieni (na podstawie zarażonych, martwych i wyzdrowiałych)
        red_intensity = min(total_infected / max_possible, 1.0)  # Maksymalna wartość czerwonego to 1.0

        # Kolor wierzchołka: im więcej zarażonych, tym bardziej czerwony
        red = int(255 * red_intensity)
        green = int(255 * (1 - red_intensity))  # Im więcej zarażonych, tym mniej zielony
        node_color = (red, green, 0)  # Zmiana na czerwony z zielonym

        # Rysowanie wierzchołka
        pygame.draw.circle(screen, node_color, pos, NODE_RADIUS)

        # Wyświetlanie parametrów SEIR
        text = f"S:{S} E:{E} I:{I} R:{R} D:{D}"
        font = pygame.font.SysFont('Arial', 14)
        text_surface = font.render(text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(pos[0], pos[1] - NODE_RADIUS - 10))
        screen.blit(text_surface, text_rect)


def update_seir(graph):
    for node in graph.nodes:
        S, E, I, R, D, immune_time = graph.nodes[node]['seir']
        beta, sigma, gamma, delta = graph.nodes[node]['seir_params']  # Pobieranie indywidualnych parametrów SEIR dla każdego wierzchołka

        neighbors = list(graph.neighbors(node))  # Lista sąsiadów

        for neighbor in neighbors:
            S_neighbor, E_neighbor, I_neighbor, R_neighbor, D_neighbor, immune_time_neighbor\
                = graph.nodes[neighbor]['seir']

            if I > 0:
                infection_probability = 0.0005 * I
                if random.random() < infection_probability:
                    print('Infecting neigbor')
                    transfer = S_neighbor * 0.05
                    G[node][neighbor]['infection_occurred'] = True
                    if transfer > 0:
                        print(transfer)
                        E_neighbor += transfer
                        S_neighbor -= transfer
                    graph.nodes[neighbor]['seir'] = S_neighbor, E_neighbor, I_neighbor, R_neighbor, D_neighbor, immune_time_neighbor

        # Obliczanie zmian SEIR
        dS = -beta * S * I * TIME_STEP  # Przejście z S do E
        dE = (beta * S * I - sigma * E) * TIME_STEP
        dI = (sigma * E - gamma * I - delta * I) * TIME_STEP
        dR = gamma * I * TIME_STEP
        dD = delta * I * TIME_STEP

        # Zwiększenie czasu, przez jaki osoba jest w stanie R
        immune_time += TIME_STEP

        # Upewnij się, że wszystkie stany są w granicach: S, E, I, R, D >= 0
        S = max(S + dS, 0)
        E = max(E + dE, 0)
        I = max(I + dI, 0)
        R = max(R + dR, 0)
        D = max(D + dD, 0)

        # Przypisanie nowych wartości SEIR do wierzchołka
        graph.nodes[node]['seir'] = (S, E, I, R, D, immune_time)

# Inicjalizacja pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NetworkX Graph with SEIRDS Simulation")
clock = pygame.time.Clock()

fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Kodowanie do MP4
video_writer = cv2.VideoWriter('symulacja.mp4', fourcc, 30.0, (WIDTH, HEIGHT))

start_ticks = pygame.time.get_ticks()

simulation_time = 1  # In minutes

# Główna pętla
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Zaktualizowanie parametrów SEIR
    for _ in range(100):
        update_seir(G)

    # Rysowanie
    screen.fill(BACKGROUND_COLOR)
    draw_graph(screen, G)

    frame = pygame.surfarray.array3d(pygame.display.get_surface())
    frame = np.transpose(frame, (1, 0, 2))  # Zamiana wymiarów na format OpenCV (wysokość, szerokość, kanały)
    frame = frame[:, :, ::-1]  # Odwrócenie kanałów RGB na BGR
    video_writer.write(frame)

    pygame.display.flip()
    clock.tick(30)

    if pygame.time.get_ticks() - start_ticks >= 60000 * simulation_time:  # 60000 ms = 60 sekund
        running = False

video_writer.release()
pygame.quit()
