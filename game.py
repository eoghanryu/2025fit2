import pyxel

TILE = 8
FIELD_SIZE = 16

TITLE = 0
PLAY  = 1
CLEAR = 2
GAMEOVER = 3

WALL_TILE  = (0, 0)
FLOOR_TILE = (1, 0)


SND_EAT   = 0
SND_CLEAR = 1
SND_OVER  = 2
SND_BGM   = 3
MUS_BGM   = 0


class Field:
    def __init__(self):
        self.map_id = 0

    def set_random_map(self):
        self.map_id = pyxel.rndi(0, 2)

    def is_walkable(self, tx, ty):
        tile = pyxel.tilemaps[self.map_id].pget(tx, ty)
        return tile == FLOOR_TILE

    def random_floor(self):
        while True:
            tx = pyxel.rndi(1, FIELD_SIZE - 2)
            ty = pyxel.rndi(1, FIELD_SIZE - 2)
            if self.is_walkable(tx, ty):
                return tx, ty

    def draw(self):
        pyxel.bltm(0, 0, self.map_id, 0, 0, 128, 128)


class Player:
    def __init__(self):
        self.tx = 1
        self.ty = 1

    def update(self, field):
        nx, ny = self.tx, self.ty

        if pyxel.btnp(pyxel.KEY_LEFT):
            nx -= 1
        elif pyxel.btnp(pyxel.KEY_RIGHT):
            nx += 1
        elif pyxel.btnp(pyxel.KEY_UP):
            ny -= 1
        elif pyxel.btnp(pyxel.KEY_DOWN):
            ny += 1

        if field.is_walkable(nx, ny):
            self.tx = nx
            self.ty = ny

    def draw(self):
        pyxel.blt(self.tx * TILE, self.ty * TILE, 0, 0, 8, 8, 8, 0)


class Enemy:
    def __init__(self, tx, ty):
        self.tx = tx
        self.ty = ty
        self.wait = 0

    def is_occupied(self, nx, ny, enemies):
        for e in enemies:
            if e is not self and e.tx == nx and e.ty == ny:
                return True
        return False

    def update(self, field, player, enemies, speed):
        self.wait += 1
        if self.wait < speed:
            return
        self.wait = 0

        dx = player.tx - self.tx
        dy = player.ty - self.ty

        if abs(dx) > abs(dy):
            dirs = [(1 if dx > 0 else -1, 0), (0, 1 if dy > 0 else -1)]
        else:
            dirs = [(0, 1 if dy > 0 else -1), (1 if dx > 0 else -1, 0)]

        for mx, my in dirs:
            nx = self.tx + mx
            ny = self.ty + my
            if field.is_walkable(nx, ny) and not self.is_occupied(nx, ny, enemies):
                self.tx = nx
                self.ty = ny
                return

    def draw(self):
        pyxel.blt(self.tx * TILE, self.ty * TILE, 0, 8, 8, 8, 8, 0)


class Fish:
    def __init__(self, field):
        self.tx, self.ty = field.random_floor()

    def respawn(self, field):
        self.tx, self.ty = field.random_floor()

    def draw(self):
        pyxel.blt(self.tx * TILE, self.ty * TILE, 0, 0, 16, 8, 8, 0)


class APP:
    def __init__(self):
        pyxel.init(128, 128, title="Survival Penguin")
        pyxel.load("game.pyxres")

       
        pyxel.sounds[SND_EAT].set(
            notes="C3E3G3",
            tones="TTT",
            volumes="333",
            effects="NNN",
            speed=10
        )

        pyxel.sounds[SND_CLEAR].set(
            notes="C4E4G4C4",
            tones="TTTT",
            volumes="3333",
            effects="NNNN",
            speed=8
        )

        pyxel.sounds[SND_OVER].set(
            notes="G3E3C3B2A2A1",
            tones="TTT",
            volumes="333",
            effects="NNN",
            speed=12
        )

        pyxel.sounds[SND_BGM].set(
            notes="C3E3G3E3",
            tones="TTTT",
            volumes="2222",
            effects="NNNN",
            speed=20
        )

        
        pyxel.musics[MUS_BGM].set([SND_BGM])

        self.state = TITLE

        self.field = Field()
        self.player = Player()
        self.enemies = []
        self.fish = None

        self.score = 0
        self.stage = 1
        self.enemy_speed = 10

        pyxel.run(self.update, self.draw)

    def start_game(self):
        self.field.set_random_map()
        self.player.tx, self.player.ty = 1, 1

        self.enemies = [
            Enemy(14, 14),
            Enemy(14, 1),
        ]

        self.fish = Fish(self.field)

        self.score = 0
        self.stage = 1
        self.enemy_speed = 10

        pyxel.playm(MUS_BGM, loop=True)
        self.state = PLAY

    def next_stage(self):
        self.stage += 1
        self.enemy_speed = max(2, int(self.enemy_speed / 1.2))

        self.field.set_random_map()
        self.player.tx, self.player.ty = 1, 1

        self.enemies = [
            Enemy(14, 1),
            Enemy(14, 14),
        ]

        self.fish.respawn(self.field)
        self.state = PLAY

    def update(self):
        if self.state == TITLE:
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.start_game()

        elif self.state == PLAY:
            self.player.update(self.field)

            for enemy in self.enemies:
                enemy.update(self.field, self.player, self.enemies, self.enemy_speed)
                if enemy.tx == self.player.tx and enemy.ty == self.player.ty:
                    pyxel.stop()
                    pyxel.play(0, SND_OVER)
                    self.state = GAMEOVER

            if self.player.tx == self.fish.tx and self.player.ty == self.fish.ty:
                self.score += 1
                pyxel.play(1, SND_EAT)
                self.fish.respawn(self.field)

                if self.score % 10 == 0:
                    pyxel.play(1, SND_CLEAR)
                    self.state = CLEAR

        elif self.state == CLEAR:
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.next_stage()

        elif self.state == GAMEOVER:
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.state = TITLE

    def draw(self):
        pyxel.cls(0)

        if self.state == TITLE:
            pyxel.text(30, 50, "Survival Penguin", 7)
            pyxel.text(30, 70, "PRESS SPACE", 8)

        elif self.state == PLAY:
            self.field.draw()
            self.fish.draw()
            self.player.draw()
            for enemy in self.enemies:
                enemy.draw()
            pyxel.text(5, 3, f"SCORE: {self.score}", 8)
            pyxel.text(90, 3, f"STAGE: {self.stage}", 8)

        elif self.state == CLEAR:
            pyxel.text(40, 50, "STAGE CLEAR!", 8)
            pyxel.text(30, 70, "PRESS SPACE", 8)

        elif self.state == GAMEOVER:
            pyxel.text(40, 50, "GAME OVER", 8)
            pyxel.text(30, 70, "PRESS SPACE", 8)


APP()
