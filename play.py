import torch

import numpy as np
from game_env import GameEnv
from game_env.serialize import SerializeWrapper

from game_ui import GameUI, USER_KEYBOARD_MAP
from ppo_train import Agent

from game import Game
from config import load

model_name = "circuit_room_2__1671437407"
# model_name = "circuit_room_8__1671546995"

layout_name = model_name.split("__")[0]

layout_name = "circuit_room_2"


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    agent = Agent().to(device)
    agent.load_state_dict(torch.load(f"./trained/{model_name}.pth", device))
    agent.eval()

    env_raw = GameEnv(layout_name)
    env = SerializeWrapper(env_raw)
    obs, info = env.reset()
    window = GameUI(env_raw.game, keyboard_map=USER_KEYBOARD_MAP, caption=layout_name)
    frozen = True
    while not window.is_closed:
        if frozen:
            window.wait_keyboard()
            frozen = False
        obs = torch.Tensor(obs).to(device)
        action, logprob, _, value = agent.get_action_and_value(obs)
        obs, reward, done, truncated, info = env.step(action.cpu().numpy())
        window.animate()

    # game = Game(*load(layout_name), move_to_axis=True).reset()

    # window = GameUI(game, keyboard_map=USER_KEYBOARD_MAP, caption=layout_name)
    # while not window.is_closed:
    #     actions = window.wait_keyboard()
    #     feedbacks = game.step(actions)
    #     for player_id, reward in feedbacks.items():
    #         if reward > 0:
    #             print(f"player_{player_id} just contributed {reward} point!")
    #     window.animate()
