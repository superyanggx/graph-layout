#! /usr/bin/python
#coding=utf-8

'''
力导向布局算法实现

2017-06-30
yanggx

影响参数：
    节点起始位置
    最大循环次数
    引力参数值
    斥力参数值

参考: 
    https://github.com/hgurmendi/graph-layout
'''

import datetime, random, os
import pygame, signal
from pygame.locals import *
from euclid import *

from mongoengine import connect
from physics_topology import PhysicsTopologyNode, PhysicsTopologyLink


MONGODB = {
    'host': '192.168.6.252',
    'port': 27017,
    'username': 'opsmart_demo',
    'password': 'q1w2e3r4',
    'db_name': 'opsmart_demo'
}

connect(MONGODB['db_name'],
        username=MONGODB['username'],
        password=MONGODB['password'],
        host=MONGODB['host'],
        port=MONGODB['port'])


def read_file(input_file=""):
    V = []
    E = []
    
    f = open(input_file, "r")
    
    count = int(f.readline())
    
    print "Leyendo " + input_file
    
    for i in range(count):
        V.append(f.readline().strip())
        
    for line in f:
        E.append(line.strip().split(" ", 2))
    
    # print V
    # print E
    return (V, E)


def read_graph():
    V = []
    E = []

    count = 0
    limit = 500
    for node in PhysicsTopologyNode.objects():
        V.append(node.host_id)
        count += 1
        if count >= limit:
            break

    for link in PhysicsTopologyLink.objects():
        source = link.source_node_id
        target = link.target_node_id
        if source not in V:
            print source
            continue
        if target not in V:
            print target
            continue

        E.append([source, target])
    
    # print len(V), len(E)
    return (V, E)


class ForceDirected(object):
    """
    力导向算法
    """
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720

    TEMPERATURE_FACTOR = 0.95
    INITIAL_TEMPERATURE = SCREEN_WIDTH / 10

    # 循环次数
    LIMIT_ITERS = 100
    # 引力参数值
    VALUE_CA = 0.03
    # 斥力参数值
    VALUE_CR = 2500

    # 界面显示参数
    FONT_SIZE = 25
    FONT_COLOR = (255, 255, 0)

    NODE_RADIUS = 12
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)
    NODE_COLOR = (255, 0, 0)

    def __init__(self, grafo):
        super(ForceDirected, self).__init__()

        self.grafo = grafo
        self.iters = self.LIMIT_ITERS
        self.iters_counter = 0

        # Constante de atraccion.
        self.c_a = self.VALUE_CA
        
        # Constante de repulsion.
        self.c_r = self.VALUE_CR

        # 节点位置
        self.pos = {}

    def screen(self):
        # Inicializa pygame
        pygame.init()
        
        # Inicializa la pantalla.
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Graph Layout")

        V, E = self.grafo

        self.label = {}
        self.font = pygame.font.Font(None, self.FONT_SIZE)
        for node in V:
            self.label[node] = self.font.render(node, 1, self.FONT_COLOR)

        # Dibuja el cuadro
        self.screen.fill(self.BLACK)

        pygame.draw.aaline(self.screen,
            self.BLUE,
            (self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 - 10),
            (self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 + 10))
        
        pygame.draw.aaline(self.screen,
            self.BLUE,
            (self.SCREEN_WIDTH / 2 - 10, self.SCREEN_HEIGHT / 2),
            (self.SCREEN_WIDTH / 2 + 10, self.SCREEN_HEIGHT / 2))

        for node in V:
            pygame.draw.circle(self.screen,
                self.NODE_COLOR,
                (int(self.pos[node].x), int(self.pos[node].y)),
                self.NODE_RADIUS,
                0
                )

            label_pos = self.label[node].get_rect()
            label_pos.centerx = self.pos[node].x
            label_pos.centery = self.pos[node].y
            self.screen.blit(self.label[node], label_pos)

        pygame.display.flip()

    def layout(self):
        V, E = self.grafo
        
        # 节点起始位置
        for node in V:
            x = random.randint(0, self.SCREEN_WIDTH)
            y = random.randint(0, self.SCREEN_HEIGHT)
            self.pos[node] = Vector2(x, y)

        self.temperature = self.INITIAL_TEMPERATURE

        # 多次计算节点位置
        for x in xrange(1,self.iters):
            self.step()

        # 显示节点坐标
        for node in V:
            print self.pos[node].x, self.pos[node].y

        # 界面显示
        self.screen()
        signal.pause()

    # Realiza una iteracion del algoritmo
    def step(self):
        V, E = self.grafo

        # Desplazamiento de los vertices.
        disp = {}
        
        # Inicializacion del desplazamiento de los vertices en 0.
        for node in V:
            disp[node] = Vector2(0, 0)

        # Fuerza de repulsion ejercida SOBRE node1 POR node2
        for node1 in V:
            for node2 in V:
                if node1 != node2:  
                    # Vector node1->node2.
                    vec = self.pos[node2] - self.pos[node1]
                    
                    # Distancia entre ambos vertices.
                    dist = vec.magnitude()
                    
                    # Calculo de la fuerza de repulsion.
                    fz_r = self.c_r / dist

                    vec.normalize()
                    
                    # Calculo del vector de repulsion.
                    vec = vec * fz_r * -1
                    
                    # Se agrega al desplazamiento del vertices.
                    disp[node1] += vec
     
        
        # Las fuerzas de atraccion se dan entre los vertices adyacentes.
        for edge in E:
            node1 = edge[0]
            node2 = edge[1]
            
            # Vector node1->node2.
            vec = self.pos[node2] - self.pos[node1]
            
            # Distancia entre ambos vertices.
            dist = vec.magnitude()
            
            # Calculo de la fuerza de atraccion.
            fz_a = self.c_a * dist**2
            
            vec.normalize()
            
            # Calculo del vector de atraccion.
            vec *= fz_a
            
            # Se agrega al desplazamiento de cada uno de los vertices involucrados.
            disp[node1] += vec
            disp[node2] -= vec

        # La fuerza de gravedad afecta a todos los vertices, atrayendolos
        # al centro de la pantalla con una fuerza relativamente leve.
        center = Vector2(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2)
        
        for node in V:
            # Vector node->center.
            vec = center - self.pos[node]
            
            # Distancia entre el centro y el vertice.
            dist = vec.magnitude()
            
            # Calculo de la fuerza de atraccion gravitatoria.
            fz_gr = self.c_a / 8 * dist**2
            
            vec.normalize()
            
            # Calculo del vector de atraccion gravitatoria.
            vec *= fz_gr
            
            # Se agrega al desplazamiento del vertice.
            disp[node] += vec

        # Los vertices se mueven de acuerdo con el desplazamiento.
        for node in V:
            # Limito el desplazamiento con la temperatura.
            if disp[node].magnitude() > self.temperature:

                disp[node].normalize()
                disp[node] *= self.temperature
            
            self.pos[node] += disp[node]
            
            # Los vertices no se pueden dibujar fuera de la pantalla.
            if self.pos[node].x >= self.SCREEN_WIDTH:
                self.pos[node].x = self.SCREEN_WIDTH
                
            if self.pos[node].x < 0:
                self.pos[node].x = 0
            
            if self.pos[node].y >= self.SCREEN_HEIGHT:
                self.pos[node].y = self.SCREEN_HEIGHT
            
            if self.pos[node].y < 0:
                self.pos[node].y = 0
            
        # Baja la temperatura luego de cada iteracion.
        self.temperature *= self.TEMPERATURE_FACTOR
        
        # self.iters_counter += 1      


def main():
    G = read_graph()
    #G = read_file("samples/davidson-harel")

    layout = ForceDirected(grafo=G)

    layout.layout()


if __name__ == '__main__':
    main()
