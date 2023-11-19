"""Tools to block signals."""
# from functools import wraps
# from PySide6.QtWidgets import QTableWidget


# def block_signals(func):
#   """Decorator to block signals temporarily."""
#   @wraps(func)
#   def wrapper(*args, **kwargs):
#     table_widget = args[0]  # Assuming the table widget is the first argument
#     try:
#       table_widget.blockSignals(True)
#       return func(*args, **kwargs)
#     finally:
#       table_widget.blockSignals(False)

#   return wrapper


# class BlockHandler:
#   """Class to handle blocking signals temporarily."""

#   def __init__(self, table: QTableWidget, handle_change_func: callable):
#     self.table = table
#     self.is_handling_change = False
#     self.handle_change_func = handle_change_func

#   @block_signals
#   def table_item_changed(self, item):
#     """Handle table item changed."""""
#     if not self.is_handling_change:
#       try:
#         self.is_handling_change = True
#         self.handle_change_func(item)
#       finally:
#         self.is_handling_change = False


# def operator(func):
#   """Decorator to mark class method as operator."""

#   def wrapper(self):
#     if self.table_item_changed()
#       self.table_item_changed()
#     func(self)
#     self.table.blockSignals(False)
#     return wrapper
