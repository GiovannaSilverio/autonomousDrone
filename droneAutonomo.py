import pygame
import math

PONTO_DE_ESTABILIDADE = 50

class Drone:
    def __init__(self):
        self.x = 400
        self.y = 150
        self.z = 0

        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        self.yaw_command = 0 
        self.throttle = 50
        self.lidar = SensorLidar()

        self.motor0 = Motor()
        self.motor1 = Motor()
        self.motor2 = Motor()
        self.motor3 = Motor()

    def motorMixing(self):
        m0 = self.throttle - self.pitch - self.roll - self.yaw_command
        m1 = self.throttle - self.pitch + self.roll + self.yaw_command
        m2 = self.throttle + self.pitch + self.roll - self.yaw_command
        m3 = self.throttle + self.pitch - self.roll + self.yaw_command

        self.motor0.setVelocidade(m0)
        self.motor1.setVelocidade(m1)
        self.motor2.setVelocidade(m2)
        self.motor3.setVelocidade(m3)

    def atualizar(self):
        self.motorMixing()

        # Mantém o yaw no intervalo -180 a 180
        if self.yaw > 180: self.yaw -= 360
        if self.yaw < -180: self.yaw += 360
        
        # Atualização de altura
        media = (self.motor0.velocidade + self.motor1.velocidade + self.motor2.velocidade + self.motor3.velocidade) / 4
        self.y = self.y - (media - PONTO_DE_ESTABILIDADE) * 0.1 #seta altura do drone, se ele fica estabilizado ou subindo/descendo

        pitch_magnitude = self.pitch * 0.2
        roll_magnitude = self.roll * 0.2 
        angulo_rad = math.radians(self.yaw)

        # Vetor de movimento para FRENTE/TRÁS (Pitch)
        dx_pitch = math.cos(angulo_rad) * pitch_magnitude #esquerda e direita
        dz_pitch = math.sin(angulo_rad) * pitch_magnitude #frente e tras
        
        #Vetor de movimento para os LADOS (Roll)
        # Este vetor é perpendicular ao veto de pitch.
        dx_roll = -math.sin(angulo_rad) * roll_magnitude #esquerda e direita
        dz_roll = math.cos(angulo_rad) * roll_magnitude #frente e tras

        # Combina os dois vetores para o movimento final
        dx = dx_pitch + dx_roll 
        dz = dz_pitch + dz_roll
        
        self.z += dz
        self.x += dx

        # Limites
        self.x = max(0, min(800, self.x))
        self.z = max(-150, min(150, self.z))
        self.y = max(0, min(300, self.y))

        # atualiza o lidar
        self.lidar.atualizar(self)


    def controlar(self, keys):
        if keys[pygame.K_UP]:
            self.throttle += 1
        if keys[pygame.K_DOWN]:
            self.throttle -= 1
        self.throttle = max(0, min(100, self.throttle))
        
        if keys[pygame.K_w]:
            self.pitch = 10
        elif keys[pygame.K_s]:
            self.pitch = -10
        else:
            self.pitch = 0

        if keys[pygame.K_d]:
            self.roll = 10
        elif keys[pygame.K_a]:
            self.roll = -10
        else:
            self.roll = 0

        # Lógica de Yaw estável e direta
        if keys[pygame.K_LEFT]:
            self.yaw -= 2.5
            self.yaw_command = 15
        elif keys[pygame.K_RIGHT]:
            self.yaw += 2.5
            self.yaw_command = -15
        else:
            self.yaw_command = 0

class SensorLidar:
    def __init__(self):
        # distancia de um drone do objeto mais próximo verticalmente 
        self.distancia = 0

    def atualizar(self, drone):
        self.distancia = 300 - drone.y


class Motor:
    def __init__(self):
        self.velocidade = 0
    def setVelocidade(self, v):
        self.velocidade = max(0, min(100, v))

# --- AMBIENTE ---
def desenhar_vista_superior(screen, drone, area):
    pygame.draw.rect(screen, (220, 240, 255), area)
    centro_x = int(drone.x)
    centro_z = area.top + area.height // 2 + int(drone.z)
    tamanho = 20

    angulo_rad = math.radians(drone.yaw)
    dx_frente = math.cos(angulo_rad) * tamanho
    dz_frente = math.sin(angulo_rad) * tamanho

    corpo = (centro_x, centro_z)
    frente = (centro_x + dx_frente, centro_z + dz_frente)

    pygame.draw.circle(screen, (100, 100, 255), corpo, 10)
    pygame.draw.line(screen, (255, 0, 0), corpo, frente, 3)

    font = pygame.font.SysFont(None, 20)
    txt = font.render("Vista de Cima (X/Z/Yaw)", True, (0, 0, 0))
    screen.blit(txt, (area.left + 10, area.top + 10))

def desenhar_vista_lateral(screen, drone, area):
    pygame.draw.rect(screen, (200, 255, 200), area)

    centro_z_tela = area.left + area.width // 2 + int(drone.z)
    centro_y_tela = area.top + int(drone.y)
    corpo_rect = pygame.Rect(0, 0, 30, 10)
    corpo_rect.center = (centro_z_tela, centro_y_tela)
    pygame.draw.rect(screen, (100, 100, 255), corpo_rect)
    nariz_offset = 15 if drone.pitch > 0 else (-15 if drone.pitch < 0 else 0)
    pygame.draw.circle(screen, (255, 100, 0), (corpo_rect.centerx + nariz_offset, corpo_rect.centery), 4)

    # Ponto inicial: centro do drone
    ponto_inicio = corpo_rect.center
    # Ponto final: na mesma horizontal do drone, mas no "chão" (y=300)
    ponto_fim = (corpo_rect.centerx, area.top + 300)
    # Desenha uma linha vermelha com 2 pixels de espessura para representar o Lidar
    pygame.draw.line(screen, (255, 0, 0), ponto_inicio, ponto_fim, 2)

    font = pygame.font.SysFont(None, 20)
    txt = font.render("Vista Lateral (Z/Y/Pitch)", True, (0, 0, 0))
    screen.blit(txt, (area.left + 10, area.top + 10))

def desenhar_telemetria(screen, drone):
    font_titulo = pygame.font.SysFont(None, 24)
    font_dados = pygame.font.SysFont(None, 22)
    cor_texto = (10, 10, 10)
    pos_x = 580
    pos_y = 35
    titulo = font_titulo.render("TELEMETRIA", True, cor_texto)
    screen.blit(titulo, (pos_x, pos_y))
    pos_y += 25
    dados = [
        f"Pos (X,Y,Z): {drone.x:.1f}, {drone.y:.1f}, {drone.z:.1f}",
        f"Att (P,R,Y): {drone.pitch:.0f}, {drone.roll:.0f}, {drone.yaw:.1f}",
        f"Throttle: {drone.throttle:.0f}",
        f"Yaw Command: {drone.yaw_command:.0f}",
        "Motores",
        f"M1(FL): {drone.motor1.velocidade:<3}  M0(FR): {drone.motor0.velocidade:<3}",
        f"M2(RL): {drone.motor2.velocidade:<3}  M3(RR): {drone.motor3.velocidade:<3}",
        f"Distância do Chão: {drone.lidar.distancia:.1f}",
    ]
    for texto in dados:
        superficie_texto = font_dados.render(texto, True, cor_texto)
        screen.blit(superficie_texto, (pos_x, pos_y))
        pos_y += 20

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