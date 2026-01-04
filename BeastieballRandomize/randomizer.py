import json

import beastie_random

with open("beastie_data.json") as f:
  BEASTIE_DATA: dict[str, dict] = json.load(f)
BEASTIE_DATA = {i: BEASTIE_DATA[i] for i in sorted(BEASTIE_DATA.keys())}

RANDO_FULL = True

def get_beastie_map_regular(random: beastie_random.BeastieRandom): # DOESNT WORK
  beastie_map = {}
  families: dict[str, list[list[str]]] = {}
  for id, beastie in BEASTIE_DATA.items():
    if not beastie["evolution"]:
      families[id] = [[id]]
  for _ in range(4):
    families_delete: list[str] = []
    for id, beastie in BEASTIE_DATA.items():
      if id not in families and beastie["evolution"]:
        children: list[list[str]] = []
        has_evo = False
        hidden_evo = ""
        for evo in beastie["evolution"]:
          evo_id = evo["specie"]
          evo_beastie = BEASTIE_DATA[evo_id]
          if evo_id in families:
            families_delete.append(evo_id)
            has_evo = True
            if evo_beastie["hidden"]:
              hidden_evo = evo_id
            else:
              evo_line = families[evo_id]
              for j in range(len(evo_line)):
                while j >= len(children):
                  children.append([])
                for k in range(len(evo_line[j])):
                  nid = evo_line[j][k]
                  if k == 0:
                    children[j].insert(
                      int(random.random(len(children[j]))),
                      nid
                    )
                  elif nid not in children[j]:
                    children[j].append(nid)
        if has_evo:
          families[id] = [[id, hidden_evo] if hidden_evo else [id], *children]
    for delete in families_delete:
      if delete in families:
        families.pop(delete)
  lines: list[list[str]] = []
  for familyId, family in families.items():
    depth = len(family)
    while depth > len(lines):
      lines.append([])
    lines[depth - 1].append(familyId)
  for i in range(len(lines)):
    lines[i] = random.shuffle(lines[i])
  for bid, beastie in BEASTIE_DATA.items():
    family = families[beastie["family"]]
    stage = -1
    offset = -1
    for i in range(len(family)):
      if bid in family[i]:
        stage = i
        offset = family[i].index(bid)
        break
    if stage == -1:
      raise Exception("ERROR!")
    line = lines[len(family) - 1]
    index = line.index(beastie["family"])
    replace_array = families[line[(index + 1 + offset) % len(line)]][stage]
    beastie_map[bid] = replace_array[
      max(0, min(len(replace_array) - 1, int(random.random() ** 4 * len(replace_array))))
    ]
  return beastie_map

def get_beastie_map_full(random: beastie_random.BeastieRandom):
  beasties = list(BEASTIE_DATA.keys())
  shuffled = random.shuffle(list(beasties))
  return {prev: shuffled[i] for i, prev in enumerate(beasties)}

get_beastie_map = get_beastie_map_full if RANDO_FULL else get_beastie_map_regular


def encounter_is_shiny(random: beastie_random.BeastieRandom, beastie_id: str):
  beastie = BEASTIE_DATA[beastie_id]
  extra_random_calls = 0 if beastie["ability_hidden"] else 1
  extra_random_calls += len(beastie["colors"])
  if beastie_id == "ibis": extra_random_calls += 4
  rng = random.spam_random(9 + extra_random_calls)
  shiny = int(random.random(1024)) == 0
  # if shiny: print(rng)
  return shiny

def encounter_seed(name: str, index: int):
  hashCode = 0
  for i in name:
    hashCode += ord(i)
    hashCode *= 691
    hashCode = hashCode % beastie_random.m
  return index + hashCode

random = beastie_random.BeastieRandom(0)

random.set_seed(2010420)
beastie_map = get_beastie_map(random)
print(beastie_map, beastie_map["cassowary1"])

# start_date = 45459.8529224537 # this stuff is for bindiva trends
# seed = 5134
# random.set_seed(start_date + seed)
# while seed < beastie_random.m:
#   random.set_seed(start_date + seed)
#   cols = random.spam_random(4)
#   if seed == 5134:
#     print(cols)
#   if cols[0] < 0.25 and cols[1] > 0.95:
#     print(seed)
#     exit()
#   seed += 1

starters = ["shroom1", "cassowary1", "frog1", "bilby1"]

from pathlib import Path

outfile = Path("randomizer_seeds.csv")

last_seed = -1
if outfile.exists():
  with outfile.open("r") as f:
    lines = f.readlines()
    last_line = lines[-1]
    last_line = last_line if last_line.strip() else lines[-2].strip()
    last_seed = int(last_line.split(",")[1])

f = outfile.open("a+")

seed = last_seed + 1
while seed < beastie_random.m:
  if seed % 10_000 == 0:
    print(" ", seed, "-", f"{(seed+1) / beastie_random.m * 100:.3f}%", end="\r")
  random.set_seed(seed)
  beastie_map = get_beastie_map(random)
  # random.set_seed(seed + encounter_seed("starter", 0))
  if encounter_is_shiny(random, beastie_map["shroom1"]):
    rares = [beastie_map["shroom1"]]
    shiny = 1
    for i in range(1, 4):
      random.set_seed(seed + encounter_seed("starter", i))
      if encounter_is_shiny(random, beastie_map[starters[i]]):
        rares.append(beastie_map[starters[i]])
        shiny += 1
    if shiny > 1:
      print(random.seed_to_string(seed), seed, *[BEASTIE_DATA[i]["name"] for i in rares])
      f.write(",".join([random.seed_to_string(seed), str(seed), *[BEASTIE_DATA[i]["name"] for i in rares]]) + "\n")
      f.flush()

  seed += 1
