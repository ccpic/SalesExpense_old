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
import matplotlib.gridspec as gridspec
from pandas.api.types import is_numeric_dtype

mpl.rcParams["font.sans-serif"] = ["SimHei"]
mpl.rcParams["font.serif"] = ["SimHei"]
mpl.rcParams["axes.unicode_minus"] = False
mpl.rcParams.update({"font.size": 16})
sns.set_style("white", {"font.sans-serif": ["simhei", "Arial"]})

myfont = fm.FontProperties(fname="C:/Windows/Fonts/msyh.ttc")

COLOR_DICT = {
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

COLOR_LIST = ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD", "#8C564B", "#E377C2"]


# COLOR_LIST = [
#     "navy",
#     "crimson",
#     "tomato",
#     "darkorange",
#     "teal",
#     "darkgreen",
#     "olivedrab",
#     "purple",
#     "deepskyblue",
#     "saddlebrown",
#     "grey",
#     "cornflowerblue",
#     "magenta",
# ]


def save_plot(path):
    # Save the figure
    plt.savefig(path, format="png", bbox_inches="tight", transparent=True, dpi=600)
    print(path + " has been saved...")

    # Close
    plt.clf()
    plt.cla()
    plt.close()


def get_cmap(n, name="hsv"):
    """Returns a function that maps each index in 0, 1, ..., n-1 to a distinct
    RGB color; the keyword argument name must be a standard mpl colormap name."""
    return plt.cm.get_cmap(name, n)


def plot_grid_barh(df, savefile, formats, fontsize=16, width=15, height=6):
    fig = plt.figure(figsize=(width, height), facecolor="white")

    gs = gridspec.GridSpec(1, df.shape[1])  # 布局为1行多列
    gs.update(wspace=0, hspace=0)  # grid各部分之间紧挨，space设为0.

    for i in range(df.shape[1]):
        ax = plt.subplot(gs[i])
        df_bar = df.iloc[:, i]

        ax = df_bar.plot(kind="barh", alpha=0.8, color=COLOR_LIST[i], edgecolor="black", zorder=3)
        for j, v in enumerate(df_bar.values):
            ax.text(v / 2, j, formats[i].format(v), ha="center", va="center", color="white", fontsize=fontsize)
            ax.axhline(j - 0.5, color="grey", linestyle="--", linewidth=0.5)  # 添加间隔线

        ax.invert_yaxis()  # 翻转y轴，最上方显示排名靠前的序列

        # 删除x,y轴所有的刻度标签，只保留最左边一张图的y轴刻度标签
        if i > 0:
            ax.set_yticklabels([])
        ax.set_xticklabels([])

        ax.set_xlabel(df.columns[i], fontproperties=myfont, fontsize=14)  # x轴标题为df的列名
        ax.xaxis.set_label_position("top")  # x轴标题改为在图表上方
        ax.yaxis.label.set_visible(False)  # 删除y轴标题

    # Save the figure
    save_plot(savefile)


def plot_hist(
    df, savefile, bins=100, has_kde=False, has_tiles=True, tiles=10, xlim=None, title=None, xlabel=None, ylabel=None, width=16, height=5
):
    fig, ax = plt.subplots(figsize=(width, height))
    df.plot(kind="hist", density=True, bins=bins, ax=ax)
    if has_kde:
        ax_new = ax.twinx()
        df.plot(kind="kde", ax=ax_new, color='darkorange')
        ax_new.get_legend().remove()
        ax_new.set_yticks([])  # 删除y轴刻度
        ax_new.set_ylabel(None)

    if xlim is not None:
        ax.set_xlim(xlim[0], xlim[1])  # 设置x轴显示limit

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_yticks([])  # 删除y轴刻度
    ax.set_ylabel(ylabel)

    # 添加百分位信息
    if has_tiles is True:

        # 计算百分位数据
        percentiles = []
        for i in range(tiles):
            percentiles.append([df.quantile((i) / tiles), "D" + str(i + 1)])  # 十分位Decile

        # 在hist图基础上绘制百分位
        for i, percentile in enumerate(percentiles):
            ax.axvline(percentile[0], color="crimson", linestyle=":")  # 竖分隔线
            ax.text(percentile[0], ax.get_ylim()[1] * 0.97, int(percentile[0]), ha="center", color="crimson", fontsize=10)
            if i < tiles - 1:
                ax.text(
                    percentiles[i][0] + (percentiles[i + 1][0] - percentiles[i][0]) / 2,
                    ax.get_ylim()[1],
                    percentile[1],
                    ha="center",
                )
            else:
                ax.text(
                    percentiles[tiles - 1][0] + (ax.get_xlim()[1] - percentiles[tiles - 1][0]) / 2,
                    ax.get_ylim()[1],
                    percentile[1],
                    ha="center",
                )

    # 添加均值、中位数等信息
    median = np.median(df.values) # 计算中位数
    mean = np.mean(df.values) # 计算平均数

    if median > mean:
        yindex_median = 0.95
        yindex_mean = 0.9
        pos_median = "left"
        pos_mean = "right"
    else:
        yindex_mean = 0.95
        yindex_median = 0.9
        pos_median = "right"
        pos_mean = "left"

    ax.axvline(median, color="crimson", linestyle=":")
    ax.text(median, ax.get_ylim()[1] * yindex_median, "中位数："+ str(int(median)), ha=pos_median, color="crimson")


    ax.axvline(mean, color="purple", linestyle=":")
    ax.text(mean, ax.get_ylim()[1] * yindex_mean, "平均数："+ str(int(mean)), ha=pos_mean, color="purple")

    # Save the figure
    save_plot(savefile)


def plot_line(
    df,
    savefile,
    colormap="tab10",
    width=15,
    height=6,
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
            color=COLOR_DICT[column],
            linewidth=2,
            label=column,
            marker=markerstyle,
            markersize=5,
            markerfacecolor="white",
            markeredgecolor=COLOR_DICT[column],
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
                    color=COLOR_DICT[column],
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
                    color=COLOR_DICT[column],
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
    save_plot(savefile)


def plot_line_simple(df, savefile, width=15, height=6, xlabelrotation=0, yfmt="{:.0%}", title="", xtitle="", ytitle=""):
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
    save_plot(savefile)


def plot_barh(
    df,
    savefile,
    stacked=True,
    width=15,
    height=6,
    xfmt="{:.0f}",
    yfmt="{:.0%}",
    labelfmt="{:.0%}",
    title=None,
    xtitle=None,
    ytitle=None,
    ymin=None,
    ymax=None,
    haslegend=True,
):
    colors = []
    for item in df.columns.tolist():
        colors.append(COLOR_DICT[item])
    ax = df.plot(kind="barh", stacked=stacked, figsize=(width, height), alpha=0.8, edgecolor="black", color=colors)
    plt.title(title, fontproperties=myfont, fontsize=18)
    plt.xlabel(xtitle, fontproperties=myfont)
    plt.ylabel(ytitle, fontproperties=myfont)
    plt.axvline(x=0, linewidth=2, color="r")

    if haslegend == True:
        plt.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), prop=myfont, fontsize=12)
    else:
        plt.legend(prop=myfont)

    # plt.setp(ax.get_xticklabels(), rotation=0, horizontalalignment='center')
    #
    # ax.xaxis.set_major_formatter(FuncFormatter(lambda y, _: xfmt.format(y)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: yfmt.format(y)))
    # ax.set_ylim([ymin, ymax])

    # Add value label
    labels = []
    for j in df.columns:
        for i in df.index:
            label = str(df.loc[i][j])
            labels.append(label)

    patches = ax.patches

    for label, rect in zip(labels, patches):
        height = rect.get_height()
        if height > 0.015:
            x = rect.get_x()
            y = rect.get_y()
            width = rect.get_width()
            if abs(width) < 3000000:
                color = "black"
            else:
                color = "white"
            ax.text(
                x + width / 2.0,
                y + height / 2.0,
                labelfmt.format(float(label)),
                ha="center",
                va="center",
                color=color,
                fontproperties=myfont,
                fontsize=10,
            )

    # Save the figure
    save_plot(savefile)


def plot_pie(savefile, sizelist, labellist, focus, title):
    # sns.set_style("white")

    # Prepare the white center circle for Donat shape
    my_circle = plt.Circle((0, 0), 0.7, color="white")

    sizelist = sizelist.transform(lambda x: x / x.sum())
    print(sizelist)
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
        counterclock=False,
        startangle=90,
    )

    for i, pie_wedge in enumerate(wedges):
        # pie_wedge.set_facecolor(COLOR_DICT[pie_wedge.get_label()])

        if focus is not None:
            if pie_wedge.get_label() == focus:
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
    fig.set_size_inches(6, 6)
    fig.gca().add_artist(my_circle)

    # Save the figure
    save_plot(savefile)


def plot_bubble(
    savefile,
    width,
    height,
    x,
    y,
    z,
    labels,
    title,
    xtitle,
    ytitle,
    z_scale=1,
    xfmt="{:.0%}",
    yfmt="{:+.0%}",
    yavgline=False,
    yavg=None,
    ylabel="",
    xavgline=False,
    xavg=None,
    xlabel="",
    ylim=None,
    xlim=None,
    showLabel=True,
    labelLimit=15,
):

    fig, ax = plt.subplots()
    fig.set_size_inches(width, height)

    if ylim is not None:
        ax.set_ylim(ymin=ylim[0], ymax=ylim[1])
    if xlim is not None:
        ax.set_xlim(xmin=xlim[0], xmax=xlim[1])

    cmap = mpl.colors.ListedColormap(np.random.rand(256, 3))
    colors = iter(cmap(np.linspace(0, 1, len(y))))

    for i in range(len(x)):
        ax.scatter(x[i], y[i], z[i] * z_scale, color=next(colors), alpha=0.6, edgecolors="black")
    if yavgline == True:
        ax.axhline(yavg, linestyle="--", linewidth=1, color="r")
    if xavgline == True:
        ax.axvline(xavg, linestyle="--", linewidth=1, color="r")
    # ax.scatter(x, y, s=z, c=color, alpha=0.6, edgecolors="grey")
    # ax.grid(which='major', linestyle=':', linewidth='0.5', color='black')

    ax.xaxis.set_major_formatter(FuncFormatter(lambda y, _: xfmt.format(y)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: yfmt.format(y)))

    np.random.seed(0)
    # for i, txt in enumerate(labels):
    #     text = plt.text(x[i],y[i], txt+"\n"+ '('+ str("{:.1%}".format(x[i])) +', ' + str("{:.1%}".format(y[i])) + ')', ha='center', va='center')
    if showLabel is True:
        texts = [
            plt.text(
                x[i],
                y[i],
                labels[i],
                ha="center",
                va="center",
                multialignment="center",
                fontproperties=myfont,
                fontsize=10,
            )
            for i in range(len(labels[:labelLimit]))
        ]
        adjust_text(texts, force_text=0.1, arrowprops=dict(arrowstyle="->", color="black"))

    if yavgline == True:
        plt.text(
            ax.get_xlim()[1],
            yavg,
            ylabel,
            ha="left",
            va="center",
            color="r",
            multialignment="center",
            fontproperties=myfont,
            fontsize=10,
        )
    if xavgline == True:
        plt.text(
            xavg,
            ax.get_ylim()[1],
            xlabel,
            ha="left",
            va="top",
            color="r",
            multialignment="center",
            fontproperties=myfont,
            fontsize=10,
        )

    plt.title(title, fontproperties=myfont)
    plt.xlabel(xtitle, fontproperties=myfont, fontsize=12)
    plt.ylabel(ytitle, fontproperties=myfont, fontsize=12)

    # Save the figure
    save_plot(savefile)


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
            color=COLOR_LIST[i],
            linewidth=2,
            label=column,
            marker=markerstyle,
            markersize=5,
            markerfacecolor="white",
            markeredgecolor=COLOR_LIST[i],
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
                    color=COLOR_LIST[i],
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
                    color=COLOR_LIST[i],
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
            color=COLOR_LIST[i],
            linewidth=2,
            label=column,
            marker=markerstyle,
            markersize=5,
            markerfacecolor="white",
            markeredgecolor=COLOR_LIST[i],
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
                    color=COLOR_LIST[i],
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
                    color=COLOR_LIST[i],
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
    save_plot(savefile)


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

    # Save the figure
    save_plot(savefile)


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
    save_plot(savefile)


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
