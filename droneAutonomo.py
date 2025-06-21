class Drone():
    def __init__(self, nome):
        #definindo os atributos
        self.nome=nome
        #efinindo cada motor do drone cm a instanciaçao
        self.motor0=Motor()
        self.motor1=Motor()
        self.motor2=Motor()
        self.motor3=Motor()
        self.sensor=Sensor()
        self.yaw=0
        self.pitch=0
        self.roll=0
        self.throttle=0

    def MotorMixing(self):
         M1 = Throttle - Pitch + Roll - Yaw  # Frente esquerda

M2 = Throttle - Pitch - Roll + Yaw  # Frente direita

M3 = Throttle + Pitch + Roll + Yaw  # Trás esquerda

M4 = Throttle + Pitch - Roll - Yaw  # Trás direita 


class Motor():
    def __init__(self, velocidade, estado):
        self.velocidade=0

    #nao deixa a velocidade ser maior que 100
    def aumentar(self, valor):
        self.velocidade += valor
        if self.velocidade > 100:
            self.velocidade = 100

    #nao deixa a velocidade ser menor que 0
    def diminuir(self, valor):
        self.velocidade -= valor
        if self.velocidade < 0:
            self.velocidade = 0

class Sensor():
    def __init__(self):
        pass



def main():
    drone=Drone("jicasDrone")


if __name__=="__main__":
    main()