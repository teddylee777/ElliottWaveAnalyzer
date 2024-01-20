import math


def calculate_fibonacci_level(low, high, fib_ratio, mode="low_to_high"):
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
    time_step,
    start_price,
    end_price,
    avg_time_interval,
    avg_price_change,
    price_weight_over_time=0.8,
):
    """주어진 파동의 데이터를 평균 시간 간격과 평균 가격 변동에 따라 정규화한 후 대각선 길이를 계산합니다."""
    normalized_time = time_step / avg_time_interval
    normalized_price = (
        (end_price - start_price) / avg_price_change * price_weight_over_time
    )
    return math.sqrt(normalized_time**2 + normalized_price**2)


def calculate_diagonals_length2(wave1, wave2):
    # 평균 시간 간격과 평균 가격 변동 계산
    avg_time_interval = (wave1.duration + wave2.duration) / 2
    avg_price_change = (
        (wave1.points[1] - wave1.points[0]) + (wave2.points[1] - wave2.points[0])
    ) / 2

    # 각 파동의 대각선 길이 계산
    diagonal_length_wave1 = calculate_diagonal_length(
        wave1.duration,
        wave1.points[0],
        wave1.points[1],
        avg_time_interval,
        avg_price_change,
    )
    diagonal_length_wave2 = calculate_diagonal_length(
        wave2.duration,
        wave2.points[0],
        wave2.points[1],
        avg_time_interval,
        avg_price_change,
    )
    print(wave1.label, diagonal_length_wave1)
    print(wave2.label, diagonal_length_wave2)
    return diagonal_length_wave1, diagonal_length_wave2


def calculate_diagonals_length1(wave1, wave2):
    """
    2024. 01. 20 이전 대각선 길이 계산 방식
    """
    width1 = wave1.duration
    width2 = wave2.duration

    height1 = abs(wave1.points[1] - wave1.points[0])
    height2 = abs(wave2.points[1] - wave2.points[0])

    low_y = min(wave1.points[0], wave1.points[1], wave2.points[0], wave2.points[1])
    high_y = max(wave1.points[0], wave1.points[1], wave2.points[0], wave2.points[1])

    min_x = min(width1, width2)
    max_x = max(width1, width2)

    total_height = high_y - low_y

    x1 = width1 / min_x
    x2 = width2 / min_x
    y1 = height1 / total_height * 100
    y2 = height2 / total_height * 100

    y_to_x_ratio = min(y1, y2) / min_x

    y1 /= y_to_x_ratio
    y2 /= y_to_x_ratio

    len1 = math.sqrt(x1**2 + y1**2)
    len2 = math.sqrt(x2**2 + y2**2)
    print(f"{wave1.label}: {len1:.2f}, {wave2.label}: {len2:.2f}")
    if len1 > len2:
        print(f"[{wave1.label}] 가 [{wave2.label}] 보다 {len1 / len2:.2f}배 길다.")
    else:
        print(f"[{wave2.label}] 가 [{wave1.label}] 보다 {len2 / len1:.2f}배 길다.")
    return len1, len2


def calculate_diagonals_length(wave1, wave2, x_to_y_ratio=1.8):
    """
    2024. 01. 20 이후 대각선 길이 계산 방식
    """
    width1 = wave1.duration
    width2 = wave2.duration

    height1 = abs(wave1.points[1] - wave1.points[0])
    height2 = abs(wave2.points[1] - wave2.points[0])

    low_y = min(wave1.points[0], wave1.points[1], wave2.points[0], wave2.points[1])
    high_y = max(wave1.points[0], wave1.points[1], wave2.points[0], wave2.points[1])

    max_x = max(width1, width2)
    max_y = max(height1, height2)
    max_height = max(height1, height2)

    width1 /= max_x
    width2 /= max_x
    print(width1, width2)

    width1 *= x_to_y_ratio
    width2 *= x_to_y_ratio

    height1 /= max_height
    height2 /= max_height
    print(height1, height2)

    len1 = math.sqrt(width1**2 + height1**2)
    len2 = math.sqrt(width2**2 + height2**2)

    print(f"{wave1.label}: {len1:.2f}, {wave2.label}: {len2:.2f}")
    if len1 > len2:
        print(f"[{wave1.label}] 가 [{wave2.label}] 보다 {len1 / len2:.2f}배 길다.")
    else:
        print(f"[{wave2.label}] 가 [{wave1.label}] 보다 {len2 / len1:.2f}배 길다.")
    return len1, len2


def wave1_longer_than_wave2(wave1, wave2):
    length1, length2 = calculate_diagonals_length(wave1, wave2)
    # print(length1, length2)
    return length1 > length2
