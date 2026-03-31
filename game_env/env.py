import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Union
import config

from game import Action, Game


from .observe import observe, PIXELS_PER_UNIT


class GameEnv(gym.Env):
    def __init__(
        self,
        layout_name: str,
        period: int = 50,
        truncate_at: Union[int, None] = None,
        terminate_at: Union[int, None] = None,
    ):
        self.game = Game(*config.load(layout_name), move_to_axis=True)
        w, h = self.game.kitchen_w, self.game.kitchen_h

        self.player_ids = [p.id for p in self.game._players]
        self.player_N = len(self.player_ids)
        self.single_player_action_space = spaces.Discrete(len(Action))
        self.action_space = spaces.Dict(
            {p_id: self.single_player_action_space for p_id in self.player_ids}
        )
        self.single_player_observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(h * PIXELS_PER_UNIT, w * PIXELS_PER_UNIT),
            dtype=np.float32,
        )
        self.observation_space = spaces.Dict(
            {p_id: self.single_player_observation_space for p_id in self.player_ids}
        )

        self.step_count = 0
        self.period = period
        self.truncate_at = truncate_at
        self.terminate_at = terminate_at
        self.periodic_return = 0.0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.game.reset()
        self.step_count = 0
        obs, info = observe(self.game), dict()
        return obs, info

    def step(self, action: Union[dict[str, int], dict[str, Action]]):
        actions = {
            p_id: a if type(a) is Action else Action(value=a)
            for p_id, a in action.items()
        }

        feedbacks = self.game.step(actions)
        reward = sum(feedbacks.values())
        terminated, truncated, info = False, False, dict()

        obs = observe(self.game)
        self.periodic_return += reward
        self.step_count += 1

        if self.step_count % self.period == 0:
            info["periodic_return"] = self.periodic_return
            self.periodic_return = 0.0

        if self.terminate_at != None:
            terminated = self.step_count >= self.terminate_at
        if self.truncate_at != None:
            truncated = self.step_count >= self.truncate_at

        return obs, reward, terminated, truncated, info
