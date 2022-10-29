import gaem


class Game(gaem.Game):
    def on_update(self, dt):
        print(dt)


gaem.run(Game())
