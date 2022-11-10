import string

import gaem


class FontAtlas(gaem.Game):
    def on_load(self):
        gaem.set_background_color(127, 127, 127)
        self.font = gaem.load_font(
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 40
        )
        self.font._init_new_texture()
        self.font._ensure_glyphs('abc')
        self.b_img = self.font._glyphs['b'].copy()
        self.img = gaem.Image(self.font._texture, 512, 512)

    def on_draw(self):
        self.img.draw()

    def on_keydown(self, event):
        if event.scancode == 'escape':
            gaem.quit()
            return


if __name__ == '__main__':
    gaem.run(
        FontAtlas(),
        title='Font atlas test app',
        width=512,
        height=512,
        vsync=True,
    )
