from __future__ import annotations
from abc import ABC, abstractmethod
import math
from models import WaveTools


class WaveRule(ABC):
    """
    base class for implementing wave rules
    """

    def __init__(self, name: str, x_y_ratio=1.7):
        self.name = name
        self.conditions = self.set_conditions()
        self.__x_y_ratio = x_y_ratio

    @property
    def x_y_ratio(self):
        return self.__x_y_ratio

    @x_y_ratio.setter
    def x_y_ratio(self, value):
        self.__x_y_ratio = value

    @abstractmethod
    def set_conditions(self):
        pass

    def __repr__(self):
        return str(self.conditions)


class Impulse(WaveRule):
    """
    Rules for an impulsive wave according to

    https://www.goldseiten-forum.com/attachment/113839-elliottwellentutorial-pdf/

    """

    def set_conditions(self):
        # condition returns TRUE -> no exit
        conditions = {  # WAVE 2
            "w2_1": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: wave2.low > wave1.low,
                "message": "End of Wave2 is lower than Start of Wave1.",
            },
            "w2_2": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: wave2.length >= 0.2 * wave1.length,
                "message": "Wave2 is shorten than 20% of Wave1.",
            },
            "w2_3": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: 9 * wave2.duration > wave1.duration,
                "message": "Wave2 is longer than 9x Wave1",
            },
            # WAVE 3
            "w3_1": {
                "waves": ["wave1", "wave3", "wave5"],
                "function": lambda wave1, wave3, wave5: not (
                    wave3.length < wave5.length and wave3.length < wave1.length
                ),
                "message": "Wave3 is the shortest Wave.",
            },
            "w3_2": {
                "waves": ["wave1", "wave3"],
                "function": lambda wave1, wave3: wave3.high > wave1.high,
                "message": "End of Wave3 is lower than End of Wave1",
            },
            "w3_3": {
                "waves": ["wave1", "wave3"],
                "function": lambda wave1, wave3: wave3.length >= wave1.length / 3.0,
                "message": "Wave3 is shorter than 1/3 of Wave1",
            },
            "w3_4": {
                "waves": ["wave2", "wave3"],
                "function": lambda wave2, wave3: wave3.length > wave2.length,
                "message": "Wave3 shorter than Wave2",
            },
            "w3_5": {
                "waves": ["wave1", "wave3"],
                "function": lambda wave1, wave3: 7 * wave3.duration > wave1.duration,
                "message": "Wave3 more than 7 times longer than Wave1.",
            },
            # WAVE 4
            "w4_1": {
                "waves": ["wave1", "wave4"],
                "function": lambda wave1, wave4: wave4.low > wave1.high,
                "message": "End of Wave4 is lower than End of Wave1",
            },
            "w4_2": {
                "waves": ["wave2", "wave4"],
                "function": lambda wave2, wave4: wave4.length > wave2.length / 3.0,
                "message": "Length of Wave4 is shorter than 1/3 of End of Wave1",
            },
            # WAVE 5
            "w5_1": {
                "waves": ["wave3", "wave5"],
                "function": lambda wave3, wave5: wave3.high < wave5.high,
                "message": "End of Wave5 is lower than End of Wave3",
            },
            "w5_2": {
                "waves": ["wave1", "wave5"],
                "function": lambda wave1, wave5: wave5.length < 2.0 * wave1.length,
                "message": "Wave5 is longer (value wise) than Wave1",
            },
        }

        return conditions


class Correction(WaveRule):
    """
    Rules for a corrective wave according to

    https://www.goldseiten-forum.com/attachment/113839-elliottwellentutorial-pdf/

    """

    def set_conditions(self):
        conditions = {  # WAVE B
            "w2_1": {
                "waves": ["wave1", "wave2"],
                "function": lambda waveA, waveB: waveA.high > waveB.high,
                "message": "End of WaveB is higher than Start of WaveA.",
            },
            "w2_2": {
                "waves": ["wave1", "wave3"],
                "function": lambda waveA, waveC: waveA.low > waveC.low,
                "message": "End of WaveB is higher than Start of WaveA.",
            },
            "w2_3": {
                "waves": ["wave1", "wave2"],
                "function": lambda waveA, waveB: waveA.length > waveB.length,
                "message": "WaveB longer than WaveA.",
            },
            "w2_4": {
                "waves": ["wave1", "wave2"],
                "function": lambda waveA, waveB: waveB.duration < 10.0 * waveA.duration,
                "message": "WaveB longer (time wise) than 10 x WaveA.",
            },
            "w2_5": {
                "waves": ["wave1", "wave3"],
                "function": lambda waveA, waveC: waveC.length > 0.6 * waveA.length,
                "message": "WaveC shorter (value wise) than 0.60 x WaveA.",
            },
            "w2_6": {
                "waves": ["wave1", "wave3"],
                "function": lambda waveA, waveC: waveC.length < 2.61 * waveA.length,
                "message": "WaveB longer (value wise) than 2.61 x WaveA.",
            },
            "w2_7": {
                "waves": ["wave1", "wave2"],
                "function": lambda waveA, waveB: waveB.length < 0.618 * waveA.length,
                "message": "WaveB longer (value wise) than 0.618 x WaveA.",
            },
            "w3_1": {
                "waves": ["wave1", "wave3"],
                "function": lambda waveA, waveC: waveC.duration < 10.0 * waveA.duration,
                "message": "WaveB longer (value wise) than 2.61 x WaveA.",
            },
            "w3_2": {
                "waves": ["wave1", "wave2"],
                "function": lambda waveA, waveB: waveB.length > 0.35 * waveA.length,
                "message": "WaveB shorter (value wise) than 0.35 x WaveA.",
            },
        }
        return conditions


class TDWave(WaveRule):
    """
    Setup for a Tiedje Dream Wave: Wave 2 corrects ~ fib level 61.8

    https://www.amazon.de/Elliott-Wellen-leicht-verst%C3%A4ndlich-Andre-Tiedje/dp/3898795039/

    """

    def set_conditions(self):
        # condition returns TRUE -> no exit
        conditions = {  # WAVE 2
            "w2_1": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: wave2.length > wave1.length * 0.59,
                "message": "End of Wave2 corrected less  50% of Wave1.",
            },
            "w2_2": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: wave2.length < wave1.length * 0.64,
                "message": "End of Wave2 corrected more than 65% of Wave1.",
            },
            "w2_3": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: 9 * wave2.duration > wave1.duration,
                "message": "Wave2 is longer than 9x Wave1",
            },
        }

        return conditions


class LeadingDiagonal(WaveRule):
    """
    Sames as Impulse but with exceptions:

    - End of Wave 4 lower than End Wave 1
    - trend lines of wave 2-4 and 1-3 converge

    """

    def set_conditions(self):
        # condition returns TRUE -> no exit
        conditions = {
            # WAVE 2
            "w2_0": {
                "waves": ["wave1", "wave2", "wave3", "wave4"],
                "function": lambda wave1, wave2, wave3, wave4: self.slope(
                    wave2.idx_end, wave4.idx_end, wave2.low, wave4.low
                )
                > self.slope(wave1.idx_end, wave3.idx_end, wave1.high, wave3.high)
                and self.slope(wave1.idx_end, wave3.idx_end, wave1.high, wave3.high)
                > 0,
                "message": "Trend lines of Wave1-3 and Wave2-4 not forming Leading Diagonal.",
            },
            "w2_1": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: wave2.low > wave1.low,
                "message": "End of Wave2 is lower than Start of Wave1.",
            },
            "w2_2": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: wave2.length >= 0.2 * wave1.length,
                "message": "Wave2 is shorten than 20% of Wave1.",
            },
            "w2_3": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: 9 * wave2.duration > wave1.duration,
                "message": "Wave2 is longer than 9x Wave1",
            },
            # WAVE 3
            "w3_1": {
                "waves": ["wave1", "wave3", "wave5"],
                "function": lambda wave1, wave3, wave5: not (
                    wave3.length < wave5.length and wave3.length < wave1.length
                ),
                "message": "Wave3 is the shortest Wave.",
            },
            "w3_2": {
                "waves": ["wave1", "wave3"],
                "function": lambda wave1, wave3: wave3.high > wave1.high,
                "message": "End of Wave3 is lower than End of Wave1",
            },
            "w3_3": {
                "waves": ["wave1", "wave3"],
                "function": lambda wave1, wave3: wave3.length >= wave1.length / 3.0,
                "message": "Wave3 is shorter than 1/3 of Wave1",
            },
            "w3_4": {
                "waves": ["wave2", "wave3"],
                "function": lambda wave2, wave3: wave3.length > wave2.length,
                "message": "Wave3 shorter than Wave2",
            },
            "w3_5": {
                "waves": ["wave1", "wave3"],
                "function": lambda wave1, wave3: 7 * wave3.duration > wave1.duration,
                "message": "Wave3 more than 7 times longer than Wave1.",
            },
            # WAVE 4
            "w4_1": {
                "waves": ["wave1", "wave4"],
                "function": lambda wave1, wave4: wave4.low < wave1.high,
                "message": "End of Wave4 is not lower than End of Wave1",
            },
            "w4_2": {
                "waves": ["wave2", "wave4"],
                "function": lambda wave2, wave4: wave4.length > wave2.length / 3.0,
                "message": "Length of Wave4 is shorter than 1/3 of End of Wave1",
            },
            # WAVE 5
            "w5_1": {
                "waves": ["wave3", "wave5"],
                "function": lambda wave3, wave5: wave3.high < wave5.high,
                "message": "End of Wave5 is lower than End of Wave3",
            },
            "w5_2": {
                "waves": ["wave1", "wave5"],
                "function": lambda wave1, wave5: wave5.length < 2.0 * wave1.length,
                "message": "Wave5 is longer (value wise) than 2.0 x Wave1",
            },
            "w5_3": {
                "waves": ["wave1", "wave5"],
                "function": lambda wave1, wave5: wave5.length > 0.70 * wave1.length,
                "message": "Wave5 is shorter (value wise) than 0.70 x Wave1",
            },
            "w5_4": {
                "waves": ["wave3", "wave5"],
                "function": lambda wave3, wave5: wave5.length < wave3.length,
                "message": "Wave5 is not shorter (value wise) than Wave3",
            },
        }

        return conditions

    def slope(self, x1: int, x2: int, y1: float, y2: float):
        """

        returns the slope between two data points

                ^
             y2 |                    P2
                |                  /
                |                /
                |              /
                |            /
             y1 |          P1
                |
                ---------------------------------------------------->
                           x1        x2

        :param x1:
        :param x2:
        :param y1:
        :param y2:
        :return:
        """
        delta_x = x2 - x1
        delta_y = y2 - y1

        if delta_x == 0:
            return 0
        else:
            return delta_y / delta_x


class Impulse3WaveLongest(WaveRule):
    """
    wave3 가 가장 긴 충격파
    """

    def is_wave1_diagonal_longer_than_wave2(self, wave1, wave2, fib_ratio=None):
        wave1_len, wave2_len = WaveTools.calculate_diagonals_length(
            wave1, wave2, self.x_y_ratio
        )
        if fib_ratio:
            return wave1_len > wave2_len * fib_ratio
        else:
            return wave1_len > wave2_len

    def set_conditions(self):
        # condition returns TRUE -> no exit
        conditions = {
            # WAVE 2
            "w2_1": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: wave2.low
                < WaveTools.calculate_fibonacci_level(
                    wave1.low, wave1.high, 0.3, "high_to_low"
                ),
                "message": "wave2 의 되돌림이 0.3 fibonacci level 보다 높아야 합니다.",
            },
            "w2_2": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: wave2.low > wave1.low,
                "message": "wave2 의 저점이 wave1 의 저점보다 높아야 합니다.",
            },
            # WAVE 3
            "w3_1": {
                "waves": ["wave1", "wave3"],
                "function": lambda wave1, wave3: wave3.high > wave1.high,
                "message": "wave3 는 wave1 고점보다 위에 있어야 합니다.",
            },
            "w3_2": {
                "waves": ["wave1", "wave3"],
                "function": lambda wave1, wave3: self.is_wave1_diagonal_longer_than_wave2(
                    wave3, wave1, 1.62
                ),
                "message": "wave3 는 wave1 의 대각길이의 1.62 이상이어야 합니다.",
            },
            # WAVE 4
            # "w4_1": {
            #     "waves": ["wave1", "wave2", "wave3", "wave4"],
            #     "function": lambda wave1, wave2, wave3, wave4: (
            #         self.is_wave1_diagonal_longer_than_wave2(wave1, wave2)
            #         and self.is_wave1_diagonal_longer_than_wave2(wave1, wave4)
            #         and not self.is_wave1_diagonal_longer_than_wave2(wave2, wave3)
            #         and self.is_wave1_diagonal_longer_than_wave2(wave3, wave4)
            #     ),
            #     "message": "wave4 는 wave1, wave3 보다 짧고, wave2는 wave1, wave3 보다 짧아야 합니다.",
            # },
            "w4_2": {
                "waves": ["wave1", "wave3", "wave4"],
                "function": lambda wave1, wave3, wave4: (
                    wave4.low
                    < WaveTools.calculate_fibonacci_level(
                        wave3.low, wave3.high, 0.24, "high_to_low"
                    )
                )
                and (wave4.low > wave1.high),
                "message": "wave3 의 피보나치 0.24 이상 그리고 wave1 고점보다 높아야 합니다.",
            },
            # WAVE 5
            "w5_1": {
                "waves": ["wave3", "wave5"],
                "function": lambda wave3, wave5: wave3.high < wave5.high,
                "message": "wave5 는 wave3 고점보다 위에 있어야 합니다.",
            },
            "w5_2": {
                "waves": ["wave1", "wave3", "wave5"],
                "function": lambda wave1, wave3, wave5: (
                    WaveTools.wave1_longer_than_wave2(wave3, wave1)
                )
                and (WaveTools.wave1_longer_than_wave2(wave3, wave5)),
                "message": "wave3은 wave1, wave5 보다 길어야 합니다.",
            },
            "w5_3": {
                "waves": ["wave3", "wave5"],
                "function": lambda wave3, wave5: (
                    wave3.diagonal_length * 0.24
                    < wave5.diagonal_length
                    < wave3.diagonal_length
                ),
                "message": "wave5 는 wave3 대각길이의 0.24 ~ 1.0 사이에 있어야 합니다.",
            },
        }

        return conditions


class Impulse1WaveLongest(WaveRule):
    """
    wave1 이 가장 긴 충격파
    """

    def is_wave1_diagonal_longer_than_wave2(self, wave1, wave2, fib_ratio=None):
        wave1_len, wave2_len = WaveTools.calculate_diagonals_length(
            wave1, wave2, self.x_y_ratio
        )
        if fib_ratio:
            return wave1_len > wave2_len * fib_ratio
        else:
            return wave1_len > wave2_len

    def is_wave1_diagonal_shorter_than_wave2(self, wave1, wave2, fib_ratio=None):
        wave1_len, wave2_len = WaveTools.calculate_diagonals_length(
            wave1, wave2, self.x_y_ratio
        )
        if fib_ratio:
            return wave1_len < wave2_len * fib_ratio
        else:
            return wave1_len < wave2_len

    def set_conditions(self):
        # condition returns TRUE -> no exit
        conditions = {
            # WAVE 2
            # OK
            "w2_1": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: wave2.low
                < WaveTools.calculate_fibonacci_level(
                    wave1.low, wave1.high, 0.2, "high_to_low"
                ),
                "message": "wave2 의 되돌림이 0.2 fibonacci level 보다 높아야 합니다.",
            },
            # OK
            "w2_2": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: wave2.low > wave1.low,
                "message": "wave2 의 저점이 wave1 저점보다 높아야 합니다.",
            },
            # WAVE 3
            # OK
            "w3_1": {
                "waves": ["wave1", "wave3"],
                "function": lambda wave1, wave3: wave3.high > wave1.high,
                "message": "wave3 는 wave1 고점보다 위에 있어야 합니다.",
            },
            # OK
            "w3_2": {
                "waves": ["wave1", "wave3"],
                "function": lambda wave1, wave3: self.is_wave1_diagonal_longer_than_wave2(
                    wave3, wave1, 0.3
                )
                and self.is_wave1_diagonal_shorter_than_wave2(wave3, wave1, 0.9),
                "message": "wave3 는 wave1 대각길이의 0.3 ~ 0.9배 사이에 있어야 합니다.",
            },
            # WAVE 4
            # OK
            "w4_1": {
                "waves": ["wave1", "wave3", "wave4"],
                "function": lambda wave1, wave3, wave4: (
                    wave4.low
                    < WaveTools.calculate_fibonacci_level(
                        wave3.low, wave3.high, 0.2, "high_to_low"
                    )
                )
                and (wave4.low > wave1.high),
                "message": "wave3 의 피보나치 0.2 이상 그리고 wave1 고점보다 높아야 합니다.",
            },
            # OK
            "w4_2": {
                "waves": ["wave2", "wave4"],
                "function": lambda wave2, wave4: self.is_wave1_diagonal_shorter_than_wave2(
                    wave4, wave2
                ),
                "message": "wave4 는 wave2 대각길이보다 짧아야 합니다.",
            },
            # WAVE 5
            # OK
            "w5_1": {
                "waves": ["wave3", "wave5"],
                "function": lambda wave3, wave5: wave3.high < wave5.high,
                "message": "wave5 는 wave3 고점보다 위에 있어야 합니다.",
            },
            # OK
            "w5_2": {
                "waves": ["wave1", "wave3", "wave5"],
                "function": lambda wave1, wave3, wave5: (
                    WaveTools.wave1_longer_than_wave2(wave1, wave3)
                )
                and (WaveTools.wave1_longer_than_wave2(wave1, wave5)),
                "message": "wave1은 wave3, wave5 보다 길어야 합니다.",
            },
            # OK
            "w5_3": {
                "waves": ["wave3", "wave5"],
                "function": lambda wave3, wave5: self.is_wave1_diagonal_longer_than_wave2(
                    wave5, wave3, 0.1  # wave5가 wave3 대각길이의 0.1배 이상
                )
                and self.is_wave1_diagonal_shorter_than_wave2(
                    wave5, wave3, 0.9
                ),  # wave5가 wave3 대각길이의 0.9배 이하
                "message": "wave5 는 wave3 대각길이의 0.1 ~ 0.9배 사이에 있어야 합니다.",
            },
        }

        return conditions


class Impulse5WaveLongest(WaveRule):
    """
    wave1 이 가장 긴 충격파
    """

    def is_wave1_diagonal_longer_than_wave2(self, wave1, wave2, fib_ratio=None):
        print("is_wave1_diagonal_longer_than_wave2", self.x_y_ratio)
        wave1_len, wave2_len = WaveTools.calculate_diagonals_length(
            wave1, wave2, self.x_y_ratio
        )
        if fib_ratio:
            return wave1_len > wave2_len * fib_ratio
        else:
            return wave1_len > wave2_len

    def is_wave1_diagonal_shorter_than_wave2(self, wave1, wave2, fib_ratio=None):
        wave1_len, wave2_len = WaveTools.calculate_diagonals_length(
            wave1, wave2, self.x_y_ratio
        )
        if fib_ratio:
            return wave1_len < wave2_len * fib_ratio
        else:
            return wave1_len < wave2_len

    def set_conditions(self):
        # condition returns TRUE -> no exit
        conditions = {
            # WAVE 2
            # OK
            "w2_1": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: wave2.low
                < WaveTools.calculate_fibonacci_level(
                    wave1.low, wave1.high, 0.2, "high_to_low"
                ),
                "message": "wave2 의 되돌림이 0.2 fibonacci level 보다 높아야 합니다.",
            },
            # OK
            "w2_2": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: wave2.low > wave1.low,
                "message": "wave2 의 저점이 wave1 저점보다 높아야 합니다.",
            },
            # WAVE 3
            # OK
            "w3_1": {
                "waves": ["wave1", "wave3"],
                "function": lambda wave1, wave3: wave3.high > wave1.high,
                "message": "wave3 는 wave1 고점보다 위에 있어야 합니다.",
            },
            # OK
            "w3_2": {
                "waves": ["wave1", "wave3"],
                "function": lambda wave1, wave3: self.is_wave1_diagonal_longer_than_wave2(
                    wave3, wave1, 1.1
                ),
                "message": "wave3 는 wave1 대각길이의 1.1배 이상이어야 합니다.",
            },
            # WAVE 4
            # OK
            "w4_1": {
                "waves": ["wave1", "wave3", "wave4"],
                "function": lambda wave1, wave3, wave4: (
                    wave4.low
                    < WaveTools.calculate_fibonacci_level(
                        wave3.low, wave3.high, 0.24, "high_to_low"
                    )
                )
                and (wave4.low > wave1.high),
                "message": "wave3 의 피보나치 0.24 이상 그리고 wave1 고점보다 높아야 합니다.",
            },
            # "w4_2": {
            #     "waves": ["wave2", "wave4"],
            #     "function": lambda wave2, wave4: self.is_wave1_diagonal_shorter_than_wave2(
            #         wave4, wave2
            #     ),
            #     "message": "wave4 는 wave2 대각길이보다 짧아야 합니다.",
            # },
            # WAVE 5
            # OK
            "w5_1": {
                "waves": ["wave3", "wave5"],
                "function": lambda wave3, wave5: wave3.high < wave5.high,
                "message": "wave5 는 wave3 고점보다 위에 있어야 합니다.",
            },
            "w5_2": {
                "waves": ["wave3", "wave5"],
                "function": lambda wave3, wave5: self.is_wave1_diagonal_longer_than_wave2(
                    wave5, wave3, 1.2
                ),
                "message": "wave5은 wave3 보다 1.2배 이상 길어야 합니다.",
            },
            "w5_3": {
                "waves": ["wave1", "wave3", "wave5"],
                "function": lambda wave1, wave3, wave5: self.is_wave1_diagonal_longer_than_wave2(
                    wave5,
                    wave3,
                )
                and self.is_wave1_diagonal_longer_than_wave2(
                    wave5,
                    wave1,
                ),
                "message": "wave5 는 wave3, wave1 보다 길어야 합니다.",
            },
        }

        return conditions


class ExpandingDiagonal(WaveRule):
    """
    Expanding Diagonal
    """

    def is_wave1_diagonal_longer_than_wave2(self, wave1, wave2, fib_ratio=None):
        print("is_wave1_diagonal_longer_than_wave2", self.x_y_ratio)
        wave1_len, wave2_len = WaveTools.calculate_diagonals_length(
            wave1, wave2, self.x_y_ratio
        )
        if fib_ratio:
            return wave1_len > wave2_len * fib_ratio
        else:
            return wave1_len > wave2_len

    def is_wave1_diagonal_shorter_than_wave2(self, wave1, wave2, fib_ratio=None):
        wave1_len, wave2_len = WaveTools.calculate_diagonals_length(
            wave1, wave2, self.x_y_ratio
        )
        if fib_ratio:
            return wave1_len < wave2_len * fib_ratio
        else:
            return wave1_len < wave2_len

    def set_conditions(self):
        # condition returns TRUE -> no exit
        conditions = {
            # WAVE 2
            # OK
            "w2_1": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: wave2.low
                < WaveTools.calculate_fibonacci_level(
                    wave1.low, wave1.high, 0.2, "high_to_low"
                ),
                "message": "wave2 의 되돌림이 0.2 fibonacci level 보다 높아야 합니다.",
            },
            # OK
            "w2_2": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: wave2.low > wave1.low,
                "message": "wave2 의 저점이 wave1 저점보다 높아야 합니다.",
            },
            # WAVE 3
            # OK
            "w3_1": {
                "waves": ["wave1", "wave3"],
                "function": lambda wave1, wave3: wave3.high > wave1.high,
                "message": "wave3 는 wave1 고점보다 위에 있어야 합니다.",
            },
            # OK
            "w3_2": {
                "waves": ["wave1", "wave3"],
                "function": lambda wave1, wave3: self.is_wave1_diagonal_longer_than_wave2(
                    wave3, wave1, 1.2
                ),
                "message": "wave3 는 wave1 대각길이의 1.2배 이상이어야 합니다.",
            },
            # WAVE 4
            # OK
            "w4_1": {
                "waves": ["wave1", "wave4"],
                "function": lambda wave1, wave4: wave4.low < wave1.high,
                "message": "wave4의 저점이 wave1 고점보다 낮아야 합니다.(고점 이탈O)",
            },
            # OK
            "w4_2": {
                "waves": ["wave2", "wave4"],
                "function": lambda wave2, wave4: wave4.low > wave2.low,
                "message": "wave4의 저점이 wave2 저점보다 높아야 합니다.",
            },
            # OK
            # "w4_3": {
            #     "waves": ["wave2", "wave4"],
            #     "function": lambda wave2, wave4: self.is_wave1_diagonal_longer_than_wave2(
            #         wave4, wave2
            #     ),
            #     "message": "wave4은 wave2 보다 길어야 합니다.",
            # },
            # WAVE 5
            # OK
            "w5_1": {
                "waves": ["wave3", "wave5"],
                "function": lambda wave3, wave5: wave3.high < wave5.high,
                "message": "wave5 는 wave3 고점보다 위에 있어야 합니다.",
            },
            # OK
            "w5_2": {
                "waves": ["wave3", "wave5"],
                "function": lambda wave3, wave5: self.is_wave1_diagonal_longer_than_wave2(
                    wave5, wave3, 1.1
                ),
                "message": "wave5은 wave3 보다 1.1배 이상 길어야 합니다.",
            },
        }

        return conditions


class ContractingDiagonal(WaveRule):
    """
    Contracting Diagonal
    """

    def is_wave1_diagonal_longer_than_wave2(self, wave1, wave2, fib_ratio=None):
        print("is_wave1_diagonal_longer_than_wave2", self.x_y_ratio)
        wave1_len, wave2_len = WaveTools.calculate_diagonals_length(
            wave1, wave2, self.x_y_ratio
        )
        if fib_ratio:
            return wave1_len > wave2_len * fib_ratio
        else:
            return wave1_len > wave2_len

    def is_wave1_diagonal_shorter_than_wave2(self, wave1, wave2, fib_ratio=None):
        wave1_len, wave2_len = WaveTools.calculate_diagonals_length(
            wave1, wave2, self.x_y_ratio
        )
        if fib_ratio:
            return wave1_len < wave2_len * fib_ratio
        else:
            return wave1_len < wave2_len

    def set_conditions(self):
        # condition returns TRUE -> no exit
        conditions = {
            # WAVE 2
            # OK
            "w2_1": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: wave2.low
                < WaveTools.calculate_fibonacci_level(
                    wave1.low, wave1.high, 0.2, "high_to_low"
                ),
                "message": "wave2 의 되돌림이 0.2 fibonacci level 보다 높아야 합니다.",
            },
            # OK
            "w2_2": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: wave2.low > wave1.low,
                "message": "wave2 의 저점이 wave1 저점보다 높아야 합니다.",
            },
            # WAVE 3
            # OK
            "w3_1": {
                "waves": ["wave1", "wave3"],
                "function": lambda wave1, wave3: wave3.high > wave1.high,
                "message": "wave3 는 wave1 고점보다 위에 있어야 합니다.",
            },
            # OK
            "w3_2": {
                "waves": ["wave1", "wave3"],
                "function": lambda wave1, wave3: self.is_wave1_diagonal_shorter_than_wave2(
                    wave3,
                    wave1,
                ),
                "message": "wave3 는 wave1 대각길이 보다 짧아야 합니다.",
            },
            # WAVE 4
            # OK
            "w4_1": {
                "waves": ["wave1", "wave4"],
                "function": lambda wave1, wave4: wave4.low < wave1.high,
                "message": "wave4의 저점이 wave1 고점보다 낮아야 합니다.(고점 이탈O)",
            },
            # OK
            "w4_2": {
                "waves": ["wave2", "wave4"],
                "function": lambda wave2, wave4: wave4.low > wave2.low,
                "message": "wave4의 저점이 wave2 저점보다 높아야 합니다.",
            },
            # OK
            "w4_3": {
                "waves": ["wave2", "wave4"],
                "function": lambda wave2, wave4: self.is_wave1_diagonal_shorter_than_wave2(
                    wave4, wave2
                ),
                "message": "wave4은 wave2 보다 짧아야 합니다.",
            },
            # WAVE 5
            # OK
            "w5_1": {
                "waves": ["wave3", "wave5"],
                "function": lambda wave3, wave5: wave3.high < wave5.high,
                "message": "wave5 는 wave3 고점보다 위에 있어야 합니다.",
            },
            # OK
            "w5_2": {
                "waves": ["wave3", "wave5"],
                "function": lambda wave3, wave5: self.is_wave1_diagonal_shorter_than_wave2(
                    wave5, wave3, 0.9
                ),
                "message": "wave5은 wave3의 길이의 0.99배 이하이어야 합니다.",
            },
        }

        return conditions
