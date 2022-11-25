'''
Combat bot for OSNR. Attacks tagged monsters.
'''
from model.bot import BotStatus
from model.runelite_bot import RuneLiteBot
import time
import pyautogui as pag
import utilities.bot_cv as bcv
from firebase_tools.fb_logger import upload_to_firebase, update_status, new_action_available, get_action, wipe_new_action
import cv2
import numpy as np
import datetime


class OSRSCombat(RuneLiteBot):
    def __init__(self):
        title = "Combat Bot"
        description = ("This bot attacks NPCs tagged using RuneLite. Position your character in the viscinity of the tagged NPCs. " +
                       "Ensure there are no RuneLite overlays currently visible in the top-left of the game-view, as this bot relies " +
                       "on Opponent Information in that position. To remove any conflicting overlays (E.g., Fishing), log out and in.")
        super().__init__(title=title, description=description)
        self.kills = 0
        self.should_loot = False
        self.should_bank = False
        self.special_cases = False
        self.username = 'undefined'


    def create_options(self):
        self.options_builder.add_slider_option("kills", "How many kills?", 1, 500)
        self.options_builder.add_checkbox_option("prefs", "Additional options", ["Loot", "Bank"])
        self.options_builder.add_checkbox_option("special_cases", "Special Cases", ["Rock Crab Training"])
        self.options_builder.add_dropdown_option("username", "Username", ["dumbartonbri", "dumbartonbri2", "dumbartonbri3"])

    def save_options(self, options: dict):
        for option in options:
            if option == "kills":
                self.kills = options[option]
                self.log_msg(f"The bot will kill {self.kills} NPCs.")
            elif option == "prefs":
                if "Loot" in options[option]:
                    self.should_loot = True
                    # self.log_msg("Looting enabled.")
                    self.log_msg("Note: Looting is not yet implemented.")
                if "Bank" in options[option]:
                    self.should_bank = True
                    # self.log_msg("Banking enabled.")
                    self.log_msg("Note: Banking is not yet implemented.")
            elif option == "special_cases":
                if 'Rock Crab Training' in options[option]:
                    self.special_cases = True
                    self.log_msg("Rock Crab Training enabled.")
            elif option == "username":
                self.username = options[option]
                self.log_msg("RuneScape username: " + self.username)
            else:
                self.log_msg(f"Unknown option: {option}")
        self.options_set = True
        # TODO: if options are invalid, set options_set flag to false
        self.log_msg("Options set successfully.")

    def main_loop(self):
        self.setup_client(window_title="RuneLite", set_layout_fixed=True, collapse_runelite_settings=False, logout_runelite=True)

        # Make sure auto retaliate is on
        self.toggle_auto_retaliate(toggle_on=True)
        time.sleep(0.5)

        # Reselect inventory
        self.mouse.move_to(self.cp_inventory, 0.2, destination_variance=3)
        self.mouse.click()
        time.sleep(0.5)

        self.killed = 0
        while self.killed < self.kills:

            if not self.status_check_passed():
                return

            # Attack NPC
            if self.special_cases:
                hp = self.get_hp()
                if (hp is not None) and (hp < 12):
                    self.run_down()
                    food_points = self.get_all_tagged_in_rect(self.rect_inventory, self.TAG_BLUE)
                    if food_points is None:
                        self.logout()
                    else:
                        self.mouse.move_to(food_points[0], .2, time_variance=.001)
                        self.mouse.click()
                    time.sleep(5)
            timeout = 60  # check for up to 60 seconds
            while not self.is_in_combat():
                if not self.status_check_passed():
                    return
                if timeout <= 0:
                    if self.special_cases:
                        self.log_msg("Timed out looking for NPC. Trying to leave and re-enter.")
                        self.run_down()
                        time.sleep(5)
                    else:
                        self.log_msg("Timed out looking for NPC.")
                        self.set_status(BotStatus.STOPPED)
                        return
                npc = self.get_nearest_tagged_NPC(self.rect_game_view)
                if npc is not None:
                    self.log_msg("Attempting to attack NPC...")
                    self.mouse.move_to(npc, duration=.2, destination_variance=2, time_variance=.001, tween='rand')
                    self.mouse.click()
                    time.sleep(3)
                    timeout -= 3
                else:
                    self.log_msg("No NPC found.")
                    time.sleep(2)
                    timeout -= 12

            if not self.status_check_passed():
                return

            # If combat is over, assume we killed the NPC.
            timeout = 90  # give our character 90 seconds to kill the NPC
            while self.is_in_combat():
                if timeout <= 0:
                    self.log_msg("Timed out fighting NPC.")
                    self.set_status(BotStatus.STOPPED)
                    return
                time.sleep(2)
                timeout -= 2
                if not self.status_check_passed():
                    return
            self.killed += 1
            self.update_progress(self.killed / self.kills)
            self.log_msg(f"Enemy killed. {self.kills - self.killed} to go!")
        self.update_progress(1)
        self.log_msg("Bot has completed all of its iterations.")
        self.set_status(BotStatus.STOPPED)

    def toggle_auto_retaliate(self, toggle_on: bool):
        '''
        Toggles auto retaliate. Assumes client window is configured.
        Args:
            toggle_on: Whether to turn on or off.
        '''
        self.log_msg("Toggling auto retaliate...")
        # click the combat tab
        self.mouse.move_to(self.cp_combat, duration=1, destination_variance=3)
        pag.click()
        time.sleep(0.5)

        # Search for the auto retaliate button (deselected)
        # If None, then auto retaliate is on.
        auto_retal_btn = bcv.search_img_in_rect(f"{bcv.BOT_IMAGES}/near_reality/cp_combat_autoretal.png", self.rect_inventory, conf=0.9)

        if toggle_on and auto_retal_btn is not None or not toggle_on and auto_retal_btn is None:
            self.mouse.move_to((644, 402), 0.2, destination_variance=5)
            pag.click()
        elif toggle_on:
            print("Auto retaliate is already on.")
        else:
            print("Auto retaliate is already off.")

    def test_loop(self, rounds=100, battle_type='crabs', loot=False, safespot=False):
        s = time.time()
        self.killed = 0
        if not bcv.search_text_in_rect(self.rect_game_view, [''], ['you were disconnected from the server']):
            update_status(self.username,
                          'combat failed',
                          f'logged out at: {datetime.datetime.now()}',
                          -1,
                          None,
                          logged_in=False)
        update_status(self.username, f'combat training {battle_type}', 'starting', self.killed, datetime.datetime.now(), True)
        try:

            while self.killed < rounds:
                # if not self.status_check_passed():
                #     return

                # Attack NPC
                timeout = 60  # check for up to 60 seconds
                while not self.is_in_combat():
                    if loot:
                        loc = self.get_nearest_tag(self.TAG_BLUE)
                        if loc is not None:
                            self.mouse.move_to(loc, 3, time_variance=.001)
                            self.mouse.click()
                            time.sleep(1)
                    # if not self.status_check_passed():
                    #     return
                    if timeout <= 0:
                        # self.log_msg("Timed out looking for NPC.")
                        # self.set_status(BotStatus.STOPPED)
                        print('no NPC')
                        if battle_type == 'crabs':
                            update_status(self.username, 'combat training', 'resetting agro', self.killed,
                                      None, True)
                            self.run_down()

                        timeout = 60
                    npc = self.get_nearest_tagged_NPC(self.rect_game_view)
                    if npc is not None:
                        # self.log_msg("Attempting to attack NPC...")
                        if safespot:
                            self.mouse.move_to(npc, duration=.1, destination_variance=3, time_variance=.001, tween='rand')
                            pag.rightClick()
                            loc = pag.locateCenterOnScreen('src/images/bot/attack_sign.png', confidence=.9)
                            if loc is not None:
                                self.mouse.move_to(loc, 0.1, time_variance=.001)
                                pag.click()
                                time.sleep(1)
                            # Check if the center has the yellow NPC square, if not, find it and click it!

                        else:
                            self.mouse.move_to(npc, duration=.1, destination_variance=3, time_variance=.001, tween='rand')
                            self.mouse.click()
                            time.sleep(3)
                        timeout -= 29
                    else:
                        # self.log_msg("No NPC found.")
                        time.sleep(2)
                        timeout -= 15
                    if new_action_available(self.username):
                        new_action = get_action(self.username)
                        if new_action == 'logout':
                            update_status(self.username, 'combat', f'combat training {battle_type}', -1, None)
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

                # if not self.status_check_passed():
                #     return

                # If combat is over, assume we killed the NPC.
                timeout = 90  # give our character 90 seconds to kill the NPC
                while self.is_in_combat():
                    if timeout <= 0:
                        # self.log_msg("Timed out fighting NPC.")
                        # self.set_status(BotStatus.STOPPED)
                        print('timeout done')
                        return
                    time.sleep(2)
                    timeout -= 2
                    # if not self.status_check_passed():
                    #     return
                self.killed += 1
                update_status(self.username,
                              'combat',
                              f'killed {self.killed} {battle_type} of {rounds} in {datetime.timedelta(seconds=round(time.time() - s, 2))}',
                              '',
                              None,
                              logged_in=True)
                print(f"Enemy killed. {rounds - self.killed} to go!")
        except Exception as e:
            update_status(self.username,
                          'combat failed: ' + battle_type,
                          f'error cost {e}\nafter {time.time()-s} seconds at: {datetime.datetime.now()}',
                          -1,
                          None,
                          logged_in=False)
            wipe_new_action(self.username)
            return
        print(f'killed {self.killed} NPCs')
        update_status(self.username,
                      'combat successful',
                      f'complete after {time.time() - s:2f} seconds at {datetime.datetime.now().strftime("%H:%M:%S")}',
                      -1,
                      None,
                      logged_in=False)

    def run_down(self):
        for i in range(3):
            self.mouse.move_to((650, 176), 0.2, destination_variance=3, time_variance=.001)
            self.mouse.click()
            time.sleep(5)
        for i in range(3):
            self.mouse.move_to((650, 42), 0.2, destination_variance=3, time_variance=.001)
            self.mouse.click()
            time.sleep(5)
        pass


if __name__ == "__main__":
    bot = OSRSCombat('travmanman')
    bot.test_loop(62, 'demons', loot=False, safespot=True)
