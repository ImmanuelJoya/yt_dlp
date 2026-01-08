import tkinter as tk
from views.main_views import MainView
from controllers.controller import AppController


def main():
    root = tk.Tk()
    view = MainView(root)
    controller = AppController(view)
    view.set_controller(controller)
    root.mainloop()


if __name__ == "__main__":
    main()
