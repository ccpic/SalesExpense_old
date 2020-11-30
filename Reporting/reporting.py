import pandas as pd
from Reporting.chart_func import *


# class Clientfile(pd.DataFrame):
#     # This class variable tells Pandas the name of the attributes
#     # that are to be ported over to derivative DataFrames.  There
#     # is a method named `__finalize__` that grabs these attributes
#     # and assigns them to newly created `SomeData`
#     _metadata = ["name"]
#
#     @property
#     def _constructor(self):
#         """This is the key to letting Pandas know how to keep
#         derivative `SomeData` the same type as yours.  It should
#         be enough to return the name of the Class.  However, in
#         some cases, `__finalize__` is not called and `my_attr` is
#         not carried over.  We can fix that by constructing a callable
#         that makes sure to call `__finlaize__` every time."""
#
#         def _c(*args, **kwargs):
#             return Clientfile(*args, **kwargs).__finalize__(self)
#
#         return _c
#
#     def __init__(self, *args, **kwargs):
#         # grab the keyword argument that is supposed to be my_attr
#         self.name = kwargs.pop("name", None)
#         super().__init__(*args, **kwargs)
#
#     def filtered(self, filter=None, filter_value=None):
#         if filter is not None and filter_value is not None:
#             mask = self[filter].isin(filter_value)
#             return self.loc[mask]
#         else:
#             return self
#
#     def report(self, values=None, index=None, aggfunc='mean', filter=None, filter_target=None):
#         pivoted = pd.pivot_table(self, values=values, index=index, aggfunc=aggfunc)  # 数据透视表
#         return pivoted


D_SORTER = {
    "潜力级别": ["H", "M", "L"],
    "科室": ["心内科", "肾内科", "老干科", "神内科", "内分泌科", "其他科室", "社区医院"],
    "医院层级": ["A", "B", "C", "D", "旗舰社区", "普通社区"],
    "职称": ["院长/副院长", "主任医师", "副主任医师", "主治医师", "住院医师", "其他"],
    "IQVIA医院潜力分位": ["D" + str(i + 1) for i in range(9, -1, -1)],
}

D_RENAME = {
    "所在科室": "科室",
    "月累计相关病人数": "潜力",
}


class Clientfile(pd.DataFrame):
    @property
    def _constructor(self):
        return Clientfile._internal_constructor(self.__class__)

    class _internal_constructor(object):
        def __init__(self, cls):
            self.cls = cls

        def __call__(self, *args, **kwargs):
            return self.cls(*args, **kwargs)

        def _from_axes(self, *args, **kwargs):
            return self.cls._from_axes(*args, **kwargs)

    # 根据列名和列值做数据筛选
    def filtered(self, filter=None):
        if filter is not None:
            # https: // stackoverflow.com / questions / 38137821 / filter - dataframe - using - dictionary
            return self[self.isin(filter).sum(1) == len(filter.keys())]
        else:
            return self

    # 透视客户数量
    def get_client_number(self, index, filter=None):
        pivoted = pd.pivot_table(self.filtered(filter), values="客户姓名", index=index, aggfunc=len)
        return pivoted

    # 透视客户平均（对可量化指标）
    def get_avg(self, values, index, columns=None, filter=None, sort_values=True):
        pivoted = pd.pivot_table(self.filtered(filter), values=values, index=index, columns=columns, aggfunc="mean")
        if sort_values is True:
            pivoted = pivoted.sort_values(by=values, ascending=False)
        return pivoted

    # 透视不重复计数（如医院数、代表数）
    def get_unique_count(self, values, index, columns=None, filter=None, sort_values=True):
        pivoted = pd.pivot_table(
            self.filtered(filter), values=values, index=index, columns=columns, aggfunc=lambda x: len(x.unique())
        )

        if sort_values is True:
            s = pivoted.sum(axis=1).sort_values(ascending=False)
            pivoted = pivoted.loc[s.index, :]  # 行按照汇总总和大小排序

        return pivoted

    # 透视客户分布（对分类指标count/len，对量化指标sum）
    def get_dist(self, index, columns, values=None, filter=None, perc=False, sort_values=True):
        if values is None or values == "客户姓名":
            values = "客户姓名"
            aggfunc = len
        else:
            values = values
            aggfunc = sum

        pivoted = pd.pivot_table(self.filtered(filter), values=values, index=index, columns=columns, aggfunc=aggfunc)

        if pivoted.shape[1] == 1 and values == "客户姓名":
            pivoted.columns = ["客户档案"]

        if sort_values is True:
            s = pivoted.sum(axis=1).sort_values(ascending=False)
            pivoted = pivoted.loc[s.index, :]  # 行按照汇总总和大小排序

        if columns in D_SORTER:
            pivoted = pivoted[D_SORTER[columns]]  # # 对于部分变量有固定列排序

        if index in D_SORTER:
            pivoted = pivoted.reindex(D_SORTER[index])  # 对于部分变量有固定排序

        if perc is True:
            pivoted = pivoted.div(pivoted.sum(axis=1), axis=0)  # 计算行汇总的百分比

        return pivoted

    # 取得一对数据客户数和人均潜力
    def get_number_potential(self, index, filter=None, sort_values=True):
        client_number = self.get_client_number(index=index, filter=filter)
        potential = self.get_avg(values="月累计相关病人数", index=index, filter=filter)
        df = pd.concat([client_number, potential], axis=1)
        df.columns = ["客户档案数", "客户平均潜力"]

        df.drop("TBA", inplace=True, errors="ignore")

        if sort_values is True:
            df.sort_values(by="客户档案数", axis=0, ascending=False, inplace=True)

        return df

    # 取得一对数据医院IQVIA潜力和医院档案潜力
    def get_potential_pair(self, filter=None, sort_values=True):
        df_clientfile = self.get_dist(index="医院", columns=None, values="月累计相关病人数", filter=filter)
        df_iqvia = self.get_dist(index="医院", columns=None, values="IQVIA医院潜力", filter=filter)
        df_combined = pd.concat([df_clientfile, df_iqvia], axis=1)
        df_combined = df_combined[(df_combined.T != 0).any()]

        if sort_values is True:
            df.sort_values(by="月累计相关病人数", axis=0, ascending=False, inplace=True)

        return df_combined

    # 高中潜客户数占比
    def get_hm_ratio(self, index, filter=None, sort_values=True):
        potential_dist = self.get_dist(index=index, columns="潜力分级", filter=filter)
        hm_ratio = (potential_dist["H"] + potential_dist["M"]) / potential_dist.sum(axis=1)
        hm_ratio.name = "H+M潜力用户占比"
        if sort_values is True:
            hm_ratio = hm_ratio.sort_values(ascending=False, index=None, filter=None)
        return hm_ratio

    # 汇总KPIs（关于档案数量的部分）
    def get_kpi_number(self, index, filter=None, sort_values=True):
        client_number = self.get_client_number(index=index, filter=filter)
        hosp_number = self.get_unique_count(values="医院", index=index, filter=filter)
        rsp_number = self.get_unique_count(values="负责代表", index=index, filter=filter)
        df = pd.concat([client_number, hosp_number, rsp_number], axis=1)
        df.columns = ["客户档案数", "覆盖医院数", "代表人数"]
        df["平均档案数/每家医院"] = df["客户档案数"] / df["覆盖医院数"]
        df["平均档案数/每位代表"] = df["客户档案数"] / df["代表人数"]
        df = df[["客户档案数", "覆盖医院数", "平均档案数/每家医院", "代表人数", "平均档案数/每位代表"]]
        if sort_values is True:
            df.sort_values(by="客户档案数", axis=0, ascending=False, inplace=True)
        if index in D_SORTER:
            df = df.reindex(D_SORTER[index])  # # 对于部分变量有固定列排序

        return df

    # 汇总KPIs（关于潜力的部分）
    def get_kpi_potential(self, index, filter=None, sort_values=True):
        client_number = self.get_client_number(index=index, filter=filter)
        potential = self.get_avg(values="月累计相关病人数", index=index, filter=filter)
        potential_dist = self.get_dist(index=index, columns="潜力级别", perc=True, filter=filter)
        df = pd.concat([client_number, potential, potential_dist], axis=1)
        print(df)
        df.columns = ["客户档案数", "平均潜力", "H档案比例", "M档案比例", "L档案比例"]
        df["H+M档案比例"] = df["H档案比例"] + df["M档案比例"]
        df = df[["客户档案数", "平均潜力", "H档案比例", "M档案比例", "H+M档案比例"]]
        if sort_values is True:
            df.sort_values(by="客户档案数", axis=0, ascending=False, inplace=True)
        if index in D_SORTER:
            df = df.reindex(D_SORTER[index])  # # 对于部分变量有固定列排序

        return df

    # 分类指标分布情况绘图
    def plot_barline_dist(self, index, columns, values=None, perc=False, filter=None, width=15, height=6, **kwargs):
        df_bar = self.get_dist(index=index, columns=columns, values=values, perc=perc, filter=filter)

        # 如果关注的是潜力分级，则加上高中潜潜力占比的折线图
        if columns == "潜力分级":
            df_line = self.get_hm_ratio(index, filter=filter, sort_values=False)  # 注意这里不能排序，否则绘图会错位
        else:
            df_line = None

        # 项目太多时可选择传参head或tail只出部分output
        if "head" in kwargs and type(kwargs["head"]) is int:
            df_bar = df_bar.head(kwargs["head"])
            if df_line is not None:
                df_line = df_line.head(kwargs["head"])
        elif "tail" in kwargs and type(kwargs["tail"]) is int:
            df_bar = df_bar.tail(kwargs["tail"])
            if df_line is not None:
                df_line = df_line.tail(kwargs["tail"])
        elif "range" in kwargs and type(kwargs["range"]) is list:
            df_bar = df_bar.iloc[kwargs["range"][0] : kwargs["range"][1], :]
            if df_line is not None:
                df_line = df_line.iloc[kwargs["range"][0] : kwargs["range"][1], :]

        # 如果值是份额（百分比）时调整绘图设置
        if values is None:
            values = "档案数"  # 如果透视没设置values，题目为档案数，否则为values
        if columns is None:
            columns = ""
        if perc is True:
            y1fmt = "{:.0%}"
            y1labelfmt = "{:.0%}"
            title = "各%s分%s%s贡献份额" % (index, columns, values)
        else:
            y1fmt = "{:.0f}"
            y1labelfmt = "{:.0f}"
            title = "各%s分%s%s" % (index, columns, values)

        plot_barline(
            df_bar=df_bar,
            df_line=df_line,
            savefile="plots/" + title + ".png",
            title=title,
            y1fmt=y1fmt,
            y1labelfmt=y1labelfmt,
            y2fmt="{:.0%}",
            y2labelfmt="{:.0%}",
            width=width,
            height=height,
        )

    # 分类指标分布情况绘图，分左右2个图，分别为绝对值堆积柱状图和百分百（份额）堆积柱状图
    def plot_twinbar_dist(self):
        pass

    # 量化数据分布和x分位绘图
    def plot_hist_dist(
        self,
        pivoted=False,
        metric="月累计相关病人数",
        index=None,
        show_kde=False,
        show_tiles=False,
        show_metrics=False,
        bins=10,
        tiles=10,
        filter=None,
        xlim=None,
        width=15,
        height=6,
    ):
        if filter is not None:
            df = self.filtered(filter)
        else:
            df = self

        if pivoted is False:
            df = df[metric]
            xlim = [0, 800]
            if show_tiles:
                title = "客户档案潜力%s分位分布" % tiles
            else:
                title = "客户档案潜力分布"
            xlabel = "潜力值（月累计相关病人数）"
        elif pivoted is True:
            df = self.get_dist(index=index, columns=None)
            title = "各%s客户档案上传数量分布" % index
            xlabel = "客户档案数量"
        ylabel = "发生频次"

        plot_hist(
            df=df,
            savefile="plots/" + title + ".png",
            show_kde=show_kde,
            show_tiles=show_tiles,
            show_metrics=show_metrics,
            bins=bins,
            tiles=tiles,
            xlim=xlim,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            width=width,
            height=height,
        )

    # 绘制份额饼图
    def plot_pie_share(self, index, values=None, filter=None, focus=None, series_limit=10, sort_values=True):
        df = self.get_dist(
            index, filter=filter, values=values, columns=None, sort_values=sort_values
        )  # 获取份额数据，只能单列，因此columns=None

        # 以下部分处理当系列过多，多于limit参数时的情况，自动将排名靠后的项归总于其他
        if df.shape[0] > series_limit:
            df2 = df.iloc[:series_limit, :]
            others = df.iloc[series_limit:, :].sum()
            others.name = "其他"
            df2 = df2.append(others)

            # 对于focus的index，如果排序在series_limit之后，强制显示，不归为其他
            if focus is not None:
                found = df2.index.str.contains(focus)
                if sum(found) == 0:
                    df2 = df2.append(df.loc[focus, :])
                    df2.loc["其他", :] = df2.loc["其他", :] - df2.loc[focus, :]

            df2 = df2.iloc[:, 0]
        else:
            df2 = df.iloc[:, 0]

        if values is None:
            values = "档案数"  # 如果透视没设置values，题目为档案数，否则为values
        title = "分%s\n%s份额" % (index, values)
        plot_pie(
            savefile="plots/" + "分%s%s份额" % (index, values) + ".png",
            sizelist=df2,
            labellist=df2.index,
            focus=focus,
            title=title,
        )

    # 绘制KPI综合展示图，以多个指标的横条型图同时展示为主
    def plot_barh_kpi(self, index, dimension, mean_vline=False, filter=None, width=15, height=6, **kwargs):
        if dimension == "number":
            df = self.get_kpi_number(index=index, filter=filter)
            formats = ["{:,.0f}", "{:,.0f}", "{:,.0f}", "{:,.0f}", "{:,.0f}"]
            title = "分%s档案数量相关综合情况" % index
        elif dimension == "potential":
            df = self.get_kpi_potential(index=index, filter=filter)
            formats = ["{:,.0f}", "{:,.0f}", "{:.0%}", "{:.0%}", "{:.0%}"]
            title = "分%s档案潜力相关综合情况" % index

        # 各指标平均值
        if mean_vline:
            mean_value = df.mean()
        else:
            mean_value = None

        # 项目太多时可选择传参head或tail只出部分output
        if "head" in kwargs and type(kwargs["head"]) is int:
            df = df.head(kwargs["head"])
        elif "tail" in kwargs and type(kwargs["tail"]) is int:
            df = df.tail(kwargs["tail"])
        elif "range" in kwargs and type(kwargs["range"]) is list:
            df = df.iloc[kwargs["range"][0] : kwargs["range"][1], :]

        if "fontsize" in kwargs:
            fontsize = kwargs["fontsize"]
        else:
            fontsize = 16

        plot_grid_barh(
            df=df,
            savefile="plots/" + title + ".png",
            formats=formats,
            vline_value=mean_value,
            fontsize=fontsize,
            width=width,
            height=height,
        )

    # 绘制覆盖/潜力散点图
    def plot_bubble_number_potential(
        self, index, filter=None, z_scale=1.00, xlim=None, ylim=None, showLabel=True, labelLimit=15, width=15, height=6,
    ):
        df = self.get_number_potential(index=index, filter=filter)
        x = df.loc[:, "客户档案数"]
        y = df.loc[:, "客户平均潜力"]
        z = x * y
        labels = df.index

        # 平均数分隔线
        xavg = x.mean()
        yavg = y.mean()
        xlabel = "平均档案数:" + "{:,.0f}".format(xavg)
        ylabel = "平均潜力:" + "{:,.0f}".format(yavg)

        title = "%s客户档案数 versus 平均潜力" % index
        xtitle = "客户档案数"
        ytitle = "客户平均潜力（月累计相关病人数）"

        plot_bubble(
            savefile="plots/" + title + ".png",
            width=width,
            height=height,
            x=x,
            y=y,
            z=z,
            z_scale=z_scale,
            labels=labels,
            title=title,
            xtitle=xtitle,
            ytitle=ytitle,
            xfmt="{:,.0f}",
            yfmt="{:,.0f}",
            xlim=xlim,
            ylim=ylim,
            showLabel=showLabel,
            labelLimit=labelLimit,
            xavgline=True,
            xavg=xavg,
            xlabel=xlabel,
            yavgline=True,
            yavg=yavg,
            ylabel=ylabel,
        )

    # 绘制医院潜力和客户档案潜力散点图
    def plot_bubble_potential_pair(
        self, filter=None, z_scale=1.00, xlim=None, ylim=None, showLabel=False, labelLimit=30, width=15, height=6,
    ):
        df = self.get_potential_pair(filter=filter)
        x = np.log(df.loc[:, "IQVIA医院潜力"])
        y = np.log(df.loc[:, "月累计相关病人数"])
        z = [50] * len(x)
        labels = df.index

        title = "IQVIA医院潜力 versus 客户档案医院潜力"
        xtitle = "IQVIA医院潜力（取对数）"
        ytitle = "客户档案医院潜力（取对数）"

        plot_bubble(
            savefile="plots/" + title + ".png",
            width=width,
            height=height,
            x=x,
            y=y,
            z=z,
            z_scale=z_scale,
            labels=labels,
            title=title,
            xtitle=xtitle,
            ytitle=ytitle,
            xfmt="{:,.0f}",
            yfmt="{:,.0f}",
            xlim=xlim,
            ylim=ylim,
            showLabel=showLabel,
            labelLimit=labelLimit,
        )


def cleandata(df):
    df.rename(columns={"所在科室": "科室", "医院全称": "医院", "省/自治区/直辖市": "省份"}, inplace=True)
    df["地区经理"] = df["地区经理"] + "(" + df["大区"] + ")"
    mask = df["医院层级"].isin(["旗舰社区", "普通社区"])
    df.loc[mask, "科室"] = "社区医院"
    mask = df["职称"].isin(["院长", "副院长"])
    df.loc[mask, "职称"] = "院长/副院长"

    return df


if __name__ == "__main__":
    df = pd.read_excel("20201130095848.xlsx")
    df_decile = pd.read_excel("decile.xlsx")
    print(df, df_decile)
    df = pd.merge(df, df_decile.loc[:, ["医院编码", "IQVIA医院潜力", "IQVIA医院潜力分位"]], how="left", on="医院编码")
    df = cleandata(df)

    # 南中国
    df = df[df["南北中国"] == "北中国"]

    # df = df[df["区域"].isin(["华中区"])]
    c = Clientfile(df)

    # P4
    # print(
    #     "档案数：%s" % df.shape[0],  # 共上传多少档案
    #     "地区经理数：%s" % len(df["地区经理"].unique()),  # 多少DSM上传
    #     "代表数数：%s" % len(df["负责代表"].unique()),  # 多少代表上传
    #     "医院数：%s" % len(df["医院"].unique()),  # 覆盖多少医院
    # )
    # P5
    # # 各医院客户档案覆盖数量分布
    # c.plot_hist_dist(
    #     pivoted=True,
    #     index="医院",
    #     bins=50,
    #     show_kde=True,
    #     show_tiles=False,
    #     show_metrics=True,
    #     xlim=[0, 200],
    #     width=6,
    #     height=8,
    # )
    #
    # # 各地区经理客户档案上传数量分布
    # c.plot_hist_dist(
    #     pivoted=True,
    #     index="地区经理",
    #     bins=10,
    #     show_kde=True,
    #     show_tiles=False,
    #     show_metrics=True,
    #     xlim=[0, 700],
    #     width=6,
    #     height=8,
    # )
    #
    # # 各负责代表客户档案上传数量分布
    # c.plot_hist_dist(
    #     pivoted=True,
    #     index="负责代表",
    #     bins=30,
    #     show_kde=True,
    #     show_tiles=False,
    #     show_metrics=True,
    #     xlim=[0, 200],
    #     width=6,
    #     height=8,
    # )
    # P6
    # # 客户档案基本分布情况
    # c.plot_pie_share(index="医院层级")  # 医院层级份额饼图
    # c.plot_pie_share(index="科室", focus="社区医院")  # 科室份额饼图
    # c.plot_pie_share(index="职称")  # 职称份额饼图
    #
    # c.plot_barh_kpi(index="医院层级", dimension="number") # P7分医院层级档案数量相关指标汇总
    # c.plot_barh_kpi(index="IQVIA医院潜力分位", dimension="number") # P8分IQVIA医院潜力分位档案数量相关指标汇总
    # c.plot_barh_kpi(index="科室", dimension="number") # P9分科室档案数量相关指标汇总
    # c.plot_barh_kpi(index="职称", dimension="number") # P10分职称档案数量相关指标汇总
    #
    # c.plot_barh_kpi(index="区域", dimension="number", mean_vline=True) # P11分区域档案数量相关指标汇总
    # c.plot_barh_kpi(index="大区", dimension="number", mean_vline=True) # P12分大区档案数量相关指标汇总
    # # P13-20
    # c.plot_barline_dist(index="大区", columns="医院层级", values=None, perc=False)
    # c.plot_barline_dist(index="大区", columns="医院层级", values=None, perc=True)
    # c.plot_barline_dist(index="大区", columns="IQVIA医院潜力分位", values=None, perc=False)
    # c.plot_barline_dist(index="大区", columns="IQVIA医院潜力分位", values=None, perc=True)
    # c.plot_barline_dist(index="大区", columns="科室", values=None, perc=False)
    # c.plot_barline_dist(index="大区", columns="科室", values=None, perc=True)
    # c.plot_barline_dist(index="大区", columns="职称", values=None, perc=False)
    # c.plot_barline_dist(index="大区", columns="职称", values=None, perc=True)
    # P21-23 各地区经理档案数量相关指标汇总
    # c.plot_barh_kpi(index="地区经理", dimension="number", range=[0, 19], fontsize=12, mean_vline=True)
    # c.plot_barh_kpi(index="地区经理", dimension="number", range=[19, 38], fontsize=12, mean_vline=True)
    # c.plot_barh_kpi(index="地区经理", dimension="number", range=[38, 57], fontsize=12, mean_vline=True)
    #
    # c.plot_hist_dist(pivoted=False, show_kde=True, show_tiles=True, bins=100, tiles=10)  # P25 档案数量十分位分布
    # c.plot_hist_dist(pivoted=False, show_kde=True, show_tiles=True, bins=100, tiles=3)  # P26 档案数量三分位分布
    # # P2
    # c.plot_pie_share(index="潜力级别")  # 潜力饼图
    # c.plot_pie_share(index="潜力级别", values="月累计相关病人数")  # 潜力饼图
    #
    # c.plot_barh_kpi(index="医院层级", dimension="potential")  # P28 分医院层级档案潜力相关指标汇总
    # c.plot_barh_kpi(index="IQVIA医院潜力分位", dimension="potential") # P29 分IQVIA医院潜力分位档案潜力相关指标汇总
    # c.plot_barh_kpi(index="科室", dimension="potential") # P30 分科室档案潜力相关指标汇总
    # c.plot_barh_kpi(index="职称", dimension="potential") # P31 分职称层级档案潜力相关指标汇总
    #
    # c.plot_barh_kpi(index="区域", dimension="potential", mean_vline=True) # P32 分区域层级档案潜力相关指标汇总
    # c.plot_barh_kpi(index="大区", dimension="potential", mean_vline=True) # P33 分大区层级档案潜力相关指标汇总

    # c.plot_barh_kpi(index="医院", dimension="potential", filter={"IQVIA医院潜力分位": ["D10"]}, width=15, heigh=15)
    # c.plot_barh_kpi(index="医院", dimension="potential", filter={"IQVIA医院潜力分位": ["D9"]}, width=15, heigh=8)

    # P34-36 分地区经理层级档案潜力相关指标汇总
    # c.plot_barh_kpi(index="地区经理", dimension="potential", range=[0, 19], fontsize=12, mean_vline=True)
    # c.plot_barh_kpi(index="地区经理", dimension="potential", range=[19, 38], fontsize=12, mean_vline=True)
    # c.plot_barh_kpi(index="地区经理", dimension="potential", range=[38, 57], fontsize=12, mean_vline=True)

    # P38-39 数量 versus 潜力 交叉分析
    # c.plot_bubble_number_potential("大区", z_scale=0.02, labelLimit=100)
    # c.plot_bubble_number_potential("地区经理", z_scale=0.01, labelLimit=100)
    # c.plot_bubble_number_potential("IQVIA医院潜力分位", z_scale=0.02, labelLimit=100)
