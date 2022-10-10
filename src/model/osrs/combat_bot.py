'''
Combat bot for OSNR. Attacks tagged monsters.
'''
from model.bot import BotStatus
from model.runelite_bot import RuneLiteBot
import time
import pyautogui as pag


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

    def create_options(self):
        self.options_builder.add_slider_option("kills", "How many kills?", 1, 300)
        self.options_builder.add_checkbox_option("prefs", "Additional options", ["Loot", "Bank"])
        self.options_builder.add_checkbox_option("special_cases", "Special Cases", ["Rock Crab Training"])

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
            else:
                self.log_msg(f"Unknown option: {option}")
        self.options_set = True
        # TODO: if options are invalid, set options_set flag to false
        self.log_msg("Options set successfully.")

    def main_loop(self):
        self.setup_client()
        self.set_compass_north()

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
            timeout = 60  # check for up to 60 seconds
            while not self.is_in_combat():
                if not self.status_check_passed():
                    return
                hp = self.get_hp()
                if hp < 10:
                    self.run_down()
                    food_points = self.get_all_tagged_in_rect(self.rect_inventory)
                    if food_points is None:
                        self.logout()
                    else:
                        self.mouse.move_to(food_points[0], .2, time_variance=.001)
                        self.mouse.click()
                    time.sleep(5)
                if timeout <= 0:
                    if self.special_cases == 'Rock Crab Training':
                        self.log_msg("Timed out looking for NPC. Trying to leave and re-enter.")
                        self.run_down()
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
                    timeout -= 6

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

    def test_loop(self, rounds=100):
        self.killed = 0
        while self.killed < rounds:
            # if not self.status_check_passed():
            #     return

            # Attack NPC
            timeout = 60  # check for up to 60 seconds
            while not self.is_in_combat():
                # if not self.status_check_passed():
                #     return
                if timeout <= 0:
                    # self.log_msg("Timed out looking for NPC.")
                    # self.set_status(BotStatus.STOPPED)
                    print('no NPC')
                    self.run_down()
                    timeout = 60
                npc = self.get_nearest_tagged_NPC(self.rect_game_view)
                if npc is not None:
                    # self.log_msg("Attempting to attack NPC...")
                    self.mouse.move_to(npc, duration=.2, destination_variance=2, time_variance=.001, tween='rand')
                    self.mouse.click()
                    time.sleep(3)
                    timeout -= 3
                else:
                    # self.log_msg("No NPC found.")
                    time.sleep(2)
                    timeout -= 6

            # if not self.status_check_passed():
            #     return

            # If combat is over, assume we killed the NPC.
            timeout = 90  # give our character 90 seconds to kill the NPC
            while self.is_in_combat():
                if timeout <= 0:
                    # self.log_msg("Timed out fighting NPC.")
                    # self.set_status(BotStatus.STOPPED)
                    return
                time.sleep(2)
                timeout -= 2
                # if not self.status_check_passed():
                #     return
            self.killed += 1
            print(f"Enemy killed. {rounds - self.killed} to go!")
        print(f'killed {self.killed} NPCs')

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
    bot = OSRSCombat()
    bot.test_loop(700)
