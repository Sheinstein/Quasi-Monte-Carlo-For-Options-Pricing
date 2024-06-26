#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author: Salifyanji Namwila
Math 96: Mathematical Finance II
05.13.2024
Final Project
"""
import argparse
import math
import os
from decimal import Decimal
from monte_carlo import monte_carlo
import matplotlib.pyplot as plt
import matplotlib.lines as ls
import colorsys
import numpy as np
import scipy.stats as stats
import tqdm
from collections import defaultdict
import multiprocessing
from binomial_tree import BinTreeOption, BlackScholes
import tqdm
import pickle


def plot_wiener_process(T,K, S0, r, sigma, steps,save_plot=False):
    """
    :param T:  Period
    :param S0: Stock price at spot time
    :param K:  Strike price
    :param r:  interest rate
    :param sigma: volatility
    :param steps: number of steps
    :param save_plot:  to save the plot
    :return:  returns a plot of a simulated stock movement
    """

    mc=monte_carlo(steps, T, S0, sigma, r, K)

    mc.wiener_method()


    plt.figure(figsize=(10, 7))
    np.linspace(1,mc.T*365,mc.steps)#to ensure the x-axis is in respective to the total time T
    plt.plot(np.linspace(1,mc.T*365,mc.steps),mc.wiener_price_path)
    plt.xlabel("Days",fontsize=18,fontweight='bold')
    plt.ylabel("Stock price",fontsize=18,fontweight='bold')
    plt.tick_params(labelsize='18')
    #plt.title("Stock price simulated based on the Wiener process",fontsize=17,fontweight='bold')
    if save_plot:
        plt.savefig("figures/"+"wiener_process",dpi=300)
    plt.show()
    plt.close()


def worker_pay_off_euler_direct(object):
    np.random.seed()
    object.euler_integration_method()
    pay_off_array = np.max([(object.K - object.euler_integration), 0])

    return pay_off_array

def worker_pay_off_euler_sim(object):
    np.random.seed()
    object.euler_integration_method(generate_path=True)
    pay_off_array = np.max([(object.K - object.euler_price_path[-1]), 0])

    return pay_off_array

def diff_monte_carlo_process(T, S0, K, r, sigma, steps,samples,save_plot=False):
    """
    :param T:  Period
    :param S0: Stock price at spot time
    :param K:  Strike price
    :param r:  interest rate
    :param sigma: volatility
    :param steps: number of steps
    :param save_plot:  to save the plot
    :return:  returns a plot of a simulated stock movement
    """

    different_mc_rep = samples
    increments = len(samples)

    # mc_pricing will be a dict a list containing  tuples of (pricing and standard error)
    mc_pricing = defaultdict(list)

    for repetition in tqdm.tqdm(different_mc_rep):

        mc_list = [monte_carlo(steps, T, S0, sigma, r, K) for i in range(repetition)]
        num_core = 3
        pool = multiprocessing.Pool(num_core)
        pay_off_list = pool.map(worker_pay_off_euler_direct, ((mc) for mc in mc_list))
        pool.close()
        pool.join()

        mean_pay_off = np.mean([pay_off for pay_off in pay_off_list])
        std_pay_off = np.std([pay_off for pay_off in pay_off_list])/np.sqrt(repetition)
        mc_pricing['euler_integration'].append((np.exp(-r*T)*mean_pay_off ,std_pay_off))

    bs = BlackScholes(T, S0, K, r, sigma)
    bs_solution=np.ones(increments)*bs.put_price()
    print(bs.put_price())


    for i in range(len(different_mc_rep)):
        print("Number of samples: ", different_mc_rep[i]," Mean :", mc_pricing['euler_integration'][i][0], " Variance :", mc_pricing['euler_integration'][i][1])


    fig, axs = plt.subplots(2,figsize=(10, 7))
    axs[0].plot(different_mc_rep, [i[0] for i in mc_pricing['euler_integration']], color='gray', label='Monte Carlo')
    axs[0].plot(different_mc_rep, bs_solution, 'r', label='Black Scholes')
    axs[0].legend()
    axs[0].set_ylabel("Option Price", fontsize=17)
    axs[0].tick_params(labelsize='18')

    axs[1].plot(different_mc_rep, [i[1] for i in mc_pricing['euler_integration']], label='Standard error')
    axs[1].set_xlabel("Monte Carlo repetition", fontsize=17)
    axs[1].legend()
    axs[1].set_ylabel("Standard error", fontsize=17)
    axs[1].tick_params(labelsize='18')
    axs[1].ticklabel_format(axis="y", style="sci", scilimits=(0, 0))

    if save_plot:
        plt.savefig("figures/" + "mc_euler_integration_diff_MC", dpi=300)
    plt.show()
    plt.close()



def diff_K_monte_carlo_process(T,different_k , S0, r, sigma, steps, repetition, save_plot=False):
    """
    :param T:  Period
    :param S0: Stock price at spot time
    :param K:  Strike price
    :param r:  interest rate
    :param sigma: volatility
    :param steps: number of steps
    :param save_plot:  to save the plot
    :return:  returns a plot of a simulated stock movement
    """

    # mc_pricing will be a dict of a list containing  tuples of (pricing and standard error)
    mc_pricing = defaultdict(list)

    for diff_strike_price in tqdm.tqdm(different_k):

        mc_list = [monte_carlo(steps, T, S0, sigma, r, diff_strike_price) for i in range(repetition)]
        num_core = 3
        pool = multiprocessing.Pool(num_core)
        pay_off_list = pool.map(worker_pay_off_euler_direct, ((mc) for mc in mc_list))
        pool.close()
        pool.join()

        mean_pay_off = np.mean([pay_off for pay_off in pay_off_list])
        std_pay_off = np.std([pay_off for pay_off in pay_off_list])/np.sqrt(repetition)
        mc_pricing['euler_integration'].append((np.exp(-r*T)*mean_pay_off,std_pay_off))

    bs_list= []
    for k in different_k:
        bs = BlackScholes(T, S0, k, r, sigma)
        bs_list.append(bs.put_price())

    fig, axs = plt.subplots(2,figsize=(10, 7))

    axs[0].plot(different_k,[i[0] for i in mc_pricing['euler_integration']],linestyle='--',linewidth=3,
                color='gray', label='Monte Carlo')
    axs[0].plot(different_k, bs_list, 'r', label='Black Scholes')
    axs[0].legend()
    axs[0].set_ylabel("Option Price",fontsize=17)
    axs[0].tick_params(labelsize='18')

    axs[1].plot(different_k,[i[1] for i in mc_pricing['euler_integration']],label='Standard error')
    axs[1].set_xlabel("Strike price K", fontsize=17)
    axs[1].legend()
    axs[1].set_ylabel("Standard error", fontsize=17)
    axs[1].tick_params(labelsize='18')
    axs[1].ticklabel_format(axis="y", style="sci",scilimits=(0,0))


    if save_plot:
        plt.savefig("figures/" + "mc_euler_integration_diff_K", dpi=300)
    plt.show()
    plt.close()

def diff_sigma_monte_carlo_process(T,K , S0, r, different_sigma, steps, repetition, save_plot=False):
    """
    :param T:  Period
    :param S0: Stock price at spot time
    :param K:  Strike price
    :param r:  interest rate
    :param sigma: volatility
    :param steps: number of steps
    :param save_plot:  to save the plot
    :return:  returns a plot of a simulated stock movement
    """

    # mc_pricing will be a dict of a list containing  tuples of (pricing and standard error)
    mc_pricing = defaultdict(list)

    for sigma in tqdm.tqdm(different_sigma):

        mc_list = [monte_carlo(steps, T, S0, sigma, r, K) for i in range(repetition)]
        num_core = 3
        pool = multiprocessing.Pool(num_core)
        pay_off_list = pool.map(worker_pay_off_euler_direct, ((mc) for mc in mc_list))
        pool.close()
        pool.join()

        mean_pay_off = np.mean([pay_off for pay_off in pay_off_list])
        std_pay_off = np.std([pay_off for pay_off in pay_off_list])/np.sqrt(repetition)
        mc_pricing['euler_integration'].append((np.exp(-r*T)*mean_pay_off,std_pay_off))

    bs_list = []
    for s in different_sigma:
        bs = BlackScholes(T, S0, K, r, s)
        bs_list.append(bs.put_price())

    fig, axs = plt.subplots(2,figsize=(10, 7))
    axs[0].plot(different_sigma,[i[0] for i in mc_pricing['euler_integration']],linestyle='--',linewidth=3,
                color='gray', label='Monte Carlo')
    axs[0].plot(different_sigma, bs_list, 'r', label='Black Scholes')
    axs[0].legend()
    axs[0].set_ylabel("Option Price",fontsize=18)
    axs[0].tick_params(labelsize='18')

    axs[1].plot(different_sigma,[i[1] for i in mc_pricing['euler_integration']],label='Standard error')
    axs[1].set_xlabel("Volatility", fontsize=18)
    axs[1].legend()
    axs[1].set_ylabel("Standard error", fontsize=18)
    axs[1].tick_params(labelsize='18')
    axs[1].ticklabel_format(axis="y", style="sci",scilimits=(0,0))


    if save_plot:
        plt.savefig("figures/" + "mc_euler_integration_diff_sigma", dpi=300)
    plt.show()
    plt.close()



def milstein_process(T, S0, K, r, sigma, steps,save_plot=False):
    """
    :param T:  Period
    :param S0: Stock price at spot time
    :param K:  Strike price
    :param r:  interest rate
    :param sigma: volatility
    :param steps: number of steps
    :param save_plot:  to save the plot
    :return:  returns a plot of a simulated stock movement
    """

    mc = monte_carlo(steps, T, S0, sigma, r, K)

    price_path=mc.milstein_method()

    plt.figure()
    np.linspace(1, mc.T * 365, mc.steps)  # to ensure the x-axis is in respective to the total time T
    plt.plot(np.linspace(1, mc.T * 365, mc.steps), mc.milstein_price_path)
    plt.xlabel("Days", fontsize=12, fontweight='bold')
    plt.ylabel("Stock price", fontsize=12, fontweight='bold')
    plt.xticks(fontweight='bold')
    plt.yticks(fontweight='bold')
    plt.title("Milestein method", fontsize=17, fontweight='bold')
    if save_plot:
        plt.savefig("figures/" + "milestein method", dpi=300)
    plt.show()
    plt.close()



def antithetic_monte_carlo_process(T, S0, K, r, sigma, steps,save_plot=False):

    mc = monte_carlo(steps, T, S0, sigma, r, K)

    path_list=mc.antithetic_wiener_method()

    plt.figure()
    plt.plot(path_list[0])
    plt.plot(path_list[1])
    plt.xlabel("Days", fontsize=12, fontweight='bold')
    plt.ylabel("Stock price", fontsize=12, fontweight='bold')
    plt.title("Antithetic Monte Carlo", fontsize=17, fontweight='bold')
    plt.xticks(fontweight='bold')
    plt.yticks(fontweight='bold')
    plt.show()
    plt.close()


def diff_iter_bump_and_revalue(
    T, S0, K, r, sigma, steps,
    epsilons=[0.5], set_seed="random",iterations=[100],contract="put", seed_nr=10,
    full_output=False, option_type="regular",
    show_plot=False, save_plot=False, save_output=False
    ):
    """
    Applies bump and revalue for for different amount of iterations.
    :param T:  Maturity in years
    :param S0: Stock price at spot time
    :param K:  Strike price
    :param r:  Risk-free interest rate (yearly rate)
    :param sigma: Volatility
    :param steps: Number of intermediate steps
    :param epsilons: bump initial stock price
    :param set_seed: random or fixed seed for the simulations
    :param seed_nr: seed to use
    :param iterations: list of number of MC simulations
    :param option_type: option's type (regular or digital)
    :param full_output: returns full output
    :param save_plot:  to save the plot
    :return:  returns a plot of a simulated stock movement
    """

    # Setup storage for results of the different MC simulations
    diff_iter, diff_eps = len(iterations), len(epsilons)
    deltas = np.zeros((diff_iter, diff_eps))
    bs_deltas = np.zeros((diff_iter, diff_eps))
    errors = np.zeros((diff_iter, diff_eps))
    std_deltas = np.zeros((diff_iter, diff_eps))

    seeds = []
    if set_seed == "fixed":
        seeds = [seed_nr for _ in range(diff_eps)]

    # Apply bump and revalue method for each number of iterations
    for i, iteration in enumerate(iterations):
        result = bump_revalue_vectorized(T, S0, K, r, sigma, steps,
                    epsilons=epsilons, seeds=seeds, reps=iteration,
                    full_output=full_output, option_type=option_type, contract=contract
                )
        deltas[i, :], bs_deltas[i, :], errors[i, :], std_deltas[i, :] = result

    if show_plot or save_plot:
        plot_bump_and_revalue(
            epsilons, iterations, errors, std_deltas, option_type,
            contract, set_seed, show_plot, save_plot
            )

    # if required output is saved
    if save_output:
        name = os.path.join(
            "Data", f"{option_type}-{contract}_bump_and_revalue_{set_seed}seed_"
            )
        save_output_ex2(name, K, sigma, deltas, bs_deltas, errors, std_deltas)

    return deltas, bs_deltas, errors, std_deltas

def bump_revalue_vectorized(
    T, S0, K, r, sigma, steps, epsilons=[0.5], seeds=[], reps=100, full_output=False, option_type="regular", contract="put"
):
    """
    Applies bump and revalue method to determine the delta at spot time
    """
    
    # Init amount of bumps (epsilons) and storage (Black Scholes) deltas
    diff_eps = len(epsilons)
    deltas = np.zeros(diff_eps)
    bs_deltas = np.zeros(diff_eps)
    std_deltas = np.zeros(diff_eps)
    discount = math.exp(-r * T)

    # Start MC simulation for each bump
    for i, eps in enumerate(epsilons):

        # Determine "bumped" price
        S0_eps = S0 + eps

        # Create bump and revalue Monte Carlo (MC) objects
        mc_revalue = monte_carlo(steps, T, S0, sigma, r, K)
        mc_bump = monte_carlo(steps, T, S0_eps, sigma, r, K)

        # Determine stock prices at maturity
        S_rev, S_bump = stock_prices_bump_revalue(
                            seeds, reps, mc_revalue, mc_bump, i
                        )

        # Determine prices and delta hedging depending at spot time
        results = payoff_and_hedge_options(
            option_type, contract, S_rev,
            S_bump, S0_eps, K, r, sigma,
            T, bs_deltas, discount, i
        )
        prices_revalue, prices_bump, bs_deltas = results

        # Mean and variance option prices bump and revalue
        mean_revalue = prices_revalue.mean()
        mean_bump = prices_bump.mean()
        var_bump = prices_bump.var()
        var_revalue = prices_revalue.var()

        # Determine MC delta and its variance
        deltas[i] = (discount * (mean_bump - mean_revalue)) / eps
        var_delta = 0
        if not seeds:
            cov_br = np.cov(prices_bump, prices_revalue)[0, 1]
            var_delta = (1 / (eps * eps)) * ((var_bump + var_revalue - 2 * cov_br) / reps)

        # print("Var BUMP:", round(var_bump, 3))
        # print("Var REVALUE", round(var_revalue, 3))
        # print("COVARIANCE:", round(cov_br, 3))
        # print("Var DELTA:", round(var_delta, 3))
        # print("========================================================")

        std_deltas[i] = math.sqrt(var_delta)

    # Determine relative (percent) errors
    errors = np.abs(1 - (deltas / bs_deltas))

    # Checks if full output is required
    if full_output:
        return deltas, bs_deltas, errors, std_deltas, prices_revalue, prices_bump

    return deltas, bs_deltas, errors, std_deltas

def stock_prices_bump_revalue(seeds, reps, mc_revalue, mc_bump, i):
    """
    """
    # Set seed (if given) and generate similar sequence for bump and revalue
    S_rev, S_bump = None, None
    if seeds:
        np.random.seed(seeds[i])
        numbers = np.random.normal(size=reps)

        # Euler method
        S_rev = mc_revalue.euler_method_vectorized(numbers)
        S_bump = mc_bump.euler_method_vectorized(numbers)

    # Otherwise generate a different sequence for bump and revalue
    else:
        numbers_rev = np.random.normal(size=reps)
        numbers_bump = np.random.normal(size=reps)

        # Euler method
        S_rev = mc_revalue.euler_method_vectorized(numbers_rev)
        S_bump = mc_bump.euler_method_vectorized(numbers_bump)

    return S_rev, S_bump

def payoff_and_hedge_options(
    option_type, contract, S_rev, S_bump, S0_eps, K, r, sigma, T, bs_deltas, discount, i
    ):
    """
    Determine payoffs at maturity and (theoretical) delta hedging at spot time
    """
    prices_revalue, prices_bump = 0, 0

    # European put option
    if option_type == "regular" and contract == "put":

        # Determine option price
        prices_revalue = np.where(K - S_rev > 0, K - S_rev, 0)
        prices_bump = np.where(K - S_bump > 0, K - S_bump, 0)

        # Theoretical delta
        d1 = (np.log(S0_eps / K) + (r + 0.5 * sigma ** 2)
              * T) / (sigma * np.sqrt(T))
        bs_deltas[i] = -stats.norm.cdf(-d1, 0.0, 1.0)

    # Digital option
    elif option_type == "digital" and contract == "call":

        # Determine option price
        prices_revalue = np.where(S_rev - K > 0, 1, 0)
        prices_bump = np.where(S_bump - K > 0, 1, 0)

        # Theoretical delta
        d2 = (np.log(S0_eps / K) + (r - 0.5 * sigma ** 2)
                * T) / (sigma * np.sqrt(T))
        num = discount * stats.norm.pdf(d2, 0.0, 1.0)
        den = sigma * S0_eps * math.sqrt(T)
        bs_deltas[i] = num / den

    return prices_revalue, prices_bump, bs_deltas

def plot_bump_and_revalue(
        epsilons, iterations, errors, std_deltas,
        option_type, contract, set_seed, show_plot=False, save_plot=False
    ):
    """
    """

    name_err = os.path.join(
        "figures",
        "errors_{}_{}_bump_and_revalue_{}seed.pdf"
        .format(option_type, contract, set_seed)
        )
    name_std = os.path.join(
        "figures",
        "stddevs_{}_{}_bump_and_revalue_{}seed.pdf"
        .format(option_type, contract, set_seed)
    )
    diff_iter, diff_eps = len(iterations), len(epsilons)
    colors, linestyles = get_N_HexCol(diff_iter), get_N_linestyles(diff_iter)

    fig = plt.figure()
    for i, iteration in enumerate(iterations):
        plt.plot(
            epsilons, errors[i, :], color=colors[i],
            linestyle=linestyles[i], label="N = {:.1e}".format(Decimal(str(iteration)))
            )

    plt.xlabel("Epsilons")
    plt.ylabel("Relative error")
    plt.yscale("log")
    plt.title("Relative error delta bump-and-revalue method \n" +
            "({} seed, {} {})".format(set_seed, option_type, contract))
    plt.legend()

    if show_plot:
        plt.show()

    if save_plot:
        plt.savefig(name_err, dpi=300)

    plt.close()

    fig = plt.figure()
    for i, iteration in enumerate(iterations):
        plt.plot(
            epsilons, std_deltas[i, :], color=colors[i],
            linestyle=linestyles[i], label="N = {:.1e}".format(Decimal(str(iteration)))
            )

    plt.xlabel("Epsilons")
    plt.ylabel("Standard deviation")
    plt.yscale("log")
    plt.title("Standard deviation delta with bump-and-revalue method\n" +
            "({} seed, {} {})".format(set_seed, option_type, contract))
    plt.legend()

    if show_plot:
        plt.show()

    if save_plot:
        plt.savefig(name_std, dpi=300)

    plt.close()


def LR_method(T, S0, K,r, sigma, steps, set_seed = "random", reps = [100],contract = "call", seed_nr = 10, option_type = "digital", show_plot = False, save_plot = False, save_output = False):

    """
    ONLY FOR DIGITAL OPTION.
    """

    # Initialize variables
    diff_reps = len(reps)
    deltas = np.zeros(diff_reps)
    std_deltas = np.zeros(diff_reps)
    discount = math.exp(-r * T)
    mc = monte_carlo(steps, T, S0, sigma, r, K)

    seeds = []
    if set_seed == "fixed":
        seeds = [seed_nr for _ in range(diff_reps)]

    # Start likelihood ratio method for a different amount of repititions
    for i, rep in enumerate(reps):

        # If given, fix seed
        if seeds:
            np.random.seed(set_seed[i])

        # Generate random normally distrivuted numbers for given repitition
        # determine stock prices and payoffs and calculate (average) deltas
        numbers = np.random.normal(size=rep)
        scores = numbers / (S0 * sigma * math.sqrt(T))
        S = mc.euler_method_vectorized(numbers)
        payoffs = np.where(S - K > 0, 1, 0)
        d = discount * payoffs * scores
        deltas[i] = d.mean()
        std_deltas[i] = payoffs.std() / math.sqrt(rep)

    # Theoretical delta
    bs_deltas = np.ones(diff_reps)
    d2 = (np.log(S0 / K) + (r - 0.5 * sigma ** 2)
            * T) / (sigma * np.sqrt(T))
    num = discount * stats.norm.pdf(d2, 0.0, 1.0)
    den = sigma * S0 * math.sqrt(T)
    bs_deltas = bs_deltas * num / den

    # Determine relative errors
    errors = np.abs(1 - (deltas / bs_deltas))

    if show_plot or save_plot:
        plot_LR(
            reps, errors, std_deltas, option_type, contract,
            set_seed, show_plot, save_plot
            )

    # Save output, if required
    if save_output:
        name = os.path.join(
            "Data", f"{option_type}-{contract}_LR_{set_seed}seed_"
        )
        save_output_ex2(name, K, sigma, deltas, bs_deltas, errors, std_deltas)

    return deltas, bs_deltas, errors, std_deltas

def plot_LR(iterations, errors, std_deltas, option_type, contract, set_seed, show_plot=False, save_plot=False):
    """
    """
    name =  os.path.join(
        "figures",
        "results_{}_{}_LR_{}seed.pdf".format(option_type, contract, set_seed)
        )

    styles = get_N_linestyles(2)
    fig, ax1 = plt.subplots()

    color = "tab:red"
    ax1.set_xlabel("Simulations")
    ax1.set_ylabel("Relative error", color=color)
    ax1.plot(iterations, errors, color=color, linestyle=styles[0], label="error")
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_yscale("log")
    ax1.set_xscale("log")
    ax1.legend

    # Add second plot to figure with shared x axis
    ax2 = ax1.twinx()
    color = "tab:blue"
    ax2.set_ylabel("Standard deviation", color=color)
    ax2.plot(iterations, std_deltas, color=color, linestyle=styles[1], label="std. dev")
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_yscale("log")

    plt.title("Relative error and standard deviation delta with LR method\n({} seed, {} {})".format(set_seed, option_type, contract))

    # Ask matplotlib for the plotted objects and their labels
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2)

    # Otherwise the right y-label is slightly clipped
    fig.tight_layout()

    if show_plot:
        plt.show()

    if save_plot:
        plt.savefig(name, dpi=300)

    plt.close()

def save_output_ex2(name, K, sigma, deltas, bs_deltas, errors, std_deltas):
    """
    """
    np.save(name + f"deltas_K={K}_sigma={sigma}.npy", deltas)
    np.save(name + f"BSdeltas_K={K}_sigma={sigma}.npy", bs_deltas)
    np.save(name + f"errors_K={K}_sigma={sigma}.npy", errors)
    np.save(name + f"deviations_K={K}_sigma={sigma}.npy", std_deltas)


def get_N_HexCol(N=5):
    """
    Generate N distinct colors with help of hsv color scheme.
    https://stackoverflow.com/questions/876853/generating-color-ranges-in-python
    """
    HSV_tuples = [(x / N, 0.5, 0.5) for x in range(N)]
    hex_out = []
    for rgb in HSV_tuples:
        rgb = map(lambda x: int(x * 255), colorsys.hsv_to_rgb(*rgb))
        hex_out.append('#%02x%02x%02x' % tuple(rgb))
    return hex_out

def get_N_linestyles(N=5):
    """
    Generate N different linestyles. Note that similar linestyles appear but if used together with the function get_N_HexCol we yield N colors and linestyles.
    """
    linestyles = list(ls.lineStyles.keys())
    for style in ["", " ", "None"]:
        linestyles.remove(style)
    styles = len(linestyles)
    return [linestyles[style % styles] for style in range(N)]


def monte_carlo_asian(T, S0, K, r, sigma, steps, period=False, reps=100):
    '''
    :param T: time in years
    :param S0: stock price at time = 0
    :param K: sttrike price
    :param r: risk free rate
    :param sigma: volatility
    :param steps: amount of intervals in time
    :param period: time window of asian average pricing in number of steps
    :param reps: amount of repetitions of the monte carlo progress
    :return: option price and list of payoffs
    '''

    # Initialize the monte carlo class
    mc = monte_carlo(steps, T, S0, sigma, r, K)
    payoffs = np.zeros(reps)

    for rep in range(reps):
        # Create wiener process
        mc.wiener_method()

        # Take chucks of periods, or all prices
        if period:
            prices = mc.wiener_price_path[::period]
        else:
            prices = mc.wiener_price_path

        # take the mean of the periods
        mean_price = (sum(prices) / len(prices))
        payoffs[rep] = max(mean_price - mc.K, 0)

    # calculate the price by finding the mean of the payoffs
    option_price = np.mean(payoffs)
    return option_price, payoffs

def control_variance_asian(T=1, S0=100, K=99, r=0.06, sigma=0.2, steps=100, reps=10000):
    '''
    Control variance on the Asian option price, taking geometric averaging as control since we have the
    Black-Scholes price of it. We pridict using a monte-carlo method.
    :param T: time in years
    :param S0: stock price at time = 0
    :param K: sttrike price
    :param r: risk free rate
    :param sigma: volatility
    :param steps: amount of intervals in time
    :param reps: amount of repetitions of the monte carlo progress
    :return: option price and list of payoffs
    '''
    # Initialize classes
    mc = monte_carlo(steps, T, S0, sigma, r, K)
    bs = BlackScholes(T, S0, K, r, sigma, steps)

    # Estimate Rho and get analytical option price
    N = steps
    rho = 0.99
    C_B = bs.asian_call_price()

    # Calculate B from different sigmas
    sigma_mean = sigma / np.sqrt(3)
    sigma_gmean =  sigma * np.sqrt(((N + 1) * (2 * N + 1)) / (6 * N ** 2))

    Beta = (sigma_mean / sigma_gmean) * rho
    payoffs = np.zeros(reps)

    # Repeat monte carlo for #reps times
    for rep in range(reps) :
        # Create wiener process
        mc.wiener_method()

        # Get price path
        prices = mc.wiener_price_path

        # Calculate both geometric mean and normal mean from same price path (Seed)
        mean_price = (sum(prices) / len(prices))
        gmean_price = stats.gmean(prices)

        # Calculate payoff of individual methods
        C_a = max(mean_price - mc.K, 0)
        C_b = max(gmean_price - mc.K, 0)

        # Apply control variance with analytical option price
        payoffs[rep] = C_a - Beta * (C_b - C_B)

    # Option price is equal to the mean of the payoffs
    option_price = np.mean(payoffs)

    return option_price, payoffs

########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################


