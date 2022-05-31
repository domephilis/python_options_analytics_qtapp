# Test Lognormal Distribution

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

x = np.random.lognormal(0.5,0.36,100000)
x1 = np.random.lognormal(0.5,0.6,100000)
x2 = np.random.lognormal(0.5,0.8,100000)

plt.hist(x,800,histtype='step',label='0.36 sigma',density=True)

# plt.hist(x,800,cumulative=True,histtype='step')

plt.hist(x1,800,histtype='step',label='0.6 sigma',density=True)
# plt.hist(x1,800,cumulative=True,histtype='step')

plt.hist(x2,800,histtype='step',label='0.8 sigma',density=True)
# plt.hist(x2,800,cumulative=True,histtype='step')

plt.show()