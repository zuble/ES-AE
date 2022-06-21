"""
This file declares the decorators which provides a simple API 
for subscribing to certain messages or perform periodic tasks through the same event loop.
"""

import asyncio
import sys
import inspect
import time
from typing import Dict, List, Tuple, Type, Union


class IMCDecoratorBase:
    """
    Base class for imcpy decorators
    """
    def add_event(self, loop, instance, fn):
        """
        Add event to the asyncio event loop
        """
        return asyncio.ensure_future(fn, loop=loop)

class Periodic(IMCDecoratorBase):
    """
    Calls the decorated function every N seconds
    """
    def __init__(self, dt: Union[int, float]):
        self.dt = dt

    def __call__(self, fn, *args, **kwargs):
        try:
            fn._decorators.append(self)
        except AttributeError:
            fn._decorators = [self]
        return fn

    def add_event(self, loop, instance, fn):
        """
        Wraps the given function in a corutine which calls it every N seconds
        :param loop: The event loop (cls._loop)
        :param instance: The instantiated class
        :param fn: The function to be called
        :return: None
        """
        # Verify function signature
        argspec = inspect.getfullargspec(fn)
        n_args = len(argspec.args) - 1 if 'self' in argspec.args else len(argspec.args)
        n_required_args = n_args - (len(argspec.defaults) if argspec.defaults else 0)
        assert n_required_args == 0, 'Functions decorated with @Periodic cannot have any required parameters.'

        async def periodic_fn():
            # If coroutine await else call normally
            is_coroutine = asyncio.iscoroutinefunction(fn)

            while True:
                last_exec = time.time()
                try:
                    (await fn()) if is_coroutine else fn()
                except Exception as e:
                    instance.on_exception(loc=fn.__qualname__, exc=e)

                await asyncio.sleep(max(0, self.dt + last_exec - time.time()))

        super().add_event(loop, instance, periodic_fn())


class Subscribe(IMCDecoratorBase):
    """
    Subscribes to the specified IMC Messages.
    Multiple types can be specified (e.g @Subscribe(imcpy.CpuUsage, imcpy.Heartbeat)
    """
    def __init__(self, *args, **kwargs):
        for arg in args:
            if arg.__module__ == '_imcpy':
                # Add to __imcsub__
                try:
                    self.subs.append(arg)
                except AttributeError:
                    self.subs = [arg]
            else:
                raise TypeError(f'Unknown message passed ({arg})')

    def __call__(self, fn, *args, **kwargs):
        try:
            fn._decorators.append(self)
        except AttributeError:
            fn._decorators = [self]

        # Verify function signature
        argspec = inspect.getfullargspec(fn)
        n_args = len(argspec.args) - 1 if 'self' in argspec.args else len(argspec.args)
        assert n_args >= 1, 'Functions decorated with @Subscribe must have a parameter for the message.'

        n_required_args = n_args - (len(argspec.defaults) if argspec.defaults else 0)
        assert n_required_args <= 1, 'Functions decorated with @Subscribe can only have one required parameter.'

        # Add typing information if not already defined
        first_arg = argspec.args[1] if 'self' in argspec.args else argspec.args[0]
        if first_arg not in argspec.annotations.keys():
            fn.__annotations__[first_arg] = self.subs[-1]

        return fn

    def add_event(self, loop, instance, fn):
        # Handled in IMCBase decorator to centralize the handling of messages
        pass


class RunOnce(IMCDecoratorBase):
    """
    Calls the decorated function once after start, at an optional time delay
    This can e.g. be used with coroutines to implement periodic functions with variable wait
    """
    def __init__(self, delay: float = 0.0):
        self.delay = delay

    def __call__(self, fn, *args, **kwargs):
        try:
            fn._decorators.append(self)
        except AttributeError:
            fn._decorators = [self]
        return fn

    def add_event(self, loop, instance, fn):
        """
        Wraps the given function in a corutine and calls it at a given time delay
        :param loop: The event loop (cls._loop)
        :param instance: The instantiated class
        :param fn: The function to be called
        :return: None
        """
        # Verify function signature
        argspec = inspect.getfullargspec(fn)
        n_args = len(argspec.args) - 1 if 'self' in argspec.args else len(argspec.args)
        n_required_args = n_args - (len(argspec.defaults) if argspec.defaults else 0)
        assert n_required_args == 0, 'Functions decorated with @Periodic cannot have any required parameters.'

        async def run_once_fn():
            # If coroutine await else call normally
            is_coroutine = asyncio.iscoroutinefunction(fn)
            await asyncio.sleep(self.delay)
            try:
                (await fn()) if is_coroutine else fn()
            except Exception as e:
                instance.on_exception(loc=fn.__qualname__, exc=e)

        super().add_event(loop, instance, run_once_fn())


if __name__ == '__main__':
    pass
