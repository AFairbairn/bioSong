import os
from tkinter import filedialog, messagebox

Large_Font = ("Verdana", 12)
Extra_Large_Font = ("Verdana", 20, "bold")


def set_dir():
    path = filedialog.askdirectory(
        initialdir=os.getcwd(), title="Select A Directory")
    os.chdir(path)
    return path


def error_popup(err_type, err_msg):
    messagebox.showerror(err_type, err_msg)


def question_popup(title, question, action):
    answer = messagebox.askyesno(title, question)
    if answer == "yes":
        action = action()
        return action


def has_numbers(input_string):
    return any(char.isdigit() for char in input_string)


# Sort search data
def sort_by(tree, col, descending):
    """Sort tree contents when a column is clicked on."""
    # grab values to sort
    data = [(tree.set(child, col), child)
            for child in tree.get_children('')]
    # reorder data
    data.sort(reverse=descending)
    for i, item in enumerate(data):
        tree.move(item[1], '', i)
    # switch the heading so that it will sort in the opposite direction
    tree.heading(col,
                 command=lambda col=col: sort_by(tree, col, int(not descending)))
