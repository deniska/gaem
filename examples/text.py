import gaem


class Game(gaem.Game):
    def on_load(self):
        self.font = gaem.load_font('assets/LondrinaSolid-Regular.ttf', 100)
        self.img = self.font.render_text_to_image(
            'Hello world', color=(255, 255, 0)
        )

        self.img.set_position(90, 100)

    def on_draw(self):
        self.img.draw()

    def on_keydown(self, event):
        if event.scancode == 'escape':
            gaem.quit()
            return


if __name__ == '__main__':
    gaem.run(Game(), title='Text example')
