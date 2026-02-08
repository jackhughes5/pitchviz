import matplotlib.pyplot as plt
import seaborn as sns
from pybaseball import statcast_pitcher, playerid_lookup, statcast
import pandas as pd

print(playerid_lookup('Skubal', 'Tarik'))

print(statcast_pitcher('2025-03-27', '2025-05-30', 669373))
