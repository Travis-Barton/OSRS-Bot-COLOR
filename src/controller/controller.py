import sys

sys.path.append('/src/firebase_tools')
sys.path.extend(['C:\\Users\\Shadow\\PycharmProjects\\OSRS-Bot-COLOR',
                 'C:\\Users\\Shadow\\PycharmProjects\\OSRS-Bot-COLOR',
                 'C:\\Users\\Shadow\\PycharmProjects\\OSRS-Bot-COLOR\\src',
                 'C:\\Users\\Shadow\\PycharmProjects\\OSRS-Bot-COLOR\\src',
                 'C:/Users/Shadow/PycharmProjects/OSRS-Bot-COLOR'])

from src.model.osrs.pastry_maker import main as pastry_main
from src.model.osrs.beer_buyer_varrok import main as beer_main
# command line arguments
import argparse
from src.firebase_tools.fb_logger import update_status, new_action_available, wipe_new_action, get_action
import pandas as pd
import pyautogui as pag


def mover(starting, ending):
    if starting == 'ge' and ending == 'beer':
        csv = pd.read_csv('src/model/osrs/action_mouse/from_ge_to_beer_bank/click_log.csv')
        csv.time = [2] + csv.time.tolist()[1:]
        for i in range(len(csv)):
            pag.moveTo(csv.iloc[i]['x'], csv.iloc[i]['y'], csv.iloc[i]['time'] * 2)
            pag.click()
    if starting == 'beer' and ending == 'ge':
        csv = pd.read_csv('src/model/osrs/action_mouse/from_beer_bank_to_ge/click_log.csv')
        csv.time = [2] + csv.time.tolist()[1:]
        for i in range(len(csv)):
            pag.moveTo(csv.iloc[i]['x'], csv.iloc[i]['y'], csv.iloc[i]['time'] * 2)
            pag.click()


if __name__ == '__main__':
    argparse = argparse.ArgumentParser()
    argparse.add_argument('-a', '--account', required=True, help='account name')
    argparse.add_argument('-l', '--loops', required=True, help='number of loops')
    argparse.add_argument('-t', '--type', required=True, help='type of action')
    argparse.add_argument('-s', '--starting', required=True, help='starting location')
    args = vars(argparse.parse_args())
    account = args['account']
    loops = int(args['loops'])
    action_type = args['type']
    starting = args['starting']
    ending = 'ge' if starting == 'beer' else 'beer'
    if action_type == 'pastry':
        if starting == 'beer':
            mover(starting, ending)
        update_status(account, status='processing pastry', action_update_type='starting pastry maker', action_value=0)
        pastry_main(loops, action_type)
    if action_type == 'beer':
        if starting == 'ge':
            mover(starting, ending)
        update_status(account, status='processing beer', action_update_type='starting beer buyer', action_value=0)
        beer_main(loops, setup=True if starting == 'ge' else False)
