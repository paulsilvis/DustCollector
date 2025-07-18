import tkinter as tk

# Your dust-collector haiku
haiku_text = (
    "Cables tamed at last\n"
    "Dust waits in silent suspense\n"
    "Fans whisper, alive."
)

# Create the window
root = tk.Tk()
root.title("Dust Collector")

# Make it fullscreen
root.attributes('-fullscreen', True)

# Add a label with your haiku
label = tk.Label(
    root,
    text=haiku_text,
    font=("Helvetica", 48),
    justify="center",
    padx=40,
    pady=40
)
label.pack(expand=True)

# Run the app
root.mainloop()

