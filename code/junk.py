import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Simple App")


def add_to_list(event=None):
    text = entry.get()
    if text:
        text_list.insert(tk.END, text)
        entry.delete(0, tk.END)


root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=3)
root.rowconfigure(0, weight=1)

frame = ttk.Frame(root)
frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

frame.columnconfigure(0, weight=1)
frame.rowconfigure(1, weight=1)

entry = ttk.Entry(frame)
entry.grid(row=0, column=0, sticky="ew")

entry.bind("<Return>", add_to_list)

entry_btn = ttk.Button(frame, text="Add", command=add_to_list)
entry_btn.grid(row=0, column=1)

text_list = tk.Listbox(frame)
text_list.grid(row=1, column=0, columnspan=2, sticky="nsew")

frame2 = tk.Frame(root)
frame2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

frame2.columnconfigure(0, weight=1)
frame2.rowconfigure(1, weight=1)

entry = tk.Entry(frame2)
entry.grid(row=0, column=0, sticky="ew")

entry.bind("<Return>", add_to_list)

entry_btn = tk.Button(frame2, text="Add", command=add_to_list)
entry_btn.grid(row=0, column=1)

text_list = tk.Listbox(frame2)
text_list.grid(row=1, column=0, columnspan=2, sticky="nsew")

root.mainloop()

