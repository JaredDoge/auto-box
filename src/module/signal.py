import keyboard


class Signal:

    def __init__(self):
        self.listeners = []

    def add_listener(self, listener, index=None):
        if not callable(listener):
            raise ValueError("Listener must be a callable function.")

        if listener not in self.listeners:
            if index:
                self.listeners.insert(index, listener)
            else:
                self.listeners.append(listener)

    def remove_listener(self, listener):
        if listener not in self.listeners:
            return

        self.listeners.remove(listener)

    def _on_event(self, event):
        for listener in self.listeners:
            if listener(event):
                break

    def hook(self):
        keyboard.hook(self._on_event)

    def unhook(self):
        keyboard.unhook(self._on_event)
