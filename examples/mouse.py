import math

import gaem


class Game(gaem.Game):
    def on_load(self):
        self.hello_img = gaem.load_image('examples/hello.png')
        w, h = gaem.get_screen_size()
        self.x = w / 2
        self.y = h / 2
        self.angle = 0.0
        self.scale = 1.0

    def on_draw(self):
        gaem.draw(
            self.hello_img,
            x=self.x,
            y=self.y,
            cx=self.hello_img.width / 2,
            cy=self.hello_img.height / 2,
            sx=self.scale,
            sy=self.scale,
            angle=self.angle,
        )

    def on_update(self, dt):
        self.angle += 1.5 * dt
        self.angle %= math.tau

    def on_mousemotion(self, event):
        self.x = event.x
        self.y = event.y

    def on_mousedown(self, event):
        if event.button == 1:
            self.scale = 0.5
        elif event.button == 3:
            self.scale = 2.0

    def on_mouseup(self, event):
        self.scale = 1.0

    def on_keydown(self, event):
        if event.scancode == 'escape':
            gaem.quit()


gaem.run(Game(), title='Mouse example')
