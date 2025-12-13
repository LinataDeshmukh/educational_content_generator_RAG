"""Adaptive learning algorithms: Q-Learning and Thompson Sampling."""

import logging
import random
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class DifficultyLevel(str, Enum):
    """Difficulty levels for questions."""
    LOW = "low"
    MEDIUM = "medium"
    HARD = "hard"


class QLearningAgent:
    """Q-Learning agent for adaptive difficulty selection."""

    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.9,
        exploration_rate: float = 0.2,
    ):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.q_table: Dict[Tuple[str, str], Dict[str, float]] = {}
        self._initialize_q_table()

    def _initialize_q_table(self) -> None:
        difficulties = [DifficultyLevel.LOW, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]
        performance_trends = ["improving", "stable", "declining"]

        for difficulty in difficulties:
            for trend in performance_trends:
                state = (difficulty.value, trend)
                self.q_table[state] = {
                    DifficultyLevel.LOW.value: 0.0,
                    DifficultyLevel.MEDIUM.value: 0.0,
                    DifficultyLevel.HARD.value: 0.0,
                }

    def get_state(self, current_difficulty: str, performance_trend: str) -> Tuple[str, str]:
        return (current_difficulty, performance_trend)

    def choose_action(
        self, state: Tuple[str, str], available_actions: Optional[List[str]] = None
    ) -> str:
        if state not in self.q_table:
            self.q_table[state] = {
                DifficultyLevel.LOW.value: 0.0,
                DifficultyLevel.MEDIUM.value: 0.0,
                DifficultyLevel.HARD.value: 0.0,
            }

        if available_actions is None:
            available_actions = [d.value for d in DifficultyLevel]

        if random.random() < self.exploration_rate:
            return random.choice(available_actions)

        q_values = self.q_table[state]
        return max(available_actions, key=lambda a: q_values.get(a, 0.0))

    def update_q_value(
        self,
        state: Tuple[str, str],
        action: str,
        reward: float,
        next_state: Optional[Tuple[str, str]] = None,
    ) -> None:
        if state not in self.q_table:
            self.q_table[state] = {d.value: 0.0 for d in DifficultyLevel}

        current_q = self.q_table[state].get(action, 0.0)
        max_next_q = max(self.q_table.get(next_state, {}).values()) if next_state else 0.0
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        self.q_table[state][action] = new_q

    def get_q_table(self) -> Dict:
        return self.q_table.copy()


class ThompsonSamplingAgent:
    """Thompson Sampling agent for exploration-exploitation balance."""

    def __init__(self):
        self.difficulty_params: Dict[str, Tuple[float, float]] = {
            DifficultyLevel.LOW.value: (1.0, 1.0),
            DifficultyLevel.MEDIUM.value: (1.0, 1.0),
            DifficultyLevel.HARD.value: (1.0, 1.0),
        }

    def choose_action(self, available_actions: Optional[List[str]] = None) -> str:
        if available_actions is None:
            available_actions = [d.value for d in DifficultyLevel]

        samples = {}
        for action in available_actions:
            alpha, beta = self.difficulty_params.get(action, (1.0, 1.0))
            samples[action] = np.random.beta(alpha, beta)

        return max(samples, key=samples.get)

    def update(self, action: str, reward: float) -> None:
        if action not in self.difficulty_params:
            self.difficulty_params[action] = (1.0, 1.0)

        alpha, beta = self.difficulty_params[action]
        if reward > 0:
            alpha += 1.0
        else:
            beta += 1.0
        self.difficulty_params[action] = (alpha, beta)

    def get_params(self) -> Dict[str, Tuple[float, float]]:
        return self.difficulty_params.copy()


class AdaptiveQuizManager:
    """Manages adaptive quiz using Q-Learning and Thompson Sampling."""

    def __init__(self):
        self.q_learning_agent = QLearningAgent()
        self.thompson_sampling_agent = ThompsonSamplingAgent()

    def calculate_performance_trend(
        self, recent_answers: List[bool], window_size: int = 3
    ) -> str:
        if len(recent_answers) < 2:
            return "stable"

        recent = recent_answers[-window_size:]
        if len(recent) < 2:
            return "stable"

        first_half = recent[: len(recent) // 2]
        second_half = recent[len(recent) // 2 :]

        first_score = sum(first_half) / len(first_half) if first_half else 0.5
        second_score = sum(second_half) / len(second_half) if second_half else 0.5

        if second_score > first_score + 0.1:
            return "improving"
        elif second_score < first_score - 0.1:
            return "declining"
        return "stable"

    def calculate_reward(self, is_correct: bool, difficulty: str) -> float:
        if is_correct:
            rewards = {
                DifficultyLevel.LOW.value: 0.5,
                DifficultyLevel.MEDIUM.value: 1.0,
                DifficultyLevel.HARD.value: 1.5,
            }
        else:
            rewards = {
                DifficultyLevel.LOW.value: -0.55,
                DifficultyLevel.MEDIUM.value: -0.50,
                DifficultyLevel.HARD.value: -0.75,
            }
        return rewards.get(difficulty, 0.0)

    def select_next_difficulty(
        self,
        current_difficulty: str,
        performance_trend: str,
        last_answer_correct: bool,
        use_thompson_sampling: bool = True,
    ) -> str:
        difficulty_levels = [d.value for d in DifficultyLevel]
        current_index = difficulty_levels.index(current_difficulty)

        if last_answer_correct:
            next_index = min(current_index + 1, len(difficulty_levels) - 1)
        else:
            next_index = max(current_index - 1, 0)

        next_difficulty = difficulty_levels[next_index]

        # Update learning algorithms
        if use_thompson_sampling:
            self.thompson_sampling_agent.update(
                next_difficulty, 1.0 if last_answer_correct else -0.5
            )
        else:
            state = self.q_learning_agent.get_state(current_difficulty, performance_trend)
            next_state = self.q_learning_agent.get_state(next_difficulty, performance_trend)
            reward = 1.0 if last_answer_correct else -0.5
            self.q_learning_agent.update_q_value(state, next_difficulty, reward, next_state)

        return next_difficulty

    def get_learning_stats(self) -> Dict:
        return {
            "q_learning": {
                "q_table": self.q_learning_agent.get_q_table(),
                "exploration_rate": self.q_learning_agent.exploration_rate,
            },
            "thompson_sampling": {
                "beta_params": self.thompson_sampling_agent.get_params(),
            },
        }

