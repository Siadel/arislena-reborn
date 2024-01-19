from py_system import resource

water = resource.Water(5)

water.value -= 8

print(water.value, water.shortage, water.over)