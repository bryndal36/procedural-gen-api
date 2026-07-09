from PIL import Image, ImageDraw
import math
import time
from typing import List, Tuple, Optional
import random

Color = Tuple[float, float, float, float]

class SpriteGenerator:
    def __init__(self):
        self.rng = random.Random()
    
    def new_img(self, w: int, h: int) -> Image.Image:
        return Image.new('RGBA', (w, h), (0, 0, 0, 0))
    
    def put(self, img: Image.Image, x: int, y: int, c: Color) -> None:
        if 0 <= x < img.width and 0 <= y < img.height:
            img.putpixel((x, y), self._color_to_rgba(c))
    
    def _color_to_rgba(self, c: Color) -> Tuple[int, int, int, int]:
        return (
            int(c[0] * 255),
            int(c[1] * 255),
            int(c[2] * 255),
            int(c[3] * 255) if len(c) > 3 else 255
        )
    
    def tone_for(self, v: float, ramp: List[Color], light_frac: float, dark_frac: float) -> Color:
        if v < light_frac:
            return ramp[0]
        if v > 1.0 - dark_frac:
            return ramp[2]
        return ramp[1]
    
    def fill_poly(self, img: Image.Image, pts: List[Tuple[float, float]], 
                  ramp: List[Color], light_frac: float = 0.3, dark_frac: float = 0.3) -> None:
        min_x = min(p[0] for p in pts)
        max_x = max(p[0] for p in pts)
        min_y = min(p[1] for p in pts)
        max_y = max(p[1] for p in pts)
        
        for y in range(int(math.floor(min_y)), int(math.ceil(max_y)) + 1):
            for x in range(int(math.floor(min_x)), int(math.ceil(max_x)) + 1):
                if self._point_in_polygon((x + 0.5, y + 0.5), pts):
                    v = 0.5
                    if max_y - min_y > 0.01:
                        v = (y + 0.5 - min_y) / (max_y - min_y)
                    self.put(img, x, y, self.tone_for(v, ramp, light_frac, dark_frac))
    
    def _point_in_polygon(self, point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def fill_ellipse(self, img: Image.Image, cx: float, cy: float, rx: float, ry: float,
                     ramp: List[Color], light_frac: float = 0.3, dark_frac: float = 0.3) -> None:
        for y in range(int(math.floor(cy - ry)), int(math.ceil(cy + ry)) + 1):
            for x in range(int(math.floor(cx - rx)), int(math.ceil(cx + rx)) + 1):
                dx = (x + 0.5 - cx) / rx
                dy = (y + 0.5 - cy) / ry
                if dx * dx + dy * dy <= 1.0:
                    v = (dy + 1.0) / 2.0
                    self.put(img, x, y, self.tone_for(v, ramp, light_frac, dark_frac))
    
    def fill_rect(self, img: Image.Image, x: int, y: int, w: int, h: int,
                  ramp: List[Color], light_frac: float = 0.3, dark_frac: float = 0.3) -> None:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                v = 0.5
                if h > 1:
                    v = (yy - y) / float(h - 1)
                self.put(img, xx, yy, self.tone_for(v, ramp, light_frac, dark_frac))
    
    def flat(self, c: Color) -> List[Color]:
        return [c, c, c]
    
    def mirror_h(self, img: Image.Image) -> None:
        w = img.width
        for y in range(img.height):
            for x in range(w // 2):
                img.putpixel((w - 1 - x, y), img.getpixel((x, y)))
    
    def outline(self, img: Image.Image, col: Color = (0.055, 0.06, 0.1, 1.0)) -> None:
        w, h = img.width, img.height
        edges = []
        
        for y in range(h):
            for x in range(w):
                pixel = img.getpixel((x, y))
                if pixel[3] > 128:
                    for nx, ny in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
                        if nx < 0 or ny < 0 or nx >= w or ny >= h:
                            edges.append((x, y))
                            break
                        neighbor = img.getpixel((nx, ny))
                        if neighbor[3] <= 128:
                            edges.append((x, y))
                            break
        
        for x, y in edges:
            self.put(img, x, y, col)
    
    def generate_player_ship(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(32, 32)
        wing_tip = self.rng.randint(1, 4)
        color_shift = self.rng.uniform(-0.08, 0.08)
        glass_shift = self.rng.uniform(-0.1, 0.1)
        hull_light = self.rng.uniform(0.18, 0.28)
        hull_dark = self.rng.uniform(0.2, 0.32)

        hull = [(0.85, 0.9 + color_shift, 0.98), (0.55, 0.65 + color_shift, 0.85), (0.3, 0.38 + color_shift, 0.6)]
        wing = [(0.72, 0.76, 0.85), (0.5, 0.55, 0.66), (0.32, 0.36, 0.46)]
        glass = [(0.7 + glass_shift, 0.95, 1.0), (0.25 + glass_shift, 0.7, 0.95), (0.1, 0.35, 0.7)]
        red = (0.85, 0.2, 0.25)
        stripe_color = self.rng.choice([(0.85, 0.2, 0.25), (0.2, 0.6, 0.85), (0.95, 0.7, 0.15)])
        has_stripe = self.rng.random() < 0.5

        self.fill_poly(img, [(wing_tip, 17), (13, 12), (13, 26), (7, 24), (wing_tip, 21)], wing)
        self.fill_poly(img, [(wing_tip, 17), (13, 12), (13, 14), (3 + wing_tip, 19)], self.flat(red))
        self.fill_rect(img, 1, 15, 2, 7, [(0.6, 0.64, 0.72), (0.42, 0.46, 0.54), (0.28, 0.31, 0.38)])
        self.fill_poly(img, [(8, 23), (11, 21), (11, 29), (9, 28)], wing)
        self.fill_poly(img, [
            (15.5, 0.5), (13, 7), (12, 15), (12, 22),
            (13.5, 29), (15.5, 30.5), (17.5, 29), (19, 22),
            (19, 15), (18, 7),
        ], hull, hull_light, hull_dark)
        self.fill_rect(img, 12, 16, 1, 6, self.flat((0.24, 0.3, 0.5)))
        self.fill_ellipse(img, 15.5, 12.5, 2.4, 4.0, glass, 0.28, 0.3)
        self.put(img, 15, 10, (0.9, 1.0, 1.0))
        self.put(img, 16, 10, (0.9, 1.0, 1.0))
        self.put(img, 15, 1, (0.95, 0.98, 1.0))
        self.put(img, 16, 1, (0.95, 0.98, 1.0))
        self.fill_rect(img, 13, 28, 6, 2, self.flat((0.3, 0.33, 0.4)))
        for x in range(14, 18):
            self.put(img, x, 29, (0.55, 0.9, 1.0))
        if has_stripe:
            for x in range(12, 20):
                self.put(img, x, 19, stripe_color)
                self.put(img, x, 20, stripe_color)

        self.mirror_h(img)
        self.outline(img)
        return img
    
    def generate_enemy_grunt(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(24, 24)
        body_shift = self.rng.uniform(-0.1, 0.1)
        glass_shift = self.rng.uniform(-0.1, 0.1)
        width_shift = self.rng.randint(-2, 2)
        has_antenna = self.rng.random() < 0.4
        antenna_height = self.rng.randint(1, 3)

        body = [(1.0, 0.55 + body_shift, 0.45), (0.82, 0.22 + body_shift, 0.2), (0.5, 0.1 + body_shift, 0.12)]
        body = [tuple(max(0, min(1, c)) for c in ramp) for ramp in body]
        dark = [(0.62, 0.16 + body_shift, 0.16), (0.5, 0.1 + body_shift, 0.12), (0.34, 0.06 + body_shift, 0.09)]
        dark = [tuple(max(0, min(1, c)) for c in ramp) for ramp in dark]
        glass = [(0.5 + glass_shift, 0.85, 0.9), (0.15 + glass_shift, 0.5, 0.6), (0.05, 0.25, 0.35)]

        self.fill_poly(img, [(1, 4), (10 + width_shift, 3), (10 + width_shift, 13), (5, 11), (1, 8)], body)
        self.fill_poly(img, [(1, 4), (10 + width_shift, 3), (10 + width_shift, 5), (2, 6)], dark)
        self.fill_rect(img, 3, 2, 3, 4, [(0.5, 0.52, 0.58), (0.36, 0.38, 0.44), (0.22, 0.24, 0.3)])
        right = 11.5 + width_shift * 0.5
        self.fill_poly(img, [
            (right, 1.5), (9 + width_shift, 6), (8.5 + width_shift, 13), (10 + width_shift, 19),
            (right, 22.5), (13 + width_shift, 19), (14.5 + width_shift, 13), (14 + width_shift, 6),
        ], body, 0.25, 0.3)
        self.fill_ellipse(img, right, 13.0, 2.0, 3.0, glass)
        self.put(img, 1, 8, (0.3, 0.06, 0.08))
        self.put(img, 1, 9, (0.3, 0.06, 0.08))
        if has_antenna:
            for ay in range(antenna_height):
                self.put(img, 11 + width_shift, 1 - ay, (0.6, 0.6, 0.7))

        self.mirror_h(img)
        self.outline(img)
        return img
    
    def generate_enemy_drone(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(16, 16)
        body_shift = self.rng.uniform(-0.1, 0.1)
        fin_offset = self.rng.randint(-1, 1)
        core_glow = self.rng.uniform(0.6, 1.0)

        body = [(1.0, 0.8 + body_shift, 0.35), (0.95, 0.55 + body_shift, 0.15), (0.6, 0.3 + body_shift, 0.08)]
        body = [tuple(max(0, min(1, c)) for c in ramp) for ramp in body]
        fin = [(0.8, 0.45 + body_shift, 0.12), (0.6, 0.3 + body_shift, 0.08), (0.4, 0.18 + body_shift, 0.04)]
        fin = [tuple(max(0, min(1, c)) for c in ramp) for ramp in fin]

        self.fill_poly(img, [(1, 3 + fin_offset), (6, 5), (6, 11), (3, 9 + fin_offset)], fin)
        self.fill_poly(img, [
            (7.5, 1.0), (5.5, 5), (5, 9), (7.5, 14.5),
            (10, 9), (9.5, 5),
        ], body, 0.25, 0.3)
        self.fill_ellipse(img, 7.5, 7.0, 1.6, 2.2, self.flat((core_glow, core_glow * 0.95, core_glow * 0.6)))
        self.put(img, 7, 1, (0.45, 0.2, 0.05))
        self.put(img, 8, 1, (0.45, 0.2, 0.05))

        self.mirror_h(img)
        self.outline(img)
        return img
    
    def generate_enemy_turret(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(32, 32)
        color_shift = self.rng.uniform(-0.08, 0.08)
        barrel_extra = self.rng.randint(-3, 3)
        dome_vary = self.rng.uniform(-0.5, 0.5)

        armor = [(0.8, 0.55 + color_shift, 0.95), (0.55, 0.28 + color_shift, 0.75), (0.32, 0.15 + color_shift, 0.5)]
        armor = [tuple(max(0, min(1, c)) for c in ramp) for ramp in armor]
        inner = self.flat((0.24, 0.1 + color_shift, 0.38))
        dome = [(0.9, 0.7 + color_shift, 1.0), (0.65, 0.38 + color_shift, 0.85), (0.4, 0.2 + color_shift, 0.58)]
        dome = [tuple(max(0, min(1, c)) for c in ramp) for ramp in dome]
        barrel = [(0.6, 0.62, 0.7), (0.42, 0.44, 0.52), (0.26, 0.28, 0.35)]

        self.fill_poly(img, [
            (9, 2), (22, 2), (28, 9), (28, 20),
            (22, 26), (9, 26), (3, 20), (3, 9),
        ], armor, 0.26, 0.28)
        self.fill_ellipse(img, 15.5, 14.0, 8.5, 8.5, inner)
        self.fill_ellipse(img, 15.5, 13.5, 5.5 + dome_vary, 5.5 + dome_vary, dome, 0.3, 0.3)
        self.put(img, 14, 10, (0.95, 0.85, 1.0))
        self.put(img, 15, 10, (0.95, 0.85, 1.0))
        self.fill_rect(img, 14, 18, 4, 10 + barrel_extra, barrel)
        self.fill_rect(img, 13, 27 + barrel_extra, 6, 2, self.flat((0.2, 0.22, 0.28)))
        for bx, by in [(6, 6), (25, 6), (6, 22), (25, 22)]:
            self.put(img, bx, by, (0.9, 0.75, 1.0))

        self.outline(img)
        return img
    
    def generate_enemy_carrier(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(48, 48)
        cs = self.rng.uniform(-0.08, 0.08)
        hull = [(1.0, 0.9 + cs, 0.5), (0.9, 0.72 + cs, 0.2), (0.6, 0.45 + cs, 0.1)]
        hull = [tuple(max(0, min(1, c)) for c in r) for r in hull]
        plate = self.flat((0.55, 0.42 + cs, 0.1))
        bay = [(0.32, 0.34, 0.4), (0.22, 0.24, 0.3), (0.13, 0.14, 0.19)]
        pod = [(0.5, 0.52, 0.58), (0.36, 0.38, 0.44), (0.22, 0.24, 0.3)]
        
        self.fill_poly(img, [
            (23.5, 2), (40, 10), (45, 25), (34, 44),
            (13, 44), (2, 25), (7, 10),
        ], hull, 0.24, 0.28)
        self.fill_rect(img, 8, 16, 32, 2, plate)
        self.fill_rect(img, 6, 30, 36, 2, plate)
        self.fill_rect(img, 10, 4, 6, 6, pod)
        self.fill_rect(img, 17, 14, 14, 20, bay)
        self.fill_rect(img, 19, 16, 10, 16, self.flat((0.1, 0.11, 0.16)))
        self.fill_ellipse(img, 23.5, 24.0, 5.0, 5.0, [(1.0, 1.0, 0.9), (1.0, 0.85, 0.4), (0.9, 0.6, 0.15)])
        self.put(img, 22, 21, (1, 1, 1))
        self.put(img, 23, 21, (1, 1, 1))
        self.fill_rect(img, 15, 42, 4, 4, pod)
        self.put(img, 16, 46, (0.6, 0.9, 1.0))
        self.put(img, 17, 46, (0.6, 0.9, 1.0))
        for bx, by in [(9, 13), (9, 27), (13, 38)]:
            self.put(img, bx, by, (1.0, 0.95, 0.7))
        
        self.mirror_h(img)
        self.outline(img)
        return img
    
    def generate_enemy_flanker(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(32, 16)
        cs = self.rng.uniform(-0.1, 0.1)
        body = [(0.6, 0.9 + cs, 1.0), (0.2, 0.7 + cs, 0.85), (0.1, 0.4 + cs, 0.6)]
        body = [tuple(max(0, min(1, c)) for c in r) for r in body]
        wing = [(0.5, 0.85 + cs, 0.95), (0.15, 0.6 + cs, 0.75), (0.08, 0.35 + cs, 0.5)]
        wing = [tuple(max(0, min(1, c)) for c in r) for r in wing]
        glass = [(0.7, 0.95, 1.0), (0.25, 0.7, 0.95), (0.1, 0.35, 0.7)]
        dark = (0.08, 0.3, 0.45)
        
        self.fill_poly(img, [
            (8, 5), (24, 5), (28, 8), (24, 11), (8, 11)
        ], body, 0.25, 0.3)
        self.fill_poly(img, [
            (24, 6), (30, 8), (24, 10)
        ], [(0.8, 1.0, 1.0), (0.4, 0.85, 0.95), (0.2, 0.6, 0.8)])
        self.fill_poly(img, [(2, 6), (10, 6), (10, 10), (2, 10)], wing)
        self.fill_poly(img, [(22, 6), (30, 6), (30, 10), (22, 10)], wing)
        self.fill_ellipse(img, 22, 8, 2.0, 1.5, glass)
        self.put(img, 21, 7, (0.9, 1.0, 1.0))
        self.fill_rect(img, 10, 7, 2, 2, self.flat(dark))
        self.put(img, 8, 7, (1, 0.9, 0.3))
        self.put(img, 8, 8, (1, 0.9, 0.3))
        self.put(img, 7, 7, (1, 0.7, 0.2, 0.8))
        self.put(img, 7, 8, (1, 0.7, 0.2, 0.8))
        self.put(img, 3, 6, (0.8, 0.8, 0.8))
        self.put(img, 3, 9, (0.8, 0.8, 0.8))
        for x in range(10, 22):
            self.put(img, x, 5, dark)
            self.put(img, x, 10, dark)
        
        self.outline(img)
        return img
    
    def generate_enemy_kamikaze(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(24, 24)
        cs = self.rng.uniform(-0.1, 0.1)
        body = [(1.0, 0.7 + cs, 0.4), (0.95, 0.45 + cs, 0.2), (0.7, 0.25 + cs, 0.1)]
        body = [tuple(max(0, min(1, c)) for c in r) for r in body]
        nose = [(1.0, 0.95, 0.6), (1.0, 0.8, 0.3), (0.9, 0.6, 0.15)]
        glass = [(0.9, 0.95, 1.0), (0.6, 0.8, 0.95), (0.3, 0.5, 0.8)]
        dark = (0.6, 0.2 + cs, 0.08)
        
        self.fill_poly(img, [
            (12, 2), (6, 10), (4, 18), (8, 22),
            (16, 22), (20, 18), (18, 10)
        ], body, 0.2, 0.35)
        self.fill_poly(img, [
            (12, 2), (9, 8), (15, 8)
        ], nose, 0.3, 0.25)
        self.fill_ellipse(img, 12, 14, 1.8, 2.0, glass)
        self.put(img, 12, 13, (0.95, 1.0, 1.0))
        self.fill_poly(img, [(2, 16), (6, 14), (6, 20), (2, 18)], body)
        self.fill_poly(img, [(22, 16), (18, 14), (18, 20), (22, 18)], body)
        self.put(img, 2, 16, dark)
        self.put(img, 2, 17, dark)
        self.put(img, 21, 16, dark)
        self.put(img, 21, 17, dark)
        self.fill_poly(img, [(8, 4), (10, 4), (10, 8), (8, 8)], body)
        self.fill_poly(img, [(14, 4), (16, 4), (16, 8), (14, 8)], body)
        self.put(img, 12, 3, (1, 0.9, 0.3))
        self.put(img, 11, 4, (1, 0.7, 0.2, 0.8))
        self.put(img, 13, 4, (1, 0.7, 0.2, 0.8))
        for y in range(8, 18):
            self.put(img, 8, y, dark)
            self.put(img, 16, y, dark)
        
        self.outline(img)
        return img
    
    def generate_enemy_bomber(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(44, 24)
        cs = self.rng.uniform(-0.1, 0.1)
        body = [(0.85, 0.55 + cs, 1.0), (0.6, 0.3 + cs, 0.8), (0.4, 0.18 + cs, 0.55)]
        body = [tuple(max(0, min(1, c)) for c in r) for r in body]
        wing = [(0.75, 0.45 + cs, 0.9), (0.5, 0.25 + cs, 0.7), (0.32, 0.15 + cs, 0.5)]
        wing = [tuple(max(0, min(1, c)) for c in r) for r in wing]
        glass = [(0.8, 0.9, 1.0), (0.4, 0.6, 0.85), (0.2, 0.35, 0.65)]
        dark = (0.35, 0.15 + cs, 0.5)
        
        self.fill_poly(img, [
            (12, 7), (32, 7), (36, 12), (32, 17), (12, 17)
        ], body, 0.25, 0.3)
        self.fill_poly(img, [
            (32, 9), (38, 12), (32, 15)
        ], [(0.9, 0.65, 1.0), (0.7, 0.4, 0.9), (0.5, 0.25, 0.7)])
        self.fill_ellipse(img, 34, 12, 1.8, 1.5, glass)
        self.put(img, 33, 11, (0.9, 0.95, 1.0))
        self.fill_poly(img, [(4, 9), (12, 9), (12, 15), (4, 15)], wing)
        self.fill_poly(img, [(32, 9), (40, 9), (40, 15), (32, 15)], wing)
        self.put(img, 4, 9, dark)
        self.put(img, 4, 10, dark)
        self.put(img, 4, 14, dark)
        self.put(img, 4, 15, dark)
        self.put(img, 39, 9, dark)
        self.put(img, 39, 10, dark)
        self.put(img, 39, 14, dark)
        self.put(img, 39, 15, dark)
        self.fill_ellipse(img, 6, 12, 1.5, 2.0, self.flat(dark))
        self.fill_ellipse(img, 37, 12, 1.5, 2.0, self.flat(dark))
        self.put(img, 6, 11, (1, 0.9, 0.3))
        self.put(img, 6, 12, (1, 0.9, 0.3))
        self.put(img, 37, 11, (1, 0.9, 0.3))
        self.put(img, 37, 12, (1, 0.9, 0.3))
        self.fill_rect(img, 18, 13, 8, 3, self.flat(dark))
        self.put(img, 20, 14, (0.9, 0.9, 0.3))
        self.put(img, 21, 14, (0.9, 0.9, 0.3))
        self.put(img, 22, 14, (0.9, 0.9, 0.3))
        self.put(img, 23, 14, (0.9, 0.9, 0.3))
        self.fill_poly(img, [(8, 10), (12, 10), (12, 14), (8, 14)], wing)
        self.fill_poly(img, [(8, 8), (10, 8), (10, 10), (8, 10)], body)
        self.fill_poly(img, [(8, 14), (10, 14), (10, 16), (8, 16)], body)
        for x in range(14, 30):
            self.put(img, x, 7, dark)
            self.put(img, x, 16, dark)
        for x in range(16, 28, 3):
            self.put(img, x, 9, (0.9, 0.7, 1.0))
            self.put(img, x, 15, (0.9, 0.7, 1.0))
        
        self.outline(img)
        return img
    
    def generate_enemy_weaver(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(28, 28)
        cs = self.rng.uniform(-0.1, 0.1)
        body = [(0.7, 1.0 + cs, 0.6), (0.4, 0.9 + cs, 0.3), (0.25, 0.6 + cs, 0.2)]
        body = [tuple(max(0, min(1, c)) for c in r) for r in body]
        core = [(0.9, 1.0 + cs, 0.8), (0.6, 0.95 + cs, 0.5), (0.4, 0.7 + cs, 0.3)]
        core = [tuple(max(0, min(1, c)) for c in r) for r in core]
        glass = [(0.95, 1.0, 0.95), (0.7, 0.9, 0.75), (0.4, 0.65, 0.5)]
        dark = (0.2, 0.5, 0.15)
        
        self.fill_poly(img, [
            (14, 2), (26, 14), (14, 26), (2, 14)
        ], body, 0.25, 0.3)
        self.fill_poly(img, [
            (14, 8), (20, 14), (14, 20), (8, 14)
        ], core, 0.3, 0.3)
        self.fill_ellipse(img, 14, 14, 2.0, 2.0, glass)
        self.put(img, 13, 13, (0.95, 1.0, 0.95))
        self.put(img, 14, 13, (0.95, 1.0, 0.95))
        self.put(img, 15, 13, (0.95, 1.0, 0.95))
        self.fill_poly(img, [(2, 12), (6, 12), (6, 16), (2, 16)], body)
        self.fill_poly(img, [(22, 12), (26, 12), (26, 16), (22, 16)], body)
        self.put(img, 2, 13, (0.8, 1.0, 0.6))
        self.put(img, 2, 14, (0.8, 1.0, 0.6))
        self.put(img, 25, 13, (0.8, 1.0, 0.6))
        self.put(img, 25, 14, (0.8, 1.0, 0.6))
        self.put(img, 13, 2, (0.8, 1.0, 0.6))
        self.put(img, 14, 2, (0.8, 1.0, 0.6))
        self.put(img, 15, 2, (0.8, 1.0, 0.6))
        self.put(img, 13, 25, (0.8, 1.0, 0.6))
        self.put(img, 14, 25, (0.8, 1.0, 0.6))
        self.put(img, 15, 25, (0.8, 1.0, 0.6))
        for y in range(12, 16):
            self.put(img, 11, y, (0.8, 1.0, 0.6))
            self.put(img, 16, y, (0.8, 1.0, 0.6))
        for x in range(12, 16):
            self.put(img, x, 11, (0.8, 1.0, 0.6))
            self.put(img, x, 16, (0.8, 1.0, 0.6))
        for y in range(6, 22):
            if y != 14:
                self.put(img, 8, y, dark)
                self.put(img, 19, y, dark)
        
        self.outline(img)
        return img
    
    def generate_boss_core(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(96, 72)
        cs = self.rng.uniform(-0.06, 0.06)
        hull = [(0.62 + cs, 0.66 + cs, 0.74), (0.42 + cs, 0.46 + cs, 0.55), (0.24 + cs, 0.27 + cs, 0.35)]
        hull = [tuple(max(0, min(1, c)) for c in r) for r in hull]
        deck = [(0.4 + cs, 0.44 + cs, 0.52), (0.3 + cs, 0.33 + cs, 0.4), (0.19 + cs, 0.21 + cs, 0.27)]
        deck = [tuple(max(0, min(1, c)) for c in r) for r in deck]
        rib = self.flat((0.2, 0.22, 0.29))
        core = [(1.0, 0.6, 0.55), (0.9, 0.15, 0.2), (0.5, 0.05, 0.1)]
        trim = self.flat((0.75, 0.16, 0.2))
        
        self.fill_poly(img, [
            (8, 4), (87, 4), (93, 20), (93, 44),
            (80, 58), (60, 66), (35, 66), (15, 58),
            (2, 44), (2, 20),
        ], hull, 0.22, 0.26)
        self.fill_rect(img, 24, 2, 48, 10, deck)
        for x in [16, 32, 62, 78]:
            self.fill_rect(img, x, 8, 2, 42, rib)
        for side_x in [8, 80]:
            self.fill_rect(img, side_x, 24, 8, 14, self.flat((0.15, 0.16, 0.22)))
            for yy in range(26, 38, 3):
                self.fill_rect(img, side_x + 1, yy, 6, 1, self.flat((0.32, 0.35, 0.42)))
        self.fill_rect(img, 26, 60, 44, 3, trim)
        self.fill_ellipse(img, 47.5, 38.0, 14.5, 14.5, self.flat((0.16, 0.18, 0.24)))
        self.fill_ellipse(img, 47.5, 38.0, 10.5, 10.5, core, 0.28, 0.3)
        self.put(img, 43, 31, (1.0, 0.85, 0.8))
        self.put(img, 44, 31, (1.0, 0.85, 0.8))
        self.put(img, 43, 32, (1.0, 0.85, 0.8))
        for bx, by in [(28, 8), (67, 8), (22, 52), (73, 52)]:
            self.put(img, bx, by, (0.85, 0.88, 0.95))
        
        self.mirror_h(img)
        self.outline(img)
        return img
    
    def generate_boss_gun(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(28, 28)
        cs = self.rng.uniform(-0.08, 0.08)
        armor = [(0.95, 0.62 + cs, 0.3), (0.75, 0.42 + cs, 0.16), (0.45, 0.24 + cs, 0.08)]
        armor = [tuple(max(0, min(1, c)) for c in r) for r in armor]
        barrel = [(0.55, 0.57, 0.64), (0.4, 0.42, 0.5), (0.25, 0.27, 0.34)]
        
        self.fill_poly(img, [
            (8, 2), (19, 2), (25, 8), (25, 17),
            (19, 23), (8, 23), (2, 17), (2, 8),
        ], armor, 0.26, 0.28)
        self.fill_ellipse(img, 13.5, 12.0, 6.0, 6.0, self.flat((0.35, 0.18, 0.06)))
        self.fill_ellipse(img, 13.5, 11.5, 3.5, 3.5, [(1.0, 0.8, 0.5), (0.9, 0.55, 0.25), (0.6, 0.32, 0.1)])
        self.fill_rect(img, 11, 16, 5, 10, barrel)
        self.fill_rect(img, 10, 25, 7, 2, self.flat((0.18, 0.2, 0.26)))
        for bx, by in [(5, 5), (22, 5), (5, 19), (22, 19)]:
            self.put(img, bx, by, (1.0, 0.85, 0.6))
        
        self.outline(img)
        return img
    
    def generate_alien_grunt(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(24, 24)
        body_shift = self.rng.uniform(-0.1, 0.1)
        shell_shift = self.rng.uniform(-0.1, 0.1)
        radius_vary = self.rng.uniform(-1.0, 1.0)
        leg_offset = self.rng.randint(-2, 2)

        body = [(0.4, 0.9 + body_shift, 0.3), (0.2, 0.7 + body_shift, 0.15), (0.1, 0.4 + body_shift, 0.08)]
        body = [tuple(max(0, min(1, c)) for c in ramp) for ramp in body]
        shell = [(0.6, 0.95 + shell_shift, 0.5), (0.35, 0.75 + shell_shift, 0.25), (0.2, 0.5 + shell_shift, 0.15)]
        shell = [tuple(max(0, min(1, c)) for c in ramp) for ramp in shell]
        eye = [(1.0, 1.0, 0.3), (0.9, 0.8 + body_shift, 0.1), (0.6, 0.5 + body_shift, 0.05)]

        self.fill_ellipse(img, 11.5, 12.0, 8.0 + radius_vary, 9.0 + radius_vary * 0.5, body, 0.25, 0.3)
        self.fill_poly(img, [
            (4, 6), (11.5, 3), (19, 6), (17, 10), (11.5, 8), (6, 10)
        ], shell, 0.3, 0.3)
        self.fill_poly(img, [
            (3, 14 + leg_offset), (6, 18), (4, 22), (2, 18)
        ], body)
        self.fill_poly(img, [
            (21, 14 + leg_offset), (18, 18), (20, 22), (22, 18)
        ], body)
        self.fill_ellipse(img, 11.5, 14.0, 3.0, 2.5, eye, 0.35, 0.3)
        self.put(img, 10, 13, (1.0, 1.0, 1.0))
        self.put(img, 13, 13, (1.0, 1.0, 1.0))

        self.outline(img)
        return img
    
    def generate_alien_drone(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(20, 20)
        cs = self.rng.uniform(-0.1, 0.1)
        body = [(0.8, 0.3 + cs, 0.9), (0.6, 0.15 + cs, 0.7), (0.35, 0.08 + cs, 0.45)]
        body = [tuple(max(0, min(1, c)) for c in r) for r in body]
        wing = [(0.9, 0.5 + cs, 1.0), (0.7, 0.3 + cs, 0.8), (0.45, 0.18 + cs, 0.55)]
        wing = [tuple(max(0, min(1, c)) for c in r) for r in wing]
        core = [(1.0, 0.8 + cs, 1.0), (0.9, 0.5 + cs, 0.9), (0.6, 0.3 + cs, 0.6)]
        core = [tuple(max(0, min(1, c)) for c in r) for r in core]
        
        self.fill_poly(img, [
            (10, 2), (16, 8), (14, 16), (6, 16), (4, 8)
        ], body, 0.25, 0.3)
        self.fill_poly(img, [
            (2, 10), (6, 8), (6, 14), (2, 12)
        ], wing)
        self.fill_poly(img, [
            (18, 10), (14, 8), (14, 14), (18, 12)
        ], wing)
        self.fill_ellipse(img, 10.0, 10.0, 2.5, 2.5, core, 0.35, 0.3)
        
        self.outline(img)
        return img
    
    def generate_mech_grunt(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(28, 28)
        color_shift = self.rng.uniform(-0.08, 0.08)
        width_vary = self.rng.randint(-2, 2)
        light_color = self.rng.choice([(1.0, 0.3, 0.3), (0.3, 1.0, 0.3), (0.3, 0.3, 1.0), (1.0, 1.0, 0.2)])

        armor = [(0.7 + color_shift, 0.75 + color_shift, 0.8), (0.45 + color_shift, 0.5 + color_shift, 0.55), (0.25 + color_shift, 0.28 + color_shift, 0.32)]
        armor = [tuple(max(0, min(1, c)) for c in ramp) for ramp in armor]
        joint = [(0.5 + color_shift, 0.55 + color_shift, 0.6), (0.35 + color_shift, 0.38 + color_shift, 0.42), (0.2 + color_shift, 0.22 + color_shift, 0.25)]
        joint = [tuple(max(0, min(1, c)) for c in ramp) for ramp in joint]

        body_w = 12 + width_vary
        arm_x = 8 + width_vary
        self.fill_rect(img, 8, 4, body_w, 16, armor, 0.25, 0.3)
        self.fill_rect(img, 6, 8, 2, 8, joint)
        self.fill_rect(img, 6 + body_w + 2, 8, 2, 8, joint)
        self.fill_rect(img, 10 + width_vary, 20, 8, 6, armor)
        self.fill_rect(img, 12 + width_vary, 2, 4, 3, joint)
        self.put(img, 13 + width_vary, 8, light_color)
        self.put(img, 14 + width_vary, 8, light_color)
        self.fill_rect(img, 9 + width_vary, 12, 10, 2, self.flat((0.3, 0.32, 0.36)))

        self.outline(img)
        return img
    
    def generate_mech_drone(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(22, 22)
        cs = self.rng.uniform(-0.08, 0.08)
        body = [(0.6 + cs, 0.65 + cs, 0.7), (0.4 + cs, 0.45 + cs, 0.5), (0.22 + cs, 0.25 + cs, 0.28)]
        body = [tuple(max(0, min(1, c)) for c in r) for r in body]
        accent = [(0.3, 0.8 + cs, 1.0), (0.15, 0.6 + cs, 0.8), (0.08, 0.35 + cs, 0.5)]
        accent = [tuple(max(0, min(1, c)) for c in r) for r in accent]
        
        self.fill_poly(img, [
            (11, 2), (18, 8), (16, 18), (6, 18), (4, 8)
        ], body, 0.25, 0.3)
        self.fill_rect(img, 3, 10, 3, 6, body)
        self.fill_rect(img, 16, 10, 3, 6, body)
        self.fill_ellipse(img, 11.0, 11.0, 3.0, 3.0, accent, 0.35, 0.3)
        self.put(img, 10, 10, (1.0, 1.0, 1.0))
        self.put(img, 12, 10, (1.0, 1.0, 1.0))
        
        self.outline(img)
        return img
    
    def generate_swarm_enemy(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(12, 12)
        cs = self.rng.uniform(-0.1, 0.1)
        body = [(1.0, 0.6 + cs, 0.2), (0.9, 0.4 + cs, 0.1), (0.6, 0.25 + cs, 0.05)]
        body = [tuple(max(0, min(1, c)) for c in r) for r in body]
        
        self.fill_poly(img, [
            (6, 1), (10, 6), (6, 11), (2, 6)
        ], body, 0.25, 0.3)
        self.put(img, 5, 5, (1.0, 1.0, 0.3))
        self.put(img, 7, 5, (1.0, 1.0, 0.3))
        
        self.outline(img)
        return img
    
    def generate_boss_alien(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(80, 64)
        cs = self.rng.uniform(-0.08, 0.08)
        body = [(0.5, 0.9 + cs, 0.4), (0.3, 0.7 + cs, 0.2), (0.15, 0.45 + cs, 0.1)]
        body = [tuple(max(0, min(1, c)) for c in r) for r in body]
        shell = [(0.7, 1.0 + cs, 0.6), (0.45, 0.8 + cs, 0.3), (0.25, 0.55 + cs, 0.18)]
        shell = [tuple(max(0, min(1, c)) for c in r) for r in shell]
        eye = [(1.0, 1.0, 0.4), (0.95, 0.85 + cs, 0.2), (0.7, 0.6 + cs, 0.1)]
        tentacle = [(0.6, 0.95 + cs, 0.5), (0.4, 0.75 + cs, 0.3), (0.22, 0.5 + cs, 0.18)]
        tentacle = [tuple(max(0, min(1, c)) for c in r) for r in tentacle]
        
        self.fill_ellipse(img, 40.0, 32.0, 30.0, 25.0, body, 0.22, 0.28)
        self.fill_poly(img, [
            (15, 12), (40, 5), (65, 12), (60, 25), (40, 20), (20, 25)
        ], shell, 0.3, 0.3)
        self.fill_ellipse(img, 40.0, 35.0, 12.0, 10.0, eye, 0.35, 0.3)
        self.put(img, 35, 32, (1.0, 1.0, 1.0))
        self.put(img, 45, 32, (1.0, 1.0, 1.0))
        
        for i in range(5):
            x_offset = 15 + i * 12
            self.fill_poly(img, [
                (x_offset, 50), (x_offset + 3, 58), (x_offset + 6, 50)
            ], tentacle)
        
        self.mirror_h(img)
        self.outline(img)
        return img
    
    def generate_boss_mech(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(88, 72)
        cs = self.rng.uniform(-0.06, 0.06)
        armor = [(0.65 + cs, 0.7 + cs, 0.75), (0.42 + cs, 0.47 + cs, 0.52), (0.24 + cs, 0.27 + cs, 0.3)]
        armor = [tuple(max(0, min(1, c)) for c in r) for r in armor]
        joint = [(0.5 + cs, 0.55 + cs, 0.6), (0.35 + cs, 0.38 + cs, 0.42), (0.2 + cs, 0.22 + cs, 0.25)]
        joint = [tuple(max(0, min(1, c)) for c in r) for r in joint]
        core = [(1.0, 0.4 + cs, 0.4), (0.85, 0.2 + cs, 0.2), (0.55, 0.1 + cs, 0.1)]
        
        self.fill_rect(img, 20, 8, 48, 50, armor, 0.22, 0.28)
        self.fill_rect(img, 8, 20, 12, 32, armor)
        self.fill_rect(img, 68, 20, 12, 32, armor)
        self.fill_rect(img, 32, 2, 24, 8, joint)
        self.fill_rect(img, 30, 58, 28, 10, armor)
        self.fill_ellipse(img, 44.0, 33.0, 10.0, 10.0, core, 0.3, 0.3)
        self.put(img, 40, 30, (1.0, 1.0, 1.0))
        self.put(img, 48, 30, (1.0, 1.0, 1.0))
        
        for x in [24, 36, 48, 60]:
            self.fill_rect(img, x, 12, 2, 42, joint)
        
        self.outline(img)
        return img
    
    def generate_vulcan_bullet(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(6, 14)
        warmth = self.rng.uniform(-0.15, 0.15)
        self.fill_ellipse(img, 2.5, 4.0, 2.5, 3.8, [(1, 1, 0.95), (1, 0.95 + warmth, 0.5), (0.95, 0.7 + warmth, 0.2)], 0.35, 0.3)
        for i in range(6):
            a = 0.75 - i * 0.12
            self.put(img, 2, 8 + i, (1.0, 0.7 + warmth, 0.25, a))
            self.put(img, 3, 8 + i, (1.0, 0.7 + warmth, 0.25, a))
        return img
    
    def generate_laser_bolt(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(8, 32)
        hue_shift = self.rng.uniform(-0.1, 0.1)
        core = (1.0, 0.4 + hue_shift, 0.9)
        core_dim = (1.0, 0.45 + hue_shift, 0.9)
        center = (1.0, 0.95 + hue_shift, 1.0)
        tip = (1.0, 0.6 + hue_shift, 0.95)
        self.fill_rect(img, 1, 4, 1, 24, self.flat((core[0], core[1], core[2], 0.4)))
        self.fill_rect(img, 6, 4, 1, 24, self.flat((core[0], core[1], core[2], 0.4)))
        self.fill_rect(img, 2, 2, 1, 28, self.flat((core_dim[0], core_dim[1], core_dim[2], 0.85)))
        self.fill_rect(img, 5, 2, 1, 28, self.flat((core_dim[0], core_dim[1], core_dim[2], 0.85)))
        self.fill_rect(img, 3, 1, 2, 30, self.flat(center))
        self.put(img, 3, 0, tip)
        self.put(img, 4, 0, tip)
        self.put(img, 3, 31, (tip[0], tip[1], tip[2], 0.6))
        self.put(img, 4, 31, (tip[0], tip[1], tip[2], 0.6))
        return img
    
    def generate_spread_bullet(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(10, 10)
        shift = self.rng.uniform(-0.1, 0.1)
        ramp = [(0.85 + shift, 1, 1), (0.3 + shift, 0.85, 1), (0.1 + shift, 0.5, 0.85)]
        ramp = [tuple(max(0, min(1, c)) for c in r) for r in ramp]
        self.fill_poly(img, [(5, 0.5), (9.5, 5), (5, 9.5), (0.5, 5)], ramp, 0.32, 0.32)
        self.fill_ellipse(img, 5.0, 5.0, 1.8, 1.8, self.flat((1, 1, 1)))
        return img
    
    def generate_missile(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(10, 18)
        shift = self.rng.uniform(-0.08, 0.08)
        body = [(0.75 + shift, 0.78 + shift, 0.85), (0.55 + shift, 0.58 + shift, 0.66), (0.36 + shift, 0.39 + shift, 0.46)]
        body = [tuple(max(0, min(1, c)) for c in r) for r in body]
        self.fill_rect(img, 3, 4, 4, 9, body)
        self.fill_poly(img, [(5, 0.5), (3, 4), (7, 4)], self.flat((0.9, 0.25, 0.25)))
        self.fill_poly(img, [(1, 12), (3, 9), (3, 13)], self.flat((0.35, 0.38, 0.45)))
        self.fill_poly(img, [(9, 12), (7, 9), (7, 13)], self.flat((0.35, 0.38, 0.45)))
        self.put(img, 4, 13, (1, 0.95, 0.6))
        self.put(img, 5, 13, (1, 0.95, 0.6))
        self.put(img, 4, 14, (1, 0.7, 0.2))
        self.put(img, 5, 14, (1, 0.7, 0.2))
        self.put(img, 4, 15, (1, 0.5, 0.1, 0.8))
        self.put(img, 5, 15, (1, 0.5, 0.1, 0.8))
        self.put(img, 4, 16, (0.95, 0.35, 0.05, 0.5))
        return img
    
    def generate_enemy_bullet(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(10, 10)
        shift = self.rng.uniform(-0.1, 0.1)
        self.fill_ellipse(img, 4.5, 4.5, 4.4, 4.4,
            [(1.0, 0.75 + shift, 0.85), (1.0, 0.35 + shift, 0.6), (0.75, 0.15 + shift, 0.4)], 0.3, 0.3)
        self.fill_ellipse(img, 4.5, 4.5, 2.0, 2.0, self.flat((1, 1, 1)))
        self.outline(img, (0.45, 0.05, 0.25))
        return img
    
    def generate_power_up(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(20, 20)
        shift = self.rng.uniform(-0.1, 0.1)
        icon_type = self.rng.randint(0, 3)
        outer = [(1, 1, 1), (0.88 + shift, 0.9 + shift, 0.95), (0.62 + shift, 0.65 + shift, 0.78)]
        outer = [tuple(max(0, min(1, c)) for c in r) for r in outer]
        self.fill_ellipse(img, 9.5, 9.5, 9.0, 9.0, outer, 0.3, 0.3)
        self.fill_ellipse(img, 9.5, 9.5, 6.5, 6.5, self.flat((0.96, 0.97 + shift, 1.0)))
        self.put(img, 6, 5, (1, 1, 1))
        self.put(img, 7, 5, (1, 1, 1))
        self.put(img, 6, 6, (1, 1, 1))
        self.outline(img, (0.25, 0.28, 0.4))
        return img
    
    def generate_bomb(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))

        img = self.new_img(12, 16)
        cs = self.rng.uniform(-0.08, 0.08)
        self.fill_ellipse(img, 5.5, 9.0, 5.0, 5.5,
            [(0.55 + cs, 0.58 + cs, 0.66), (0.36 + cs, 0.39 + cs, 0.47), (0.2 + cs, 0.22 + cs, 0.29)], 0.28, 0.3)
        self.fill_rect(img, 5, 2, 2, 3, self.flat((0.45, 0.48, 0.55)))
        self.put(img, 5, 1, (1.0, 0.85, 0.3))
        self.put(img, 6, 0, (1.0, 0.6, 0.15))
        self.put(img, 3, 6, (0.75, 0.78, 0.86))
        self.put(img, 4, 6, (0.75, 0.78, 0.86))
        self.outline(img)
        return img
    
    def generate_explosion_sheet(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))
        
        frames = 6
        size = 32
        sheet = self.new_img(size * frames, size)
        c = (15.5, 15.5)
        
        for f in range(frames):
            img = self.new_img(size, size)
            self.rng.seed(5000 + f)
            t = f / float(frames - 1)
            
            if f < 4:
                r = min(5.0 + (15.0 - 5.0) * t * 1.6, 15.0)
                for y in range(size):
                    for x in range(size):
                        dx = x - c[0]
                        dy = y - c[1]
                        d = math.sqrt(dx * dx + dy * dy) + self.rng.uniform(-1.5, 1.5)
                        if d < r * 0.35:
                            img.putpixel((x, y), (255, 255, 242, 255))
                        elif d < r * 0.6:
                            img.putpixel((x, y), (255, 230, 102, 255))
                        elif d < r * 0.85:
                            img.putpixel((x, y), (255, 140, 31, 255))
                        elif d < r:
                            img.putpixel((x, y), (217, 64, 20, 255))
            else:
                rin = 9.0 + (13.5 - 9.0) * (f - 4)
                rout = rin + 3.0
                fade = 1.0 - (f - 4) * 0.4
                for y in range(size):
                    for x in range(size):
                        dx = x - c[0]
                        dy = y - c[1]
                        d = math.sqrt(dx * dx + dy * dy) + self.rng.uniform(-1.2, 1.2)
                        if rin <= d <= rout:
                            if self.rng.random() < 0.3:
                                img.putpixel((x, y), (102, 77, 71, int(255 * fade)))
                            else:
                                img.putpixel((x, y), (255, 115, 26, int(255 * fade)))
            
            for k in range(10 - f):
                ang = self.rng.random() * 2 * math.pi
                rad = (6.0 + (17.0 - 6.0) * t) * self.rng.uniform(0.8, 1.15)
                px = c[0] + math.cos(ang) * rad
                py = c[1] + math.sin(ang) * rad
                self.put(img, int(px), int(py), (1, 0.85, 0.3, 1.0 - t * 0.5))
            
            sheet.paste(img, (f * size, 0))
        
        return sheet
    
    def generate_spark_sheet(self, seed: Optional[int] = None) -> Image.Image:
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))
        
        sheet = self.new_img(36, 12)
        white = (1, 1, 1)
        yellow = (1, 0.9, 0.4)
        orange = (1, 0.6, 0.2)
        
        img0 = self.new_img(12, 12)
        for px, py in [(5, 5), (6, 5), (5, 6), (6, 6)]:
            self.put(img0, px, py, white)
        for px, py in [(4, 5), (4, 6), (7, 5), (7, 6), (5, 4), (6, 4), (5, 7), (6, 7)]:
            self.put(img0, px, py, yellow)
        sheet.paste(img0, (0, 0))
        
        img1 = self.new_img(12, 12)
        for px, py in [(5, 5), (6, 5), (5, 6), (6, 6)]:
            self.put(img1, px, py, white)
        for px, py in [(3, 5), (3, 6), (8, 5), (8, 6), (5, 3), (6, 3), (5, 8), (6, 8)]:
            self.put(img1, px, py, yellow)
        for px, py in [(3, 3), (8, 3), (3, 8), (8, 8)]:
            self.put(img1, px, py, orange)
        sheet.paste(img1, (12, 0))
        
        img2 = self.new_img(12, 12)
        for px, py in [(2, 5), (2, 6), (9, 5), (9, 6), (5, 2), (6, 2), (5, 9), (6, 9)]:
            self.put(img2, px, py, (1, 0.6, 0.2, 0.8))
        for px, py in [(2, 2), (9, 2), (2, 9), (9, 9)]:
            self.put(img2, px, py, (1, 0.5, 0.15, 0.5))
        sheet.paste(img2, (24, 0))
        
        return sheet
    
    def generate_background_stars(self, seed: Optional[int] = None, width: int = 240, height: int = 360) -> Image.Image:
        self.rng.seed(seed if seed is not None else 42)
        
        img = self.new_img(width, height)
        for y in range(height):
            for x in range(width):
                img.putpixel((x, y), (3, 5, 13, 255))
        
        nebula_colors = [(31, 13, 56), (13, 26, 56), (41, 13, 36)]
        for i in range(10):
            cx = self.rng.randint(0, width - 1)
            cy = self.rng.randint(0, height - 1)
            r = self.rng.randint(28, 70)
            col = nebula_colors[self.rng.randint(0, len(nebula_colors) - 1)]
            strength = self.rng.uniform(0.35, 0.8)
            
            for y in range(max(0, cy - r), min(height, cy + r + 1)):
                for x in range(max(0, cx - r), min(width, cx + r + 1)):
                    dx = (x - cx) / r
                    dy = (y - cy) / r
                    d = math.sqrt(dx * dx + dy * dy)
                    if d < 1.0:
                        a = (1.0 - d) * (1.0 - d) * strength
                        px = x % width
                        py = y % height
                        existing = img.getpixel((px, py))
                        new_r = min(existing[0] + int(col[0] * a), 255)
                        new_g = min(existing[1] + int(col[1] * a), 255)
                        new_b = min(existing[2] + int(col[2] * a), 255)
                        img.putpixel((px, py), (new_r, new_g, new_b, 255))
        
        for i in range(130):
            b = self.rng.uniform(0.12, 0.4)
            x = self.rng.randint(0, width - 1)
            y = self.rng.randint(0, height - 1)
            img.putpixel((x, y), (int(b * 255), int(b * 255), int(b * 1.15 * 255), 255))
        
        for i in range(22):
            b2 = self.rng.uniform(0.4, 0.55)
            x = self.rng.randint(0, width - 1)
            y = self.rng.randint(0, height - 1)
            img.putpixel((x, y), (int(b2 * 255), int(b2 * 255), int(b2 * 1.1 * 255), 255))
        
        return img
    
    def apply_color_tint(self, img: Image.Image, primary_color: Optional[tuple] = None, 
                         secondary_color: Optional[tuple] = None, accent_color: Optional[tuple] = None) -> Image.Image:
        """Apply color tinting to a sprite based on luminance"""
        if not any([primary_color, secondary_color, accent_color]):
            return img
        
        result = img.copy()
        pixels = result.load()
        
        for y in range(result.height):
            for x in range(result.width):
                r, g, b, a = pixels[x, y]
                if a == 0:
                    continue
                
                # Calculate luminance
                luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
                
                # Apply color based on luminance range
                if luminance > 0.7 and accent_color:
                    # Bright areas get accent color
                    new_r = int(r * accent_color[0])
                    new_g = int(g * accent_color[1])
                    new_b = int(b * accent_color[2])
                elif luminance > 0.4 and secondary_color:
                    # Mid-tones get secondary color
                    new_r = int(r * secondary_color[0])
                    new_g = int(g * secondary_color[1])
                    new_b = int(b * secondary_color[2])
                elif primary_color:
                    # Dark areas get primary color
                    new_r = int(r * primary_color[0])
                    new_g = int(g * primary_color[1])
                    new_b = int(b * primary_color[2])
                else:
                    continue
                
                # Clamp values
                new_r = max(0, min(255, new_r))
                new_g = max(0, min(255, new_g))
                new_b = max(0, min(255, new_b))
                
                pixels[x, y] = (new_r, new_g, new_b, a)
        
        return result
    
    def generate_player_animated(self, seed: Optional[int] = None, frames: int = 4) -> Image.Image:
        """Generate animated player ship with engine thrust animation"""
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))
        
        base_ship = self.generate_player_ship(seed)
        frame_width = base_ship.width
        frame_height = base_ship.height
        
        sheet = self.new_img(frame_width * frames, frame_height)
        
        for i in range(frames):
            frame = base_ship.copy()
            
            # Add engine thrust animation
            thrust_length = 4 + (i % 2) * 3  # Alternates between 4 and 7 pixels
            thrust_colors = [
                (1.0, 0.9, 0.3, 0.9),  # Bright yellow
                (1.0, 0.6, 0.1, 0.7),  # Orange
                (1.0, 0.3, 0.05, 0.5)  # Red-orange
            ]
            
            # Draw thrust flames
            for y_offset in range(thrust_length):
                alpha = 0.9 - (y_offset * 0.15)
                color_idx = min(y_offset // 2, len(thrust_colors) - 1)
                color = thrust_colors[color_idx]
                
                # Left engine
                self.put(frame, 13, 30 + y_offset, (color[0], color[1], color[2], color[3]))
                self.put(frame, 14, 30 + y_offset, (color[0], color[1], color[2], color[3]))
                
                # Right engine
                self.put(frame, 17, 30 + y_offset, (color[0], color[1], color[2], color[3]))
                self.put(frame, 18, 30 + y_offset, (color[0], color[1], color[2], color[3]))
            
            sheet.paste(frame, (i * frame_width, 0))
        
        return sheet
    
    def generate_enemy_animated(self, enemy_type: str, seed: Optional[int] = None, frames: int = 4) -> Image.Image:
        """Generate animated enemy sprite with idle/firing animation"""
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))
        
        # Map enemy types to their generation functions
        enemy_map = {
            "enemy_grunt": self.generate_enemy_grunt,
            "enemy_drone": self.generate_enemy_drone,
            "enemy_turret": self.generate_enemy_turret,
            "alien_grunt": self.generate_alien_grunt,
            "mech_grunt": self.generate_mech_grunt,
        }
        
        if enemy_type not in enemy_map:
            raise ValueError(f"Animation not available for {enemy_type}")
        
        base_enemy = enemy_map[enemy_type](seed)
        frame_width = base_enemy.width
        frame_height = base_enemy.height
        
        sheet = self.new_img(frame_width * frames, frame_height)
        
        for i in range(frames):
            frame = base_enemy.copy()
            
            # Add subtle pulsing animation
            pulse_intensity = 0.1 + (i / frames) * 0.2
            
            # Add glow effect to specific pixels based on enemy type
            if enemy_type in ["enemy_turret", "mech_grunt"]:
                # Turret/mech: pulse the weapon/core
                glow_color = (1.0, 0.5, 0.2, pulse_intensity)
                center_x = frame_width // 2
                center_y = frame_height // 2
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        if 0 <= center_x + dx < frame_width and 0 <= center_y + dy < frame_height:
                            self.put(frame, center_x + dx, center_y + dy, glow_color)
            else:
                # Other enemies: subtle body pulse
                pixels = frame.load()
                for y in range(frame_height):
                    for x in range(frame_width):
                        r, g, b, a = pixels[x, y]
                        if a > 0:
                            # Slight brightness variation
                            brightness = 1.0 + (pulse_intensity * 0.3 * ((i % 2) * 2 - 1))
                            new_r = min(255, int(r * brightness))
                            new_g = min(255, int(g * brightness))
                            new_b = min(255, int(b * brightness))
                            pixels[x, y] = (new_r, new_g, new_b, a)
            
            sheet.paste(frame, (i * frame_width, 0))
        
        return sheet
    
    def generate_firing_animation(self, sprite_type: str, seed: Optional[int] = None, frames: int = 6) -> Image.Image:
        """Generate firing animation with muzzle flash"""
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))
        
        # Get base sprite
        sprite_map = {
            "player": self.generate_player_ship,
            "enemy_turret": self.generate_enemy_turret,
            "mech_grunt": self.generate_mech_grunt,
        }
        
        if sprite_type not in sprite_map:
            raise ValueError(f"Firing animation not available for {sprite_type}")
        
        base_sprite = sprite_map[sprite_type](seed)
        frame_width = base_sprite.width
        frame_height = base_sprite.height
        
        sheet = self.new_img(frame_width * frames, frame_height)
        
        for i in range(frames):
            frame = base_sprite.copy()
            
            # Add muzzle flash in early frames
            if i < 3:
                flash_intensity = 1.0 - (i * 0.3)
                flash_size = 3 + i
                
                # Determine flash position based on sprite type
                if sprite_type == "player":
                    flash_x = frame_width // 2
                    flash_y = 2
                else:
                    flash_x = frame_width // 2
                    flash_y = frame_height - 3
                
                # Draw flash
                for dx in range(-flash_size, flash_size + 1):
                    for dy in range(-flash_size, flash_size + 1):
                        distance = (dx * dx + dy * dy) ** 0.5
                        if distance <= flash_size:
                            alpha = flash_intensity * (1.0 - distance / flash_size)
                            px, py = flash_x + dx, flash_y + dy
                            if 0 <= px < frame_width and 0 <= py < frame_height:
                                self.put(frame, px, py, (1.0, 0.9, 0.3, alpha))
            
            sheet.paste(frame, (i * frame_width, 0))
        
        return sheet
    
    def generate_damaged_state(self, sprite_type: str, seed: Optional[int] = None) -> Image.Image:
        """Generate damaged version of a sprite"""
        self.rng.seed(seed if seed is not None else int(time.time_ns() & 0xFFFFFFFF))
        
        # Get base sprite
        sprite_map = {
            "player": self.generate_player_ship,
            "enemy_grunt": self.generate_enemy_grunt,
            "enemy_turret": self.generate_enemy_turret,
            "alien_grunt": self.generate_alien_grunt,
            "mech_grunt": self.generate_mech_grunt,
        }
        
        if sprite_type not in sprite_map:
            raise ValueError(f"Damaged state not available for {sprite_type}")
        
        base_sprite = sprite_map[sprite_type](seed)
        damaged = base_sprite.copy()
        
        pixels = damaged.load()
        width, height = damaged.size
        
        # Add damage effects
        for _ in range(15):  # 15 damage spots
            x = self.rng.randint(0, width - 1)
            y = self.rng.randint(0, height - 1)
            
            # Only damage non-transparent pixels
            if pixels[x, y][3] > 0:
                # Darken the pixel
                r, g, b, a = pixels[x, y]
                pixels[x, y] = (r // 2, g // 2, b // 2, a)
                
                # Add smoke/fire effect
                if self.rng.random() < 0.3:
                    smoke_color = (0.3, 0.3, 0.3, 0.6)
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            px, py = x + dx, y + dy
                            if 0 <= px < width and 0 <= py < height:
                                self.put(damaged, px, py, smoke_color)
        
        return damaged
