import pandas as pd
from src.utilities.mouse_utils import MouseUtils
csv = 'src/model/osrs/action_mouse/string_bow/click_log.csv'
mouse = MouseUtils()
df = pd.read_csv(csv)

df.time = [2] + df.time[1:].tolist()
for _ in range(98):
    for i in range(len(df)):
        mouse.move_to((df.x[i], df.y[i]), df.time[i], 1, .0005, tween='rand')
        mouse.click()
