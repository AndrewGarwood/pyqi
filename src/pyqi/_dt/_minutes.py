"""
*`@file`* `_dt/_minutes.py`
"""

class From():
    
    @staticmethod
    def seconds(n: float | int) -> float:
        return n / 60
    
    @staticmethod
    def milliseconds(n: float | int) -> float:
        return n / (60 * 1000)
    
    @staticmethod
    def minsecstr(s: str, /) -> float:
        """
        *`@returns`* `minutes (float)`
        - expects `s` to be of format `%M:%S` or `%M`
        - mantissa of float is percentage of 60 seconds.
        """
        parts: list[str] = s.split(":")
        minutes: float = float(parts[0])
        seconds: float = float(parts[1]) if len(parts) > 1 else 0.0
        return minutes + (seconds / 60.0)

    @staticmethod
    def timestr(s: str, /) -> float:
        """
        *`@returns`* `minutes (float)`
        - expects `s` to be of format `%H:%M:%S` or `%H:%M:%S.%f`
        - converts total duration into minutes (e.g. 1 hour = 60.0 minutes)
        - mantissa of float contains fractional minutes including milliseconds
        """
        parts: list[str] = s.split(":")
        hours: float = float(parts[0])
        minutes: float = float(parts[1]) if len(parts) > 1 else 0.0
        seconds: float = float(parts[2]) if len(parts) > 2 else 0.0
        # Hours to minutes, plus base minutes, plus seconds/milliseconds converted to minutes
        return (hours * 60.0) + minutes + (seconds / 60.0)


class To():
    @staticmethod
    def seconds(n: float | int) -> float:
        return n * 60
    
    @staticmethod
    def milliseconds(n: float | int) -> float:
        return n * (60 * 1000)
    
    @staticmethod
    def minsecstr(n: float | int, /) -> str:
        """
        *`@returns`* `str (like fmt %M:%S)`
        - assumes mantissa of float is percentage of 60 seconds.
        """
        # Separate whole minutes from fractional minutes using floor division
        minutes = int(n // 1)
        
        # Multiply the remaining decimal fraction by 60 to convert back to seconds
        # round() prevents IEEE 754 floating-point precision issues (e.g., 0.299999999999997)
        seconds: int = round((n - minutes) * 60)

        # Handle overflow if seconds rounded up to 60
        if seconds == 60:
            minutes += 1
            seconds = 0
        # Format with zero-padded 2-digit integers for standard time format compliance
        return f"{minutes:02d}:{seconds:02d}"
    
    @staticmethod
    def timestr(n: float | int, /) -> str:
        """
        *`@returns`* `str (like fmt %H:%M:%S or %H:%M:%S.%f)`
        - expects total minutes `n`
        - includes 3 decimal precision for milliseconds if fractional seconds exist
        """
        total_seconds: float = round(float(n) * 60.0, 3)
        
        # Extract hours, minutes, and total floating-point seconds
        hours: int = int(total_seconds // 3600)
        remaining_seconds: float = total_seconds % 3600
        minutes: int = int(remaining_seconds // 60)
        seconds_float: float = round(remaining_seconds % 60, 3)

        # Check for whole seconds vs millisecond presence
        if seconds_float.is_integer():
            return f"{hours:02d}:{minutes:02d}:{int(seconds_float):02d}"
        
        # Split seconds and fractional milliseconds to preserve 2-digit zero-padding for whole seconds
        whole_seconds: int = int(seconds_float // 1)
        ms: int = round((seconds_float - whole_seconds) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}.{ms:03d}"