```python
def video_speed(speed=1.2):
    """
    Adjusts the video speed of the video player.

    Args:
        speed (float): Video speed multiplier. Allowed values: 1.2, 1.5, 1.75, 2.0.
    """
    allowed_speeds = {1.2: 1.2, 1.5: 1.5, 1.75: 1.75, 2.0: 2.0}
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs, video_speed=allowed_speeds[speed])
        return wrapper
    return decorator
```