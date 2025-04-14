import json
import pyglet

import time

from constants import DEFAULT_CONFIG, CONFIG_PATH, WINDOW_TITLE
from states.menus import MainMenuState, SettingsState, PauseState
from states.playstate import PlayState
from rendering import Renderer

vertex_attributes = {
    'position': {'format': 'f', 'count': 3, 'location': 0, 'instance': False},
    'colour': {'format': 'f', 'count': 4, 'location': 1, 'instance': False},
}

point_vertex_domain = pyglet.graphics.vertexdomain.VertexDomain(vertex_attributes)
line_vertex_domain = pyglet.graphics.vertexdomain.VertexDomain(vertex_attributes)
fragment_vertex_domain = pyglet.graphics.vertexdomain.VertexDomain(vertex_attributes)

domains = {
    "points": point_vertex_domain,
    "lines": line_vertex_domain,
    "fragments": fragment_vertex_domain,
}

def load_config(file_path=CONFIG_PATH):
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
            return config
    except FileNotFoundError:
        print("Configuration file not found. Using default settings.")
        return DEFAULT_CONFIG
    except json.JSONDecodeError:
        print(f"Error decoding {file_path}. Using default settings.")
        return DEFAULT_CONFIG
    
def save_config(config, file_path=CONFIG_PATH):
    try:
        with open(file_path, 'w') as file:
            json.dump(config, file, indent=4)
    except IOError as e:
        print(f"Error saving configuration: {e}")

def initiate_app():
    global user_input
    user_input = {
        "mouse_buttons": [],
        "modifiers": [],
        "mouse_position": [0.0, 0.0],
        "mouse_delta": [0.0, 0.0],
        "keys": [],
    }

    global frame_count, fps, start_time
    frame_count = 0
    fps = 0.0
    start_time = time.time()

    global config
    config = load_config()
    win_width = config["window_width"]
    win_height = config["window_height"]

    global mouse_position
    mouse_position = [0.0, 0.0]

    global mouse_delta
    mouse_delta = [0.0, 0.0]

    global window
    window = pyglet.window.Window(
        width=win_width,
        height=win_height,
        caption=WINDOW_TITLE
    )

    global renderer
    renderer = Renderer()

    game_funcs = {
        "change_state": change_state,
        "exit_game": exit_game,
        "shader_program": renderer.shader_program
    }

    draw_batches = {
        "points": pyglet.graphics.Batch(),
        "lines": pyglet.graphics.Batch(),
        "fragments": pyglet.graphics.Batch()
    }

    global game_states
    game_states = {
        "play": PlayState(window, game_funcs, domains, draw_batches),
        "main_menu": MainMenuState(window, game_funcs, domains, draw_batches),
        "settings": SettingsState(window, game_funcs, domains, draw_batches),
        "pause": PauseState(window, game_funcs, domains, draw_batches)
    }

    fov = game_states["play"].static_camera.fov
    znear = game_states["play"].static_camera.znear
    far = game_states["play"].static_camera.zfar

    renderer.set_projection_matrix(win_width, win_height, fov, znear, far)

    @window.event
    def on_mouse_motion(x, y, dx, dy):
        user_input["mouse_position"] = [x, y]
        user_input["mouse_delta"] = [dx, dy]

    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        if buttons not in user_input["mouse_buttons"]:
            user_input["mouse_buttons"].append(buttons)
        user_input["mouse_position"] = [x, y]
        user_input["mouse_delta"] = [dx, dy]

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        if button not in user_input["mouse_buttons"]:
            user_input["mouse_buttons"].append(button)
        if modifiers not in user_input["modifiers"]:
            user_input["modifiers"].append(modifiers)

        user_input["mouse_position"] = [x, y]

    @window.event
    def on_mouse_release(x, y, button, modifiers):
        if button in user_input["mouse_buttons"]:
            user_input["mouse_buttons"].remove(button)
        user_input["mouse_position"] = [x, y]

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol not in user_input["keys"]:
            user_input["keys"].append(symbol)
        if modifiers not in user_input["modifiers"]:
            user_input["modifiers"].append(modifiers)
        if symbol == pyglet.window.key.ESCAPE:
            return pyglet.event.EVENT_HANDLED

    @window.event
    def on_key_release(symbol, _):
        if symbol in user_input["keys"]:
            user_input["keys"].remove(symbol)
        if symbol in user_input["modifiers"]:
            user_input["modifiers"].remove(symbol)

    @window.event
    def on_draw():
        window.clear()
        draw_batches["points"].draw()
        draw_batches["lines"].draw()
        draw_batches["fragments"].draw()

        for label in debug_labels:
            label.draw()

    @window.event
    def on_close():
        exit_game()
     
    global debug_labels
    debug_labels = initiate_debug_labels(window)

    global current_state
    current_state = None

def exit_game():
    save_config(config)
    pyglet.app.exit()    

def update_debug_text(_):
    global frame_count, fps, start_time
    frame_count += 1
    current_time = time.time()
    delta_time = current_time - start_time

    if delta_time >= 1.0:
        fps = frame_count / delta_time
        frame_count = 0
        start_time = current_time

    debug_labels[0].text = f"FPS: {fps:.2f}. Game State: {current_state}"
    debug_labels[1].text = f"Window Size: {
        window.width
    }x{
        window.height
    }"
    debug_labels[2].text = f"Mouse Position: {
        user_input["mouse_position"][0]
    }, {
        user_input["mouse_position"][1]
    }"

    window.clear()

def change_state(new_state):
    if new_state not in game_states:
        raise ValueError(f"Invalid state name: {new_state}.")
    global current_state
    current_state = game_states[new_state]

def run_app():
    global current_state
    current_state = game_states["play"]
    pyglet.clock.schedule_interval(cycle_state, 1/config["fps"])
    pyglet.app.run()

def cycle_state(delta_time):
    current_state.update(delta_time, user_input)
    update_debug_text(delta_time)

def initiate_debug_labels(window):
    debug_label1 = pyglet.text.Label(
        "",
        font_name="Arial",
        font_size=14,
        x=10,
        y=window.height - 10,
        anchor_x="left",
        anchor_y="top",
        color=(255, 255, 255, 255)
    )
    debug_label2 = pyglet.text.Label(
        "",
        font_name="Arial",
        font_size=14,
        x=10,
        y=window.height - 30,
        anchor_x="left",
        anchor_y="top",
        color=(255, 255, 255, 255)
    )
    debug_label3 = pyglet.text.Label(
        "",
        font_name="Arial",
        font_size=14,
        x=10,
        y=window.height - 50,
        anchor_x="left",
        anchor_y="top",
        color=(255, 255, 255, 255)
    )

    return [debug_label1, debug_label2, debug_label3]

if __name__ == "__main__":
    initiate_app()
    run_app()