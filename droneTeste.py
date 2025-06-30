import pygame
import sys

# --- Constantes ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 150, 255)
RED = (255, 0, 0)
GRAY = (50, 50, 50)
OBSTACLE_COLOR = GRAY

class Motor:
    """Representa um único motor do drone."""
    def __init__(self):
        self.speed = 0

    def set_speed(self, speed):
        self.speed = max(0, min(speed, 100))

class LidarSensor:
    """Simula um sensor LiDAR que mede a distância vertical."""
    def __init__(self, drone, environment):
        self.drone = drone
        self.environment = environment
        self.beam_end_y = self.drone.y

    def measure_height(self):
        x = int(self.drone.x)
        # Garante que o X esteja dentro dos limites da tela
        if not (0 <= x < self.environment.get_width()):
            return SCREEN_HEIGHT - self.drone.y

        # Projeta um feixe para baixo a partir da posição do drone
        for y in range(int(self.drone.y), self.environment.get_height()):
            if self.environment.get_at((x, y)) == OBSTACLE_COLOR:
                self.beam_end_y = y
                return y - self.drone.y # Distância até o obstáculo

        # Se não encontrar obstáculo, retorna a distância até o fim da tela
        self.beam_end_y = self.environment.get_height()
        return self.environment.get_height() - self.drone.y

class Drone:
    """Drone com controle 100% manual."""
    def __init__(self, x, y, environment):
        self.x = x
        self.y = y

        self.pitch = 0  # Controlado pelo usuário (não implementado neste exemplo)
        self.roll = 0   # Controlado pelo usuário com setas esq/dir
        self.throttle = 40 # Aceleração inicial
        
        self.motors = [Motor() for _ in range(4)]
        self.sensor = LidarSensor(self, environment)

    def motor_mixing(self):
        """Calcula a velocidade de cada motor. Essencialmente para visualização."""
        # A lógica de mixing continua aqui, mas o voo é mais direto
        m0 = self.throttle + self.roll
        m1 = self.throttle - self.roll
        m2 = self.throttle + self.roll
        m3 = self.throttle - self.roll

        self.motors[0].set_speed(m0)
        self.motors[1].set_speed(m1)
        self.motors[2].set_speed(m2)
        self.motors[3].set_speed(m3)
        
    def update(self, dt):
        # MUDANÇA CRÍTICA: NENHUMA LÓGICA DE CONTROLE AQUI
        # O drone não toma mais decisões baseadas na altura.
        
        # 1. A física continua a mesma: o throttle move o drone
        # O valor de 50 é o ponto de equilíbrio para pairar (neutralizar a gravidade simulada)
        vertical_movement = (self.throttle - 50) * 0.1
        self.y -= vertical_movement * (dt / 16.6) # Ajuste pelo delta time para consistência

        # Movimento horizontal baseado no input do usuário
        self.x += self.roll * 0.2 * (dt / 16.6)

        # 2. Chama o motor_mixing para atualizar os valores dos motores para a telemetria
        self.motor_mixing()

        # 3. Mantém o drone dentro dos limites da tela
        self.y = max(10, min(self.y, SCREEN_HEIGHT - 10))
        self.x = max(10, min(self.x, SCREEN_WIDTH - 10))

    def draw(self, screen):
        # O sensor continua desenhando seu feixe
        self.sensor.measure_height() # Mede para saber onde desenhar a linha
        pygame.draw.line(screen, RED, (self.x, self.y), (self.x, self.sensor.beam_end_y), 1)
        
        # Desenha o corpo do drone
        drone_rect = pygame.Rect(self.x - 15, self.y - 8, 30, 16)
        pygame.draw.ellipse(screen, BLUE, drone_rect)
        pygame.draw.line(screen, BLACK, (self.x - 25, self.y), (self.x + 25, self.y), 3)

def create_environment(width, height):
    """Cria a superfície do ambiente com obstáculos."""
    env = pygame.Surface((width, height))
    env.fill(WHITE)
    pygame.draw.rect(env, OBSTACLE_COLOR, (0, height - 20, width, 20))
    pygame.draw.rect(env, OBSTACLE_COLOR, (100, height - 100, 200, 80))
    pygame.draw.rect(env, OBSTACLE_COLOR, (450, height - 180, 250, 160))
    pygame.draw.rect(env, OBSTACLE_COLOR, (800, height - 80, 150, 60))
    return env

def draw_telemetry(screen, drone, font):
    """Exibe informações do drone na tela."""
    # A medição é feita aqui apenas para exibição
    height = drone.sensor.measure_height()
    
    texts = [
        "CONTROLANDO MANUALMENTE",
        f"Altitude Medida pelo Sensor: {height:.2f}",
        f"Throttle: {drone.throttle:.2f} (Controle com Setas Cima/Baixo)",
        f"Roll: {drone.roll} (Controle com Setas Esq/Dir)",
    ]
    
    for i, text in enumerate(texts):
        text_surface = font.render(text, True, BLACK)
        screen.blit(text_surface, (10, 10 + i * 22))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simulador de Sensor LiDAR (Voo Manual)")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 28)

    environment = create_environment(SCREEN_WIDTH, SCREEN_HEIGHT)
    drone = Drone(SCREEN_WIDTH / 2, 100, environment)

    running = True
    while running:
        dt = clock.tick(FPS)
        if dt == 0: continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- MUDANÇA: CONTROLE MANUAL DIRETO ---
        keys = pygame.key.get_pressed()
        
        # Controle de Throttle (subir/descer)
        if keys[pygame.K_UP]:
            drone.throttle += 0.5
        if keys[pygame.K_DOWN]:
            drone.throttle -= 0.5
        
        # Limita o throttle para não sair do controle
        drone.throttle = max(0, min(100, drone.throttle))

        # Controle de Roll (esquerda/direita)
        if keys[pygame.K_LEFT]:
            drone.roll = -30
        elif keys[pygame.K_RIGHT]:
            drone.roll = 30
        else:
            drone.roll = 0
        
        # --- Lógica da Simulação ---
        drone.update(dt)

        # --- Desenho na Tela ---
        screen.blit(environment, (0, 0))
        drone.draw(screen)
        draw_telemetry(screen, drone, font)
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()