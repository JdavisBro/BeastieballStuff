import json
import math

import beastie_random
import roguelike_boons

with open("beastie_data.json") as f:
  BEASTIE_DATA: dict[str, dict] = json.load(f)
BEASTIE_DATA = {i: BEASTIE_DATA[i] for i in sorted(BEASTIE_DATA.keys())}

BOON_DECK = ["level", "level", "level", "level", "heal", "heal", "heal", "heal", "heal", "recruit", "recruit", "recruit", "recruit", "recruit", "recruit", "play", "play", "play", "play", "trait", "trait", "sp", "sp", "alllevel", "alllevel"];

class RoguelikeState():
    def __init__(self, seed="0"):
        self.boons: list[roguelike_boons.Boon] = []
        self.rng = beastie_random.BeastieRandom(0.)
        self.rng.seed_from_string(seed)
        self.seed = self.rng.i
        self.round = 0
        self.boon_deck = [i for i in BOON_DECK]
        self.families = [ "psychic","rat","olm1","possum1","football1","kettle1","yeti","turtle1","gremlin","shroom1","bilby1","clam","seal1","ibis","jellyfish1","moth1","cassowary1","nerd1","seabird1","frog1","platypus1","okapi","snake","cheerleader1","swift","clown1","millipede1","beluga","crab","ghost1","dragonfly","shark1","lyrebird1","bat1","serval1","croc","spirit1","alien1","mudskipper","disruptor","wizard","daredevil1","rainbow","monkey","shy","fox1","tricky1","magpie1","dog1","mantis","kangaroo1","bestie","rocklizard1","opossum","horseshoe" ]
        self.families.remove("shroom1")

    def new(self):
        boon = roguelike_boons.boon_map["recruit"]()
        print(boon.desc(False, self))
        print(boon.desc(False, self))

    def boss_reward(self):
        return self.round > 0 and self.round % 4 == 0

    def boon_power(self, strong_opponent):
        return strong_opponent or self.boss_reward()

    def generate_boon(self):
        boon: roguelike_boons.Boon = None
        while not boon or not (boon in self.boons and (not self.boss_reward() or boon.type != "heal")):
            ind = int(self.rng.random(len(self.boon_deck)))
            boon = roguelike_boons.boon_map[self.boon_deck[ind]]
            self.boon_deck.remove(boon.type)
        return boon.shuffle(self.rng)

    def generate_boons(self):
        self.boons = []
        for _ in range(3):
            self.boons.append(self.generate_boon())

    def generate_opponent_team(self, difficulty: int=0):
        team = []
        seed = self.seed + self.round
        self.rng.set_seed(seed)
        team_n = 0
        team_level = 10 + (self.round * 2) + (5 * pow(int(self.round / 4), 1.35))
        team_hp = 100 + (self.round * 4) + (self.round * 5 / 12) + (4 * pow(int(self.round / 4), 1.35))
        if difficulty == 0:
            team_n = 2 + int(self.round >= 12) 
            team_level *= 0.5 + 0.1 * self.rng.random()
            team_hp *= 0.7 + 0.05 * self.rng.random()
        elif difficulty == 1:
            team_n = 2 + int(self.round >= 12) 
            team_level *= 0.75 + 0.1 * self.rng.random()
            team_hp *= 0.88 + 0.04 * self.rng.random()
        elif difficulty == 2:
            team_n = 3 if self.round < 11 else 1 if self.round == 11 else 5
            team_hp = max(100, team_hp * 1.25)
        team_hp = 5 * round(team_hp / 5)
        return

    def generate_recruit(self):
        stop = False
        while not stop:
            ind = int(self.rng.random(len(self.families)))
            id = self.families[ind]
            self.families.remove(id)
            specie = BEASTIE_DATA[id]
            roguelvl = specie["roguelvl"]
            stop = (roguelvl if roguelvl > -1 else specie["tamelvl"] + specie["hidden"]) <= int(1 + math.sqrt(2.5 * (self.round / 11)) + self.rng.random())
        self.rng.spam_random(9)
        if not specie["ability_hidden"]:
            self.rng.random()
        self.rng.spam_random(len(specie["colors"]))
        if id == "ibis":
            self.rng.spam_random(5)
        # no shiny roll
        if specie["palettes"] > 1:
            self.rng.random()
        if id != "crab" and specie["spr_alt"]:
            self.rng.random()
        return specie["name"]
    
state = RoguelikeState("ROGUE")
state.new()
