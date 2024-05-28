#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author: Salifyanji Namwila
Course: Math 96: Mathematical Finance II
Date: 05.13.2024
Description: Final Project implementing various Monte Carlo simulation techniques
for options pricing.
"""

import numpy as np
import math

class MonteCarlo:
    """
    A class for pricing options using Monte Carlo methods in financial modeling.

    Attributes:
        steps (int): Number of time steps in the simulation.
        T (float): Total time of the option until expiration.
        S0 (float): Initial stock price.
        sigma (float): Volatility of the underlying asset.
        r (float): Risk-free interest rate.
        K (float): Strike price of the option.
        market (str): Market type ('EU' for European, 'USA' for American).
        option_type (str): Type of the option ('call' or 'put').
    """

    def __init__(self, steps, T, S0, sigma, r, K, market="EU", option_type="call"):
        """
        Constructs all the necessary attributes for the MonteCarlo object.
        """
        self.steps = steps
        self.T = T
        self.S0 = S0
        self.sigma = sigma
        self.r = r
        self.K = K
        self.dt = T / steps
        self.price = S0
        self.market = market.upper()
        self.option_type = option_type.lower()
        assert self.market in ["EU", "USA"], "Market not found. Choose EU or USA"
        assert self.option_type in ["call", "put"], "Non-existing option type."

    def wiener_method(self):
        """
        Simulates price paths using the Wiener process (geometric Brownian motion).
        """
        price = self.price
        self.wiener_price_path = np.zeros(self.steps)
        for i in range(self.steps):
            self.wiener_price_path[i] = price
            ds = self.r * price * self.dt + self.sigma * price * np.random.normal(0, 1) * np.sqrt(self.dt)
            price += ds

    def euler_integration_method(self, generate_path=False):
        """
        Simulates the final asset price using the Euler integration method, optionally
        generating the full price path.

        Args:
            generate_path (bool): Whether to generate the full price path or not.

        Returns:
            float: Final simulated asset price.
            np.array: Full simulated price path (if generate_path is True).
        """
        self.euler_integration = self.S0 * np.exp((self.r - 0.5 * self.sigma**2) * self.T + self.sigma * np.sqrt(self.T) * np.random.normal(0, 1))

        if generate_path:
            price = self.price
            self.euler_price_path = np.zeros(self.steps)
            for i in range(self.steps):
                self.euler_price_path[i] = price
                ds = price * math.exp((self.r-0.5*self.sigma**2)*self.dt + self.sigma*np.random.normal(0, 1) * math.sqrt(self.dt))
                price = ds

            return self.euler_integration, self.euler_price_path

        return self.euler_integration

    def euler_method_vectorized(self, random_numbers):
        """
        Vectorized version of the Euler method for faster computation.

        Args:
            random_numbers (np.array): Pre-generated array of random numbers.

        Returns:
            np.array: Vectorized simulation results.
        """
        self.euler_vectorized = self.S0 * np.exp((self.r - 0.5 * self.sigma**2) * self.T + self.sigma * random_numbers)
        return self.euler_vectorized

    def milstein_method(self):
        """
        Simulates price paths using the Milstein method, which includes correction for discretization errors.

        Notes:
            Adds a correction term to the geometric Brownian motion to account for discretization errors.
        """
        price = self.price
        self.milstein_price_path = np.zeros(self.steps)
        for i in range(self.steps):
            self.milstein_price_path[i] = price
            epsilon = np.random.normal(0, 1)
            ds = (1 + (self.r-.5*self.sigma**2)*self.dt + self.sigma * epsilon * np.sqrt(self.T) +
                  0.5 * self.sigma**2 * epsilon**2 * self.dt)
            price *= ds

    def antithetic_wiener_method(self):
        """
        Enhances efficiency by using the antithetic variate technique to reduce variance in the simulation.

        Returns:
            list: A list of price paths for both original and antithetic paths.
        """
        n_paths = 1000
        paths_list = []
        price = self.price
        anti_price = self.price
        for k in range(int(n_paths/2)):
            wiener_price_path = np.zeros(self.steps)
            anti_wiener_price_path = np.zeros(self.steps)

            for i in range(self.steps):
                epsilon = np.random.normal(0, 1)
                wiener_price_path[i] = price
                anti_wiener_price_path[i] = anti_price
                ds = self.r * price * self.dt + self.sigma * price * epsilon * np.sqrt(self.dt)
                anti_ds = self.r * anti_price * self.dt + self.sigma * price * -epsilon * np.sqrt(self.dt)

                price += ds
                anti_price += anti_ds

            paths_list.append(wiener_price_path)
            paths_list.append(anti_wiener_price_path)

        return paths_list