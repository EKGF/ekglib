import asyncio
import functools
from typing import AsyncGenerator, Callable, Any, Optional, List

import pandas as pd
from io import BytesIO

R = Any  # Type received by the generator
S = Any  # Type sent by the generator


def async_source(
    func: Callable[..., AsyncGenerator[S, None]],
) -> Callable[..., AsyncGenerator[S, None]]:
    """Async source decorator that outputs data of type S."""

    @functools.wraps(func)
    async def wrapper(
        *args: Any, next: Optional[List[AsyncGenerator[Any, S]]] = None
    ) -> AsyncGenerator[S, None]:
        name = func.__doc__.split('\n')[0] if func.__doc__ else func.__name__
        print(f'Starting {name}')
        if next:
            # Prime each next step
            await asyncio.gather(*(nxt.asend(None) for nxt in next))

        gen = func(*args)
        async for value in gen:
            if next:
                # Send value to next steps
                await asyncio.gather(*(nxt.asend(value) for nxt in next))
            yield value

        print(f'Finished {name}')
        if next:
            # Close next steps
            await asyncio.gather(*(nxt.aclose() for nxt in next))

    return wrapper


def async_step(
    func: Callable[..., AsyncGenerator[S, R]],
) -> Callable[..., AsyncGenerator[S, R]]:
    """Async step decorator that receives data of type R and outputs data of type S."""

    @functools.wraps(func)
    async def wrapper(
        *args: Any, next: Optional[List[AsyncGenerator[Any, S]]] = None
    ) -> AsyncGenerator[S, R]:
        name = func.__doc__.split('\n')[0] if func.__doc__ else func.__name__
        print(f'Starting {name}')
        if next:
            await asyncio.gather(*(nxt.asend(None) for nxt in next))

        gen = func(*args)
        await gen.asend(None)  # Prime the generator

        try:
            while True:
                value = yield
                if value is not None:
                    # Send the value to the generator
                    await gen.asend(value)
                    # Process all results from the generator
                    try:
                        while True:
                            result = await gen.__anext__()
                            if next:
                                await asyncio.gather(
                                    *(nxt.asend(result) for nxt in next)
                                )
                            yield result
                    except StopAsyncIteration:
                        pass
        finally:
            print(f'Finished {name}')
            if next:
                await asyncio.gather(*(nxt.aclose() for nxt in next))

    return wrapper


def async_sink(
    func: Callable[..., AsyncGenerator[None, R]],
) -> Callable[..., AsyncGenerator[None, R]]:
    """Async sink decorator that receives data of type R."""

    @functools.wraps(func)
    async def wrapper(
        *args: Any, next: Optional[List[AsyncGenerator[Any, None]]] = None
    ) -> AsyncGenerator[None, R]:
        name = func.__doc__.split('\n')[0] if func.__doc__ else func.__name__
        print(f'Starting {name}')
        gen = func(*args)
        await gen.asend(None)  # Prime the generator
        try:
            while True:
                value = yield
                if value is not None:
                    await gen.asend(value)
        finally:
            print(f'Finished {name}')
            await gen.aclose()

    return wrapper


# Example usage with docstrings:
@async_source
async def read_csv_from_bytes(csv_bytes: bytes) -> AsyncGenerator[pd.DataFrame, None]:
    """Read CSV from Bytes"""
    df = await asyncio.to_thread(pd.read_csv, BytesIO(csv_bytes))
    print(f'DataFrame read from CSV: \n{df.head()}')
    yield df


@async_step
async def process_each_row() -> AsyncGenerator[pd.Series, pd.DataFrame]:
    """Process Each Row"""
    while True:
        df: pd.DataFrame = yield  # type: ignore[misc]
        if df is not None:
            for _, row in df.iterrows():
                print(f'Processing row: {row}')
                yield row


@async_sink
async def process_row(
    row_processor: Callable[[pd.Series], None],
) -> AsyncGenerator[None, pd.Series]:
    """Process Row Sink"""
    try:
        while True:
            row: pd.Series = yield
            if row is not None:
                await asyncio.to_thread(row_processor, row)
    except GeneratorExit:
        print('Sink closed')


def example_row_processor(row: pd.Series) -> None:
    print(f'Processed row: {row}')


async def run_pipeline():
    csv_content = b"""name,age,city
Alice,30,London
Bob,25,New York
Charlie,35,San Francisco"""

    sink = process_row(example_row_processor)
    step = process_each_row(next=[sink])
    source = read_csv_from_bytes(csv_content, next=[step])

    async for _ in source:
        pass


def main():
    try:
        asyncio.run(run_pipeline())
    except KeyboardInterrupt:
        print('\nProcess interrupted by user')
    except Exception as e:
        print(f'An error occurred: {e}')
        import traceback

        traceback.print_exc()


if __name__ == '__main__':
    main()
