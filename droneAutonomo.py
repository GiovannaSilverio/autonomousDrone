import pygame
import math

# --- DRONE ---
class Drone:
    def __init__(self):
        self.x = 400  # Esquerda-direita
        self.y = 300  # Altura
        self.z = 0    # Frente-trás

        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        self.yaw_command = 0 
        self.throttle = 50

        self.motor0 = Motor()
        self.motor1 = Motor()
        self.motor2 = Motor()
        self.motor3 = Motor()

    def motorMixing(self):
        m0 = self.throttle - self.pitch + self.roll - self.yaw_command
        m1 = self.throttle - self.pitch - self.roll + self.yaw_command
        m2 = self.throttle + self.pitch - self.roll - self.yaw_command
        m3 = self.throttle + self.pitch + self.roll + self.yaw_command

        self.motor0.setVelocidade(m0)
        self.motor1.setVelocidade(m1)
        self.motor2.setVelocidade(m2)
        self.motor3.setVelocidade(m3)

    def atualizar(self):
        self.motorMixing()

        # Aplica o comando de rotação para alterar o ângulo yaw do drone
        # O valor 0.5 controla a velocidade da rotação
        self.yaw += self.yaw_command * 0.15

        # Mantém o yaw no intervalo -180 a 180 para evitar números muito grandes
        if self.yaw > 180: self.yaw -= 360
        if self.yaw < -180: self.yaw += 360
        
        # Atualização de altura
        media = (self.motor0.velocidade + self.motor1.velocidade + self.motor2.velocidade + self.motor3.velocidade) / 4
        self.y -= (media - 50) * 0.1

        # --- CORREÇÃO DA LÓGICA DE MOVIMENTO ---
        # `pitch` agora é positivo para frente, então não precisamos mais negar
        magnitude = self.pitch * 0.2
        angulo_rad = math.radians(self.yaw)

        dz = math.sin(angulo_rad) * magnitude
        dx = math.cos(angulo_rad) * magnitude
        
        self.z += dz
        self.x += dx

        # Limites
        self.x = max(0, min(800, self.x))
        self.z = max(-150, min(150, self.z))
        self.y = max(0, min(300, self.y))


    def controlar(self, keys):
        if keys[pygame.K_UP]:
            self.throttle += 1
        if keys[pygame.K_DOWN]:
            self.throttle -= 1
        if keys[pygame.K_w]:
            self.pitch = 10
        elif keys[pygame.K_s]:
            self.pitch = -10
        else:
            self.pitch = 0

        if keys[pygame.K_a]:
            self.roll = -10
        elif keys[pygame.K_d]:
            self.roll = 10
        else:
            self.roll = 0

        if keys[pygame.K_LEFT]:
            self.yaw_command -= 2
        if keys[pygame.K_RIGHT]:
            self.yaw_command += 2

        self.throttle = max(0, min(100, self.throttle))

class Motor:
    def __init__(self):
        self.velocidade = 0
    def setVelocidade(self, v):
        self.velocidade = max(0, min(100, v))

# --- AMBIENTE ---
def desenhar_vista_superior(screen, drone, area):
    pygame.draw.rect(screen, (220, 240, 255), area)

    # Correção no cálculo da posição de desenho
    centro_x = int(drone.x)
    centro_z = area.top + area.height // 2 + int(drone.z)
    tamanho = 20

    angulo_rad = math.radians(drone.yaw)
    dx_frente = math.cos(angulo_rad) * tamanho # Cosseno para X
    dz_frente = math.sin(angulo_rad) * tamanho # Seno para Z

    corpo = (centro_x, centro_z)
    frente = (centro_x + dx_frente, centro_z + dz_frente)

    pygame.draw.circle(screen, (100, 100, 255), corpo, 10)
    pygame.draw.line(screen, (255, 0, 0), corpo, frente, 3)

    font = pygame.font.SysFont(None, 20)
    txt = font.render("Vista de Cima (X/Z/Yaw)", True, (0, 0, 0))
    screen.blit(txt, (area.left + 10, area.top + 10))

def desenhar_vista_lateral(screen, drone, area):
    pygame.draw.rect(screen, (200, 255, 200), area)

    centro_z = area.left + area.width // 2 + int(drone.z)
    centro_y = area.top + area.height // 2 + int(drone.y)
    tamanho = 20

    pitch_rad = math.radians(drone.pitch)
    dz = math.sin(pitch_rad) * tamanho
    dy = -math.cos(pitch_rad) * tamanho

    corpo = (centro_z, centro_y)
    frente = (centro_z + dz, centro_y + dy)

    pygame.draw.circle(screen, (100, 100, 255), corpo, 10)
    pygame.draw.line(screen, (255, 100, 0), corpo, frente, 3)

    font = pygame.font.SysFont(None, 20)
    txt = font.render("Vista Lateral (Z/Y/Pitch)", True, (0, 0, 0))
    screen.blit(txt, (area.left + 10, area.top + 10))

def desenhar_telemetria(screen, drone):
    """Desenha os dados de telemetria do drone na tela."""
    font_titulo = pygame.font.SysFont(None, 24)
    font_dados = pygame.font.SysFont(None, 22)
    cor_texto = (10, 10, 10)  # Quase preto
    pos_x = 600  # Posição X no canto direito
    pos_y = 35   # Posição Y no topo

    # Lista de dados para exibir
    telemetria = []
    
    # Título
    titulo = font_titulo.render("--- TELEMETRIA ---", True, cor_texto)
    screen.blit(titulo, (pos_x, pos_y))

    # Dados
    pos_y += 25
    dados = [
        f"Pos (X,Y,Z): {drone.x:.1f}, {drone.y:.1f}, {drone.z:.1f}",
        f"Att (P,R,Y): {drone.pitch:.1f}, {drone.roll:.1f}, {drone.yaw:.1f}",
        f"Throttle: {drone.throttle:.0f}",
        "--- Motores ---",
        f"M0: {drone.motor0.velocidade:<3}  M1: {drone.motor1.velocidade:<3}",
        f"M3: {drone.motor3.velocidade:<3}  M2: {drone.motor2.velocidade:<3}",
    ]

    # Renderiza cada linha de dados
    for texto in dados:
        superficie_texto = font_dados.render(texto, True, cor_texto)
        screen.blit(superficie_texto, (pos_x, pos_y))
        pos_y += 20  # Incrementa Y para a próxima linha

# --- MAIN ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Drone 3D Simulado - Duas Vistas")
    clock = pygame.time.Clock()

    drone = Drone()
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        drone.controlar(keys)
        drone.atualizar()

        # Divisão da tela
        tela_cima = pygame.Rect(0, 0, 800, 300)
        tela_lado = pygame.Rect(0, 300, 800, 300)

        screen.fill((255, 255, 255))
        desenhar_vista_superior(screen, drone, tela_cima)
        desenhar_vista_lateral(screen, drone, tela_lado)
        desenhar_telemetria(screen, drone)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
