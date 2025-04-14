from states.gamestate import GameState
from constants import KEY

class Menu(GameState):
    def __init__(self, window, game_funcs, domains, draw_batches, **kwargs):
        super().__init__(window, game_funcs, domains, draw_batches, **kwargs)


class MainMenuState(Menu):
    def __init__(self, window, game_funcs, domains, draw_batches, **kwargs):
        super().__init__(window, game_funcs, domains, draw_batches, **kwargs)

    def parse_input(self, input):
        if KEY.ESCAPE in input["keys"]:
            input["keys"].remove(KEY.ESCAPE)
            self.game_funcs["exit_game"]()


class SettingsState(Menu):
    def __init__(self, window, game_funcs, domains, draw_batches, **kwargs):
        super().__init__(window, game_funcs, domains, draw_batches, **kwargs)


class PauseState(Menu):
    def __init__(self, window, game_funcs, domains, draw_batches, **kwargs):
        super().__init__(window, game_funcs, domains, draw_batches, **kwargs)

    def parse_input(self, input):
        if KEY.ESCAPE in input["keys"]:
            input["keys"].remove(KEY.ESCAPE)
            self.game_funcs["change_state"]("main_menu")



        