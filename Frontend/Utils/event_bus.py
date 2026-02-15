"""
Simple Event Bus for inter-component communication in the application.
Allows components to subscribe to events and publish events to trigger actions.
"""

# Global event registry to store subscribers
_subscribers = {}


def subscribe(event_name, callback):
    """
    Subscribe to an event with a callback function.
    
    Args:
        event_name (str): The name of the event to subscribe to
        callback (callable): The function to call when the event is published
    """
    if event_name not in _subscribers:
        _subscribers[event_name] = []
    
    _subscribers[event_name].append(callback)


def publish(event_name, **kwargs):
    """
    Publish an event to all subscribers.
    
    Args:
        event_name (str): The name of the event to publish
        **kwargs: Additional arguments to pass to subscriber callbacks
    """
    if event_name in _subscribers:
        for callback in _subscribers[event_name]:
            try:
                callback(**kwargs)
            except Exception as e:
                print(f"Error in event callback for '{event_name}': {e}")


def unsubscribe(event_name, callback):
    """
    Unsubscribe a callback from an event.
    
    Args:
        event_name (str): The name of the event
        callback (callable): The callback function to remove
    """
    if event_name in _subscribers:
        try:
            _subscribers[event_name].remove(callback)
        except ValueError:
            pass


def clear_subscribers(event_name=None):
    """
    Clear all subscribers for an event, or all events if event_name is None.
    
    Args:
        event_name (str, optional): The specific event to clear. If None, clears all.
    """
    global _subscribers
    
    if event_name is None:
        _subscribers = {}
    elif event_name in _subscribers:
        _subscribers[event_name] = []
