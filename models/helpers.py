from models.WavePattern import WavePattern
import pandas as pd
import time
import plotly.graph_objects as go


def timeit(func):
    def wrapper(*arg, **kw):
        t1 = time.perf_counter_ns()
        res = func(*arg, **kw)
        t2 = time.perf_counter_ns()
        print("took:", t2 - t1, "ns")
        return res

    return wrapper


def plot_cycle(df, wave_cycle, title: str = ""):
    data = go.Ohlc(
        x=df["Date"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"]
    )

    monowaves = go.Scatter(
        x=wave_cycle.dates,
        y=wave_cycle.values,
        text=wave_cycle.labels,
        mode="lines+markers+text",
        textposition="middle right",
        textfont=dict(size=15, color="#2c3035"),
        line=dict(color=("rgb(111, 126, 130)"), width=3),
    )
    layout = dict(title=title)
    fig = go.Figure(data=[data, monowaves], layout=layout)
    fig.update(layout_xaxis_rangeslider_visible=False)

    fig.show()


def convert_yf_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts a yahoo finance OHLC DataFrame to column name(s) used in this project

    old_names = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    new_names = ['Date', 'Open', 'High', 'Low', 'Close']

    :param df:
    :return:
    """
    df_output = pd.DataFrame()

    df_output["Date"] = list(df.index)
    df_output["Date"] = pd.to_datetime(df_output["Date"], format="%Y-%m-%d %H:%M:%S")

    df_output["Open"] = df["Open"].to_list()
    df_output["High"] = df["High"].to_list()
    df_output["Low"] = df["Low"].to_list()
    df_output["Close"] = df["Close"].to_list()

    return df_output


def plot_pattern(df: pd.DataFrame, wave_pattern: WavePattern, title: str = ""):
    data = go.Candlestick(
        x=df["Date"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"]
    )

    monowaves = go.Scatter(
        x=wave_pattern.dates,
        y=wave_pattern.values,
        text=wave_pattern.labels,
        mode="lines+markers+text",
        textposition="middle right",
        textfont=dict(size=15, color="#2c3035"),
        line=dict(color=("rgb(111, 126, 130)"), width=3),
    )
    layout = dict(title=title)
    fig = go.Figure(data=[data, monowaves], layout=layout)
    fig.update(layout_xaxis_rangeslider_visible=False)

    start_date = df.loc[0, "Date"].date().strftime("%Y-%m-%d")
    end_date = df.loc[len(df) - 1, "Date"].date().strftime("%Y-%m-%d")

    all_dates = pd.date_range(start_date, end_date, freq="D")

    # df["Date"] 컬럼을 Python date 객체로 변환
    df_dates = df["Date"].dt.date.values

    # all_dates에서 df["Date"]에 없는 날짜 찾기
    missing_dates = [d.date() for d in all_dates if d.date() not in df_dates]

    fig.update_xaxes(rangebreaks=[dict(values=missing_dates)])

    return fig


def plot_monowave(df, monowave, title: str = ""):
    data = go.Ohlc(
        x=df["Date"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"]
    )

    monowaves = go.Scatter(
        x=monowave.dates,
        y=monowave.points,
        mode="lines+markers+text",
        textposition="middle right",
        textfont=dict(size=15, color="#2c3035"),
        line=dict(color=("rgb(111, 126, 130)"), width=3),
    )
    layout = dict(title=title)
    fig = go.Figure(data=[data, monowaves], layout=layout)
    fig.update(layout_xaxis_rangeslider_visible=False)

    fig.show()
