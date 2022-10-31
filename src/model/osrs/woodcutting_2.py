from model.runelite_bot import RuneLiteBot
import time
from utilities.runelite_cv import isolate_colors, get_contour_positions, Color, get_contours
import pyautogui as pag
import numpy as np
import random as rd
import pandas as pd
from model.bot import BotStatus
import cv2
import utilities.bot_cv as bcv
import os
from firebase_tools.fb_logger import upload_to_firebase, get_action, wipe_new_action, update_status, new_action_available
import datetime


class Woodcutting(RuneLiteBot):
    def __init__(self):
        title = "wooductting bot"
        description = ("This bot will cut wood with the option of fletching, burning or banking the logs.")
        super().__init__(title=title, description=description)
        self.running_time = 0
        self.multi_select_example = None
        self.menu_example = None
        self.version = "1.0.0"
        self.author = "Travis Barton"
        self.author_email = "travisdatabarton@gmail.com"


    def create_options(self):
        '''
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        '''
        self.options_builder.add_slider_option("logs_cut", "How many logs to cut", 1, 360)  # max 180 minutes
        self.options_builder.add_dropdown_option("action", "what to do with logs", ['bank', 'fletch', 'burn', 'drop'])  # max 180 minutes
        self.options_builder.add_dropdown_option('account', "what account is this?", ['travmanman', 'dumbartonbri', 'humblejob', 'miner49erguy'])

        self.options_builder.add_dropdown_option("fletch_option", "what to do if fletch", ['1', '2', '3', '4', '5'])

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False. No need to set bot status.
        """
        self.options_set = True
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
                self.log_msg(f"Bot will run for {self.running_time} rounds.")
            elif option == "account":
                self.username = options[option]
                self.log_msg(f"Bot will run with account: {self.username}.")
            else:
                self.log_msg(f"Unknown option: {option}")
                self.options_set = False

        if self.options_set:
            self.log_msg("Options set successfully.")
        else:
            self.log_msg("Failed to set options.")
            print("Developer: ensure option keys are correct, and that the option values are being accessed correctly.")

    def main_loop(self, runs=250, color=None):
        # setup the bot
        if color is None:
            color = self.TAG_PURPLE
        self.setup_client('RuneLite', True, True, True)
        self.set_camera_zoom(43)
        self.set_status(BotStatus.RUNNING)
        # start the bot
        last_inventory_pos = self.inventory_slots[6][3]
        last_inventory_rgb = pag.pixel(last_inventory_pos.x, last_inventory_pos.y)
        logs = 0
        failed_searches = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            if not self.status_check_passed():
                return

            # If inventory is full
            if pag.pixel(last_inventory_pos.x, last_inventory_pos.y) != last_inventory_rgb:
                logs += 28
                self.log_msg(f"Logs cut: ~{logs}")
                if self.action == 'bank':
                    # TODO: THIS ONLY WORKS FOR ::DI AND IS A TEMPORARY SOLUTION
                    bank = self.get_nearest_tag(self.TAG_BLUE)
                    if bank is None:
                        self.log_msg("Could not find bank.")
                        self.set_status(BotStatus.STOPPED)
                        return
                    self.mouse.move_to(bank)
                    self.mouse.click()
                    time.sleep(3)
                    if not self.deposit_inventory():
                        self.set_status(BotStatus.STOPPED)
                        return
                    self.close_bank()
                elif self.action == 'fletch':
                    self.mouse.move_to(self.inventory_slots[0][0], .2, 1, .01, 'rand')
                    self.mouse.click()

                    self.mouse.move_to(self.inventory_slots[0][3], .2, 1, .01, 'rand')
                    self.mouse.click()
                    pag.press(self.fletch_option)
                elif self.action == 'burn':
                    pass

                else:
                    self.drop_inventory()
                    time.sleep(1)
                continue

            if not self.status_check_passed():
                return

            # Check to logout
            if self.logout_on_friends and self.friends_nearby():
                self.log_msg("Friends nearby. Logging out.")
                self.logout()
                self.set_status(BotStatus.STOPPED)
                return

            # Find a tree
            tree = self.get_nearest_tag(self.TAG_PINK)
            if tree is None:
                failed_searches += 1
                if failed_searches > 10:
                    self.log_msg("No tagged trees found. Logging out.")
                    self.logout()
                    self.set_status(BotStatus.STOPPED)
                    return
                time.sleep(1)
                continue

            # Click tree and wait to start cutting
            self.mouse.move_to(tree)
            self.mouse.click()
            time.sleep(3)

            # Wait so long as the player is cutting
            timer = 0
            while bcv.search_text_in_rect(self.rect_game_view, ["Woodcutting"], ["Not"]):
                self.update_progress((time.time() - start_time) / end_time)
                if not self.status_check_passed():
                    return
                if timer % 5 == 0:
                    self.log_msg("Chopping tree...")
                time.sleep(2)
                timer += 2
            self.log_msg("Idle...")

            if not self.status_check_passed():
                return

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.logout()
        self.set_status(BotStatus.STOPPED)

    def test_loop(self, idle='fletching'):
        try:
            last_inventory_pos = self.inventory_slots[6][3]
            last_inventory_rgb = pag.pixel(last_inventory_pos.x, last_inventory_pos.y)
            logs = 0
            s = time.time()
            update_status(self.username, 'woodcutting', f'starting', logs, datetime.datetime.now(), True)

            for l in range(15000):
                if not bcv.search_text_in_rect(self.rect_game_view, [''], ['you were disconnected from the server']):
                    update_status(self.username,
                                  'WOODCUT failed',
                                  f'logged out at: {datetime.datetime.now()}',
                                  -1,
                                  None,
                                  logged_in=False)
                tree = self.get_nearest_tag(self.TAG_PINK)
                if tree is None:
                    time.sleep(1)
                    continue
                else:
                    self.mouse.move_to(tree, .2, 2, .01, 'rand')
                    self.mouse.click()
                    time.sleep(3)
                    while bcv.search_text_in_rect(self.rect_game_view, ["Woodcutting", 'woodcuttirg', 'woodcuttirig'],
                                                  ["Not", 'No[', 'nol', 'n[', 'nt', 'nl']):
                        time.sleep(2)
                        continue
                if pag.pixel(last_inventory_pos.x, last_inventory_pos.y) != last_inventory_rgb:
                    logs += 28
                    if idle == 'firemaking':
                        j = 0
                        while j < 4:
                            self.mouse.move_to(self.inventory_slots[0][0], .2, 1, .01, 'rand')
                            self.mouse.click()

                            self.mouse.move_to(self.inventory_slots[6][3], .5, 1, .01, 'rand')
                            self.mouse.click()
                            exit = False
                            s = time.time()
                            while not exit:
                                if pag.locateCenterOnScreen('src/images/bot/firemaking.png', confidence=.9) is not None:
                                    exit = True
                                elif time.time() - s > 10:
                                    exit = True
                                else:
                                    continue
                            time.sleep(2)
                            j += 1
                    if idle == 'fletching' or idle == 'bank_n_fletch':
                        self.mouse.move_to(self.inventory_slots[0][0], .2, 1, .01, 'rand')
                        self.mouse.click()

                        self.mouse.move_to(self.inventory_slots[0][2], .5, 1, .01, 'rand')
                        self.mouse.click()
                        time.sleep(1)
                        pag.press('SPACE')
                        time.sleep(50)
                    if idle == 'bank' or idle == 'bank_n_fletch':
                        try:
                            loc = self.get_nearest_tag(self.TAG_PURPLE)
                            if loc is None:
                                raise Exception("Bank not found")
                            self.mouse.move_to(loc, .2, 1, .01, 'rand')
                            self.mouse.click()
                            time.sleep(12)
                            if idle == 'bank':
                                deposit  = pag.locateCenterOnScreen('src/images/bot/bank_deposit_all.png', confidence=.9)
                                if deposit is None:
                                    time.sleep(3)
                                    deposit = pag.locateCenterOnScreen('src/images/bot/bank_deposit_all.png', confidence=.9)
                                self.mouse.move_to(deposit, .2, 1, .01, 'rand')
                                self.mouse.click()
                                self.mouse.move_to((489, 47), .2, 1, .01, 'rand')
                                self.mouse.click()
                                time.sleep(1)
                            else:
                                pag.keyDown('SHIFT')
                                self.mouse.move_to(self.inventory_slots[0][1], .2, 1, .01, 'rand')
                                self.mouse.click()
                                pag.keyUp('SHIFT')
                            time.sleep(.1)
                        except Exception as e:
                            print(f'could not find bank: {e}')
                            continue
                        # self.mouse.move_to((646, 152), .2, 1, .01, 'rand')
                        # self.mouse.click()
                        # time.sleep(10)
                if new_action_available(self.username):
                    new_action = get_action(self.username)
                    if new_action == 'logout':
                        update_status(self.username, 'agility', 'rek training', -1, None, False)
                        # self.logout()
                        wipe_new_action(self.username)
                        return
                    elif new_action == 'update':
                        screen = pag.screenshot(self.username + '-temp.png',
                                                region=(self.rect_inventory.start.x, self.rect_inventory.start.y,
                                                        self.rect_inventory.end.x - self.rect_inventory.start.x,
                                                        self.rect_inventory.end.y - self.rect_inventory.start.y))
                        screen = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
                        upload_to_firebase(self.username + '-temp.png')
                        wipe_new_action(self.username)
                update_status(self.username,
                              'woodcutting',
                              f'cut {logs} in {datetime.timedelta(seconds=round(time.time() - s, 2))} seconds',
                              '',
                              None,
                              logged_in=True)
        except Exception as e:
            update_status(self.username,
                          'WOODCUT failed',
                          f'error cost {e}\nafter {time.time() - s} seconds at: {datetime.datetime.now()}',
                          -1,
                          None,
                          logged_in=False)
            wipe_new_action(self.username)
            return
        print(f'logged {logs} logs')
        update_status(self.username,
                      'woodcut successful',
                      f'complete after {time.time() - s:2f} seconds at {datetime.datetime.now().strftime("%H:%M:%S")}',
                      -1,
                      None,
                      logged_in=False)


if __name__ == '__main__':
    ab = Woodcutting('dumbartionbri')
    ab.test_loop('bank')
    # while True:
    #     tree = ab.get_nearest_tag(ab.TAG_PINK)
    #     if tree is not None:
    #         ab.mouse.move_to(tree)
    #         ab.mouse.click()
    #         time.sleep(7)
    #     time.sleep(2)
