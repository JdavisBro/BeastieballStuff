import beastie_random

class Boon():
    type = "none"

    def __init__(self):
        self.rand = 0.

    def shuffle(self, rng: beastie_random.BeastieRandom):
        self.rand = rng.random()
        return self
    
    def value(self, power: bool):
        return 0
    
    def desc(self, power: bool, roguelike):
        return "unimplemented boon type"

class BoonLevel(Boon):
    type = "level"

    def value(self, power):
        return round((5 if power else 3) + (-1 + 2 * self.rand))
    
    def desc(self, power):
        return f"Levels selected Beastie by +{self.value(power)}"

class BoonAllLevel(Boon):
    type = "alllevel"

    def value(self, power):
        return int((2 if power else 1) + self.rand + 1)
    
    def desc(self, power):
        return f"Levels all Beasties by +{self.value(power)}"

class BoonHeal(Boon):
    type = "heal"

    def value(self, power):
        return int((100 if power else 55) * (0.8 + 0.2 * self.rand))

    def desc(self, power):
        return f"Increases all Beasties max HP by +25 and heals +{self.value(power)}"

class BoonRecruit(Boon):
    type = "recruit"

    def value(self, power):
        return 2 if power else 0
    
    def desc(self, power, roguelike):
        players = [roguelike.generate_recruit() for _ in range(4)]
        val = self.value(power)
        return f"Recruit new Beastie from {', '.join(players)} at average party Level{' + 2' if val else ''}"

boon_map = {
    "level": BoonLevel,
    "alllevel": BoonAllLevel,
    "heal": BoonHeal,
    "recruit": BoonRecruit,
}
