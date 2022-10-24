import pyautogui as pag
from src.utilities.mouse_utils import MouseUtils
from src.model.osrs.woodcutting_2 import Woodcutting
import time
import random as rd
from src.firebase_tools.fb_logger import update_status, new_action_available, wipe_new_action, get_action
import datetime
import numpy as np

mouse = MouseUtils()
bot = Woodcutting('dumbartonbri')


def get_near_bar():

    # mouse.move_to((567, 149), .15, 0, .001, 'rand')
    # mouse.click()
    # mouse.move_to((630, 146), .2, 0, .001, 'rand')
    # mouse.click()
    # drink_potion()
    # time.sleep(11)
    # mouse.move_to((602, 123), .2, 0, .001, 'rand')
    # mouse.click()
    # drink_potion()
    # time.sleep(14.5)
    mouse.move_to((593, 142), .2, 0, .001, 'rand')
    mouse.click()
    drink_potion()
    time.sleep(5 + rd.gauss(0, .05))
    drink_potion()
    time.sleep(27.)
    return True


def chugg_potions():
    drink_potion()
    time.sleep(1)
    drink_potion()
    time.sleep(1)
    drink_potion()
    time.sleep(1)
    drink_potion()


def buy_beers():
    loc = bot.get_nearest_tag(bot.TAG_BLUE)
    itt = 0
    while loc is None and itt < 200:
        loc = bot.get_nearest_tag(bot.TAG_BLUE)
        itt += 1
        time.sleep(1)
    if loc is None:
        return False
    mouse.move_to(loc, .09, 0, 0.001, 'rand')
    mouse.click()
    time.sleep(1.1)
    itt = 0
    while pag.locateCenterOnScreen('src/images/dialog_screens/varrok_barman.png') is None:
        if itt > 20:
            return buy_beers()
        if pag.locateCenterOnScreen('src/images/bot/logout_screen.png') is not None:
            return False
        itt += 1
        time.sleep(1)
        continue
    pag.press('SPACE')
    time.sleep(.7 + np.abs(rd.gauss(0, .001)))
    pag.press('1')
    time.sleep(.7  + np.abs(rd.gauss(0, .001)))
    pag.press('SPACE')
    time.sleep(.7  + np.abs(rd.gauss(0, .001)))
    pag.press('SPACE')
    return True


def return_to_bank(deposit_pot=False, walk=False):
    if walk:
        mouse.move_to((567, 149), .15, 0, .001, 'rand')
        mouse.click()
    mouse.move_to((681, 66), 1, time_variance=.001)
    mouse.click()
    # drink_potion()
    time.sleep(37)  # alter for run
    loc = bot.get_nearest_tag(bot.TAG_PINK)
    long_sleep = False
    while loc is None:
        time.sleep(1)  #
        loc = bot.get_nearest_tag(bot.TAG_PINK)
        long_sleep = True

    # drink_potion()
    mouse.move_to((loc[0]+3, loc[1]), .12, 0, 0, 'rand')
    mouse.click()
    itt = 0
    while pag.locateCenterOnScreen('src/images/bot/bank_deposit_all.png') is None:
        if itt > 25:
            return_to_bank(deposit_pot, walk)
        if pag.locateCenterOnScreen('src/images/bot/logout_screen.png') is not None:
            return False
        itt += 1
        time.sleep(1)
        continue
    if deposit_pot:
        mouse.move_to(bot.inventory_slots[0][1], .15, 1, .001, 'rand')
        mouse.click()
        withdraw_energy_pot()
    mouse.move_to(bot.inventory_slots[0][2], .15, 1, .001, 'rand')
    mouse.click()
    # mouse.move_to((481, 51), .75, 1, .001, 'rand')
    # mouse.click()
    #
    # if long_sleep:
    if walk:
        mouse.move_to((567, 149), .15, 0, .001, 'rand')
        mouse.click()
    return True, not long_sleep


def withdraw_energy_pot():
    # drink energy pot
    loc_pot = pag.locateCenterOnScreen('src/images/bot/energy_pot.png')
    mouse.move_to(loc_pot, .12, 0, 0, 'rand')
    mouse.click()


def drink_potion():
    mouse.move_to(bot.inventory_slots[0][1], .3, 1, .001, 'rand')
    mouse.click()

def get_status_update(username):
    if new_action_available(username):
        new_action = get_action(username)
        if new_action == 'logout':
            update_status(username, 'beer runs', 'loggout of beer run', -1, '', logged_in=False)
            # self.logout()
            wipe_new_action(username)
            return False
        elif new_action == 'update':
            update_status(username, 'beer runs', 'updates not available yet', -1, '')
            # self.logout()
            wipe_new_action(username)
            return True
    return True


def main():
    update_status('dumbartonbri',
                  status='running beer',
                  action_update_type='starting',
                  action_value=0,
                  logged_in=True,
                  last_login=datetime.datetime.now()
                  )
    time_runs = []
    beer = 0
    run = True
    for _ in range(550):
        s = time.time()
        status = get_status_update('dumbartonbri')
        if not status:  # in this case the update is inside the function
            break
        status = get_near_bar()
        if not status:
            update_status('dumbartonbri',
                          status='running beer',
                          action_update_type='failed',
                          action_value=_,
                          logged_in=False)
            raise Exception('something went wrong traveling to the bar')
        for i in range(27):
            status = buy_beers()
            if not status:
                update_status('dumbartonbri',
                              status='running beer',
                              action_update_type='failed buying beer',
                              action_value=_,
                              logged_in=False)
                raise Exception(f'Something went wrong buting beer {i}')

        status, run = return_to_bank(deposit_pot=False, walk=True)
        if not status:
            update_status('dumbartonbri',
                          status='running beer',
                          action_update_type='failed returning to bank',
                          action_value=_,
                          logged_in=False)
            raise Exception('something went wrong depositing beer')
        time_runs.append(time.time() - s)
        beer += 27
        beer_report = f'Run: {_}\n' +\
                      f'average time: {sum(time_runs) / len(time_runs):.2f} seconds\n' + \
                      f'beer/hr: {60*60 * 27 / (sum(time_runs) / len(time_runs)):.2f}\n' + \
                      f'gp/hr revenue: {(101 - 2) * 3600 * 27 / (sum(time_runs) / len(time_runs)):,.2f}\n'
        print('\n' + beer_report)
        update_status('dumbartonbri',
                      status='running beer',
                      action_update_type=beer_report,
                      action_value=_,
                      logged_in=True
                      )

if __name__ == '__main__':
    main()