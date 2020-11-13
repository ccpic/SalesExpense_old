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
        if values is None:
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

        print(pivoted)
        return pivoted

    # 取得一对数据客户数和人均潜力
    def get_number_potential(self, index, filter=None, sort_values=True):
        client_number = self.get_client_number(index=index, filter=filter)
        potential = self.get_avg(values="月累计相关病人数", index=index, filter=filter)
        df = pd.concat([client_number, potential], axis=1)
        df.columns = ["客户档案数", "客户平均潜力"]

        df.drop('TBA', inplace=True)

        if sort_values is True:
            df.sort_values(by="客户档案数", axis=0, ascending=False, inplace=True)

        return df

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

        return df

    # 分类指标分布情况绘图
    def plot_barline_dist(
        self, savefile, index, columns, values=None, perc=False, filter=None, width=15, height=6, **kwargs
    ):
        df_bar = self.get_dist(index=index, columns=columns, values=values, perc=perc, filter=filter)

        if columns == "潜力分级":
            df_line = self.get_hm_ratio(index, filter=filter, sort_values=False)  # 注意这里不能排序，否则绘图会错位
        else:
            df_line = None

        # 项目太多时可选择传参head或tail只出部分output
        if "head" in kwargs and type(kwargs["head"]) is int:
            df_bar = df_bar.head(kwargs["head"])
            if df_line is not None:
                df_line = df_line.head(kwargs["head"])
        if "tail" in kwargs and type(kwargs["tail"]) is int:
            df_bar = df_bar.tail(kwargs["tail"])
            if df_line is not None:
                df_line = df_line.tail(kwargs["tail"])

        # 如果值是份额（百分比）时调整绘图设置
        if values is None:
            values = "档案数"  # 如果透视没设置values，题目为档案数，否则为values
        if columns is None:
            columns = ""
        if perc is True:
            y1fmt = "{:.0%}"
            y1labelfmt = "{:.0%}"
            title = "各%s%s%s贡献份额" % (index, columns, values)
        else:
            y1fmt = "{:.0f}"
            y1labelfmt = "{:.0f}"
            title = "各%s%s%s" % (index, columns, values)

        plot_barline(
            df_bar=df_bar,
            df_line=df_line,
            savefile=savefile,
            title=title,
            y1fmt=y1fmt,
            y1labelfmt=y1labelfmt,
            y2fmt="{:.0%}",
            y2labelfmt="{:.0%}",
            width=width,
            height=height,
        )

    # 量化数据分布和x分位绘图
    def plot_hist_dist(self, savefile, metric="月累计相关病人数", tiles=10, filter=None, width=15, height=6):
        if filter is not None:
            df = self.filtered(filter)
        else:
            df = self
        df = df[metric]

        if metric == "月累计相关病人数":
            xlim = [0, 800]
            title = "客户档案潜力%s分位分布" % tiles
            xlabel = "潜力值（月累计相关病人数）"
            ylabel = "对应潜力客户档案数"

        plot_hist(
            df=df,
            savefile=savefile,
            tiles=tiles,
            xlim=xlim,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            width=width,
            height=height,
        )

    # 绘制份额饼图，如有负值（如负净增长）则绘制对应的条形图
    def plot_share(self, savefile, index, values=None, filter=None, focus=None, series_limit=10, sort_values=True):
        df = self.get_dist(index, filter=filter, columns=None, sort_values=sort_values)  # 获取份额数据，只能单列，因此columns=None

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
        plot_pie(savefile=savefile, sizelist=df2, labellist=df2.index, focus=focus, title=title)

    # 绘制KPI综合展示图，以多个指标的横条型图同时展示为主
    def plot_barh_kpi(self, savefile, index, dimension, filter=None, width=15, height=6, **kwargs):
        if dimension == "number":
            df = c.get_kpi_number(index=index, filter=filter)
            formats = ['{:,.0f}', '{:,.0f}','{:,.0f}','{:,.0f}','{:,.0f}']
        elif dimension == "potential":
            df = c.get_kpi_potential(index=index, filter=filter)
            formats = ['{:,.0f}','{:,.0f}', '{:.0%}', '{:.0%}', '{:.0%}']

        # 项目太多时可选择传参head或tail只出部分output
        if "head" in kwargs and type(kwargs["head"]) is int:
            df = df.head(kwargs["head"])
        if "tail" in kwargs and type(kwargs["tail"]) is int:
            df = df.tail(kwargs["tail"])

        if "fontsize" in kwargs:
            fontsize = kwargs['fontsize']
        else:
            fontsize = 16

        plot_grid_barh(df=df, savefile=savefile, formats=formats, fontsize=fontsize, width=width, height=height)


if __name__ == "__main__":
    df = pd.read_excel("data.xlsx")
    df.rename(columns={"所在科室": "科室", "医院全称": "医院"}, inplace=True)
    df = df[df["团队"] == "血压团队"]
    df = df[df["区域"].isin(["华中区"])]
    df["地区经理2"] = df["地区经理"] + "(" + df["大区"] + ")"

    mask = df["医院层级"].isin(["旗舰社区", "普通社区"])
    df.loc[mask, "科室"] = "社区医院"
    c = Clientfile(df)
    # c.plot_barline_dist(
    #     index="大区", columns="科室", values=None, savefile="test.png", perc=False, filter={"区域": ["华东区", "华南区"]}
    # )
    # c.plot_hist_dist("test.png", tiles=3)
    # print(c.plot_share("潜力级别"))
    # c.plot_share(savefile="test.png",index="科室", focus="社区医院")
    # c.plot_barline_dist(
    #     index="大区", values="月累计相关病人数", columns="医院层级", savefile="test.png", perc=True
    # )

    # c.plot_barh_kpi(savefile="test.png", index="大区", dimension="potential")
    df = c.get_number_potential(index="负责代表")
    x = df.loc[:,'客户档案数']
    y = df.loc[:,'客户平均潜力']
    z = x*y
    labels = df.index
    plot_bubble(
        savefile = "test.png",
        x=x,
        y=y,
        z=z,
        z_scale=0.01,
        labels=labels,
        title=None,
        xtitle=None,
        ytitle=None,
        xfmt="{:,.0f}",
        yfmt="{:,.0f}",
        labelLimit=200,
        # xlim=xlim,
        # ylim=ylim,
        # showLabel=showLabel,
        # labelLimit=labelLimit,
    )