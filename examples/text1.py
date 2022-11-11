import gaem


class Game(gaem.Game):
    def on_load(self):
        gaem.set_background_color(50, 50, 50)
        self.font = gaem.load_font('assets/LondrinaSolid-Regular.ttf', 100)
        self.w = 500
        self.h = 100

    def on_draw(self):
        gaem.draw_rect(100, 200, self.w, self.h)
        self.font.draw('Hello world', x=100, y=200, h=self.h, w=self.w)

    def on_keydown(self, event):
        if event.scancode == 'escape':
            gaem.quit()
            return
        elif event.scancode == 'left':
            self.w -= 20
        elif event.scancode == 'right':
            self.w += 20
        elif event.scancode == 'up':
            self.h -= 20
        elif event.scancode == 'down':
            self.h += 20


if __name__ == '__main__':
    gaem.run(Game(), title='Text example', vsync=True)
