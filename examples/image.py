import random

import gaem

MAX_SPEED = 200


class Game(gaem.Game):
    def on_load(self):
        self.hello_img = gaem.load_image('examples/hello.png')
        self.x = 20
        self.y = 15
        self.reset_speed()

    def reset_speed(self):
        self.dx = random.uniform(-MAX_SPEED, MAX_SPEED)
        self.dy = random.uniform(-MAX_SPEED, MAX_SPEED)

    def on_draw(self):
        gaem.draw(self.hello_img, x=self.x, y=self.y)

    def on_update(self, dt):
        w, h = gaem.get_screen_size()
        self.x += self.dx * dt
        self.y += self.dy * dt
        if self.x < 0:
            self.x = 0
            self.dx *= -1
        if self.y < 0:
            self.y = 0
            self.dy *= -1
        if self.x > w - self.hello_img.width:
            self.x = w - self.hello_img.width
            self.dx *= -1
        if self.y > h - self.hello_img.height:
            self.y = h - self.hello_img.height
            self.dy *= -1

    def on_keydown(self, event):
        if event.scancode == 'space':
            self.reset_speed()


gaem.run(Game(), title='Logo bounce')
