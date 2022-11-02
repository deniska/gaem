import math

import gaem

TANK_SPEED = 300
TANK_ROTATION_SPEED = 3
BULLET_SPEED = 900


class AtlasExample(gaem.Game):
    def on_load(self):
        gaem.set_background_color(237, 228, 162)
        self.atlas = gaem.load_atlas('assets/sheet_tanks.xml')
        self.pew_sound = gaem.load_sound('assets/tank_shoot.wav')
        self.move_sound = gaem.load_sound('assets/tank_move.wav')
        self.move_sound.volume = 0.8
        self.move_sound_channel = None
        w, h = gaem.get_screen_size()
        self.tank_x = w / 2
        self.tank_y = h / 2
        self.tank_angle = 0.0
        self.tank_color = 'Red'
        self.barrel_angle = 0.0
        self.bullets = []

    def on_draw(self):
        c = self.tank_color
        body = self.atlas[f'tank{c}_outline']
        barrel = self.atlas[f'barrel{c}_outline']
        body.center()
        body.draw(
            x=self.tank_x, y=self.tank_y, angle=self.tank_angle - math.tau / 4
        )
        barrel.cx = barrel.width / 2
        barrel.cy = barrel.height * 0.85
        barrel.draw(
            x=self.tank_x,
            y=self.tank_y,
            angle=self.barrel_angle - math.tau / 4,
        )
        for bullet in self.bullets:
            bullet.draw(angle=bullet.angle - math.tau / 4)

    def on_update(self, dt):
        moving = False
        if gaem.is_key_pressed('w'):
            self.tank_x += dt * TANK_SPEED * math.cos(self.tank_angle)
            self.tank_y -= dt * TANK_SPEED * math.sin(self.tank_angle)
            moving = True
        if gaem.is_key_pressed('s'):
            self.tank_x -= dt * TANK_SPEED * math.cos(self.tank_angle)
            self.tank_y += dt * TANK_SPEED * math.sin(self.tank_angle)
            moving = True
        if gaem.is_key_pressed('a'):
            self.tank_angle += dt * TANK_ROTATION_SPEED
            moving = True
        if gaem.is_key_pressed('d'):
            self.tank_angle -= dt * TANK_ROTATION_SPEED
            moving = True
        x, y = gaem.get_mouse_position()
        self.barrel_angle = math.atan2(self.tank_y - y, x - self.tank_x)
        for bullet in self.bullets:
            bullet.x += dt * BULLET_SPEED * math.cos(bullet.angle)
            bullet.y -= dt * BULLET_SPEED * math.sin(bullet.angle)
        self.bullets = [
            b for b in self.bullets if abs(b.x) < 10000 and abs(b.y) < 10000
        ]
        if moving and self.move_sound_channel is None:
            self.move_sound_channel = self.move_sound.play(looping=True)
        elif not moving and self.move_sound_channel is not None:
            self.move_sound_channel.stop()
            self.move_sound_channel = None

    def on_mousedown(self, event):
        bullet = self.atlas[f'bullet{self.tank_color}_outline'].copy()
        bullet.center()
        bullet.angle = self.barrel_angle
        bullet.x = self.tank_x
        bullet.y = self.tank_y
        self.bullets.append(bullet)
        self.pew_sound.play()

    def on_keydown(self, event):
        if event.scancode == 'escape':
            gaem.quit()
        color = {
            '1': 'Red',
            '2': 'Green',
            '3': 'Blue',
            '4': 'Beige',
            '5': 'Black',
        }.get(event.scancode)
        if color:
            self.tank_color = color


gaem.run(AtlasExample(), title='Atlas example', width=1280, height=720)
