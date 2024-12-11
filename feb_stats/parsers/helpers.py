def remove_percentage(x: str) -> str:
    return x.split()[0]


def add_hours(x: str) -> str:
    return "00:" + str(x)  # Add hours to min:seconds
