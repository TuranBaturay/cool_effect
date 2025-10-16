import batFramework as bf
import pygame
from random import randint
from collections import namedtuple
import sys

Point = namedtuple("Point",["position","velocity"])

PARTICLE_SPEED = 40
PARTICLE_COUNT = 70
MAX_LINES = 4
MAX_PARTICLES = 1000
MOUSE_RADIUS = 60
FPS = 0 
WIDTH, HEIGHT = 1280,720



class Main(bf.Scene):
    def do_when_added(self):
        self.set_clear_color(bf.color.BLACK)
        self.add_actions(
            bf.Action("fullscreen").add_key_control(pygame.K_F11),
            bf.Action("increase").add_mouse_control(4),
            bf.Action("decrease").add_mouse_control(5)

        )

        self.particle_count = bf.gui.SyncedVar[int](PARTICLE_COUNT)
    
        self.points : list[Point] = [
            Point(pygame.Vector2(bf.utils.random_point_on_screen(10)),pygame.Vector2(PARTICLE_SPEED,0).rotate(randint(0,360))) \
            for _ in range(self.particle_count.value)
            ]

        self.distances = [[] for _ in range(self.particle_count.value)]
        self.root.add(bf.gui.BasicDebugger())

        self.particle_count.bind(self,self.set_point_number)
        slider = bf.gui.Slider(text="",synced_var = self.particle_count).set_range(2,MAX_PARTICLES).set_step(1)
        slider.set_padding(2).set_color(None)
        slider.set_outline_width(0)
        slider.meter.set_outline_width(0)
        slider.meter.handle.set_outline_width(0)
        slider.draw_focused = lambda *args : None
        self.mouse_vector = pygame.Vector2()
        self.root.add(slider)

    def set_mouse_radius(self,value):
        global MOUSE_RADIUS
        
        MOUSE_RADIUS = max(20,value)
        
    def set_point_number(self,n:int):
            n = int(n)
            current_length = len(self.points)
            if n < current_length:
                self.points = self.points[:n]
                self.distances = self.distances[:n] 
            else:
                diff = n - current_length
                self.points.extend([
                    Point(pygame.Vector2(bf.utils.random_point_on_screen(10)),pygame.Vector2(PARTICLE_SPEED,0).rotate(randint(0,360))) \
                    for _ in range(diff)
                ])
                self.distances.extend([[] for _ in range(diff)])

    def do_update(self,dt):

        self.mouse_vector.update(*pygame.mouse.get_pos())
        
        if self.actions["fullscreen"]:
            pygame.display.toggle_fullscreen()

        if self.actions["increase"]:
            self.set_mouse_radius(MOUSE_RADIUS + 10)
        if self.actions["decrease"]:
            self.set_mouse_radius(MOUSE_RADIUS - 10)

    
        for p in self.points:
            p.position.update(p.position + p.velocity * dt)
            if p.position.x > bf.const.WIDTH:
                p.position.x = bf.const.WIDTH
                p.velocity.x*=-1
            elif p.position.x < 0:
                p.position.x = 0
                p.velocity.x*=-1

            if p.position.y > bf.const.HEIGHT:
                p.position.y = bf.const.HEIGHT
                p.velocity.y*=-1
            elif p.position.y < 0:
                p.position.y = 0
                p.velocity.y*=-1

            if p.position == self.mouse_vector:
                continue
            repulsion_vector = p.position - self.mouse_vector
            distance_squared = repulsion_vector.length_squared()
            if distance_squared  < MOUSE_RADIUS*MOUSE_RADIUS:
                force = repulsion_vector.normalize()        
                p.velocity.update(force * PARTICLE_SPEED * 8 * (0.5 + (1-distance_squared/(MOUSE_RADIUS*MOUSE_RADIUS))))
            elif p.velocity.length_squared() > PARTICLE_SPEED*PARTICLE_SPEED:
                p.velocity.update(p.velocity.normalize()*PARTICLE_SPEED)
                
        for index,p in enumerate(self.points):
            all_distances = []
            for index2,p2 in enumerate(self.points):
                if p is p2: continue
                all_distances.append((p.position.distance_squared_to(p2.position), p2))
            
            all_distances.sort(key=lambda v : v[0]) 
            self.distances[index] = all_distances[:MAX_LINES] 
                
    def do_final_draw(self,surface):
        color = pygame.Color((255,255,255))
        
        for index,p in enumerate(self.points):
            for i,d in enumerate(self.distances[index]):
                factor = 1- max(0.1,i / MAX_LINES)
                pygame.draw.aaline(surface,bf.color.mult(color,factor), p.position, d[1].position)

        for p in self.points:
            pygame.draw.aacircle(surface,color, p.position, 3)

        pygame.draw.aacircle(surface, color , self.mouse_vector, MOUSE_RADIUS, 1 )
if __name__ == "__main__":
    bf.init((WIDTH,HEIGHT),pygame.SCALED | pygame.RESIZABLE,fps_limit=60, vsync=False)
    bf.Manager(Main("main")).run()
    
