import pyautogui as pag
from src.utilities.mouse_utils import MouseUtils
from src.model.osrs.woodcutting_2 import Woodcutting
import time
import random as rd
from src.firebase_tools.fb_logger import update_status, new_action_available, wipe_new_action, get_action
import datetime
import numpy as np
pricing = {'pies': 173, 'pastry': 72}
mouse = MouseUtils()
bot = Woodcutting('dumbartonbri')


def setup(food_type='pastry'):
    mouse.move_to(bot.cp_inventory, .1, 1, .001)
    mouse.click()
    tag = bot.get_nearest_tag(bot.TAG_BLUE)
    if tag is None:
        return False
    mouse.move_to(tag, .1, 1, .001, 'rand')
    mouse.click()
    time.sleep(.6)
    if food_type == 'pastry':
        mouse.move_to((311, 335), .1, 1, .001, 'rand')
        pag.rightClick()
        mouse.move_to((310, 374), .1, 1, .001, 'rand')
        mouse.click()
        time.sleep(2 + np.abs(rd.gauss(0, .001)))
        pag.press('9')
        time.sleep(1)
        pag.press('ENTER')
        mouse.move_to((442, 330), .1, 1, .001, 'rand')
        mouse.click()
        mouse.move_to((489, 44), .1, 1, .01)
        mouse.click()
    if food_type == 'pies':
        mouse.move_to((311, 335), .1, 1, .001, 'rand')
        pag.rightClick()
        mouse.move_to((310, 374), .1, 1, .001, 'rand')
        mouse.click()
        time.sleep(2 + np.abs(rd.gauss(0, .001)))
        pag.press('1')
        time.sleep(.6)
        pag.press('4')
        time.sleep(.7)
        pag.press('ENTER')
        mouse.move_to((442, 330), .1, 1, .001, 'rand')
        mouse.click()
        mouse.move_to((489, 44), .1, 1, .01)
        mouse.click()


def deposit_withdraw_pastry():
    tag = bot.get_nearest_tag(bot.TAG_BLUE)
    if tag is None:
        return False
    mouse.move_to(tag, .1, 1, .001, 'rand')
    mouse.click()
    time.sleep(.6)
    mouse.move_to((442, 330), .1, 1, .001, 'rand')
    mouse.click()
    flour = pag.locateCenterOnScreen('src/images/bot/flour_pot.png', confidence=.7)
    water_jug = pag.locateCenterOnScreen('src/images/bot/water_jug.png', confidence=.7)
    if flour is None or water_jug is None:
        return False
    mouse.move_to(flour, .1, 1, .01)
    mouse.click()
    mouse.move_to(water_jug, .1, 1, .01)
    mouse.click()
    mouse.move_to((489, 44), .1, 1, .01)
    mouse.click()
    return True


def deposit_withdraw_pie():
    tag = bot.get_nearest_tag(bot.TAG_BLUE)
    if tag is None:
        return False
    mouse.move_to(tag, .1, 1, .001, 'rand')
    mouse.click()
    time.sleep(.6)
    mouse.move_to((442, 330), .1, 1, .001, 'rand')
    mouse.click()
    item_1 = pag.locateCenterOnScreen('src/images/bot/pastry_dough.png', confidence=.7)
    item_2 = pag.locateCenterOnScreen('src/images/bot/pie_dish.png', confidence=.7)
    if item_1 is None or item_2 is None:
        return False
    mouse.move_to(item_1, .1, 1, .01)
    mouse.click()
    mouse.move_to(item_2, .1, 1, .01)
    mouse.click()
    mouse.move_to((489, 44), .1, 1, .01)
    mouse.click()
    return True


def make_pastry():
    mouse.move_to(bot.inventory_slots[0][0], .1, 1, .05)
    mouse.click()
    mouse.move_to(bot.inventory_slots[4][0], .1, 1, .05)
    mouse.click()
    time.sleep(.65 + np.abs(rd.gauss(0, .01)))
    pag.press('2')
    time.sleep(11)
    return True


def make_pie_crust():
    mouse.move_to(bot.inventory_slots[0][0], .1, 1, .05)
    mouse.click()
    mouse.move_to(bot.inventory_slots[4][0], .1, 1, .05)
    mouse.click()
    time.sleep(.65 + np.abs(rd.gauss(0, .01)))
    pag.press('SPACE')
    time.sleep(16)
    return True


def main(loops, loop_type='pastry'):
    setup(loop_type)
    objects = 0
    speed_num = []
    for i in range(loops):
        s = time.time()
        if loop_type == 'pastry':
            if not deposit_withdraw_pastry():
                print(f'issue with depositing')
                update_status('dumbartonbri',
                              status='processing pastry',
                              action_update_type='failed depositing pastry',
                              action_value=i,
                              logged_in=False)
                return False
            if not make_pastry():
                print(f'pastry making issue')
                return False
            objects += 9
        if loop_type == 'pies':
            if not deposit_withdraw_pie():
                print(f'issue with depositing')
                update_status('dumbartonbri',
                              status='processing pies',
                              action_update_type='failed depositing pies',
                              action_value=i,
                              logged_in=False)
                return False
            if not make_pie_crust():
                print(f'pie making issue')
                return False
            objects += 14
        speed = time.time() - s
        speed_num.append(speed)
        avg_runs = sum(speed_num)/len(speed_num)
        process_report = f'Run: {i}\n' \
                         f'{objects} {loop_type} made\n' \
                         f'average time {avg_runs:,}\n' \
                         f'objects/hr: {3600*objects/sum(speed_num):,.2f}\n' \
                         f'gp/hr profit: {pricing[loop_type]*3600*objects/sum(speed_num):,.2f}'
        print(process_report)
        update_status('dumbartonbri',
                      status=f'processing {loop_type}',
                      action_update_type=process_report,
                      action_value=i,
                      logged_in=True
                      )
    update_status('dumbartonbri',
                  status=f'processing {loop_type}',
                  action_update_type=process_report,
                  action_value=loops,
                  logged_in=False
                  )
    return True


if __name__ == '__main__':
    main(100, 'pastry')
