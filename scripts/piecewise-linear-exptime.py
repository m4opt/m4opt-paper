from matplotlib import pyplot as plt
import numpy as np
from scipy import stats

q = np.pad(np.linspace(0.05, 0.95, 5), (1, 0))
log_flux = np.linspace(-3, 3)
p = stats.norm.cdf(log_flux)
t = np.exp(0.5 * log_flux)
ax = plt.axes()
ax.plot(t, p)
ax.set_xlim(0, 3)
ax.set_ylim(0, 1)

tq = np.exp(0.5 * stats.norm.ppf(q))
for n, (x, y) in enumerate(zip(tq, q)):
    if n > 0:
        ax.text(x, y, rf' $(\epsilon_{{i{n}}}, \xi_{n})$', va='top')
ax.plot(tq, q, '-o')
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.set_xlabel('Exposure time')
ax.set_ylabel('Detection efficiency')
ax.set_xticks([])
ax.plot(3, 0, '>k', clip_on=False)
plt.savefig('figures/piecewise-linear-exptime.pdf')
