import keyboard


class Signal:

    def __init__(self):
        self.listeners = []

    def add_listener(self, listener, index=None):
        if not callable(listener):
            raise ValueError("Listener must be a callable function.")

        if listener not in self.listeners:
            if index is None:
                self.listeners.append(listener)
            else:
                self.listeners.insert(index, listener)

    def remove_listener(self, listener):
        if listener not in self.listeners:
            return

        self.listeners.remove(listener)

    def _on_event(self, event):
        for listener in self.listeners:
            if listener(event):
                return

    def hook(self):
        keyboard.hook(self._on_event)

    def unhook(self):
        keyboard.unhook(self._on_event)
