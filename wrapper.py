from models.WavePattern import WavePattern
from models import WaveRules, WaveTools
from models.WaveAnalyzer import WaveAnalyzer
from models.WaveOptions import WaveOptionsGenerator5, WaveOptionsGeneratorCustom5
from models.helpers import plot_pattern
import pandas as pd


def detect_zigzag(df: pd.DataFrame, threshold: float) -> list[tuple]:
    zigzag_points = []
    last_pivot = 0
    up_trend = True

    for i in range(1, len(df)):
        if up_trend:
            if df["Low"].iloc[i] <= df["Low"].iloc[last_pivot]:
                if zigzag_points:
                    zigzag_points.pop()
                zigzag_points.append((df.index[i], df["Low"].iloc[i]))
                last_pivot = i

            elif df["High"].iloc[i] / df["Low"].iloc[last_pivot] - 1 >= threshold:
                zigzag_points.append((df.index[i], df["High"].iloc[i]))
                up_trend = False
                last_pivot = i
        else:
            if df["High"].iloc[i] >= df["High"].iloc[last_pivot]:
                if zigzag_points:
                    zigzag_points.pop()
                zigzag_points.append((df.index[i], df["High"].iloc[i]))
                last_pivot = i

            elif df["High"].iloc[last_pivot] / df["Low"].iloc[i] - 1 >= threshold:
                zigzag_points.append((df.index[i], df["Low"].iloc[i]))
                up_trend = True
                last_pivot = i

    return zigzag_points


def find_impulsive(
    df: pd.DataFrame,
    threshold: float = 0.05,
    n_skip_from: int = 0,
    n_skip_to: int = 8,
    x_y_ratio: float = 1.7,
):
    """ """
    wa = WaveAnalyzer(df=df, threshold=float(threshold), verbose=False)
    wave_options_impulse = WaveOptionsGeneratorCustom5(up_to=int(n_skip_to))
    wave_options_impulse.up_from = int(n_skip_from)
    wave_options_impulse.populate()

    rules_to_check = [
        WaveRules.Impulse1WaveLongest(
            "1파가 가장긴 충격파", x_y_ratio=round(float(x_y_ratio), 1)
        ),
        WaveRules.Impulse3WaveLongest(
            "3파가 가장긴 충격파", x_y_ratio=round(float(x_y_ratio), 1)
        ),
        WaveRules.Impulse5WaveLongest(
            "5파가 가장긴 충격파", x_y_ratio=round(float(x_y_ratio), 1)
        ),
        WaveRules.ExpandingDiagonal(
            "Expanding Diagonal", x_y_ratio=round(float(x_y_ratio), 1)
        ),
        WaveRules.ContractingDiagonal(
            "Contracting Diagonal", x_y_ratio=round(float(x_y_ratio), 1)
        ),
        WaveRules.Correction("correction", x_y_ratio=round(float(x_y_ratio), 1)),
    ]

    correction_rules_to_check = [WaveRules.Correction("correction")]

    wavepatterns_up = set()

    for new_option_impulse in wave_options_impulse.options_sorted:
        waves_up = wa.find_impulsive_wave_zigzag(wave_config=new_option_impulse.values)
        if waves_up:
            wavepattern_up = WavePattern(waves_up, verbose=True)

            for rule in rules_to_check:
                if wavepattern_up.check_rule(rule):
                    if wavepattern_up in wavepatterns_up:
                        continue
                    else:
                        wavepatterns_up.add(wavepattern_up)
                        print(
                            f"{rule.name} 검출되었습니다: {new_option_impulse.values}"
                        )
                        wavepatterns_up.add(wavepattern_up)
                else:
                    msg = wavepattern_up.violation
                    print(f"{rule.name} 검출 실패: {msg}")

    wavepatterns_up = list(wavepatterns_up)
    wavepatterns_down = set()

    if len(wavepatterns_up) > 0:
        # Impulse Wave 파동 검출
        # A-B-C 파동 검출
        for wavepattern_up in wavepatterns_up:
            for new_option_impulse in wave_options_impulse.options_sorted:
                waves_down = wa.find_corrective_wave(
                    idx_start=wavepattern_up.idx_end,
                    wave_config=new_option_impulse.values,
                )
                if waves_down:
                    wavepattern_down = WavePattern(waves_down, verbose=True)
                    for rule in correction_rules_to_check:
                        if wavepattern_down.check_rule(rule):
                            if wavepattern_down in wavepatterns_down:
                                print("SKIPPING")
                                continue
                            else:
                                wavepatterns_down.add(wavepattern_down)
                                print(f"{rule.name} found: {new_option_impulse}")
                                fig = plot_pattern(
                                    df=df,
                                    wave_pattern=wavepattern_down,
                                    title=str(new_option_impulse),
                                )
                                if fig:
                                    tab2.plotly_chart(fig)
                        else:
                            fig = plot_pattern(
                                df=df,
                                wave_pattern=wavepattern_down,
                                title=str(new_option_impulse),
                            )
                            if fig:
                                tab2.plotly_chart(fig)
