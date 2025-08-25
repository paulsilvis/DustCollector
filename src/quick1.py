import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

fig, ax = plt.subplots()
xdata, ydata = [], []
line, = ax.plot([], [])

def update(frame):
    xdata.append(frame)
    ydata.append(random.randint(0, 10))
    line.set_data(xdata, ydata)
    ax.relim()
    ax.autoscale_view()
    return line,

ani = animation.FuncAnimation(fig, update, frames=range(100), interval=500)
plt.tight_layout()
plt.show()
