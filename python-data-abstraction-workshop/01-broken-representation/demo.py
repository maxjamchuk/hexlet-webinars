from fixtures import WORLD
from game import get_tile


print("Stage 01: representation changed", flush=True)
print("The game still expects world[y][x].", flush=True)
print("An error is expected.", flush=True)
print(get_tile(WORLD, 1, 0))
