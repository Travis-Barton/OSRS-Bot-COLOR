import pyautogui as pag
import time
import random as rd
import datetime
import numpy as np
import os
import sys
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path + "\\..\\..\\")
sys.path.append(dir_path + "\\..\\..\\..\\")
from model.runelite_bot import RuneLiteBot
from firebase_tools.fb_logger import update_status, new_action_available, wipe_new_action, get_action

class BeerBot(RuneLiteBot):
    def __init__(self):
        title = "Beer buying Bot"
        description = ("This bot buys beer from varrock and banks it. It will run for a specified amount of time.")
        super().__init__(title=title, description=description)
        self.running_time = 0
        self.multi_select_example = None
        self.menu_example = None
        self.options_set = True
        self.setup = False
        self.loops = 100
        self.username = 'dumbartonbri'

    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the self. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        self.options_builder.add_slider_option("beer_laps", "How many laps to run?", 1, 180)  # max 180 minutes
        self.options_builder.add_dropdown_option('account', "what account is this?", ['dumbartonbri', 'humblejob', 'miner49erguy'])
        self.options_builder.add_checkbox_option('setup', "run setup?", [True, False])

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the self.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False. No need to set bot status.
        """
        self.options_set = True
        for option in options:
            if option == "beer_laps":
                self.loops = options[option]
                self.log_msg(f"Bot will run for {self.loops} loops.")
            elif option == "account":
                self.username = options[option]
                self.log_msg(f"Bot will run with account: {self.username}.")
            elif option == "setup":
                self.setup = options[option][0]
                self.log_msg(f"Bot setup is set to: {self.setup}.")
            else:
                self.log_msg(f"Unknown option: {option}")

        if self.options_set:
            self.log_msg("Options set successfully.")
        else:
            self.log_msg("using defaults")
            print("Developer: ensure option keys are correct, and that the option values are being accessed correctly.")
            self.setup = False
            self.loops = 100
            self.username = 'dumbartonbri'


    def setup_bot(self):

        loc = self.get_nearest_tag(self.TAG_PINK)
        while loc is None:
            time.sleep(1)  #
            loc = self.get_nearest_tag(self.TAG_PINK)
        self.mouse.move_to((loc[0] + 3, loc[1]), .12, 0, 0, 'rand')
        self.mouse.click()
        time.sleep(2)
        loc_money = pag.locateCenterOnScreen('images/bot/coins_stack.png', confidence=.9)
        self.mouse.move_to(loc_money, .12, 0, 0, 'rand')
        pag.keyDown('shift')
        self.mouse.click()
        pag.keyUp('shift')

    def get_near_bar(self, dist=False):
        self.mouse.move_to((593, 142), .2, 0, .001, 'rand')
        self.mouse.click()
        time.sleep(22. if not dist else 0.1)
        return True

    def chugg_potions(self):
        self.drink_potion()
        time.sleep(1)
        self.drink_potion()
        time.sleep(1)
        self.drink_potion()
        time.sleep(1)
        self.drink_potion()

    def buy_beers(self):
        loc = self.get_nearest_tag(self.TAG_BLUE)
        itt = 0
        while loc is None and itt < 200:
            loc = self.get_nearest_tag(self.TAG_BLUE)
            itt += 1
            time.sleep(.25)
        if loc is None:
            return False
        self.mouse.move_to(loc, .05, 0, 0.001, 'rand')
        self.mouse.click()
        time.sleep(1.1)
        itt = 0
        while pag.locateCenterOnScreen('images/dialog_screens/varrok_barman.png') is None:
            if itt > 6:
                return self.buy_beers()
            if pag.locateCenterOnScreen('images/bot/logout_screen.png') is not None:
                return False
            itt += 1
            time.sleep(1)
            continue
        pag.press('SPACE')
        time.sleep(.7 + np.abs(rd.gauss(0, .001)))
        pag.press('1')
        time.sleep(.7 + np.abs(rd.gauss(0, .001)))
        pag.press('SPACE')
        time.sleep(.7 + np.abs(rd.gauss(0, .001)))
        pag.press('SPACE')
        return True

    def return_to_bank(self, deposit_pot=False, walk=False, dist=False):
        if walk:
            self.mouse.move_to((567, 149), .15, 0, .001, 'rand')
            self.mouse.click()
        self.mouse.move_to((698, 69), 1, time_variance=.001)
        self.mouse.click()
        # drink_potion()
        time.sleep(22 if not dist else .1)  # alter for run

    def deposit_in_bank(self, walk=False):
        loc = self.get_nearest_tag(self.TAG_PINK)
        long_sleep = False
        while loc is None:
            time.sleep(1)  #
            loc = self.get_nearest_tag(self.TAG_PINK)
            long_sleep = True

        # drink_potion()
        self.mouse.move_to((loc[0] + 3, loc[1]), .12, 0, 0, 'rand')
        self.mouse.click()
        itt = 0
        while pag.locateCenterOnScreen('images/bot/bank_deposit_all.png') is None:
            if itt > 10:
                return self.deposit_in_bank(walk)
            if pag.locateCenterOnScreen('images/bot/logout_screen.png') is not None:
                return False
            itt += 1
            time.sleep(1)
            continue
        self.mouse.move_to(self.inventory_slots[0][2], .15, 1, .001, 'rand')
        pag.keyDown('shift')
        self.mouse.click()
        pag.keyUp('shift')
        # self.mouse.move_to((481, 51), .75, 1, .001, 'rand')
        # self.mouse.click()
        #
        # if long_sleep:
        if walk:
            self.mouse.move_to((567, 149), .15, 0, .001, 'rand')
            self.mouse.click()
        return True, not long_sleep

    def withdraw_energy_pot(self):
        # drink energy pot
        loc_pot = pag.locateCenterOnScreen('images/bot/energy_pot.png')
        self.mouse.move_to(loc_pot, .12, 0, 0, 'rand')
        self.mouse.click()

    def drink_potion(self):
        self.mouse.move_to(self.inventory_slots[0][1], .3, 1, .001, 'rand')
        self.mouse.click()

    def get_status_update(self, username):
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

    def main_loop(self):
        if self.setup:
            self.setup_bot()
        update_status(self.username,
                      status='running beer',
                      action_update_type='starting',
                      action_value=0,
                      logged_in=True,
                      last_login=datetime.datetime.now()
                      )
        time_runs = []
        beer = 0
        run = True
        for _ in range(self.loops):
            s = time.time()
            status = self.get_status_update(self.username)
            if not status:  # in this case the update is inside the function
                break
            status = self.get_near_bar()
            if not status:
                update_status(self.username,
                              status='running beer',
                              action_update_type='failed',
                              action_value=_,
                              logged_in=False)
                raise Exception('something went wrong traveling to the bar')
            for i in range(27):
                status = self.buy_beers()
                if not status:
                    update_status(self.username,
                                  status='running beer',
                                  action_update_type='failed buying beer',
                                  action_value=_,
                                  logged_in=False)
                    raise Exception(f'Something went wrong buting beer {i}')
            self.return_to_bank(deposit_pot=False, walk=True)
            status, run = self.deposit_in_bank(walk=True)
            if not status:
                update_status(self.username,
                              status='running beer',
                              action_update_type='failed returning to bank',
                              action_value=_,
                              logged_in=False)
                raise Exception('something went wrong depositing beer')
            time_runs.append(time.time() - s)
            beer += 27
            beer_report = f'Run: {_}\n' + \
                          f'average time: {sum(time_runs) / len(time_runs):.2f} seconds\n' + \
                          f'beer/hr: {60 * 60 * 27 / (sum(time_runs) / len(time_runs)):.2f}\n' + \
                          f'gp/hr revenue: {(101 - 2) * 3600 * 27 / (sum(time_runs) / len(time_runs)):,.2f}\n'
            print('\n' + beer_report)
            update_status(self.username,
                          status='running beer',
                          action_update_type=beer_report,
                          action_value=_,
                          logged_in=True
                          )

    def distributed_main(self, loops, accounts, setup=False):
        """
        perform the main loop on several screens one at a time
        :param loops: number of loops to run
        :param accounts: list of accounts to run
        :param setup: if true will set up the bots
        :return:
        """
        if setup:
            for _ in accounts:
                self.setup_bot()
                self.cycle_windows()
        for account in accounts:
            update_status(account,
                          status='running beer',
                          action_update_type='starting',
                          action_value=0,
                          logged_in=True,
                          last_login=datetime.datetime.now()
                          )
        time_runs = [[] for _ in range(len(accounts))]
        beer = [0 for _ in range(len(accounts))]
        run = True
        stopped = []
        for account in accounts:  # initialize the accounts
            if account in stopped:
                continue
            status = self.get_status_update(account)
            if not status:  # in this case the update is inside the function
                stopped.append(account)
                continue
            status = self.get_near_bar(True)
            if not status:
                update_status(account,
                              status='running beer',
                              action_update_type='failed',
                              action_value=_,
                              logged_in=False)
                raise Exception('something went wrong traveling to the bar')
            self.cycle_windows()
        for _ in range(loops):
            s = time.time()
            for account in accounts:  # buy beer
                if account in stopped:
                    continue
                for i in range(27):
                    status = self.buy_beers()
                    if not status:
                        update_status(account,
                                      status='running beer',
                                      action_update_type='failed buying beer',
                                      action_value=_,
                                      logged_in=False)
                        raise Exception(f'Something went wrong buting beer {i}')

                self.return_to_bank(walk=True, dist=True)
                self.cycle_windows()
            for account in accounts:
                if account in stopped:
                    continue
                status, run = self.deposit_in_bank(walk=True)
                time.sleep(.1)
                if not status:
                    update_status(account,
                                  status='running beer',
                                  action_update_type='failed returning to bank',
                                  action_value=_,
                                  logged_in=False)
                    raise Exception('something went wrong depositing beer')
                status = self.get_near_bar(True)
                self.cycle_windows()
            for i, account in enumerate(accounts):
                if account in stopped:
                    continue
                time_runs[i].append(time.time() - s)
                beer[i] += 27
                beer_report = f'Run: {_}\n' + \
                              f'average time: {sum(time_runs[i]) / len(time_runs[i]):.2f} seconds\n' + \
                              f'beer/hr: {60 * 60 * 27 / (sum(time_runs[i]) / len(time_runs[i])):.2f}\n' + \
                              f'gp/hr revenue: {(101 - 2) * 3600 * 27 / (sum(time_runs[i]) / len(time_runs[i])):,.2f}\n'
                print('\n' + beer_report)
                update_status(account,
                              status='running beer',
                              action_update_type=beer_report,
                              action_value=_,
                              logged_in=True
                              )

    def cycle_windows(self):
        """
        cycle through the windows
        :return:
        """
        pag.keyDown('ctrl')
        pag.keyDown('winleft')
        time.sleep(.01)
        pag.press('4')
        time.sleep(.01)
        pag.keyUp('winleft')
        pag.keyUp('ctrl')


if __name__ == '__main__':
    # main(132)
    bot = BeerBot()
    bot.main_loop()