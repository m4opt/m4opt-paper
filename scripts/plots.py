"""Matplotlib style customization."""

from matplotlib import pyplot as plt


def customize_style(columns=1):
    if columns == 1:
        target_width = 3.5  # ApJ column size in inches
    else:
        target_width = 7.25  # ApJ two-column text width in inches
    width, height = plt.rcParams["figure.figsize"]
    plt.style.use("seaborn-v0_8-paper")
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = "Times New Roman"
    plt.rcParams['mathtext.fontset'] = 'stix'
    plt.rcParams["figure.figsize"] = (target_width, height * target_width / width)
