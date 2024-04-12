from scipy.optimize import fsolve
import numpy as np
import matplotlib.pyplot as plt

# Define the sigmoid function
def sigmoid(x, k, x0=365):
    return 1 / (1 + np.exp(-k * (x - x0)))

# We aim for f(0) close to 1 and f(365) close to 0.5 for a midpoint transition
# Let's experiment with a k value that gives us a nice curve from 1 to 0 across 365 days

# Trial and error or optimization could find a suitable k, but let's start with a guess
k_guess = 0.01

# Generate a range of days
days = np.linspace(0, 365, 1000)
# Calculate the sigmoid function for these days with our guess for k
scores = sigmoid(days, k_guess)

# Plot the result
plt.figure(figsize=(10, 6))
plt.plot(days, scores, label=f'Sigmoid with k={k_guess}')
plt.xlabel('Days Old')
plt.ylabel('Score')
plt.title('Sigmoidal Score Transition from 1 to 0 Over 365 Days')
plt.legend()
plt.grid(True)

plt.savefig('img/sigmoid.png')
