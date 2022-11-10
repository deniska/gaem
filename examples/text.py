import gaem

string = 'Hello world'


class Game(gaem.Game):
    def on_load(self):
        gaem.set_background_color(127, 127, 127)
        self.font = gaem.load_font('assets/LondrinaSolid-Regular.ttf', 100)
        self.img = self.font.render_text_to_image(string, color=(255, 255, 0))

        self.img.set_position(90, 100)

    def on_draw(self):
        self.img.draw()
        self.font.draw(string, x=90, y=230, color=(0, 0, 255))

    def on_keydown(self, event):
        if event.scancode == 'escape':
            gaem.quit()
            return


if __name__ == '__main__':
    gaem.run(Game(), title='Text example', vsync=True)
