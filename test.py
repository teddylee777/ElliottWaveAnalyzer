from __future__ import annotations
import FinanceDataReader as fdr
from models.WavePattern import WavePattern
from models import WaveRules
from models.WaveAnalyzer import WaveAnalyzer
from models.WaveOptions import WaveOptionsGenerator5
from models.helpers import plot_pattern
import pandas as pd
import numpy as np

# import importlib

# importlib.reload(WaveRules)

# df = pd.read_csv(r"data/btc-usd_1d.csv")
# df


if __name__ == "__main__":
    df = fdr.DataReader("454910", "2023-10-20", "2024-01-18").reset_index()[
        ["Date", "Open", "High", "Low", "Close"]
    ]

    idx_start = np.argmin(np.array(list(df["Low"])))

    wa = WaveAnalyzer(df=df, verbose=False)
    wave_options_impulse = WaveOptionsGenerator5(
        up_to=5
    )  # generates WaveOptions up to [15, 15, 15, 15, 15]

    # impulse = Impulse("impulse")
    # leading_diagonal = LeadingDiagonal("leading diagonal")
    # correction = Correction("correction")
    # tdwave = TDWave("TD Wave")
    impulse_custom = WaveRules.ImpulseCustom("impulse_custom")
    # rules_to_check = [impulse, leading_diagonal, correction, tdwave]
    rules_to_check = [impulse_custom]

    print(f"Start at idx: {idx_start}")
    print(f"will run up to {wave_options_impulse.number / 1e6}M combinations.")

    # set up a set to store already found wave counts
    # it can be the case, that 2 WaveOptions lead to the same WavePattern.
    # This can be seen in a chart, where for example we try to skip more maxima as there are. In such a case
    # e.g. [1,2,3,4,5] and [1,2,3,4,10] will lead to the same WavePattern (has same sub-wave structure, same begin / end,
    # same high / low etc.
    # If we find the same WavePattern, we skip and do not plot it

    wavepatterns_up = set()

    wave_configs = [
        # [2, 0, 1, 0, 0],
        # [2, 0, 2, 0, 0],
        # [2, 0, 3, 0, 0],
        # [2, 0, 3, 1, 1],
        # [2, 0, 3, 1, 2],
        [2, 0, 1, 0, 2],
        # [2, 0, 3, 2, 1],
        # [2, 0, 3, 2, 2],
    ]

    for wave_config in wave_configs:
        waves_up = wa.find_impulsive_wave(idx_start=idx_start, wave_config=wave_config)

        if waves_up:
            wavepattern_up = WavePattern(waves_up, verbose=True)

            for rule in rules_to_check:
                if wavepattern_up.check_rule(rule):
                    if wavepattern_up in wavepatterns_up:
                        print("SKIPPING")
                        fig = plot_pattern(
                            df=df,
                            wave_pattern=wavepattern_up,
                            title=str(wave_config),
                        )
                        if fig:
                            fig.show()
                        continue
                    else:
                        wavepatterns_up.add(wavepattern_up)
                        print(f"{rule.name} found: {wave_config}")
                        fig = plot_pattern(
                            df=df,
                            wave_pattern=wavepattern_up,
                            title=str(wave_config),
                        )
                        if fig:
                            fig.show()
                else:
                    fig = plot_pattern(
                        df=df,
                        wave_pattern=wavepattern_up,
                        title=str(wave_config),
                    )
                    if fig:
                        fig.show()
