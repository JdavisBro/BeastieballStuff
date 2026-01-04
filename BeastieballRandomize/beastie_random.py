m = 4294967296.0
c = 1.0
a = 22695477.0

rchar_key = "0123456789BCDFGHJKLMNPQRTVWXY"
base = len(rchar_key)

class BeastieRandom:
  def __init__(self, seed: float):
    self.i = seed % m

  def set_seed(self, seed: float):
    self.i = seed % m

  def random(self, max: float=1):
    self.i = (self.i * a + c) % m
    return max * abs(self.i / m)

  def spam_random(self, count: int):
    return [self.random() for _ in range(count)]

  def seed_to_string(self, seed: int = 0):
    value = ""
    seed = seed if seed else self.i
    while seed > 0:
      mod = seed % base
      value = rchar_key[mod] + value
      seed = int(seed / base)
    return value

  def seed_from_string(self, seed: str):
    # seed = seed.upper().replace("A", "4").replace("I", "1").replace("O", "0").replace("E", "3").replace("U", "V") # this isn't applied by accident. 
    seed = seed.upper()
    length = len(seed)
    value = 0
    index = 0
    while length:
      char = seed[length - 1]
      if char in rchar_key:
        pos = rchar_key.index(char)
        value += pos * (base ** index)
        index += 1
      length -= 1
    self.set_seed(value)
    return value
  
  def shuffle(self, array: list):
    length = len(array)
    last = 0
    i = 0
    while length:
      length -= 1
      i = self.random(length)
      # print(i)
      i = int(i)
      last = array[length]
      array[length] = array[i]
      array[i] = last
    return array
