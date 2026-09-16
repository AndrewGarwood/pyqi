"""
*`@file`* `_dt/_seconds.py`
"""

class From():
    @staticmethod
    def hours(n: float | int, /):
        return float(n) * pow(60, 2)

    @staticmethod
    def minutes(n: float | int, /):
        return float(n) * 60.0    

    @staticmethod
    def microseconds(n: float | int, /):
        return float(n) / pow(10, 6)

class To():
    @staticmethod
    def hours(n: float, /):
        return n / pow(60.0, 2)
    @staticmethod
    def minutes(n: float | int, /) -> float:
        return float(n) / 60.0

    @staticmethod
    def minsecstr(n: float | int, /) -> str:
        """
        *`@returns`* `str (like fmt %M:%S)`
        """
        n = int(n)
        minutes = n // 60
        seconds = n % 60        
        # Handle overflow if seconds rounded up to 60
        if seconds == 60:
            minutes += 1
            seconds = 0
        return f"{minutes:02d}:{seconds:02d}"
