"""Тесты логики игры «Кликер» (задание 3 повышенной сложности)."""

import unittest

from core.clicker import ClickerGame


class TestClickerGame(unittest.TestCase):
    """Проверка начисления очков и работы таймера."""

    def test_start_resets_state(self):
        game = ClickerGame(duration=5)
        game.click()
        game.start()
        self.assertTrue(game.active)
        self.assertEqual(game.score, 0)
        self.assertEqual(game.clicks, 0)
        self.assertEqual(game.elapsed, 0.0)

    def test_click_increases_score(self):
        game = ClickerGame(duration=5)
        game.start()
        self.assertEqual(game.click(), 1)
        self.assertEqual(game.click(), 2)
        self.assertEqual(game.score, 2)

    def test_clicks_ignored_when_inactive(self):
        game = ClickerGame(duration=5)
        self.assertEqual(game.click(), 0)
        self.assertEqual(game.score, 0)

    def test_timer_finishes_game(self):
        game = ClickerGame(duration=1.0)
        game.start()
        for _ in range(3):
            game.click()

        self.assertTrue(game.update(0.5))
        self.assertFalse(game.update(0.6))
        self.assertFalse(game.active)
        self.assertEqual(game.best_score, 3)

    def test_time_left_never_negative(self):
        game = ClickerGame(duration=1.0)
        game.start()
        game.update(2.0)
        self.assertEqual(game.time_left, 0.0)

    def test_clicks_per_second(self):
        game = ClickerGame(duration=10)
        game.start()
        game.click()
        game.click()
        game.update(2.0)
        self.assertEqual(game.clicks_per_second, 1.0)

    def test_best_score_keeps_maximum(self):
        game = ClickerGame(duration=1.0)
        game.start()
        game.click()
        game.update(1.0)

        game.start()
        game.click()
        game.click()
        game.update(1.0)
        self.assertEqual(game.best_score, 2)

    def test_invalid_duration(self):
        with self.assertRaises(ValueError):
            ClickerGame(duration=0)

    def test_invalid_dt(self):
        game = ClickerGame(duration=5)
        game.start()
        with self.assertRaises(ValueError):
            game.update(-1)


if __name__ == "__main__":
    unittest.main()
