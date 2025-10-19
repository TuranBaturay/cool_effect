import batFramework as bf
import pygame
from random import randint
from collections import namedtuple, Counter
import sys
from darkstyle import DarkStyle

Point = namedtuple("Point", ["position", "velocity", "color"])

PARTICLE_SPEED = 15
PARTICLE_COUNT = 100
MAX_LINES = 4
MAX_PARTICLES = 300
MOUSE_RADIUS = 40
MIN_MOUSE_RADIUS = 10
FPS = 60
WIDTH, HEIGHT = 640, 480
# WIDTH, HEIGHT = 1280, 720
PARTICLE_RADIUS = 1


def get_point_color():
    return (255, 255, 255)
    return tuple(randint(100, 255) for _ in range(3))


class Main(bf.Scene):
    def do_when_added(self):
        self.add_actions(
            bf.Action("fullscreen").add_key_control(pygame.K_F11),
            bf.Action("increase").add_mouse_control(4),
            bf.Action("decrease").add_mouse_control(5),
            bf.Action("reverse").add_mouse_control(3).set_holding(),
        )

        self.particle_count = bf.gui.SyncedVar[int](PARTICLE_COUNT)

        self.points: list[Point] = [
            Point(
                pygame.Vector2(bf.utils.random_point_on_screen(10)),
                pygame.Vector2(PARTICLE_SPEED, 0).rotate(randint(0, 360)),
                # tuple(randint(100,255) for _ in range(3))
                get_point_color(),
            )
            for _ in range(self.particle_count.value)
        ]

        self.distances = [[] for _ in range(self.particle_count.value)]
        self.root.add(
            bf.gui.BasicDebugger().add_constraints(bf.gui.AnchorBottomRight())
        )

        self.mouse_vector = pygame.Vector2()

        # setup slider
        self.particle_count.bind(self, self.set_point_number)

        slider = (
            bf.gui.Slider(text="", synced_var=self.particle_count)
            .set_range(1, MAX_PARTICLES)
            .set_step(1)
        )
        slider.add_constraints(
            bf.gui.Margin(margin_bottom=20),
            bf.gui.CenterX(),
            bf.gui.PercentageWidth(0.1).set_priority(2),
            bf.gui.MinWidth(100),
        )

        slider.meter.handle.add_constraints(
            bf.gui.AspectRatio(1, bf.axis.VERTICAL), bf.gui.PercentageRectHeight(1.4)
        )

        fps_label = bf.gui.Label("0").add_constraints(bf.gui.Margin(10, 10))

        bf.Timer(
            loop=-1,
            duration=0.5,
            end_callback=lambda: fps_label.set_text(
                str(round(self.manager.clock.get_fps()))
            ),
        ).start()

        self.root.add(slider, fps_label)

        # aura effect for particles
        self.aura = pygame.Surface((PARTICLE_RADIUS * 20, PARTICLE_RADIUS * 20))
        center = self.aura.get_rect().center
        max_brightness = 60
        for i in range(PARTICLE_RADIUS * 8, 2, -1):
            color = [
                int(max_brightness - max_brightness * i / (PARTICLE_RADIUS * 8))
                for _ in range(3)
            ]
            pygame.draw.aacircle(self.aura, color, center, i)

    def set_mouse_radius(self, value):
        global MOUSE_RADIUS
        MOUSE_RADIUS = max(MIN_MOUSE_RADIUS, value)

    def set_point_number(self, n: int):
        n = int(n)
        current_length = len(self.points)
        if n < current_length:
            self.points = self.points[:n]
            self.distances = self.distances[:n]
        else:
            diff = n - current_length
            self.points.extend(
                [
                    Point(
                        pygame.Vector2(bf.utils.random_point_on_screen(10)),
                        pygame.Vector2(PARTICLE_SPEED, 0).rotate(randint(0, 360)),
                        get_point_color(),
                    )
                    for _ in range(diff)
                ]
            )
            self.distances.extend([[] for _ in range(diff)])

    def do_update(self, dt):

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
                p.velocity.x *= -1
            elif p.position.x < 0:
                p.position.x = 0
                p.velocity.x *= -1

            if p.position.y > bf.const.HEIGHT:
                p.position.y = bf.const.HEIGHT
                p.velocity.y *= -1
            elif p.position.y < 0:
                p.position.y = 0
                p.velocity.y *= -1

            if p.position == self.mouse_vector:
                continue
            repulsion_vector = p.position - self.mouse_vector
            distance_squared = repulsion_vector.length_squared()

            radius = MOUSE_RADIUS
            if self.actions["reverse"]:
                radius += 40
            radius *= radius
            if distance_squared < radius:
                force = repulsion_vector.normalize()
                if self.actions["reverse"]:
                    p.velocity.update(
                        -force
                        * PARTICLE_SPEED
                        * 4
                        * (0.5 + (distance_squared / (MOUSE_RADIUS * MOUSE_RADIUS)))
                    )
                else:
                    p.velocity.update(
                        force
                        * PARTICLE_SPEED
                        * max(
                            1,
                            8 * (1 - distance_squared / (MOUSE_RADIUS * MOUSE_RADIUS)),
                        )
                    )
            elif p.velocity.length_squared() > PARTICLE_SPEED * PARTICLE_SPEED:
                p.velocity.update(p.velocity.normalize() * PARTICLE_SPEED)

        for index, p in enumerate(self.points):
            all_distances = []
            for index2, p2 in enumerate(self.points):
                if p is p2:
                    continue
                all_distances.append((p.position.distance_squared_to(p2.position), p2))

            all_distances.sort(key=lambda v: v[0])
            self.distances[index] = all_distances[:MAX_LINES]

        counts = Counter(tuple(p.position) for p in self.points)
        overlapping = [p for p in self.points if counts[tuple(p.position)] > 1]
        angle = 0
        for p in overlapping:
            p.velocity.rotate_ip(angle)
            p.velocity.update(p.velocity * 2)
            angle += 45

    def do_early_draw(self, surface):
        # color = pygame.Color((255, 255, 255))
        offset = pygame.Vector2(self.aura.get_size()) * 0.5
        # color = pygame.Color(tuple(randint(100,255) for _ in range(3)))
        for index, p in enumerate(self.points):
            for i, d in enumerate(self.distances[index]):
                if index == i:
                    continue
                factor = 1 - max(0.1, i / MAX_LINES)
                pygame.draw.aaline(
                    # surface, bf.color.mult(color, factor), p.position, d[1].position
                    surface,
                    bf.color.mult(p.color, factor),
                    p.position,
                    d[1].position,
                )

        for p in self.points:
            # pygame.draw.aacircle(surface, color, p.position, PARTICLE_RADIUS * 2)
            pygame.draw.aacircle(surface, p.color, p.position, PARTICLE_RADIUS * 2)
            surface.blit(
                self.aura, (p.position - offset), special_flags=pygame.BLEND_ADD
            )

        if self.root.hovered == self.root:
            pygame.draw.aacircle(
                surface,
                "white" if not self.actions["reverse"] else "orange",
                self.mouse_vector,
                int(MOUSE_RADIUS),
                1,
            )


if __name__ == "__main__":
    bf.init(
        (WIDTH, HEIGHT),
        pygame.SCALED | pygame.RESIZABLE,
        resource_path="data",
        default_font="fonts/Metropolis-Black.otf",
        default_font_size=22,
        fps_limit=FPS,
        vsync=False,
    )
    bf.gui.StyleManager().add(DarkStyle())
    bf.FontManager().set_default_antialias(True)
    bf.Manager(Main("main")).run()
