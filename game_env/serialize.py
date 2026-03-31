import gymnasium as gym

from typing import Union

from .env import GameEnv

from gymnasium.vector.utils import batch_space

import numpy as np


class SerializeWrapper(gym.Env):
    def __init__(self, env: Union[GameEnv, gym.vector.SyncVectorEnv]):
        super().__init__()
        self.env = env
        if type(self.env) is gym.vector.SyncVectorEnv:
            assert all(type(e) is GameEnv for e in self.env.envs)
            e: GameEnv = self.env.envs[0]
            self.is_vector_env = True
            self.copy_N = self.env.num_envs
        else:
            assert type(self.env) is GameEnv
            e = self.env
            self.is_vector_env = False
            self.copy_N = 1

        self.player_ids, self.player_N = e.player_ids, e.player_N
        self.N = self.player_N * self.copy_N
        self.single_observation_space = e.single_player_observation_space

        self.observation_space = batch_space(self.single_observation_space, n=self.N)
        self.single_action_space = e.single_player_action_space
        self.action_space = batch_space(self.single_action_space, n=self.N)

    def reset(self, **kwargs):
        _obs, info = self.env.reset(**kwargs)
        return self.flatten(_obs), info

    def flatten(self, _obs):
        return np.concatenate(
            [
                _obs[p_id] if self.is_vector_env else np.expand_dims(_obs[p_id], axis=0)
                for p_id in self.player_ids
            ],
            axis=0,
        )

    def step(self, action: np.ndarray):
        _action = dict()
        for i, p_id in enumerate(self.player_ids):
            begin = i * self.copy_N
            _action[p_id] = action[begin : begin + self.copy_N]
            if not self.is_vector_env:
                _action[p_id] = _action[p_id].squeeze()

        _obs, _reward, _terminated, _truncated, info = self.env.step(_action)

        obs = self.flatten(_obs)

        if not self.is_vector_env:
            _reward, _terminated, _truncated = [_reward], [_terminated], [_truncated]
        reward = np.concatenate([_reward] * self.player_N, axis=0)
        terminated = np.concatenate([_terminated] * self.player_N, axis=0)
        truncated = np.concatenate([_truncated] * self.player_N, axis=0)

        return obs, reward, terminated, truncated, info
