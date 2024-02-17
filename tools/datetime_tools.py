import datetime


def datetime_str(with_symbol: bool = True) -> str:
    result = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not with_symbol:
        for i in [':', '-', ' ']:
            result = result.replace(i, '')
    return result
