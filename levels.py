class Levels:
    levels = []
    currentLevel = -1

    def __init__(self):
        self.levels.append(Level1())
        self.levels.append(Level2())
        self.levels.append(Level3())
        self.levels.append(Level4())
        self.levels.append(Level5())
        self.levels.append(Level5())
        self.levels.append(Level5())

    #return next level without switching to that level
    def get_next_level(self):
        if len(self.levels) > self.currentLevel + 1:
            return self.levels[self.currentLevel+1]
        else:
            self.currentLevel = 0
            return self.levels[self.currentLevel+1]

    #return next level and switch to that level
    def next_level(self):
        self.currentLevel = self.currentLevel + 1
        if len(self.levels) > self.currentLevel:
            return self.levels[self.currentLevel]
        else:
            self.currentLevel = 0
            return self.levels[self.currentLevel]

class Level:
    def __init__(self):
        self.info = ""
        self.unlocked = False
        self.grid_size = 5

    def check_condition(self, cubes, score, moves, time):
        pass

class Level1(Level):
    def __init__(self):
        Level.__init__(self)
        self.info = "Create 32 in 22 moves"
        self.unlocked = True
        self.grid_size = 3

    def check_condition(self, cubes, score, moves, time):
        #print(cube.number)
        #print(moves)
        #print(time)
        for cube in cubes:
            if cube[2].number == 32 and moves < 22:
                return "won"

            if moves >= 22:
                return "lost"

class Level2(Level):
    def __init__(self):
        Level.__init__(self)
        self.info = "Create 32 in 15 seconds"
        self.grid_size = 5
        self.unlocked = True

    def check_condition(self, cubes, score, moves, time):
        for cube in cubes:
            if cube[2].number == 32 and time < 15:
                return "won"
            if time >= 15:
                return "lost"

class Level3(Level):
    def __init__(self):
        Level.__init__(self)
        self.info = "Get 200 points in 20 seconds"

    def check_condition(self, cubes, score, moves, time):
        if score >= 200 and time < 20:
            return "won"
        
        if time >= 20:
            return "lost"

class Level4(Level):
    def __init__(self):
        Level.__init__(self)
        self.info = "Create two tiles of 8 in 15 moves"
        self.unlocked = True
        self.nr_of_tiles = 0
        self.grid_size = 4
    def check_condition(self, cubes, score, moves, time):
        for cube in cubes:
            if cube[2].number == 8:
                self.nr_of_tiles = self.nr_of_tiles + 1
        if self.nr_of_tiles >= 2:
                self.nr_of_tiles = 0
                return "won"
        elif self.nr_of_tiles < 2 and moves == 15:
            self.nr_of_tiles = 0
            return "lost"
        else:
            self.nr_of_tiles = 0

class Level5(Level):
    def __init__(self):
        self.info = "Create two of 4 and one of 8 in 12 moves"
        self.nr_of_four = 0
        self.nr_of_eight = 0
        self.unlocked = True
        self.grid_size = 5

    def check_condition(self, cubes, score, moves, time):
        for cube in cubes:
            if cube[2].number == 8:
                self.nr_of_eight += 1
            if cube[2].number == 4:
                self.nr_of_four += 1

        if self.nr_of_four >= 2 and self.nr_of_eight >= 1 and moves < 12:
            self.nr_of_four = 0
            self.nr_of_eight = 0
            return "won"
        elif moves == 12:
            self.nr_of_four = 0
            self.nr_of_eight = 0
            return "lost"
        else:
            self.nr_of_four = 0
            self.nr_of_eight = 0

