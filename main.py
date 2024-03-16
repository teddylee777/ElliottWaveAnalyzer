import streamlit as st
import FinanceDataReader as fdr
from models.WavePattern import WavePattern
from models import WaveRules, WaveTools
from models.WaveAnalyzer import WaveAnalyzer
from models.WaveOptions import WaveOptionsGenerator5, WaveOptionsGeneratorCustom5
from models.helpers import plot_pattern
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt


st.title("Elliot Wave Analyzer")


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


def plot_graph(df, threshold=0.05):
    points_to_highlight = detect_zigzag(df, threshold)

    # Extracting index and price for highlighting
    indexes = [point[0] for point in points_to_highlight]
    prices = [point[1] for point in points_to_highlight]

    # Plotting the line chart for 'Close' vs. 'Date'
    fig, axes = plt.subplots()
    fig.set_size_inches(10, 6)
    axes.plot(df["Date"], df["Close"], label="Close Price")

    # Highlighting specified points with scatter plot
    plt.scatter(df.iloc[indexes]["Date"], prices, color="red")

    # Enhancing the plot
    axes.set_xlabel("Date")
    axes.set_ylabel("Close Price")
    axes.set_title("Stock Price with Highlighted Points")
    plt.legend()
    plt.grid(True)
    # plt.xticks(rotation=45)
    plt.tight_layout()
    return fig
    # Show the plot
    # plt.show()


plot_figure = st.empty()


with st.sidebar:
    start_date = st.date_input("시작일", datetime.date(2019, 1, 1))
    end_date = st.date_input("종료일", datetime.date(2022, 4, 30))
    stock_code = st.text_input("종목코드", "000660")
    threshold = st.number_input(
        "Threshold", min_value=0.01, max_value=0.5, value=0.05, step=0.01
    )

    print(start_date, end_date, stock_code)

    st.markdown(
        """
        - KOSPI: `KS11`
        - KOSDAQ: `KQ11`
        - 다우존스: `DJI`
        - 나스닥: `IXIC`
        - 미국종목(티커): `AAPL`
        - 비트코인: `BTC/KRW`
        - 달러: `USD/KRW`
        - 미국5년만기 국채수익률: `US5YT`

                """
    )
    selected_algos = [
        "1파가 가장긴 충격파",
        "3파가 가장긴 충격파",
        "5파가 가장긴 충격파",
        "Expanding Diagonal",
        "Contracting Diagonal",
    ]

    selected = st.selectbox("알고리즘", selected_algos)

    n_skip_from = st.number_input(
        label="SKIP From", min_value=0, max_value=30, value=0, step=1
    )
    n_skip_to = st.number_input(
        label="SKIP To", min_value=0, max_value=30, value=8, step=1
    )
    x_y_ratio = st.number_input(
        label="X/Y 비율", min_value=1.2, max_value=2.5, value=1.7, step=0.1
    )
    apply_btn = st.button("조회")

    # log = st.empty()
    st.markdown("## Debugging")
    show_all = st.checkbox("웨이브 패턴 전체보기", value=False)


tab1, tab2 = st.tabs(["검출 패턴", "자격 미달"])

if apply_btn:
    log_msg = []
    df = fdr.DataReader(stock_code, start_date, end_date).reset_index()[
        ["Date", "Open", "High", "Low", "Close"]
    ]
    idx_start = np.argmin(np.array(list(df["Low"])))

    fig = plot_graph(df, float(threshold))
    plot_figure.pyplot(fig)

    wa = WaveAnalyzer(df=df, threshold=float(threshold), verbose=False)
    wave_options_impulse = WaveOptionsGeneratorCustom5(up_to=int(n_skip_to))
    # wave_options_impulse.up_to = int(n_skip_to)
    wave_options_impulse.up_from = int(n_skip_from)
    wave_options_impulse.populate()

    print(f"Start at idx: {idx_start}")
    st.write(f"계산할 조합의 수: {wave_options_impulse.number} 번")

    if selected == "1파가 가장긴 충격파":
        rules_to_check = [
            WaveRules.Impulse1WaveLongest(
                selected, x_y_ratio=round(float(x_y_ratio), 1)
            )
        ]
    elif selected == "3파가 가장긴 충격파":
        rules_to_check = [
            WaveRules.Impulse3WaveLongest(
                selected, x_y_ratio=round(float(x_y_ratio), 1)
            )
        ]
    elif selected == "5파가 가장긴 충격파":
        rules_to_check = [
            WaveRules.Impulse5WaveLongest(
                selected, x_y_ratio=round(float(x_y_ratio), 1)
            )
        ]
    elif selected == "Expanding Diagonal":
        rules_to_check = [
            WaveRules.ExpandingDiagonal(selected, x_y_ratio=round(float(x_y_ratio), 1))
        ]
    elif selected == "Contracting Diagonal":
        rules_to_check = [
            WaveRules.ContractingDiagonal(
                selected, x_y_ratio=round(float(x_y_ratio), 1)
            )
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
                        tab1.markdown(f"#### `[{rule.name}]` 검출되었습니다.")
                        wavepatterns_up.add(wavepattern_up)
                        print(f"{rule.name} found: {new_option_impulse.values}")
                        fig = plot_pattern(
                            df=df,
                            wave_pattern=wavepattern_up,
                            title=str(new_option_impulse),
                        )
                        if fig:
                            tab1.plotly_chart(fig)
                        wavepatterns_up.add(wavepattern_up)
                else:
                    msg = wavepattern_up.violation
                    log_msg.append(msg)
                    if show_all:
                        tab2.markdown(f"#### 설명```{msg}```")
                        fig = plot_pattern(
                            df=df,
                            wave_pattern=wavepattern_up,
                            title=str(new_option_impulse),
                        )
                        if fig:
                            tab2.plotly_chart(fig)
                        tab2.markdown("----")

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
