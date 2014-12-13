__version__ = '1.3.0'

from random import randint, random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, OptionProperty, ObjectProperty, StringProperty
from kivy.graphics import Color, BorderImage
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.utils import platform
from kivy.factory import Factory
from levels import Levels

platform = platform()
app = None

if platform == 'android':
    # Support for Google Play
    import gs_android
    leaderboard_highscore = 'CgkI0InGg4IYEAIQBg'
    achievement_block_32 = 'CgkI0InGg4IYEAIQCg'
    achievement_block_64 = 'CgkI0InGg4IYEAIQCQ'
    achievement_block_128 = 'CgkI0InGg4IYEAIQAQ'
    achievement_block_256 = 'CgkI0InGg4IYEAIQAg'
    achievement_block_512 = 'CgkI0InGg4IYEAIQAw'
    achievement_block_1024 = 'CgkI0InGg4IYEAIQBA'
    achievement_block_2048 = 'CgkI0InGg4IYEAIQBQ'
    achievement_block_4096 = 'CgkI0InGg4IYEAIQEg'
    achievement_100x_block_512 = 'CgkI0InGg4IYEAIQDA'
    achievement_1000x_block_512 = 'CgkI0InGg4IYEAIQDQ'
    achievement_100x_block_1024 = 'CgkI0InGg4IYEAIQDg'
    achievement_1000x_block_1024 = 'CgkI0InGg4IYEAIQDw'
    achievement_10x_block_2048 = 'CgkI0InGg4IYEAIQEA'
    achievements = {
        32: achievement_block_32,
        64: achievement_block_64,
        128: achievement_block_128,
        256: achievement_block_256,
        512: achievement_block_512,
        1024: achievement_block_1024,
        2048: achievement_block_2048,
        4096: achievement_block_4096}

    from kivy.uix.popup import Popup
    class GooglePlayPopup(Popup):
        pass

else:
    achievements = {}

class ButtonBehavior(object):
    # this is a port of the Kivy 1.8.0 version, the current android versino
    # still use 1.7.2. This is going to be removed soon.
    state = OptionProperty('normal', options=('normal', 'down'))
    last_touch = ObjectProperty(None)
    def __init__(self, **kwargs):
        self.register_event_type('on_press')
        self.register_event_type('on_release')
        super(ButtonBehavior, self).__init__(**kwargs)

    def _do_press(self):
        self.state = 'down'

    def _do_release(self):
        self.state = 'normal'

    def on_touch_down(self, touch):
        if super(ButtonBehavior, self).on_touch_down(touch):
            return True
        if touch.is_mouse_scrolling:
            return False
        if not self.collide_point(touch.x, touch.y):
            return False
        if self in touch.ud:
            return False
        touch.grab(self)
        touch.ud[self] = True
        self.last_touch = touch
        self._do_press()
        self.dispatch('on_press')
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            return True
        if super(ButtonBehavior, self).on_touch_move(touch):
            return True
        return self in touch.ud

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return super(ButtonBehavior, self).on_touch_up(touch)
        assert(self in touch.ud)
        touch.ungrab(self)
        self.last_touch = touch
        self._do_release()
        self.dispatch('on_release')
        return True

    def on_press(self):
        pass

    def on_release(self):
        pass


class Number(Widget):
    number = NumericProperty(2)
    scale = NumericProperty(.1)
    colors = {
        1: get_color_from_hex('#37988F'),
        2: get_color_from_hex('#37988F'),
        4: get_color_from_hex('#3C3C3C'),
        8: get_color_from_hex('#E16F33'),
        16: get_color_from_hex('#37988F'),
        32: get_color_from_hex('#3C3C3C'),
        64: get_color_from_hex('#E16F33'),
        128: get_color_from_hex('#37988F'),
        256: get_color_from_hex('#3C3C3C'),
        512: get_color_from_hex('#E16F33'),
        1024: get_color_from_hex('#37988F'),
        2048: get_color_from_hex('#3C3C3C'),
        4096: get_color_from_hex('#E16F33'),
        8192: get_color_from_hex('#37988F')}

    def __init__(self, **kwargs):
        if 'number' in kwargs:
            self.number = kwargs['number']
        super(Number, self).__init__(**kwargs)
        anim = Animation(scale=1., d=.15, t='out_quad')
        anim.bind(on_complete=self.clean_canvas)
        anim.start(self)

    def clean_canvas(self, *args):
        self.canvas.before.clear()
        self.canvas.after.clear()

    def move_to_and_destroy(self, pos):
        self.destroy()
        #anim = Animation(opacity=0., d=.25, t='out_quad')
        #anim.bind(on_complete=self.destroy)
        #anim.start(self)

    def destroy(self, *args):
        self.parent.remove_widget(self)

    def move_to(self, pos):
        if self.pos == pos:
            return
        Animation(pos=pos, d=.1, t='out_quad').start(self)

    def on_number(self, instance, value):
        if platform == 'android':
            if value in achievements:
                app.gs_unlock(achievements[value])
            if value == 512:
                app.gs_increment(achievement_100x_block_512)
                app.gs_increment(achievement_1000x_block_512)
            elif value == 1024:
                app.gs_increment(achievement_100x_block_1024)
                app.gs_increment(achievement_1000x_block_1024)
            elif value == 2048:
                app.gs_increment(achievement_10x_block_2048)

class LevelButton(Widget):
    number = NumericProperty(0)
    scale = NumericProperty(.1)
    color = StringProperty("#3C3C3C")
    level = ""
    game_widget = ""

    def __init__(self, lvl, widg, **kwargs):
        super(LevelButton, self).__init__(**kwargs)
        self.level = lvl
        if self.level.unlocked:
            print("color changing")
            self.color = "#37988F"
        self.game_widget = widg
        anim = Animation(scale=1., d=.15, t='out_quad')
        anim.bind(on_complete=self.clean_canvas)
        anim.start(self)

    def clean_canvas(self, *args):
        self.canvas.before.clear()
        self.canvas.after.clear()

    def on_touch_down(self, touch):
        # do some ninja shit
        if self.collide_point(touch.x, touch.y) and self.level.unlocked:
            self.game_widget.current_level = self.level
            self.game_widget.restart()

class Game2048(Widget):

    cube_size = NumericProperty(10)
    cube_padding = NumericProperty(10)
    score = NumericProperty(0)
    moves = NumericProperty(0)
    mytime = NumericProperty(0)
    ended = False
    win_value = False
    level_info = StringProperty("")

    def __init__(self, **kwargs):
        super(Game2048, self).__init__()

        self.levels = Levels()
        self.current_level = self.levels.next_level()
        self.level_info = self.current_level.info
        self.grid_size = self.current_level.grid_size
        self.grid = self.current_level.grid[:]

        # bind keyboard
        Window.bind(on_key_down=self.on_key_down)
        Window.on_keyboard = lambda *x: None

        #schedule clock
        Clock.schedule_interval(self.update_time, 1)
        self.restart()

    #######################################################
    #                 Event handlers                      #
    #######################################################

    def on_key_down(self, window, key, *args):
        if key == 273:
            self.move("up")
        elif key == 274:
            self.move("down")
        elif key == 276:
            self.move("right")
        elif key == 275:
            self.move("left")
        elif key == 27 and platform == 'android':
            from jnius import autoclass
            PythonActivity = autoclass('org.renpy.android.PythonActivity')
            PythonActivity.mActivity.moveTaskToBack(dTrue)
            return True

        # if game won or lost
        if self.get_game_status() != None:
            self.end()
            self.ended = True

        if (self.has_empty() or self.can_combine()) and self.moved and not self.ended:
            Clock.schedule_once(self.spawn_number, .20)

    def on_touch_up(self, touch):
        print("ontouch up")
        v = Vector(touch.pos) - Vector(touch.opos)
        if v.length() < dp(20):
            return

        # detect direction
        dx, dy = v
        if abs(dx) > abs(dy):
            if dx > 0:
                self.move("left")
            else:
                self.move("right")
        else:
            if dy > 0:
                self.move("up")
            else:
                self.move("down")

        # if game won or lost
        if self.get_game_status() != None:
            self.end()
            self.ended = True

        if (self.has_empty() or self.can_combine()) and self.moved and not self.ended:
            Clock.schedule_once(self.spawn_number, .20)

        return True

    ##########################################################
    #                   Selectors                            #
    ##########################################################

    def iterate_grid(self, grid):
        for ix in range(len(grid)):
            for iy in range(len(grid)):
                child = grid[ix][iy]
                yield ix, iy, child

    def get_cubes(self):
        cubes = []
        for ix, iy, child in self.iterate_grid(self.grid):
            if child and not(child == "Blocked"):
                cubes.append([ix, iy, child])
        return cubes

    def get_empty(self):
        empty = []
        for ix, iy, child in self.iterate_grid(self.grid):
                if not child:
                    empty.append([ix, iy])
        return empty

    def get_cube_pos(self, ix, iy):
        padding = self.cube_padding
        cube_size = self.cube_size
        return [
            (self.x + padding) + ix * (cube_size + padding),
            (self.y + padding) + iy * (cube_size + padding)]

    def get_game_status(self):
        # check level end
        game_status = self.current_level.check_condition(self.get_cubes(), self.score, self.moves, self.mytime)
        return game_status

    def can_combine(self):
        grid = self.grid
        for iy in range(4):
            for ix in range(3):
                cube1 = grid[ix][iy]
                cube2 = grid[ix + 1][iy]
                if cube1.number == cube2.number:
                    return True

        for ix in range(4):
            for iy in range(3):
                cube1 = grid[ix][iy]
                cube2 = grid[ix][iy + 1]
                if cube1.number == cube2.number:
                    return True

    def has_empty(self):
        if len(self.get_empty()) != 0:
            return True
        return False

    ######################################################
    ######################################################

    def build_grid(self):
        self.grid = []
        for i in range(len(self.current_level.grid)):
            self.grid.append([])
            for j in self.current_level.grid[i]:
                self.grid[i].append(j)

    def create_blocked_cubes(self, *args):
        for ix, iy, child in self.iterate_grid(self.grid):
            if child == "Blocked":
                self.grid[ix][iy] = None
                self.spawn_number_at(ix, iy, 1)

    def update_time(self, callback):
        if not self.ended:
            self.mytime = self.mytime + 1

    def rebuild_background(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(230/255., 230/255., 230/255.)
            #BorderImage(pos=self.pos, size=self.size, source='data/round.png')
            #Color(60/255., 60/255., 60/255.)
            csize = self.cube_size, self.cube_size
            for ix, iy, child in self.iterate_grid(self.grid):
                BorderImage(pos=self.get_cube_pos(ix, iy), size=csize,
                source='data/square2.png')

    def reposition(self, *args):
        # calculate the size of a number
        l = min(self.width, self.height)
        padding = (l / float(self.grid_size)) / 8. - 7
        cube_size = (l - (padding * 6)) / float(self.grid_size)
        self.cube_size = cube_size
        self.cube_padding = padding

        self.rebuild_background()

        for i in self.get_cubes():
            i[2].size = cube_size, cube_size
            i[2].pos = self.get_cube_pos(i[0], i[1])

    def spawn_number(self, *args):
        empty = self.get_empty()
        if len(empty) == 0:
            return
        value = 2 if random() < .9 else 4
        maxnum = len(empty) - 1
        random_index = randint(0, maxnum)
        ix = empty[random_index][0]
        iy = empty[random_index][1]
        self.spawn_number_at(ix, iy, value)

    def spawn_number_at(self, ix, iy, value):
        number = Number(
                size=(self.cube_size, self.cube_size),
                pos=self.get_cube_pos(ix, iy),
                number=value)
        self.grid[ix][iy] = number
        print("Number test:",self.grid[ix][iy].number)
        self.add_widget(number)

    def move(self, direction):
        if direction == "left" or direction == "up":
            rng = range(self.grid_size-1, -1, -1)
        elif direction == "right" or direction == "down":
            rng = range(self.grid_size)

        grid = self.grid
        self.moved = False

        for i in range(self.grid_size):
            # get cubes for the current line
            cubes = []
            # interate from 0=>4 or 4=>0
            for j in rng:
                if direction == "left" or direction == "right":
                    ix = j
                    iy = i
                elif direction == "up" or direction == "down":
                    ix = i
                    iy = j
                cube = self.grid[ix][iy]
                if cube:
                    cubes.append(cube)
            # combine cubes
            self.combine(cubes)

            # update grid
            for j in rng:
                if direction == "left" or direction == "right":
                    ix = j
                    iy = i
                elif direction == "up" or direction == "down":
                    ix = i
                    iy = j

                cube = cubes.pop(0) if cubes else None
                if grid[ix][iy] != cube:
                    self.moved = True
                grid[ix][iy] = cube
                if not cube or cube == "Blocked":
                    continue

                pos = self.get_cube_pos(ix, iy)
                if cube.pos != pos:
                    cube.move_to(pos)

        if not self.ended and self.moved:
            self.moves = self.moves + 1

    def combine(self, cubes):
        if len(cubes) <= 1:
            return cubes
        index = 0
        while index < len(cubes) - 1:
            cube1 = cubes[index]
            cube2 = cubes[index + 1]
            if cube1.number == cube2.number:
                cube1.number *= 2
                if not self.ended:
                    self.score += cube1.number
                cube2.move_to_and_destroy(cube1.pos)
                del cubes[index + 1]

            index += 1

    def end(self):
        end = self.ids.end.__self__
        self.remove_widget(end)
        self.add_widget(end)
        text = ""

        if self.get_game_status() == "won":
            text = "WIN"
            next_level = self.levels.get_next_level()
            next_level.unlocked = True
            next_level.color = "#37988F"
            self.ids.next_level_button.opacity = 1

        elif self.get_game_status() == "lost":
            text = "FAILED"
            self.ids.next_level_button.opacity = 0.5

        self.ids.end_label.text = text
        Animation(opacity=1., d=.5).start(end)
        app.gs_score(self.score)

    def restart(self):
        self.score = 0
        self.moves = 0
        self.mytime = 0
        self.ended = False
        self.level_info = self.current_level.info
        for i in self.get_cubes():
            i[2].destroy()
        self.ids.levelsgrid.clear_widgets()
        self.grid_size = self.current_level.grid_size
        self.build_grid()
        self.reposition()

        Clock.schedule_once(self.create_blocked_cubes, .1)
        Clock.schedule_once(self.spawn_number, .1)
        Clock.schedule_once(self.spawn_number, .1)
        self.ids.end.opacity = 0
        self.ids.levelspane.opacity = 0

    def next_level(self):
        self.current_level = self.levels.next_level()
        self.level_info = self.current_level.info
        self.restart()

    def all_levels(self):
        levelspane = self.ids.levelspane.__self__
        end = self.ids.end.__self__
        self.remove_widget(levelspane)
        self.ids.end.opacity = 0
        self.remove_widget(end)
        self.add_widget(levelspane)

        ix = 0
        iy = 0
        for lvl_index in range(len(self.levels.levels)):
            level_button = LevelButton(
                           self.levels.levels[lvl_index],
                           self,
                           size=(self.cube_size, self.cube_size),
                           pos=self.get_cube_pos(ix, iy),
                           number=lvl_index)
            self.ids.levelsgrid.add_widget(level_button)
            ix = ix + 1
            if ix > 5:
                ix = 0
                iy = iy + 1

        self.ids.levelspane.opacity = 1

class Game2048App(App):
    use_kivy_settings = False

    def build_config(self, config):
        if platform == 'android':
            config.setdefaults('play', {'use_google_play': '0'})

    def build(self):
        global app
        app = self

        if platform == 'android':
            self.use_google_play = self.config.getint('play', 'use_google_play')
            if self.use_google_play:
                gs_android.setup(self)
            else:
                Clock.schedule_once(self.ask_google_play, .5)
        else:
            # remove all the leaderboard and achievement buttons
            scoring = self.root.ids.scoring
            scoring.parent.remove_widget(scoring)

    def gs_increment(self, uid):
        if platform == 'android' and self.use_google_play:
            gs_android.increment(uid, 1)

    def gs_unlock(self, uid):
        if platform == 'android' and self.use_google_play:
            gs_android.unlock(uid)

    def gs_score(self, score):
        if platform == 'android' and self.use_google_play:
            gs_android.leaderboard(leaderboard_highscore, score)

    def gs_show_achievements(self):
        if platform == 'android':
            if self.use_google_play:
                gs_android.show_achievements()
            else:
                self.ask_google_play()

    def gs_show_leaderboard(self):
        if platform == 'android':
            if self.use_google_play:
                gs_android.show_leaderboard(leaderboard_highscore)
            else:
                self.ask_google_play()

    def ask_google_play(self, *args):
        popup = GooglePlayPopup()
        popup.open()

    def activate_google_play(self):
        self.config.set('play', 'use_google_play', '1')
        self.config.write()
        self.use_google_play = 1
        gs_android.setup(self)

    def on_pause(self):
        if platform == 'android':
            gs_android.on_stop()
        return True

    def on_resume(self):
        if platform == 'android':
            gs_android.on_start()

    def _on_keyboard_settings(self, *args):
        return

if __name__ == '__main__':
    Factory.register('ButtonBehavior', cls=ButtonBehavior)
    Game2048App().run()
