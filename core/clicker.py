"""Правила игры «Кликер» (задание 3 повышенной сложности)."""


class ClickerGame:
    """Игра на скорость кликов за ограниченное время."""

    def __init__(self, duration: float = 10.0) -> None:
        if duration <= 0:
            raise ValueError("Длительность раунда должна быть положительной")

        self.duration = float(duration)
        self.score = 0
        self.clicks = 0
        self.best_score = 0
        self.elapsed = 0.0
        self.active = False

    def start(self) -> None:
        """Начинает новый раунд."""
        self.score = 0
        self.clicks = 0
        self.elapsed = 0.0
        self.active = True

    def click(self) -> int:
        """Обрабатывает клик и возвращает текущий счёт."""
        if self.active:
            self.clicks += 1
            self.score += 1
        return self.score

    def update(self, dt: float) -> bool:
        """Продвигает таймер на dt секунд; True, если раунд ещё идёт."""
        if dt < 0:
            raise ValueError("dt не может быть отрицательным")

        if not self.active:
            return False

        self.elapsed = min(self.duration, self.elapsed + dt)
        if self.elapsed >= self.duration:
            self.active = False
            self.best_score = max(self.best_score, self.score)

        return self.active

    @property
    def time_left(self) -> float:
        """Сколько секунд осталось до конца раунда."""
        return max(0.0, self.duration - self.elapsed)

    @property
    def clicks_per_second(self) -> float:
        """Среднее число кликов в секунду."""
        if self.elapsed <= 0:
            return 0.0
        return round(self.clicks / self.elapsed, 2)

    def reset_best(self) -> None:
        """Сбрасывает рекорд."""
        self.best_score = 0
