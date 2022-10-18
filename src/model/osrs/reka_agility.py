from model.runelite_bot import RuneLiteBot
import time
from utilities.runelite_cv import isolate_colors, get_contour_positions, Color, get_contours
import pyautogui as pag
import numpy as np
import random as rd
import pandas as pd
from model.bot import BotStatus
from firebase_tools.fb_logger import update_status, new_action_available, get_action, \
    wipe_new_action, upload_to_firebase
import cv2
import datetime


class RekAgilityBot(RuneLiteBot):
    def __init__(self, mouse_csv='src/files/agility/click_log.csv', username='test'):
        title = "Seers Agility Bot"
        description = ("This bot will complete the Seers' Village Agility Course. Put your character on the first"
                       " roof to begin. Marks will only be collected every 8 laps to save on time.")
        super().__init__(title=title, description=description)
        self.running_time = 0
        self.multi_select_example = None
        self.menu_example = None
        self.version = "1.0.0"
        self.author = "Travis Barton"
        self.author_email = "travisdatabarton@gmail.com"
        self.mouse_info = pd.read_csv(mouse_csv, index_col=0)
        self.mouse_info.time = self.mouse_info.time.iloc[1:].tolist() + [3]
        self.username = username

    def create_options(self):
        '''
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        '''
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 360)  # max 180 minutes

    def save_options(self, options: dict):
        '''
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False. No need to set bot status.
        '''
        self.options_set = True
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
                self.log_msg(f"Bot will run for {self.running_time} rounds.")
            else:
                self.log_msg(f"Unknown option: {option}")
                self.options_set = False

        if self.options_set:
            self.log_msg("Options set successfully.")
        else:
            self.log_msg("Failed to set options.")
            print("Developer: ensure option keys are correct, and that the option values are being accessed correctly.")

    def main_loop(self, runs=250, color=None):
        pass

    def check_for_mark(self, region=None, confidence=.6):
        LOC = pag.locateOnScreen(f'src/files/agility/fast_rek_run/screenshots/grace_mark.png', confidence=confidence,
                                 region=region)
        if LOC is not None:
            # self.log_msg(f'Grace mark found')
            mid = pag.center(LOC)
            self.mouse.move_to((mid.x, mid.y), .2, 1, .005, 'rand')
            self.mouse.click()
            time.sleep(3.4 + np.abs(rd.gauss(0, .1)))
            return True
        else:
            return False

    def check_for_fall(self):
        min_map = (self.rect_minimap.start.x, self.rect_minimap.start.y,
                   self.rect_minimap.end.x - self.rect_minimap.start.x,
                   self.rect_minimap.end.y - self.rect_minimap.start.y)
        shot = pag.screenshot(imageFilename='src/images/temp/temp_screenshot_fall.png', region=min_map)
        hist = shot.histogram()
        if hist[0] > 1500:  # if black pixels are more than 500
            return False
        else:
            return True

    def fast_rout(self):
        # self.log_msg('starting speed run..')
        for i in range(8):
            if i == 2:
                if self.check_for_fall():
                    self.mouse.move_to((661, 50), .2, 1, .005, 'rand')
                    self.mouse.click()
                    time.sleep(8.38 + np.abs(rd.gauss(0, .01)))
                    loc = pag.locateCenterOnScreen('src/files/agility/fast_rek_run/screenshots/fall_shot.png',
                                                   confidence=.52)
                    if loc is None:
                        loc = pag.locateCenterOnScreen('src/files/agility/fast_rek_run/screenshots/fall_shot2.png',
                                                       confidence=.52)
                    if loc is None:
                        loc = pag.locateCenterOnScreen('src/files/agility/fast_rek_run/screenshots/fall_shot3.png',
                                                       confidence=.52)
                    self.mouse.move_to((loc.x, loc.y), .2, 1, .005, 'rand')
                    self.mouse.click()
                    time.sleep(7.98 + np.abs(rd.gauss(0, .01)))
                    return
            if i == 3:
                if self.check_for_fall():
                    self.mouse.move_to((616, 66), .2, 1, .005, 'rand')
                    self.mouse.click()
                    time.sleep(7.98 + np.abs(rd.gauss(0, .01)))
                    loc = pag.locateCenterOnScreen('src/files/agility/fast_rek_run/screenshots/fall_shot.png',
                                                   confidence=.52)
                    if loc is None:
                        loc = pag.locateCenterOnScreen('src/files/agility/fast_rek_run/screenshots/fall_shot2.png',
                                                       confidence=.52)
                    if loc is None:
                        loc = pag.locateCenterOnScreen('src/files/agility/fast_rek_run/screenshots/fall_shot3.png',
                                                       confidence=.52)
                    self.mouse.move_to((loc.x, loc.y), .2, 1, .005, 'rand')
                    self.mouse.click()
                    time.sleep(7.98 + np.abs(rd.gauss(0, .01)))
                    return
            if i == 7:
                conf = .8
                try:
                    loc = pag.locateCenterOnScreen(f'src/files/agility/fast_rek_run/screenshots/mouse_shot_{i}.png',
                                                   confidence=conf, region=None)
                    self.mouse.move_to((loc.x, loc.y), .2, 1 if i < 7 else 0, .005, 'rand')
                    self.mouse.click()
                    time.sleep(self.mouse_info.iloc[i, 3] + 1 + np.abs(rd.gauss(0, .5)))
                except:
                    loc = pag.locateCenterOnScreen(f'src/files/agility/fast_rek_run/screenshots/mouse_shot_{i}.png',
                                                   confidence=.5, region=None)
                    self.mouse.move_to((loc.x, loc.y), .2, 1 if i < 7 else 0, .005, 'rand')
                    self.mouse.click()
                    time.sleep(self.mouse_info.iloc[i, 3] + 1 + np.abs(rd.gauss(0, .5)))
                time.sleep(3 + np.abs(rd.gauss(0, .05)))
                return
            self.mouse.move_to(self.mouse_info.iloc[i, 0:2].tolist(), .2, 1 if i < 6 else 0, .005, 'rand')
            self.mouse.click()
            time.sleep(self.mouse_info.iloc[i, 3] + np.abs(rd.gauss(0, .1)))
        time.sleep(5)

    def vision_run(self):
        for i in range(8):
            self.check_for_mark()
            # self.check_for_mark(region=(self.rect_game_view.start.x, self.rect_game_view.start.y,
            #                             self.rect_game_view.end.x - self.rect_game_view.start.x,
            #                             self.rect_game_view.end.y - self.rect_game_view.start.y))
            if i == 2:
                if self.check_for_fall():
                    self.mouse.move_to((661, 50), .2, 1, .005, 'rand')
                    self.mouse.click()
                    time.sleep(7.98 + np.abs(rd.gauss(0, .01)))
                    loc = pag.locateCenterOnScreen('src/files/agility/fast_rek_run/screenshots/fall_shot.png',
                                                   confidence=.52)
                    if loc is None:
                        loc = pag.locateCenterOnScreen('src/files/agility/fast_rek_run/screenshots/fall_shot2.png',
                                                       confidence=.52)
                    if loc is None:
                        loc = pag.locateCenterOnScreen('src/files/agility/fast_rek_run/screenshots/fall_shot3.png',
                                                       confidence=.52)
                    self.mouse.move_to((loc.x, loc.y), .2, 1, .005, 'rand')
                    self.mouse.click()
                    time.sleep(7.98 + np.abs(rd.gauss(0, .01)))
                    return
            if i == 3:
                if self.check_for_fall():
                    self.mouse.move_to((616, 66), .2, 1, .005, 'rand')
                    self.mouse.click()
                    time.sleep(8.38 + np.abs(rd.gauss(0, .01)))
                    loc = pag.locateCenterOnScreen('src/files/agility/fast_rek_run/screenshots/fall_shot.png',
                                                   confidence=.52)
                    if loc is None:
                        loc = pag.locateCenterOnScreen('src/files/agility/fast_rek_run/screenshots/fall_shot3.png',
                                                       confidence=.52)
                    if loc is None:
                        loc = pag.locateCenterOnScreen('src/files/agility/fast_rek_run/screenshots/fall_shot2.png',
                                                       confidence=.52)
                    self.mouse.move_to((loc.x, loc.y), .2, 1, .005, 'rand')
                    self.mouse.click()
                    time.sleep(7.98 + np.abs(rd.gauss(0, .01)))
                    return
            conf = .8
            region = (183, 0, 356 - 183, pag.size()[1])
            try:
                loc = pag.locateCenterOnScreen(f'src/files/agility/fast_rek_run/screenshots/mouse_shot_{i}.png',
                                               confidence=conf, region=region if i == 3 else None)
                self.mouse.move_to((loc.x, loc.y), .2, 1 if i < 7 else 0, .005, 'rand')
                self.mouse.click()
                time.sleep(self.mouse_info.iloc[i, 3] + 1.1 + np.abs(rd.gauss(0, .5)))
            except:
                loc = pag.locateCenterOnScreen(f'src/files/agility/fast_rek_run/screenshots/mouse_shot_{i}.png',
                                               confidence=.5, region=region if i == 3 else None)
                self.mouse.move_to((loc.x, loc.y), .2, 1 if i < 7 else 0, .005, 'rand')
                self.mouse.click()
                time.sleep(self.mouse_info.iloc[i, 3] + 1 + np.abs(rd.gauss(0, .5)))
        time.sleep(5)

    def click_on_color(self, color):
        map = self.rect_game_view
        map = (map.start.x, map.start.y, map.end.x - map.start.x, map.end.y - map.start.y)
        pag.screenshot(imageFilename='src/images/temp/temp_screenshot.png', region=map)
        path_tagged = isolate_colors('src/images/temp/temp_screenshot.png', [color], "get_all_tagged_in_rect")
        contours = get_contours(path_tagged)
        # coords = get_contour_positions(contours)
        coords = rd.choice(contours[0])[0]
        print(contours[0])
        self.mouse.move_to((coords[0], coords[1]), .2, 0, .001)
        self.mouse.click()
        # cv2.imshow('mask', mask)
        # cv2.imshow('result', result)
        # cv2.waitKey()
        return (coords[0], coords[1])

    def test_loop(self, laps=500):
        s = time.time()
        try:
            i = 0
            login_time = datetime.datetime.now()
            update_status(self.username, 'agility', 'fast rek run laps', i,
                          last_login=login_time)
            while i < laps:
                start = time.time()
                if i % 8 == 0:
                    ab.vision_run()
                else:
                    ab.fast_rout()
                print(f'run {i} took {time.time() - start} seconds')
                update_status(self.username, 'agility', 'fast rek run laps', i, last_login=login_time)
                if new_action_available(self.username):
                    new_action = get_action(self.username)
                    if new_action == 'logout':
                        update_status(self.username, 'agility', 'rek training', -1, False)
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
                i += 1

        except Exception as e:
            update_status(self.username,
                          'agility failed',
                          f'error cost {e}\nafter {time.time()-s} seconds at: {datetime.datetime.now()}',
                          -1,
                          False)
            wipe_new_action(self.username)
            return
        update_status(self.username,
                      'agility successful',
                      f'complete after {time.time() - s:2f} seconds at {datetime.datetime.now().strftime("%H:%M:%S")}',
                      -1,
                      False)


if __name__ == '__main__':
    ab = RekAgilityBot(
        mouse_csv='C:\\Users\\sivar\\PycharmProjects\\OSRS-Bot-COLOR\\src\\files\\agility\\fast_rek_run\\fast_run.csv',
        username='travmanman')
    ab.test_loop(15)
