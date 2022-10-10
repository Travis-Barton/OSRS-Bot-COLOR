'''
Serves as the mediator between a bot and the UI. Methods should likely not be modified.
'''

from model.bot import Bot, BotStatus
from view.bot_view import BotView


class BotController(object):
    def __init__(self, model, view):
        '''
        Constructor.
        '''
        self.model: Bot = model
        self.view: BotView = view

    def play_pause(self):
        '''
        Play/pause btn clicked on view.
        '''
        self.model.play_pause()

    def stop(self):
        '''
        Stop btn clicked on view.
        '''
        self.model.stop()

    def get_options_view(self, parent):
        '''
        Called from view. Fetches the options view from the model.
        '''
        self.model.set_status(BotStatus.CONFIGURING)
        return self.model.get_options_view(parent)

    def save_options(self, options):
        '''
        Called from view. Tells model to save options.
        '''
        self.model.save_options(options)
        self.model.set_status(BotStatus.STOPPED)

    def abort_options(self):
        '''
        Called from view when options window is closed manually.
        '''
        self.update_log("Bot configuration aborted.")
        self.model.set_status(BotStatus.STOPPED)

    def update_status(self):
        '''
        Called from model. Tells view to update status.
        '''
        status = self.model.status
        if status == BotStatus.RUNNING:
            self.view.frame_info.update_status_running()
        elif status == BotStatus.PAUSED:
            self.view.frame_info.update_status_paused()
        elif status == BotStatus.STOPPED:
            self.view.frame_info.update_status_stopped()
        elif status == BotStatus.CONFIGURING:
            self.view.frame_info.update_status_configuring()

    def update_progress(self):
        '''
        Called from model. Tells view to update progress.
        '''
        self.view.frame_info.update_progress(self.model.progress)

    def update_log(self, msg: str, overwrite: bool = False):
        '''
        Called from model. Tells view to update log.
        '''
        self.view.frame_output_log.update_log(msg, overwrite)

    def clear_log(self):
        '''
        Called from model. Tells view to clear log.
        '''
        self.view.frame_output_log.clear_log()

    def change_model(self, model: Bot):
        '''
        Called from view. Swaps the controller's model, halting the old one. Reconfigures the info frame.
        Args:
            model: The new model to use.
        '''
        if self.model is not None:
            self.model.stop()
            self.model.options_set = False
        self.model = model
        if self.model is not None:
            self.view.frame_info.setup(title=model.title, description=model.description)
        else:
            self.view.frame_info.setup(title="", description="")
        self.clear_log()


class MockBotController(object):

    def __init__(self, model):
        '''
        A mock controller for testing purposes. Allows you to run a bot without a UI.
        Usage:
            # Within your Bot's class...
            if __name__ == '__main__':
                bot = MyBot()
                bot.set_controller(MockBotController(bot))
                time.sleep(2)
                bot.main_loop()
        '''
        self.model: Bot = model

    def update_status(self):
        '''
        Called from model. Tells view to update status
        '''
        print(f"Updating status on UI to: {self.model.status}")

    def update_progress(self):
        '''
        Called from model. Tells view to update progress.
        '''
        print(f"Updating progress bar on view to: {self.model.progress * 100}")  # might have the math wrong here

    def update_log(self, msg: str, overwrite: bool = False):
        '''
        Called from model. Tells view to update log.
        '''
        print(f"Send log msg to UI: {msg}")

    def clear_log(self):
        '''
        Called from model. Tells view to clear log.
        '''
        print("--- Clearing log ---")
