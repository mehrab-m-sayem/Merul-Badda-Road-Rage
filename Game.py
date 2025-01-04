import OpenGL.GL as GL
import OpenGL.GLUT as GLUT
import numpy as np
import time

# Window dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 650

LANES = 10  
ROAD_WIDTH = 2 * 50  
SAFE_ZONE_HEIGHT = 50  
VEHICLE_TYPES = [
    {"width": 40, "height": 20, "speed": 1000, "color": (1.0, 0.0, 0.0), "shape": "car"},  
    {"width": 60, "height": 25, "speed": 800, "color": (1.0, 0.5, 0.0), "shape": "bus"},  
    {"width": 30, "height": 15, "speed": 1500, "color": (1.0, 1.0, 0.0), "shape": "bike"}   
]

PLAYER_SIZE = 20
PLAYER_SPEED = 50
PLAYER_COLOR = (0.0, 1.0, 0.0)

class Game:
    def __init__(self):
        self.reset_game()

    def plotting_point(self, x, y):
        GL.glBegin(GL.GL_POINTS)
        GL.glVertex2f(x, y)
        GL.glEnd()

    def zone_zero_conversion(self, x, y, zone):
        if   zone == 0: return x, y
        elif zone == 1: return y, x
        elif zone == 2: return y, -x
        elif zone == 3: return -x, y
        elif zone == 4: return -x, -y
        elif zone == 5: return -y, -x
        elif zone == 6: return -y, x
        elif zone == 7: return x, -y

    def actual_zone_conversion(self, x, y, zone):
        if   zone == 0: return x, y
        elif zone == 1: return y, x
        elif zone == 2: return -y, x
        elif zone == 3: return -x, y
        elif zone == 4: return -x, -y
        elif zone == 5: return -y, -x
        elif zone == 6: return y, -x
        elif zone == 7: return x, -y

    def draw_line(self, x1, y1, x2, y2, dashed=False):
        dx = x2 - x1
        dy = y2 - y1
        zone = 0
        if abs(dx) >= abs(dy):
            if   dx >= 0 and dy >= 0: zone = 0
            elif dx < 0 and dy >= 0: zone = 3
            elif dx < 0 and dy < 0: zone = 4
            elif dx >= 0 and dy < 0: zone = 7
        else:
            if   dx >= 0 and dy >= 0: zone = 1
            elif dx < 0 and dy >= 0: zone = 2
            elif dx < 0 and dy < 0: zone = 5
            elif dx >= 0 and dy < 0: zone = 6

        x1, y1 = self.zone_zero_conversion(x1, y1, zone)
        x2, y2 = self.zone_zero_conversion(x2, y2, zone)
        dx = x2 - x1
        dy = y2 - y1
        d = dy - (dx / 2)
        x = x1
        y = y1
        if not dashed or (x // 10) % 2:
            x_origin, y_origin = self.actual_zone_conversion(x, y, zone)
            self.plotting_point(x_origin, y_origin)
        while x < x2:
            x += 1
            if d < 0:
                d = d + dy
            else:
                d = d + (dy - dx)
                y += 1
            if not dashed or (x // 10) % 2:
                x_origin, y_origin = self.actual_zone_conversion(x, y, zone)
                self.plotting_point(x_origin, y_origin)

    def circle_drawing(self, circ_x, circ_y, r):
        x, y = 0, r
        d = 1 - r

        while x <= y:
            self.plotting_point(circ_x + x, circ_y + y)
            self.plotting_point(circ_x + y, circ_y + x)
            self.plotting_point(circ_x - y, circ_y + x)
            self.plotting_point(circ_x - x, circ_y + y)
            self.plotting_point(circ_x - x, circ_y - y)
            self.plotting_point(circ_x - y, circ_y - x)
            self.plotting_point(circ_x + y, circ_y - x)
            self.plotting_point(circ_x + x, circ_y - y)
            if d < 0:
                d += (2 * x + 3)
            else:
                d += (2 * (x - y) + 5)
                y -= 1
            x += 1

    def reset_game(self):
        self.player_pos = np.array([WINDOW_WIDTH // 2, PLAYER_SIZE])
        self.vehicles = []
        self.score = 0
        self.game_over = False
        self.pause = False
        self.last_spawn_time = time.time()
        self.spawn_interval = 2.0 
        self.player_crossed_roads = 0  
        self.can_move_vertically = True 

        self.lanes = []
        current_y = 0
        for i in range(LANES):
            if i % 2 == 1: 
                lane_height = ROAD_WIDTH
                is_road = True
            else: 
                lane_height = SAFE_ZONE_HEIGHT
                is_road = False

            self.lanes.append({
                "y": current_y,
                "height": lane_height,
                "is_road": is_road,
                "direction": 1 if i % 4 == 1 else -1 if i % 4 == 3 else 0
            })
            current_y += lane_height

    def spawn_vehicle(self):
        road_lanes = [lane for lane in self.lanes if lane["is_road"]]
        if not road_lanes:
            return

        for _ in range(2): 
            lane = np.random.choice(road_lanes)
            vehicle_type = np.random.choice(VEHICLE_TYPES)

            if lane["direction"] > 0:
                x = -vehicle_type["width"]
            else:
                x = WINDOW_WIDTH

            self.vehicles.append({
                "x": x,
                "y": lane["y"] + np.random.uniform(0, ROAD_WIDTH - vehicle_type["height"]),
                "type": vehicle_type,
                "direction": lane["direction"]
            })

    def update(self, delta_time):
        if self.game_over or self.pause:
            return

        for vehicle in self.vehicles[:]:
            vehicle["x"] += vehicle["type"]["speed"] * vehicle["direction"] * delta_time

            if (vehicle["direction"] > 0 and vehicle["x"] > WINDOW_WIDTH or
                vehicle["direction"] < 0 and vehicle["x"] + vehicle["type"]["width"] < 0):
                self.vehicles.remove(vehicle)

        current_time = time.time()
        if current_time - self.last_spawn_time >= self.spawn_interval:
            self.spawn_vehicle()
            self.last_spawn_time = current_time

        self.check_collisions()

        if self.player_pos[1] + PLAYER_SIZE >= WINDOW_HEIGHT:
            self.score += 10
            self.player_pos[1] = PLAYER_SIZE
            self.spawn_interval = max(0.5, self.spawn_interval * 0.95)  

    def check_collisions(self):
        player_rect = {
            "x1": self.player_pos[0], "y1": self.player_pos[1],
            "x2": self.player_pos[0] + PLAYER_SIZE, "y2": self.player_pos[1] + PLAYER_SIZE
        }

        for vehicle in self.vehicles:
            vehicle_rect = {
                "x1": vehicle["x"], "y1": vehicle["y"],
                "x2": vehicle["x"] + vehicle["type"]["width"],
                "y2": vehicle["y"] + vehicle["type"]["height"]
            }

            if (player_rect["x1"] < vehicle_rect["x2"] and
                player_rect["x2"] > vehicle_rect["x1"] and
                player_rect["y1"] < vehicle_rect["y2"] and
                player_rect["y2"] > vehicle_rect["y1"]):
                self.game_over = True
                print(f"Game Over! Final Score: {self.score}")

    def draw(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        for lane in self.lanes:
            if lane["is_road"]:
                GL.glColor3f(0.2, 0.2, 0.2)  
                self.draw_rectangle(0, lane["y"], WINDOW_WIDTH, lane["height"])
                self.draw_road_stripes(lane)
            else:
                GL.glColor3f(0.3, 0.6, 0.3) 
                self.draw_rectangle(0, lane["y"], WINDOW_WIDTH, lane["height"])

        for vehicle in self.vehicles:
            GL.glColor3f(*vehicle["type"]["color"])
            self.draw_vehicle(vehicle)

        GL.glColor3f(*PLAYER_COLOR)
        self.draw_rectangle(self.player_pos[0], self.player_pos[1],
                            PLAYER_SIZE, PLAYER_SIZE)

        GL.glColor3f(1.0, 1.0, 1.0)
        self.draw_text(f"Score: {self.score}", 10, WINDOW_HEIGHT - 30)

        if self.game_over:
            self.draw_text("Game Over! Press R to restart",
                           WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2)
        elif self.pause:
            self.draw_text("PAUSED", WINDOW_WIDTH//2 - 40, WINDOW_HEIGHT//2)

        GLUT.glutSwapBuffers()

    def draw_rectangle(self, x, y, width, height):
        self.draw_line(x, y, x + width, y) 
        self.draw_line(x + width, y, x + width, y + height)  
        self.draw_line(x + width, y + height, x, y + height) 
        self.draw_line(x, y + height, x, y) 

    def draw_road_stripes(self, lane):
        stripe_width = 10
        stripe_height = 5
        gap = 20
        start_y = lane["y"] + (lane["height"] / 2 - stripe_height / 2)

        GL.glColor3f(1.0, 1.0, 1.0) 
        for x in range(0, WINDOW_WIDTH, stripe_width + gap):
            self.draw_rectangle(x, start_y, stripe_width, stripe_height)

    def draw_text(self, text, x, y):
        GL.glRasterPos2f(x, y)
        for char in str(text):
            GLUT.glutBitmapCharacter(GLUT.GLUT_BITMAP_HELVETICA_18, ord(char))

    def draw_vehicle(self, vehicle):
        if vehicle["type"]["shape"] == "car":
            self.draw_car(vehicle["x"], vehicle["y"], vehicle["type"]["width"], vehicle["type"]["height"])
        elif vehicle["type"]["shape"] == "bus":
            self.draw_bus(vehicle["x"], vehicle["y"], vehicle["type"]["width"], vehicle["type"]["height"])
        elif vehicle["type"]["shape"] == "bike":
            self.draw_bike(vehicle["x"], vehicle["y"], vehicle["type"]["width"], vehicle["type"]["height"])

    def draw_car(self, x, y, width, height):
        self.draw_rectangle(x, y, width, height)
        window_width = width * 0.5
        window_height = height * 0.4
        window_x = x + (width - window_width) / 2
        window_y = y + (height - window_height) / 2
        self.draw_rectangle(window_x, window_y, window_width, window_height)

    def draw_bus(self, x, y, width, height):
        self.draw_rectangle(x, y, width, height)
        window_width = width * 0.6
        window_height = height * 0.5
        window_x = x + (width - window_width) / 2
        window_y = y + (height - window_height) / 2
        self.draw_rectangle(window_x, window_y, window_width, window_height)

    def draw_bike(self, x, y, width, height):
        self.draw_rectangle(x, y, width, height)
        wheel_radius = height * 0.3
        wheel_x1 = x + width * 0.2
        wheel_x2 = x + width * 0.8
        wheel_y = y + height * 0.2
        self.circle_drawing(wheel_x1, wheel_y, wheel_radius)
        self.circle_drawing(wheel_x2, wheel_y, wheel_radius)

# Initialize and run the game
game = Game()

def update_frame(value):
    delta_time = 1 / 60  
    game.update(delta_time)
    game.draw()
    GLUT.glutTimerFunc(int(delta_time * 1000), update_frame, 0)

def handle_keyboard_input(key, x, y):
    if game.game_over:
        if key == b'r':
            game.reset_game()
    elif game.pause:
        if key == b'p':
            game.pause = False
    else:
        if key == b'w' and game.can_move_vertically:
            game.player_pos[1] += PLAYER_SPEED
        elif key == b's' and game.can_move_vertically:
            game.player_pos[1] -= PLAYER_SPEED
        elif key == b'a':
            game.player_pos[0] -= PLAYER_SPEED
        elif key == b'd':
            game.player_pos[0] += PLAYER_SPEED
        elif key == b'p':
            game.pause = True

def reshape_window(width, height):
    GL.glViewport(0, 0, width, height)
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    GL.glOrtho(0, width, 0, height, -1, 1)
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glLoadIdentity()

def main():
    GLUT.glutInit()
    GLUT.glutInitDisplayMode(GLUT.GLUT_DOUBLE | GLUT.GLUT_RGB)
    GLUT.glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    GLUT.glutCreateWindow(b"Road Rage Game")

    GL.glClearColor(0.0, 0.0, 0.0, 1.0)
    reshape_window(WINDOW_WIDTH, WINDOW_HEIGHT)

    GLUT.glutDisplayFunc(game.draw)
    GLUT.glutKeyboardFunc(handle_keyboard_input)
    GLUT.glutTimerFunc(0, update_frame, 0)

    GLUT.glutMainLoop()

if __name__ == "__main__":
    main()
