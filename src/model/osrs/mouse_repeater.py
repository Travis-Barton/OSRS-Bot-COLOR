import pandas as pd
from src.utilities.mouse_utils import MouseUtils
csv = 'src/model/osrs/action_mouse/cut_shortbow/click_log.csv'
mouse = MouseUtils()
df = pd.read_csv(csv)

df.time = [2] + df.time[1:].tolist()
for _ in range(1000):
    for i in range(len(df)):
        mouse.move_to((df.x[i], df.y[i]), df.time[i], 3, .05, tween='rand')
        mouse.click()
