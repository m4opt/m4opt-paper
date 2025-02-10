import numpy as np
from matplotlib import pyplot as plt
from plots import customize_style

customize_style()


def cases(*args):
    *args, else_value = args
    while args:
        *args, cond, if_value = args
        else_value = np.where(cond, if_value, else_value)
    return else_value


fig_width, fig_height = plt.rcParams["figure.figsize"]
scale = 0.5
fig, axs = plt.subplots(
    3,
    2,
    sharex=True,
    sharey="row",
    figsize=(2 * scale * fig_width, 3 * scale * fig_height),
    tight_layout=True,
)

t = np.linspace(0, 0.6, 1000)
axs[0, 0].plot(t, cases(t <= 0.2, 1, t <= 0.4, -1, 0))
axs[1, 0].plot(t, cases(t <= 0.2, t, t <= 0.4, 0.4 - t, 0))
axs[2, 0].plot(
    t,
    cases(
        t <= 0.2,
        0.5 * t**2,
        t <= 0.4,
        0.02 + 0.2 * (t - 0.2) - 0.5 * (t - 0.2) ** 2,
        0.04,
    ),
)
t = np.linspace(0, 1, 1000)
axs[1, 1].plot(t, cases(t <= 0.3, t, t <= 0.5, 0.3, t <= 0.8, 0.8 - t, 0))
axs[0, 1].plot(t, cases(t <= 0.3, 1, t <= 0.5, 0, t <= 0.8, -1, 0))
axs[2, 1].plot(
    t,
    cases(
        t <= 0.3,
        0.5 * t**2,
        t <= 0.5,
        0.045 + 0.3 * (t - 0.3),
        t <= 0.8,
        0.105 + 0.3 * (t - 0.5) - 0.5 * (t - 0.5) ** 2,
        0.15,
    ),
)
axs[2, 0].set_xlabel("time")
axs[2, 1].set_xlabel("time")
axs[0, 0].set_ylabel("acceleration")
axs[1, 0].set_ylabel("velocity")
axs[2, 0].set_ylabel("position")
axs[0, 0].set_title("short slew")
axs[0, 1].set_title("long slew")

axs[0, 0].set_yticks([-1, 0, 1])
axs[0, 0].set_yticklabels(["-|max|", "0", "+|max|"])
axs[1, 0].set_yticks([0, 0.3])
axs[1, 0].set_yticklabels(["0", "max"])
axs[2, 0].set_yticks([0])
axs[2, 0].set_yticklabels(["0"])
axs[2, 0].set_xticks([])
axs[2, 1].set_xticks([])

fig.savefig("figures/slew.pdf")
