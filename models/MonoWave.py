from __future__ import annotations
import numpy as np
from models.functions import hi, lo, next_hi, next_lo
import math
import pandas as pd


class MonoWave:
    def __init__(
        self,
        lows: np.array,
        highs: np.array,
        dates: np.array,
        idx_start: int,
        skip: int = 0,
    ):
        self.lows_arr = lows
        self.highs_arr = highs
        self.dates_arr = dates
        self.skip_n = skip
        self.idx_start = idx_start
        self.idx_end = int

        self.count = int  # the count of the monowave, e.g. 1, 2, A, B, etc
        self.degree = (
            1  # 1 = lowest timeframe level, 2 as soon as a e.g. 12345 is found etc.
        )

        self.date_start = str
        self.date_end = str

        self.low = float
        self.high = float
        self.low_idx = int
        self.high_idx = int

    @property
    def labels(self) -> str:
        return str(self.count)

    @property
    def length(self) -> float:
        return abs(self.high - self.low)

    @property
    def diagonal_length(self) -> float:
        # x 좌표 (idx_start, idx_end)의 최소값과 최대값
        x_min = min(self.idx_start, self.idx_end)
        x_max = max(self.idx_start, self.idx_end)

        # y 좌표 (high, low)를 퍼센트 등락폭으로 환산
        if self.low != 0:
            percent_change = ((self.high - self.low) / self.low) * 100
        else:
            percent_change = 0

        # y의 정규화 (퍼센트 등락폭을 0과 1 사이의 값으로 정규화)

        # 정규화된 y 값과 원래 x 값으로 대각선 길이 계산
        return math.sqrt((self.idx_end - self.idx_start) ** 2 + (percent_change) ** 2)

    @property
    def duration(self) -> int:
        return self.idx_end - self.idx_start

    @classmethod
    def from_wavepattern(cls, wave_pattern):
        lows = highs = dates = np.zeros(10)  # dummy arrays to init class

        if len(wave_pattern.waves.keys()) == 5:
            low = wave_pattern.waves.get("wave1").low
            low_idx = wave_pattern.waves.get("wave1").low_idx
            high = wave_pattern.waves.get("wave5").high
            high_idx = wave_pattern.waves.get("wave5").high_idx
            date_start = wave_pattern.waves.get("wave1").date_start
            date_end = wave_pattern.waves.get("wave5").date_end

            monowave_up = cls(lows, highs, dates, 0)

            (
                monowave_up.low,
                monowave_up.low_idx,
                monowave_up.high,
                monowave_up.high_idx,
            ) = (low, low_idx, high, high_idx)
            monowave_up.date_start, monowave_up.date_end = date_start, date_end

            monowave_up.degree = wave_pattern.waves.get("wave1").degree + 1
            return monowave_up

        elif len(wave_pattern.waves.keys()) == 3:
            low = wave_pattern.waves.get("wave3").low
            low_idx = wave_pattern.waves.get("wave3").low_idx
            high = wave_pattern.waves.get("wave1").high
            high_idx = wave_pattern.waves.get("wave1").high_idx
            date_start = wave_pattern.waves.get("wave1").date_start
            date_end = wave_pattern.waves.get("wave3").date_end

            monowave_down = cls(lows, highs, dates, 0)
            (
                monowave_down.low,
                monowave_down.low_idx,
                monowave_down.high,
                monowave_down.high_idx,
            ) = (low, low_idx, high, high_idx)
            monowave_down.date_start, monowave_down.date_end = date_start, date_end

            monowave_down.degree = wave_pattern.waves.get("wave1").degree + 1

            return monowave_down

        else:
            raise ValueError("WavePattern other than 3 or 5 waves implemented, yet.")

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, idx: int) -> "MonoWave":
        """
        Class method to initialize a MonoWave instance from a DataFrame row.

        :param df: DataFrame containing zigzag pattern data
        :param idx: Row index in the DataFrame to create the MonoWave from
        :return: An instance of MonoWave or its subclasses
        """
        if idx >= len(df) - 1:
            raise ValueError("Index out of range for DataFrame")

        # Assuming lows and highs are derived from the 'Low' and 'High' columns of the DataFrame
        lows = np.array([df.iloc[idx]["Low"]])
        highs = np.array([df.iloc[idx]["High"]])
        dates = np.array([pd.to_datetime(df.iloc[idx]["Date"])])

        # Create a dummy instance with minimal data just for demonstration
        instance = cls(lows, highs, dates, idx_start=idx)
        instance.date_start = dates[0]
        instance.date_end = dates[
            0
        ]  # Assuming single day for simplicity; adjust as needed
        instance.low = lows[0]
        instance.high = highs[0]
        instance.low_idx = idx
        instance.high_idx = idx
        # Adjust other properties as needed
        instance.degree = (
            1  # 1 = lowest timeframe level, 2 as soon as a e.g. 12345 is found etc.
        )

        return instance


class MonoWaveUp(MonoWave):
    """
    Describes a upwards movement, which can have [skip_n] smaller downtrends
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.high, self.high_idx = self.find_end()
        self.low = self.lows_arr[self.idx_start]
        self.low_idx = self.idx_start
        self.idx_end = self.high_idx
        self.date_start = self.dates_arr[self.idx_start]
        self.date_end = self.dates_arr[self.high_idx]

    @classmethod
    def from_dataframe(cls, df, idx):
        if idx >= len(df) - 1:
            raise IndexError("DataFrame index out of range.")

        row = df.iloc[idx]

        # Assuming the DataFrame structure matches your data expectation
        indexes = np.array(row["index"])
        lows = np.array([row["Low"]])
        highs = np.array([row["High"]])
        dates = np.array([pd.to_datetime(row["Date"])])

        instance = cls.__new__(cls)  # Instantiate without calling __init__

        # Directly set required attributes
        instance.lows_arr = lows
        instance.highs_arr = highs
        instance.dates_arr = dates
        instance.idx_start = idx
        instance.idx_end = idx  # Assuming the end index is the same for simplicity
        instance.date_start = dates[0]
        instance.date_end = dates[0]  # Adjust as necessary
        instance.low = lows[0]
        instance.high = highs[0]
        instance.low_idx = idx
        instance.high_idx = idx
        instance.skip_n = 0  # Set skip_n if necessary
        instance.degree = 1  # Set degree if necessary
        # Manually set any other necessary attributes
        return instance

    def find_end(self):
        """
        Finds the end of this MonoWave

        :param idx_start:
        :return:
        """
        high, high_idx = hi(self.lows_arr, self.highs_arr, self.idx_start)
        low_at_start = self.lows_arr[self.idx_start]

        if high is None:
            return None, None

        for _ in range(self.skip_n):
            act_high, act_high_idx = next_hi(
                self.lows_arr, self.highs_arr, high_idx, high
            )
            if act_high is None:
                return None, None

            if act_high > high:
                high = act_high
                high_idx = act_high_idx
                if np.min(self.lows_arr[self.idx_start : act_high_idx] < low_at_start):
                    return None, None

        return high, high_idx

    @property
    def dates(self) -> list:
        return [self.date_start, self.date_end]

    @property
    def points(self):
        return self.low, self.high


class MonoWaveDown(MonoWave):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.low, self.low_idx = self.find_end()
        self.high = self.highs_arr[self.idx_start]
        self.high_idx = self.idx_start

        self.date_start = self.dates_arr[self.idx_start]
        if self.low is not None:
            self.date_end = self.dates_arr[self.low_idx]
            self.idx_end = self.low_idx
        else:
            self.date_end = None
            self.idx_end = None

    @classmethod
    def from_dataframe(cls, df, idx):
        if idx >= len(df) - 1:
            raise IndexError("DataFrame index out of range.")

        row = df.iloc[idx]
        next_row = df.iloc[idx + 1] if idx + 1 < len(df) else df.iloc[idx]

        # For downward waves, we assume the high is at the start and low at the end
        # Adjust this logic based on your specific DataFrame structure
        lows = np.array([row["Low"], next_row["Low"]])
        highs = np.array([row["High"], next_row["High"]])
        dates = np.array(
            [pd.to_datetime(row["Date"]), pd.to_datetime(next_row["Date"])]
        )

        instance = cls.__new__(cls)  # Instantiate without calling __init__

        # Directly set required attributes
        instance.lows_arr = lows
        instance.highs_arr = highs
        instance.dates_arr = dates
        instance.idx_start = idx
        instance.idx_end = idx + 1  # Adjust if your logic differs
        instance.date_start = dates[0]
        instance.date_end = dates[-1]  # Ensure this captures the end date correctly
        instance.low = min(lows)
        instance.high = max(highs)
        instance.low_idx = lows.argmin()
        instance.high_idx = highs.argmax()
        instance.skip_n = 0  # Set skip_n if necessary
        instance.degree = 1  # Set degree if necessary
        # Manually set any other necessary attributes
        return instance

    @property
    def dates(self) -> list:
        return [self.date_start, self.date_end]

    @property
    def points(self):
        return self.high, self.low

    def find_end(self):
        """
        Finds the end of this MonoWave (downwards)

        :return:
        """

        low, low_idx = lo(self.lows_arr, self.highs_arr, self.idx_start)
        high_at_start = self.highs_arr[self.idx_start]
        if low is None:
            return None, None

        for _ in range(self.skip_n):
            act_low, act_low_idx = next_lo(self.lows_arr, self.highs_arr, low_idx, low)
            if act_low is None:
                return None, None

            if act_low < low:
                low = act_low
                low_idx = act_low_idx
                if np.max(self.highs_arr[self.idx_start : act_low_idx]) > high_at_start:
                    return None, None

            # TODO what to do if no more minima can be found?
            # if act_low > low:
            #    return None, None
        # if low > np.min(self.lows_arr[low_idx:]):
        #    return None, None
        # else:
        return low, low_idx
