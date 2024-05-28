 ---
# Quasi-Monte-Carlo for Options Pricing

## Overview
This project aims to enhance the efficiency and accuracy of traditional Monte Carlo (MC) simulation methods by incorporating Quasi-Monte Carlo (QMC) techniques and variance reduction strategies. My focus is on demonstrating the empirical advantages of these methods in the context of financial modeling.

## Features
- **Options Pricing**: Utilize Monte Carlo simulations to compute option prices.
- **Greek Delta Calculation**: Employ the bump-and-revalue method to calculate the Greek delta.
- **Seed Configuration**: Choose between fixed and random seeds for simulation reproducibility and variability.
- **Comparative Analysis**: Compare daily versus weekly hedging strategies using default or custom parameters.

## Usage
To interact with the project, you will primarily use `main.py`, which is equipped to handle various command line arguments for different functionalities.

### Getting Help
To view the available options and their default settings, use the help command:
```bash
./main.py --help
```

### Example Command
The following example demonstrates how to run simulations comparing daily and weekly hedging strategies using the bump and revalue method:
```bash
./main.py -func 'bump_and_revalue'
```

### Output
The output consists of three arrays:
1. **Monte Carlo Result**: The result of the Monte Carlo simulation.
2. **Black-Scholes Solution**: The theoretical solution derived from the Black-Scholes model.
3. **Relative Error**: The relative error between the Monte Carlo result and the Black-Scholes solution.

Each row in the arrays corresponds to a different sample size, while each column represents different values of epsilon (the precision of the bump in the bump-and-revalue method).

## Contributing
This project  was designed and implemented  by Salifyanji J. Namwila

---

