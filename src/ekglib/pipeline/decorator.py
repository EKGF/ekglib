import functools
from typing import AsyncGenerator, Callable, TypeVar, Any

# Type variables for generics
R = TypeVar('R')  # Type received by the generator
S = TypeVar('S')  # Type sent by the generator


# Define the source decorator with generic typing
def async_source(name: str) -> Callable[..., Callable[..., AsyncGenerator[S, None]]]: # type: ignore
    """Generic async source decorator that outputs data of type S."""
    def decorator(func: Callable[..., AsyncGenerator[S, None]]) -> Callable[..., AsyncGenerator[S, None]]:
        @functools.wraps(func)
        async def wrapper(*args: Any) -> AsyncGenerator[S, None]:
            print(f"Starting {name}")
            async for value in func(*args):
                yield value
            print(f"Finished {name}")
        return wrapper
    return decorator

# Define a generic step decorator with priming
def async_step(name: str) -> Callable[..., Callable[..., AsyncGenerator[S, R]]]: # type: ignore
    """Generic async step decorator that receives data of type R and outputs data of type S."""
    def decorator(func: Callable[..., AsyncGenerator[S, R]]) -> Callable[..., AsyncGenerator[S, R]]:
        @functools.wraps(func)
        async def wrapper(*args: Any) -> AsyncGenerator[S, R]:
            gen = func(*args)  # Create the generator
            await gen.asend(None)  # Prime the generator
            print(f"Starting {name}")
            try:
                async for value in gen:
                    yield value
            finally:
                print(f"Finished {name}")
        return wrapper
    return decorator

# Define a generic sink decorator with priming
def async_sink(name: str) -> Callable[..., Callable[..., AsyncGenerator[None, R]]]: # type: ignore
    """Generic async sink decorator that receives data of type R."""
    def decorator(func: Callable[..., AsyncGenerator[None, R]]) -> Callable[..., AsyncGenerator[None, R]]:
        @functools.wraps(func)
        async def wrapper(*args: Any) -> AsyncGenerator[None, R]:
            gen = func(*args)  # Create the generator
            await gen.asend(None)  # Prime the generator
            print(f"Starting {name}")
            try:
                async for value in gen:
                    pass  # Consume all values from the generator (it's a sink)
            finally:
                print(f"Finished {name}")
                yield None
        return wrapper
    return decorator

