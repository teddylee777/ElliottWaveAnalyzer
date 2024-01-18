from __future__ import annotations
from abc import ABC, abstractmethod
import math


class WaveRule(ABC):
    """
    base class for implementing wave rules
    """

    def __init__(self, name: str):
        self.name = name
        self.conditions = self.set_conditions()

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


class ImpulseCustom(WaveRule):
    """
    Rules for an impulsive wave according to

    https://www.goldseiten-forum.com/attachment/113839-elliottwellentutorial-pdf/

    """

    def calculate_fibonacci_level(self, low, high, fib_ratio, mode="low_to_high"):
        """
        Calculate the Fibonacci level based on a given ratio and mode.

        :param low: The low point of the wave.
        :param high: The high point of the wave.
        :param fib_ratio: The Fibonacci ratio to apply.
        :param mode: The mode of calculation ('low_to_high' or 'high_to_low').
        :return: The calculated Fibonacci level.
        """
        if mode == "low_to_high":
            return low + (high - low) * fib_ratio
        elif mode == "high_to_low":
            return high - (high - low) * fib_ratio
        else:
            raise ValueError("Invalid mode. Use 'low_to_high' or 'high_to_low'.")

    # 단위 기준 정규화 (Unit Basis Normalization) 방식으로 파동의 대각선 길이를 계산하는 전체 파이썬 코드
    def calculate_diagonal_length(
        self, time_step, start_price, end_price, avg_time_interval, avg_price_change
    ):
        """주어진 파동의 데이터를 평균 시간 간격과 평균 가격 변동에 따라 정규화한 후 대각선 길이를 계산합니다."""
        normalized_time = time_step / avg_time_interval
        normalized_price = (end_price - start_price) / avg_price_change
        return math.sqrt(normalized_time**2 + normalized_price**2)

    def calculate_diagonals_length(self, wave1, wave2):
        # 예제 데이터
        # wave1 = {"time_step": 9, "start_price": 42550, "end_price": 89100}
        # wave2 = {"time_step": 17, "start_price": 74700, "end_price": 124500}

        # 평균 시간 간격과 평균 가격 변동 계산
        avg_time_interval = (wave1.duration + wave2.duration) / 2
        avg_price_change = (
            (wave1.points[1] - wave1.points[0]) + (wave2.points[1] - wave2.points[0])
        ) / 2

        # 각 파동의 대각선 길이 계산
        diagonal_length_wave1 = self.calculate_diagonal_length(
            wave1.duration,
            wave1.points[0],
            wave1.points[1],
            avg_time_interval,
            avg_price_change,
        )
        diagonal_length_wave2 = self.calculate_diagonal_length(
            wave2.duration,
            wave2.points[0],
            wave2.points[1],
            avg_time_interval,
            avg_price_change,
        )
        print(wave1.label, diagonal_length_wave1)
        print(wave2.label, diagonal_length_wave2)
        return diagonal_length_wave1, diagonal_length_wave2

    def wave1_longer_than_wave2(self, wave1, wave2):
        length1, length2 = self.calculate_diagonals_length(wave1, wave2)
        print(length1, length2)
        return length1 > length2

    def set_conditions(self):
        # condition returns TRUE -> no exit
        conditions = {
            # WAVE 2
            # "w2_1": {
            #     "waves": ["wave1", "wave2"],
            #     "function": lambda wave1, wave2: (wave2.low > wave1.low)
            #     and (wave2.low < wave1.low * 1.382),
            #     "message": "wave2 는 wave1 저점보다 위에 있으며, wave1 저점의 1.382배 이하에 있어야 합니다.",
            # },
            "w2_1": {
                "waves": ["wave1", "wave2"],
                "function": lambda wave1, wave2: wave2.low
                < self.calculate_fibonacci_level(
                    wave1.low, wave1.high, 0.3, "high_to_low"
                ),
                "message": "wave2 의 되돌림이 0.3 fibonacci level 보다 높아야 합니다.",
            },
            # "w2_3": {
            #     "waves": ["wave1", "wave2"],
            #     "function": lambda wave1, wave2: 9 * wave2.duration > wave1.duration,
            #     "message": "Wave2 is longer than 9x Wave1",
            # },
            # # WAVE 3
            "w3_1": {
                "waves": ["wave1", "wave3"],
                "function": lambda wave1, wave3: wave3.high > wave1.high,
                "message": "wave3 는 wave1 고점보다 위에 있어야 합니다.",
            },
            "w3_2": {
                "waves": ["wave1", "wave3"],
                "function": lambda wave1, wave3: wave3.diagonal_length
                > wave1.diagonal_length * 1.62,
                "message": "wave3 는 wave1 의 대각길이의 1.62 이상이어야 합니다.",
            },
            # "w3_3": {
            #     "waves": ["wave1", "wave3"],
            #     "function": lambda wave1, wave3: wave3.length >= wave1.length / 3.0,
            #     "message": "Wave3 is shorter than 1/3 of Wave1",
            # },
            # "w3_4": {
            #     "waves": ["wave2", "wave3"],
            #     "function": lambda wave2, wave3: wave3.length > wave2.length,
            #     "message": "Wave3 shorter than Wave2",
            # },
            # "w3_5": {
            #     "waves": ["wave1", "wave3"],
            #     "function": lambda wave1, wave3: 7 * wave3.duration > wave1.duration,
            #     "message": "Wave3 more than 7 times longer than Wave1.",
            # },
            # WAVE 4
            "w4_1": {
                "waves": ["wave1", "wave2", "wave3", "wave4"],
                "function": lambda wave1, wave2, wave3, wave4: (
                    (wave4.diagonal_length < wave1.diagonal_length)
                    and (wave4.diagonal_length < wave3.diagonal_length)
                    and (wave2.diagonal_length < wave1.diagonal_length)
                    and (wave2.diagonal_length < wave3.diagonal_length)
                ),
                "message": "wave4 는 wave1, wave3 보다 짧고, wave2는 wave1, wave3 보다 짧아야 합니다.",
            },
            "w4_2": {
                "waves": ["wave1", "wave3", "wave4"],
                "function": lambda wave1, wave3, wave4: (
                    wave4.low
                    < self.calculate_fibonacci_level(
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
                "waves": ["wave1", "wave5"],
                "function": lambda wave1, wave5: wave5.diagonal_length
                > wave1.diagonal_length,
                "message": "wave5 는 wave1 보다 길어야 합니다.",
            },
            "w5_3": {
                "waves": ["wave1", "wave3", "wave5"],
                "function": lambda wave1, wave3, wave5: (
                    # wave3.diagonal_length > wave1.diagonal_length
                    self.wave1_longer_than_wave2(wave3, wave1)
                )
                # and (wave3.diagonal_length > wave5.diagonal_length),
                and (self.wave1_longer_than_wave2(wave3, wave5)),
                "message": "wave3은 wave1, wave5 보다 길어야 합니다.",
            },
            "w5_4": {
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
