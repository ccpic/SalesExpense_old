import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns
import matplotlib.font_manager as fm
import numpy as np
import types
from adjustText import adjust_text
import itertools
import matplotlib.cm as cm

mpl.rcParams["font.sans-serif"] = ["SimHei"]
mpl.rcParams["font.serif"] = ["SimHei"]
mpl.rcParams["axes.unicode_minus"] = False
mpl.rcParams.update({"font.size": 16})
sns.set_style("white", {"font.sans-serif": ["simhei", "Arial"]})

myfont = fm.FontProperties(fname="C:/Windows/Fonts/msyh.ttc")

color_dict = {
    "拜阿司匹灵": "navy",
    "波立维": "crimson",
    "泰嘉": "teal",
    "帅信": "darkgreen",
    "帅泰": "olivedrab",
    "倍林达": "darkorange",
    "阿司匹林": "navy",
    "氯吡格雷": "teal",
    "替格瑞洛": "darkorange",
    "国产阿司匹林": "grey",
    "华东区": "navy",
    "华西区": "crimson",
    "华南区": "teal",
    "华北区": "darkgreen",
    "华中区": "darkorange",
    "一线城市": "navy",
    "二线城市": "crimson",
    "三线城市": "teal",
    "四线城市": "darkgreen",
    "五线城市": "darkorange",
    "25MG10片装": "darkgreen",
    "25MG20片装": "olivedrab",
    "75MG7片装": "darkorange",
    "吸入性糖皮质激素(ICS)": "navy",
    "短效β2受体激动剂(SABA)": "crimson",
    "长效β2受体激动剂(LABA)": "tomato",
    "抗白三烯类药物(LTRA)": "teal",
    "黄嘌呤类": "darkorange",
    "长效抗胆碱剂(LAMA)": "darkgreen",
    "短效抗胆碱剂(SAMA)": "olivedrab",
    "LABA+ICS固定复方制剂": "purple",
    "SAMA+SABA固定复方制剂": "deepskyblue",
    "非类固醇类呼吸道消炎药": "saddlebrown",
    "其他": "grey",
    "布地奈德": "navy",
    "丙酸倍氯米松": "crimson",
    "丙酸氟替卡松": "darkorange",
    "环索奈德": "darkgreen",
    "异丙肾上腺素": "grey",
    "特布他林": "navy",
    "沙丁胺醇": "crimson",
    "丙卡特罗": "navy",
    "福莫特罗": "crimson",
    "班布特罗": "darkorange",
    "妥洛特罗": "teal",
    "环仑特罗": "darkgreen",
    "茚达特罗": "purple",
    "孟鲁司特": "navy",
    "普仑司特": "crimson",
    "多索茶碱": "navy",
    "茶碱": "crimson",
    "二羟丙茶碱": "tomato",
    "氨茶碱": "darkorange",
    "复方胆氨": "darkgreen",
    "二羟丙茶碱氯化钠": "teal",
    "复方妥英麻黄茶碱": "olivedrab",
    "复方茶碱麻黄碱": "purple",
    "茶碱,盐酸甲麻黄碱,暴马子浸膏": "saddlebrown",
}

color_list = [
    "navy",
    "crimson",
    "tomato",
    "darkorange",
    "teal",
    "darkgreen",
    "olivedrab",
    "purple",
    "deepskyblue",
    "saddlebrown",
    "grey",
    "cornflowerblue",
    "magenta",
]


def get_cmap(n, name="hsv"):
    """Returns a function that maps each index in 0, 1, ..., n-1 to a distinct
    RGB color; the keyword argument name must be a standard mpl colormap name."""
    return plt.cm.get_cmap(name, n)


def plot_line(
    df,
    savefile,
    colormap="tab10",
    width=12,
    height=5,
    xlabelrotation=0,
    ylabelperc=False,
    title="",
    xtitle="",
    ytitle="",
):
    # Choose seaborn style
    sns.set_style("white")

    # Create a color palette
    # palette = plt.get_cmap(colormap)

    # prepare the plot and its size
    fig, ax = plt.subplots()
    fig.set_size_inches(width, height)

    # Generate the lines
    count = 0
    for column in df:
        markerstyle = "o"
        if column == "泰嘉":
            markerstyle = "D"

        plt.plot(
            df.index,
            df[column],
            color=color_dict[column],
            linewidth=2,
            label=column,
            marker=markerstyle,
            markersize=5,
            markerfacecolor="white",
            markeredgecolor=color_dict[column],
        )

        endpoint = -1
        while isinstance(df.values[endpoint][count], str) or df.values[endpoint][count] == float("inf"):
            endpoint = endpoint - 1
            if abs(endpoint) == len(df.index):
                break
        if abs(endpoint) < len(df.index):
            if df.values[endpoint][count] <= 3:
                plt.text(
                    df.index[endpoint],
                    df.values[endpoint][count],
                    "{:.1%}".format(df.values[endpoint][count]),
                    ha="left",
                    va="center",
                    size="small",
                    color=color_dict[column],
                )

        startpoint = 0
        while isinstance(df.values[startpoint][count], str) or df.values[startpoint][count] == float("inf"):
            startpoint = startpoint + 1
            if startpoint == len(df.index):
                break

        if startpoint < len(df.index):
            if df.values[startpoint][count] <= 3:
                plt.text(
                    df.index[startpoint],
                    df.values[startpoint][count],
                    "{:.1%}".format(df.values[startpoint][count]),
                    ha="right",
                    va="center",
                    size="small",
                    color=color_dict[column],
                )
        count += 1

    # Customize the major grid
    plt.grid(which="major", linestyle=":", linewidth="0.5", color="grey")

    # Rotate labels in X axis as there are too many
    plt.setp(ax.get_xticklabels(), rotation=xlabelrotation, horizontalalignment="center")

    # Change the format of Y axis to 'x%'
    if ylabelperc == True:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: "{:.0%}".format(y)))

    # Add titles
    plt.title(title, fontproperties=myfont, fontsize=18)
    plt.xlabel(xtitle, fontproperties=myfont)
    plt.ylabel(ytitle, fontproperties=myfont)

    # Shrink current axis by 20% and put a legend to the right of the current axis
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), labelspacing=1.5, prop={"family": "SimHei"})

    ymax = ax.get_ylim()[1]
    if ymax > 3:
        ax.set_ylim(ymax=3)

    # Save the figure
    plt.savefig(savefile, format="png", bbox_inches="tight", dpi=600)

    # Close
    plt.clf()
    plt.cla()
    plt.close()


def plot_line_simple(df, savefile, width=15, height=9, xlabelrotation=0, yfmt="{:.0%}", title="", xtitle="", ytitle=""):
    # Choose seaborn style
    sns.set_style("white")

    # prepare the plot and its size
    fig, ax = plt.subplots()
    fig.set_size_inches(width, height)

    # Generate the lines
    for column in df:
        markerstyle = "o"

        plt.plot(
            df.index, df[column], linewidth=2, label=column, marker=markerstyle, markersize=5, markerfacecolor="white"
        )

    # Customize the major grid
    plt.grid(which="major", linestyle=":", linewidth="0.5", color="grey")

    # Rotate labels in X axis as there are too many
    plt.setp(ax.get_xticklabels(), rotation=xlabelrotation, horizontalalignment="center")

    # Change the format of Y axis to 'x%'
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: yfmt.format(y)))

    # Add titles
    plt.title(title, fontproperties=myfont, fontsize=18)
    plt.xlabel(xtitle, fontproperties=myfont)
    plt.ylabel(ytitle, fontproperties=myfont)

    # Shrink current axis by 20% and put a legend to the right of the current axis
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), labelspacing=1, prop={"family": "SimHei"})

    # Save the figure
    plt.savefig(savefile, format="png", bbox_inches="tight", dpi=600)

    # Close
    plt.clf()
    plt.cla()
    plt.close()


def plot_pie(sizelist, labellist, savefile, width=6, height=6, title=None, color_dict=None):
    sns.set_style("white")

    # Prepare the white center circle for Donat shape
    my_circle = plt.Circle((0, 0), 0.7, color="white")

    sizelist = sizelist.transform(lambda x: x / x.sum())
    sizelist_mask = []
    for size in sizelist:
        sizelist_mask.append(abs(size))

    # Draw the pie chart
    wedges, texts, autotexts = plt.pie(
        sizelist_mask,
        labels=labellist,
        autopct="%1.1f%%",
        pctdistance=0.85,
        wedgeprops={"linewidth": 3, "edgecolor": "white"},
        textprops={"family": "Simhei"},
    )

    for i, pie_wedge in enumerate(wedges):
        if color_dict is not None:
            pie_wedge.set_facecolor(color_dict[pie_wedge.get_label()])

        if pie_wedge.get_label() == "泰嘉":
            pie_wedge.set_hatch("//")
        if sizelist[i] < 0:
            pie_wedge.set_facecolor("white")

    for i, autotext in enumerate(autotexts):
        autotext.set_color("white")
        autotext.set_fontsize(10)
        autotext.set_text("{:.1%}".format(sizelist[i]))
        if sizelist[i] < 0:
            autotext.set_color("r")

    # Add title at the center
    plt.text(0, 0, title, horizontalalignment="center", verticalalignment="center", size=20, fontproperties=myfont)

    # Combine circle part and pie part
    fig = plt.gcf()
    fig.set_size_inches(width, height)
    fig.gca().add_artist(my_circle)

    # Save
    plt.savefig(savefile, format="png", bbox_inches="tight", dpi=600)

    # Close
    plt.clf()
    plt.cla()
    plt.close()


def plot_bubble_m(
    x,
    y,
    z,
    labels,
    savefile,
    avggr=None,
    width=12,
    height=5,
    xfmt="{:.0%}",
    yfmt="{:+.0%}",
    ylabel="市场平均\n增长率",
    xavgline=False,
    avgms=None,
    title=None,
    xtitle=None,
    ytitle=None,
    ymin=None,
    ymax=None,
    label_fontsize=16,
    color_dict=None,
):
    fig, ax = plt.subplots()
    fig.set_size_inches(width, height)

    if color_dict == None:
        colors = iter(cm.bwr(np.linspace(0, 1, len(y))))

    if avggr is not None:
        ax.axhline(avggr, linestyle="--", linewidth=1, color="r")
    if xavgline == True:
        ax.axvline(avgms, linestyle="--", linewidth=1, color="r")
    for i in range(len(x)):
        if color_dict == None:
            ax.scatter(x[i], y[i], z[i], color=next(colors), alpha=0.6, edgecolors="black")
        else:
            ax.scatter(x[i], y[i], z[i], color=color_dict[labels[i]], alpha=0.6, edgecolors="black")
    # ax.scatter(x, y, s=z, c=color, alpha=0.6, edgecolors="grey")
    # ax.grid(which='major', linestyle=':', linewidth='0.5', color='black')

    ax.xaxis.set_major_formatter(FuncFormatter(lambda y, _: xfmt.format(y)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: yfmt.format(y)))
    ax.set_ylim([ymin, ymax])

    np.random.seed(0)
    # for i, txt in enumerate(labels):
    #     text = plt.text(x[i],y[i], txt+"\n"+ '('+ str("{:.1%}".format(x[i])) +', ' + str("{:.1%}".format(y[i])) + ')', ha='center', va='center')
    texts = [
        plt.text(
            x[i],
            y[i],
            labels[i],
            ha="center",
            va="center",
            multialignment="center",
            fontproperties=myfont,
            fontsize=label_fontsize,
        )
        for i in range(len(labels))
    ]
    adjust_text(texts, force_text=0.05, arrowprops=dict(arrowstyle="->", color="black"))
    if avggr is not None:
        plt.text(
            ax.get_xlim()[1],
            avggr,
            ylabel + ":\n" + yfmt.format(avggr),
            ha="left",
            va="center",
            color="r",
            multialignment="center",
        )
    if xavgline == True:
        plt.text(
            avgms,
            ax.get_ylim()[1],
            "全国平均\n份额:\n" + xfmt.format(avgms),
            ha="left",
            va="top",
            color="r",
            multialignment="center",
        )

    plt.title(title, fontproperties=myfont, fontsize=20)
    plt.xlabel(xtitle, fontproperties=myfont)
    plt.ylabel(ytitle, fontproperties=myfont)

    # Save
    plt.savefig(savefile, format="png", bbox_inches="tight", transparent=True, dpi=600)

    # Close
    plt.clf()
    plt.cla()
    plt.close()


def plot_bubble(
    x,
    y,
    z,
    avggr,
    labels,
    savefile,
    width=12,
    height=5,
    xfmt="{:.1%}",
    yfmt="{:+.1%}",
    ylabel="市场平均\n增长率",
    xavgline=False,
    avgms=None,
    title=None,
    xtitle=None,
    ytitle=None,
    ymin=None,
    ymax=None,
    fontsize=14,
):
    fig, ax = plt.subplots()
    fig.set_size_inches(width, height)

    ax.axhline(avggr, linestyle="--", linewidth=1, color="r")
    if xavgline == True:
        ax.axvline(avgms, linestyle="--", linewidth=1, color="r")
    for i in range(len(x)):
        ax.scatter(x[i], y[i], z[i], color=color_list[i], alpha=0.6, edgecolors="black")
    # ax.scatter(x, y, s=z, c=color, alpha=0.6, edgecolors="grey")
    # ax.grid(which='major', linestyle=':', linewidth='0.5', color='black')

    ax.xaxis.set_major_formatter(FuncFormatter(lambda y, _: xfmt.format(y)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: yfmt.format(y)))
    ax.set_ylim([ymin, ymax])

    np.random.seed(0)
    # for i, txt in enumerate(labels):
    #     text = plt.text(x[i],y[i], txt+"\n"+ '('+ str("{:.1%}".format(x[i])) +', ' + str("{:.1%}".format(y[i])) + ')', ha='center', va='center')
    texts = [
        plt.text(
            x[i],
            y[i],
            labels[i] + "\n" + "(" + str(xfmt.format(x[i])) + ", " + str(yfmt.format(y[i])) + ")",
            ha="center",
            va="center",
            multialignment="center",
            fontproperties=myfont,
            fontsize=fontsize,
        )
        for i in range(len(labels))
    ]
    adjust_text(texts, force_text=0.05, arrowprops=dict(arrowstyle="->", color="black"))
    plt.text(
        ax.get_xlim()[1],
        avggr,
        ylabel + ":\n" + yfmt.format(avggr),
        ha="left",
        va="center",
        color="r",
        multialignment="center",
        fontproperties=myfont,
        fontsize=fontsize,
    )
    if xavgline == True:
        plt.text(
            avgms,
            ax.get_ylim()[1],
            "全国平均\n份额:\n" + xfmt.format(avgms),
            ha="left",
            va="top",
            color="r",
            multialignment="center",
            fontproperties=myfont,
            fontsize=fontsize,
        )

    plt.title(title, fontproperties=myfont, fontsize=20)
    plt.xlabel(xtitle, fontproperties=myfont)
    plt.ylabel(ytitle, fontproperties=myfont)

    # Save
    plt.savefig(savefile, format="png", bbox_inches="tight", transparent=True, dpi=600)

    # Close
    plt.clf()
    plt.cla()
    plt.close()


def plot_dual_line(
    df1,
    df2,
    savefile,
    colormap="tab10",
    width=14,
    height=8,
    xlabelrotation=0,
    title1=None,
    xtitle1=None,
    ytitle1=None,
    title2=None,
    xtitle2=None,
    ytitle2=None,
):
    # Choose seaborn style
    sns.set_style("white")

    # Create a color palette
    # palette = plt.get_cmap(colormap)

    # prepare the plot and its size
    fig = plt.figure(figsize=(width, height), facecolor="white")

    # Generate the lines of df1
    ax = plt.subplot(1, 2, 1)
    count = 0
    for i, column in enumerate(df1):
        markerstyle = "o"
        if column == "泰嘉":
            markerstyle = "D"

        plt.plot(
            df1.index,
            df1[column],
            color=color_list[i],
            linewidth=2,
            label=column,
            marker=markerstyle,
            markersize=5,
            markerfacecolor="white",
            markeredgecolor=color_list[i],
        )

        endpoint = -1
        while np.isnan(df1.values[endpoint][count]) or df1.values[endpoint][count] == float("inf"):
            endpoint = endpoint - 1
            if abs(endpoint) == len(df1.index):
                break
        if abs(endpoint) < len(df1.index):
            if df1.values[endpoint][count] <= 3:
                plt.text(
                    df1.index[endpoint],
                    df1.values[endpoint][count],
                    "{:.1%}".format(df1.values[endpoint][count]),
                    ha="left",
                    va="center",
                    size="small",
                    color=color_list[i],
                )

        startpoint = 0
        while np.isnan(df1.values[startpoint][count]) or df1.values[startpoint][count] == float("inf"):
            startpoint = startpoint + 1
            if startpoint == len(df1.index):
                break

        if startpoint < len(df1.index):
            if df1.values[startpoint][count] <= 3:
                plt.text(
                    df1.index[startpoint],
                    df1.values[startpoint][count],
                    "{:.1%}".format(df1.values[startpoint][count]),
                    ha="right",
                    va="center",
                    size="small",
                    color=color_list[i],
                )
        count += 1

    # Customize the major grid
    plt.grid(which="major", linestyle=":", linewidth="0.5", color="grey")

    # Rotate labels in X axis as there are too many
    plt.setp(ax.get_xticklabels(), rotation=xlabelrotation, horizontalalignment="center")

    # Change the format of Y axis to 'x%'
    ax.yaxis.set_major_formatter(plt.NullFormatter())

    # Add titles
    plt.title(title1, fontproperties=myfont, fontsize=18)
    plt.xlabel(xtitle1, fontproperties=myfont)
    plt.ylabel(ytitle1, fontproperties=myfont)

    ax = plt.subplot(1, 2, 2)
    count = 0
    for i, column in enumerate(df2):
        markerstyle = "o"
        if column == "泰嘉":
            markerstyle = "D"

        plt.plot(
            df2.index,
            df2[column],
            color=color_list[i],
            linewidth=2,
            label=column,
            marker=markerstyle,
            markersize=5,
            markerfacecolor="white",
            markeredgecolor=color_list[i],
        )

        endpoint = -1
        while np.isnan(df2.values[endpoint][count]) or df2.values[endpoint][count] == float("inf"):
            endpoint = endpoint - 1
            if abs(endpoint) == len(df2.index):
                break
        if abs(endpoint) < len(df2.index):
            if df2.values[endpoint][count] <= 3:
                plt.text(
                    df2.index[endpoint],
                    df2.values[endpoint][count],
                    "{:+.1%}".format(df2.values[endpoint][count]),
                    ha="left",
                    va="center",
                    size="small",
                    color=color_list[i],
                )

        startpoint = 0
        while np.isnan(df2.values[startpoint][count]) or df2.values[startpoint][count] == float("inf"):
            startpoint = startpoint + 1
            if startpoint == len(df2.index):
                break

        if startpoint < len(df2.index):
            if df2.values[startpoint][count] <= 3:
                plt.text(
                    df2.index[startpoint],
                    df2.values[startpoint][count],
                    "{:+.1%}".format(df2.values[startpoint][count]),
                    ha="right",
                    va="center",
                    size="small",
                    color=color_list[i],
                )
        count += 1

    # Customize the major grid
    plt.grid(which="major", linestyle=":", linewidth="0.5", color="grey")

    # Rotate labels in X axis as there are too many
    plt.setp(ax.get_xticklabels(), rotation=xlabelrotation, horizontalalignment="center")

    # Change the format of Y axis to 'x%'
    ax.yaxis.set_major_formatter(plt.NullFormatter())

    # Add titles
    plt.title(title2, fontproperties=myfont, fontsize=18)
    plt.xlabel(xtitle2, fontproperties=myfont)
    plt.ylabel(ytitle2, fontproperties=myfont)

    # Shrink current axis by 20% and put a legend to the right of the current axis
    # box = ax.get_position()
    # ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc="center left", bbox_to_anchor=(1.1, 0.5), labelspacing=1, prop={"family": "SimHei"})

    # ymax = ax.get_ylim()[1]
    # if ymax > 3:
    #     ax.set_ylim(ymin=-1, ymax=3)

    # Save the figure
    plt.savefig(savefile, transparent=True, format="png", bbox_inches="tight", dpi=600)

    # Close
    plt.clf()
    plt.cla()
    plt.close()


def plot_bar_line(
    x,
    y_bar,
    y_line1,
    y_line2,
    savefile,
    y_bar_label,
    y_line1_label,
    y_line2_label,
    width=14,
    height=8,
    unit="(亿)",
    title=None,
    ymin=0,
    ymax=None,
):

    fig, ax = plt.subplots()
    fig.set_size_inches(width, height)
    ax2 = ax.twinx()  # Create another axes that shares the same x-axis as ax.

    ax.bar(x, y_bar, color="teal", width=15, label=y_bar_label)
    ax2.plot(
        x, y_line1, color="crimson", label=y_line1_label, linewidth=3, marker="o", markersize=9, markerfacecolor="white"
    )
    ax2.plot(
        x, y_line2, color="orange", label=y_line2_label, linewidth=3, marker="o", markersize=9, markerfacecolor="white"
    )
    ax2.set_ylim(ymin, ymax)
    ax.set_ylabel("滚动年销售额" + unit)
    ax2.set_ylabel("同比增长率")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: "{:,.1f}".format(y)))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda y, _: "{:+.0%}".format(y)))

    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc=2)

    ax.grid(which="major", axis="both", linestyle=":", linewidth="1", color="grey")

    plt.title(title, fontproperties=myfont, fontsize=20)

    plt.savefig(savefile, transparent=True, format="png", bbox_inches="tight", dpi=600)


def plot_barline(
    df_bar,
    savefile,
    df_line=None,
    stacked=True,
    width=15,
    height=6,
    y1fmt="{:.0%}",
    y1labelfmt="{:.0%}",
    y2fmt="{:.0%}",
    y2labelfmt="{:.0%}",
    title=None,
    xtitle=None,
    ytitle=None,
):

    ax = df_bar.plot(kind="bar", stacked=stacked, figsize=(width, height), alpha=0.8, edgecolor="black")

    plt.title(title, fontproperties=myfont, fontsize=18)
    plt.xlabel(xtitle, fontproperties=myfont)
    plt.ylabel(ytitle, fontproperties=myfont)

    plt.legend(loc="center left", bbox_to_anchor=(1.0, 0.5))
    # plt.setp(ax.get_xticklabels(), rotation=0, horizontalalignment='center')

    # ax.xaxis.set_major_formatter(FuncFormatter(lambda y, _: xfmt.format(y)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: y1fmt.format(y)))
    # ax.set_ylim([ymin, ymax])

    # Add value label
    labels = []
    for j in df_bar.columns:
        for i in df_bar.index:
            label = str(df_bar.loc[i][j])
            labels.append(label)

    patches = ax.patches

    for label, rect in zip(labels, patches):
        height = rect.get_height()
        if height > 0.015:
            x = rect.get_x()
            y = rect.get_y()
            width = rect.get_width()
            ax.text(
                x + width / 2.0,
                y + height / 2.0,
                y1labelfmt.format(float(label)),
                ha="center",
                va="center",
                color="white",
                fontproperties=myfont,
                fontsize=10,
            )

    if df_line is not None:

        # 增加次坐标轴
        ax2 = ax.twinx()

        ax2.plot(
            df_line.index,
            df_line.values,
            label=df_line.name,
            color="crimson",
            linewidth=2,
            marker="o",
            markersize=3,
            markerfacecolor="white",
        )

        for i in range(len(df_line)):
            plt.text(
                x=df_line.index[i],
                y=df_line[i],
                s=y2labelfmt.format(float(df_line[i])),
                ha="center",
                va="bottom",
                size="small",
                color="crimson",
            )

        # 次坐标轴标签格式
        ax2.yaxis.set_major_formatter(FuncFormatter(lambda y, _: y2fmt.format(y)))

        # 合并图例
        bars, labels = ax.get_legend_handles_labels()
        lines, labels2 = ax2.get_legend_handles_labels()
        plt.legend(bars + lines, labels + labels2, loc="center left", bbox_to_anchor=(1.0, 0.5))
        ax.get_legend().remove()

    # Save the figure
    plt.savefig(savefile, format="png", bbox_inches="tight", transparent=True, dpi=600)

    # Close
    plt.clf()
    plt.cla()
    plt.close()


def refine_outlier(df, column, upper_threshold):

    index_list = df.index.tolist()
    for i, idx in enumerate(index_list):
        if df.loc[idx, column] > upper_threshold:
            if column == "Product_n":
                index_list[i] = idx + " 商品数：" "{:.1f}".format((df.loc[idx, column])) + "!!!"
            elif column == "GR":
                index_list[i] = idx + " 增长率：" "{:.0%}".format((df.loc[idx, column])) + "!!!"
    df.index = index_list
    df.loc[df[column] > upper_threshold, column] = upper_threshold

    return df
