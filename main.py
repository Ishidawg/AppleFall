import pyxel

SCENE_TITLE = 0
SCENE_PLAY = 1

TILE_SIZE = 16

PLAYER_WIDTH = TILE_SIZE
PLAYER_HEIGHT = TILE_SIZE
PLAYER_SPEED = 2

COLLECTABLE_OBJ_WIDTH = TILE_SIZE
COLLECTABLE_OBJ_HEIGHT = TILE_SIZE
COLLECTABLE_OBJ_SPEED = 1

WINDOW_WIDTH = 800 // 6
WINDOW_HEIGHT = 600 // 6
FPS = 60
TITLE = "Demo Game"


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = PLAYER_WIDTH
        self.h = PLAYER_HEIGHT

    def update(self):
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.x += PLAYER_SPEED
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.x -= PLAYER_SPEED

        # Use clamp instead to prevent player to go out of screen bounds
        self.x = pyxel.clamp(self.x, 0, pyxel.width - self.w)

    def draw(self):
        pyxel.blt(
            self.x, self.y, 0, 16, 0, self.w, self.h, 0
        )  # End 0 indicates the color to be 'ignored'


class CollectableObj:
    def __init__(self, x, y, img_idx, img_x, img_y, speed):
        self.x = x
        self.y = y
        self.w = COLLECTABLE_OBJ_WIDTH
        self.h = COLLECTABLE_OBJ_HEIGHT
        self.image_idx = img_idx
        self.image_x = img_x
        self.image_y = img_y
        self.speed = speed

    def update_position(self):
        self.y = 0
        self.x = pyxel.rndi(0, pyxel.width - self.w)

    def update(self):
        self.y += self.speed

    def draw(self):
        pyxel.blt(
            self.x,
            self.y,
            self.image_idx,
            self.image_x,
            self.image_y,
            self.w,
            self.h,
            0,
        )


class App:
    def __init__(self):
        pyxel.init(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, title=TITLE, fps=FPS)
        pyxel.integer_scale(True)

        # Image Bank - Sprite Sheet - Sprites Order:
        # 1 - background, 2 - basket, 3 - regular_apple
        # 4 - golden_apple, 5 - crystal_apple, 6 - rotten_apple
        pyxel.images[0].load(0, 0, "assets/spritesheet.png", False)

        # Sound Bank
        pyxel.sounds[0].pcm("sounds/background.ogg")
        pyxel.sounds[1].pcm("sounds/gameplay.ogg")
        pyxel.sounds[2].pcm("sounds/eat.ogg")
        pyxel.channels[1].gain = 1

        # Instance Main Classes
        self.player = Player(0, pyxel.height - PLAYER_HEIGHT)
        self.regular_apple = CollectableObj(
            x=0, y=0, img_idx=0, img_x=32, img_y=0, speed=COLLECTABLE_OBJ_SPEED
        )
        self.golden_apple = CollectableObj(
            x=0, y=0, img_idx=0, img_x=48, img_y=0, speed=COLLECTABLE_OBJ_SPEED + 0.5
        )
        self.crystal_apple = CollectableObj(
            x=0, y=0, img_idx=0, img_x=64, img_y=0, speed=COLLECTABLE_OBJ_SPEED + 1
        )
        self.rotten_apple = CollectableObj(
            x=0, y=0, img_idx=0, img_x=80, img_y=0, speed=COLLECTABLE_OBJ_SPEED
        )

        self.collectables = [
            self.regular_apple,
            self.golden_apple,
            self.crystal_apple,
            self.rotten_apple,
        ]
        self.current_apple = self.collectables[
            pyxel.rndi(0, len(self.collectables) - 1)
        ]

        self.scene = SCENE_TITLE
        self.game_score = 0
        self.scroll_y = 0
        self.show_stats = False
        self.stop_scrolling = True
        self.is_crt_enabled = False

        pyxel.play(0, 0, loop=True)

        pyxel.run(self.update, self.draw)

    def update_stats(self):
        if pyxel.btnp(pyxel.KEY_F1):
            self.show_stats = not self.show_stats

        pyxel.perf_monitor(self.show_stats)

    def toogle_crt(self):
        pyxel.screen_mode(2 if self.is_crt_enabled else 0)

    def tile_background(self):
        cols = (pyxel.width // TILE_SIZE) + 1
        rows = (pyxel.height // TILE_SIZE) + 2

        for x in range(cols):
            for y in range(-1, rows):
                pos_x = x * TILE_SIZE
                pos_y = (y * TILE_SIZE) + int(
                    self.scroll_y
                )  # Float will cause visual artifacts

                pyxel.blt(pos_x, pos_y, 0, 0, 0, TILE_SIZE, TILE_SIZE)

    def update_score(self):
        if self.current_apple == self.collectables[1]:  # GOLDEN_APPLE
            iteration_value = 2
        elif self.current_apple == self.collectables[2]:  # CRYSTAL_APPLE
            iteration_value = 3
        elif self.current_apple == self.collectables[3]:  # ROTTEN_APPLE
            iteration_value = -5
        else:  # REGULAR_APPLE
            iteration_value = 1

        self.game_score += iteration_value

    def update_current_apple(self):
        self.current_apple = self.collectables[
            pyxel.rndi(0, len(self.collectables) - 1)
        ]
        self.current_apple.update_position()

    def check_collision(self):
        x_axis = abs(self.player.x - self.current_apple.x) < PLAYER_WIDTH
        y_axis = abs(self.player.y - self.current_apple.y) < PLAYER_HEIGHT

        if x_axis and y_axis:
            pyxel.play(1, 2)
            self.update_score()
            self.update_current_apple()
        if self.current_apple.y >= pyxel.height:
            self.update_current_apple()

        # DEBUG - Exit game when an appple hits screen bounds (bottom)
        # if self.current_apple.y >= pyxel.height:
        #    pyxel.quit()

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            pyxel.quit()

        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y):
            self.stop_scrolling = not self.stop_scrolling

        if pyxel.btnp(pyxel.KEY_F1):
            self.is_crt_enabled = not self.is_crt_enabled
            self.toogle_crt()

        if self.scene == SCENE_TITLE:
            self.update_title_scene()
        elif self.scene == SCENE_PLAY:
            self.update_play_scene()

    def update_title_scene(self):
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            self.scene = SCENE_PLAY
            pyxel.play(0, 1, loop=True)

    def update_play_scene(self):
        self.player.update()
        self.current_apple.update()
        self.scroll_y = (self.scroll_y + 0.5) % TILE_SIZE if self.stop_scrolling else 0
        self.check_collision()
        # self.update_stats()

    def draw(self):
        pyxel.cls(0)
        self.tile_background()

        if self.scene == SCENE_TITLE:
            self.draw_title_scene()
        elif self.scene == SCENE_PLAY:
            self.draw_play_scene()

    def draw_title_scene(self):
        start_title = "APPLE FALL"
        start_title_width = len(start_title) * pyxel.FONT_WIDTH
        pyxel.text(
            ((pyxel.width - start_title_width) // 2) + 1,
            30,
            start_title,
            pyxel.COLOR_RED,
        )
        pyxel.text(
            (pyxel.width - start_title_width) // 2, 30, start_title, pyxel.COLOR_WHITE
        )

        play_text = "(A / ENTER) to play!"
        play_text_width = len(play_text) * pyxel.FONT_WIDTH
        pyxel.text(
            ((pyxel.width - play_text_width) // 2) + 1,
            50,
            play_text,
            pyxel.COLOR_DARK_BLUE,
        )
        pyxel.text(
            (pyxel.width - play_text_width) // 2, 50, play_text, pyxel.COLOR_WHITE
        )

        option_text = "(Y / SPACE) background scroll"
        option_text_width = len(option_text) * pyxel.FONT_WIDTH
        pyxel.text(
            ((pyxel.width - option_text_width) // 2) + 1,
            60,
            option_text,
            pyxel.COLOR_DARK_BLUE,
        )
        pyxel.text(
            (pyxel.width - option_text_width) // 2, 60, option_text, pyxel.COLOR_WHITE
        )

        crt_text = "(F1) toggle CRT"
        crt_text_width = len(crt_text) * pyxel.FONT_WIDTH
        pyxel.text(
            ((pyxel.width - crt_text_width) // 2) + 1,
            70,
            crt_text,
            pyxel.COLOR_LIME,
        )
        pyxel.text((pyxel.width - crt_text_width) // 2, 70, crt_text, pyxel.COLOR_WHITE)

        quit_text = "(B / ESC) to quit"
        quit_text_width = len(quit_text) * pyxel.FONT_WIDTH
        pyxel.text(
            ((pyxel.width - quit_text_width) // 2) + 1,
            80,
            quit_text,
            pyxel.COLOR_DARK_BLUE,
        )
        pyxel.text(
            (pyxel.width - quit_text_width) // 2, 80, quit_text, pyxel.COLOR_WHITE
        )

    def draw_play_scene(self):
        self.player.draw()
        self.current_apple.draw()

        score_text = f"score: {self.game_score}"
        score_width = len(score_text) * pyxel.FONT_WIDTH
        pyxel.text(
            ((pyxel.width - score_width) // 2) + 1, 2, score_text, pyxel.COLOR_DARK_BLUE
        )
        pyxel.text((pyxel.width - score_width) // 2, 2, score_text, pyxel.COLOR_WHITE)


if __name__ == "__main__":
    App()
