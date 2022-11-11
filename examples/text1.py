import gaem


class Game(gaem.Game):
    def on_load(self):
        gaem.set_background_color(50, 50, 50)
        self.font = gaem.load_font('assets/LondrinaSolid-Regular.ttf', 100)
        self.w = 500
        self.h = 100
        self.align = gaem.TextAlign.LEFT
        self.multiline = True

    def on_draw(self):
        gaem.draw_rect(10, 20, self.w, self.h)
        if self.multiline:
            h = self.h
        else:
            h = None
        self.font.draw(
            'Hello world', x=10, y=20, w=self.w, h=h, align=self.align
        )

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
        elif event.scancode == 'q':
            self.align = gaem.TextAlign.LEFT
        elif event.scancode == 'w':
            self.align = gaem.TextAlign.CENTER
        elif event.scancode == 'e':
            self.align = gaem.TextAlign.RIGHT
        elif event.scancode == 'a':
            self.multiline = not self.multiline


if __name__ == '__main__':
    gaem.run(Game(), title='Text example', vsync=True)
