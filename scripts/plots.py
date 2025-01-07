"""Matplotlib style customization."""
from matplotlib import pyplot as plt

def customize_style():
    target_width = 3.5  # ApJ column size in inches
    width, height = plt.rcParams["figure.figsize"]
    plt.style.use("seaborn-v0_8-paper")
    plt.rcParams["figure.figsize"] = (target_width, height * target_width / width)
