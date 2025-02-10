import numpy as np
from matplotlib import pyplot as plt
from plots import customize_style
from scipy import stats

customize_style()

approx_color = "darkmagenta"
exact_color = "tab:blue"
# exact_color, *_ = (
#     props["color"] for props in iter(plt.rcParams["axes.prop_cycle"])
# )

q = np.pad(np.linspace(0.05, 0.95, 5), (1, 0))
log_flux = np.linspace(-3, 3)
p = stats.norm.cdf(log_flux)
t = np.exp(0.5 * log_flux)
fig, ax = plt.subplots(tight_layout=True)
ax.plot(t, p, color=exact_color)
ax.set_xlim(0, 3)
ax.set_ylim(0, 1)

tq = np.exp(0.5 * stats.norm.ppf(q))
ax.plot(tq, q, ":", marker="o", color=approx_color, clip_on=False)
for n, (x, y) in enumerate(zip(tq, q)):
    kwargs = {}
    if n == 0:
        kwargs["ha"] = "left"
        kwargs["va"] = "top"
        kwargs["xytext"] = (0, -4)
    elif n == 1:
        kwargs["ha"] = "left"
        kwargs["va"] = "center"
        kwargs["xytext"] = (2, 0)
    else:
        kwargs["ha"] = "right"
        kwargs["va"] = "bottom"
        kwargs["xytext"] = (-2, 2)
    ax.annotate(
        rf" $(\epsilon_{{i{n}}}, \xi_{n})$",
        (x, y),
        textcoords="offset points",
        color=approx_color,
        **kwargs,
    )
ax.spines["right"].set_color("none")
ax.spines["top"].set_color("none")
ax.plot(3, 0, ">k", clip_on=False)
ax.set_xlabel("Exposure time")
ax.set_ylabel("Detection efficiency")
ax.set_xticks([])
plt.savefig("figures/piecewise-linear-exptime.pdf")
