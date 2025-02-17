'''TODO: Documentation
'''

from bge import logic
import time
from uplogic.physics import on_collision  # noqa


def on_pre_draw(callback):
    ULEventManager.update_on.append(callback)


def on_post_draw(callback):
    ULEventManager.update_on.append(callback)


def get_event_manager():
    if ULEventManager.update not in ULEventManager.update_on:
        ULEventManager.update_on.append(ULEventManager.update)


def set_update_loop(loop):
    ULEventManager.set_update_on(loop)


class ULEventManager():
    '''Manager for `ULEvent` objects, not inteded for manual use.
    '''
    events = {}
    callbacks = []
    done = []
    update_on = logic.getCurrentScene().post_draw

    @classmethod
    def set_update_on(cls, li):
        if cls.update in cls.update_on:
            cls.update_on.remove(cls.update)
        if cls.update not in li:
            li.append(cls.update)
        cls.update_on = li

    @classmethod
    def update(cls):
        for cb in cls.callbacks.copy():
            cb()

    @classmethod
    def update(cls):
        for cb in cls.callbacks.copy():
            cb()

    @classmethod
    def log(cls):
        if cls.events:
            print('Events:')
            for evt in cls.events:
                print(f'\t{evt}:\t{cls.events[evt].content}')

    @classmethod
    def schedule(cls, cb):
        get_event_manager()
        cls.callbacks.append(cb)

    @classmethod
    def cancel(cls, cb):
        get_event_manager()
        if cb in cls.callbacks:
            cls.callbacks.remove(cb)

    @classmethod
    def bind(cls, cb):
        get_event_manager()
        cls.schedule(cb)

    @classmethod
    def unbind(cls, cb):
        get_event_manager()
        cls.cancel(cb)

    @classmethod
    def register(cls, event):
        get_event_manager()
        cls.events[event.id] = event
        cls.schedule(event.remove)

    @classmethod
    def send(cls, id, content, messenger) -> None:
        get_event_manager()
        ULEvent(id, content, messenger)

    @classmethod
    def receive(cls, id):
        get_event_manager()
        return cls.events.get(id, None)

    @classmethod
    def consume(cls, id):
        get_event_manager()
        return cls.events.pop(id, None)


class ULEvent():
    '''Event generated by `uplogic.events.send()`.

    **Not intended for manual use.**

    :param `id`: Identifier of the event; can be anything, not just `str`.
    :param `content`: This can be used to store data in an event.
    :param `messenger`: Can be used to store an object.
    '''

    def __init__(self, id, content=None, messenger=None):
        self.id = id
        self.content = content
        self.messenger = messenger
        ULEventManager.schedule(self.register)

    def register(self):
        ULEventManager.register(self)
        ULEventManager.cancel(self.register)

    def remove(self):
        ULEventManager.events.pop(self.id, None)
        ULEventManager.cancel(self.remove)


def send(id, content=None, messenger=None) -> None:
    '''Send an event that can be reacted to.

    :param `id`: Identifier of the event; can be anything, not just `str`.
    :param `content`: This can be used to store data in an event.
    :param `messenger`: Can be used to store an object.
    '''
    ULEventManager.send(id, content, messenger)


def receive(id) -> ULEvent:
    '''Check if an event has occured.

    :param `id`: Identifier of the event; can be anything, not just `str`.

    :returns: `ULEvent` with `id`, `content` and `messenger` as attributes.
    '''
    return ULEventManager.receive(id)


def consume(id: str):
    '''Check if an event has occured. This will remove the event.

    :param `id`: Identifier of the event; can be anything, not just `str`.

    :returns: `ULEvent` with `id`, `content` and `messenger` as attributes.
    '''
    return ULEventManager.consume(id, None)


def bind(id, callback) -> None:
    '''Bind a callback to an event.

    :param `id`: Name of the event; can be anything, not just `str`.
    :param `callback`: This callback will be called every time the event is
    triggered.
    '''
    class BoundCallback():
        def __init__(self, id, cb) -> None:
            self.id = id
            self.callback = cb
            ULEventManager.bind(self._check_evt)

        def _check_evt(self):
            evt = receive(self.id)
            if evt:
                self.callback(evt)

        def unbind(self):
            ULEventManager.unbind(self._check_evt)

    return BoundCallback(id, callback)


class ScheduledEvent():
    '''Event generated by `uplogic.events.schedule()`.

    :param `delay`: Delay with which to send the event in seconds.
    :param `id`: Identifier of the event; can be anything, not just `str`
    :param `content`: This can be used to store data in an event.
    :param `messenger`: Can be used to store an object.
    '''

    def __init__(self, delay, id, content, messenger):
        self.time = time.time()
        self.delay = self.time + delay
        self.id = id
        self.content = content
        self.messenger = messenger
        ULEventManager.schedule(self.send_scheduled)

    def send_scheduled(self):
        if time.time() >= self.delay:
            ULEventManager.cancel(self.send_scheduled)
            ULEvent(self.id, self.content, self.messenger)

    def cancel(self):
        ULEventManager.cancel(self.send_scheduled)


def schedule(id: str, delay=0.0, content=None, messenger=None) -> ScheduledEvent:
    '''Send an event that can be reacted to with a delay.

    :param `id`: Name of the event; can be anything, not just `str`. If `id` is callable, `content` can be used as argument.
    :param `content`: This can be used to store data in an event.
    :param `messenger`: Can be used to store an object.
    :param `delay`: Delay with which to send the event in seconds.
    '''
    if callable(id):
        return ScheduledCallback(id, delay, content)
    return ScheduledEvent(delay, id, content, messenger)


class ScheduledCallback():
    '''Event generated by `uplogic.events.schedule_callback()`.

    **Not intended for manual use.**

    :param `cb`: Callback to be evaluated.
    :param `delay`: Delay with which to call the function in seconds.
    :param `arg`: If this is defined, callback will be called with this
    argument.
    '''

    def __init__(self, cb, delay=0.0, arg=None):
        self.time = time.time()
        self.delay = self.time + delay
        self.callback = cb
        self.arg = arg
        ULEventManager.schedule(self.call_scheduled)

    def call_scheduled(self):
        if time.time() >= self.delay:
            ULEventManager.cancel(self.call_scheduled)
            if self.arg is not None:
                self.callback(self.arg)
            else:
                self.callback()

    def cancel(self):
        ULEventManager.cancel(self.call_scheduled)


def schedule_callback(cb, delay=0.0, arg=None) -> ScheduledCallback:
    '''Call a function with a delay. The function can have an argument when
    defined as a keyword.

    Callback cannot return anything.

    :param `cb`: Callback to be evaluated.
    :param `delay`: Delay with which to call the function in seconds.
    :param `arg`: If this is defined, callback will be called with this
    argument.
    '''
    return ScheduledCallback(cb, delay, arg)
