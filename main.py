import streamlit as st
import FinanceDataReader as fdr
from models.WavePattern import WavePattern
from models import WaveRules
from models.WaveAnalyzer import WaveAnalyzer
from models.WaveOptions import WaveOptionsGenerator5, WaveOptionsGeneratorCustom5
from models.helpers import plot_pattern
import pandas as pd
import numpy as np
import datetime


st.title("Elliot Wave Analyzer")


with st.sidebar:
    start_date = st.date_input("시작일", datetime.date(2023, 10, 25))
    end_date = st.date_input("종료일", datetime.date(2023, 12, 23))
    stock_code = st.text_input("종목코드", "454910")

    print(start_date, end_date, stock_code)

    apply_btn = st.button("조회")

    # log = st.empty()
    st.markdown("## Debugging")
    show_all = st.checkbox("웨이브 패턴 전체보기", value=True)

tab1, tab2 = st.tabs(["검출 패턴", "자격 미달"])
if apply_btn:
    log_msg = []
    df = fdr.DataReader(stock_code, start_date, end_date).reset_index()[
        ["Date", "Open", "High", "Low", "Close"]
    ]
    idx_start = np.argmin(np.array(list(df["Low"])))

    wa = WaveAnalyzer(df=df, verbose=False)
    wave_options_impulse = WaveOptionsGeneratorCustom5(up_to=5)

    impulse_custom = WaveRules.ImpulseCustom("impulse_custom")
    rules_to_check = [impulse_custom]

    print(f"Start at idx: {idx_start}")
    print(f"will run up to {wave_options_impulse.number / 1e6}M combinations.")

    wavepatterns_up = set()

    for new_option_impulse in wave_options_impulse.options_sorted:
        waves_up = wa.find_impulsive_wave(
            idx_start=idx_start, wave_config=new_option_impulse.values
        )
        # print(new_option_impulse)
        if waves_up:
            wavepattern_up = WavePattern(waves_up, verbose=True)

            for rule in rules_to_check:
                if wavepattern_up.check_rule(rule):
                    if wavepattern_up in wavepatterns_up:
                        # print("SKIPPING")
                        continue
                    else:
                        wavepatterns_up.add(wavepattern_up)
                        print(f"{rule.name} found: {new_option_impulse.values}")
                        fig = plot_pattern(
                            df=df,
                            wave_pattern=wavepattern_up,
                            title=str(new_option_impulse),
                        )
                        if fig:
                            tab1.plotly_chart(fig)
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

    # log_msg = "\n".join(log_msg)
    # log.markdown(f"```{log_msg}```")
