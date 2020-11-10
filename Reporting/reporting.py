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
    "所在科室": ["心内科", "肾内科", "老干科", "神内科", "内分泌科", "其他科室", "社区医院"],
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
    def filtered(self, filter=None, filter_value=None):
        if filter is not None and filter_value is not None:
            if type(filter_value) is str:
                mask = self[filter] == filter_value
                return self.loc[mask]
            elif type(filter_value) is list:
                mask = self[filter].isin(filter_value)
                return self.loc[mask]
            else:
                return self
        else:
            return self

    # 透视客户数量
    def get_client_number(self, index, filter=None, filter_value=None):
        pivoted = pd.pivot_table(self.filtered(filter, filter_value), values="客户姓名", index=index, aggfunc=len)
        return pivoted

    # 透视客户平均（对可量化指标）
    def get_avg(self, values, index, columns=None, filter=None, filter_value=None, sort_values=True):
        pivoted = pd.pivot_table(
            self.filtered(filter, filter_value), values=values, index=index, columns=columns, aggfunc="mean"
        )
        if sort_values is True:
            pivoted = pivoted.sort_values(by=values, ascending=False)
        return pivoted

    # 透视客户分布（对分类指标）
    def get_dist(self, index, columns, filter=None, filter_value=None, show_perc=False, sort_values=True):
        pivoted = pd.pivot_table(
            self.filtered(filter, filter_value), values="客户姓名", index=index, columns=columns, aggfunc=len
        )

        if columns in D_SORTER:
            pivoted = pivoted[D_SORTER[columns]]  # 列排序

        if sort_values is True:
            s = pivoted.sum(axis=1).sort_values(ascending=False)
            pivoted = pivoted.loc[s.index, :]  # 行按照汇总总和大小排序

        if show_perc is True:
            pivoted = pivoted.div(pivoted.sum(axis=1), axis=0)  # 计算行汇总的百分比

        return pivoted

    # 高中潜客户数占比
    def get_hm_ratio(self, index, filter=None, filter_value=None, sort_values=True):
        potential_dist = self.get_dist(index=index, columns="潜力分级", filter=filter, filter_value=filter_value)
        hm_ratio = (potential_dist["H"] + potential_dist["M"]) / potential_dist.sum(axis=1)
        hm_ratio.name = "H+M潜力用户占比"
        if sort_values is True:
            hm_ratio = hm_ratio.sort_values(ascending=False, index=None, filter=None, filter_value=None)
        return hm_ratio

    # 分类指标分布情况绘图
    def plot_barline_dist(self, index, columns, savefile, filter=None, filter_value=None, width=16, height=5, **kwargs):
        df_bar = self.get_dist(index=index, columns=columns, filter=filter, filter_value=filter_value)
        print(df_bar)
        if columns == "潜力分级":
            df_line = self.get_hm_ratio(
                index, filter=filter, filter_value=filter_value, sort_values=False
            )  # 注意这里不能排序，否则绘图会错位
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

        plot_barline(
            df_bar=df_bar,
            df_line=df_line,
            savefile=savefile,
            y1fmt="{:.0f}",
            y1labelfmt="{:.0f}",
            y2fmt="{:.0%}",
            y2labelfmt="{:.0%}",
            width=width,
            height=height,
        )


if __name__ == "__main__":
    df = pd.read_excel("data.xlsx")
    df = df[df["团队"] == "血压团队"]
    df["地区经理2"] = df["地区经理"] + "(" + df["大区"] + ")"
    print(df)
    mask = df["医院层级"].isin(["旗舰社区", "普通社区"])
    df.loc[mask, "所在科室"] = "社区医院"
    # c = Clientfile(df)
    # c.plot_barline_dist(
    #     index="地区经理2", columns="所在科室", savefile="test.png", tail=20, filter="区域", filter_value=["华东区", "华南区"]
    # )
    data = df["月累计相关病人数"]
    fig, ax = plt.subplots(figsize=(16, 5))
    data.plot(kind="hist", density=True, bins=100)
    data.plot(kind="kde")

    ax.set_xlabel("潜力值（月累计相关病人数）")
    ax.set_xlim(0, 800)
    ax.set_title("客户档案潜力分布")
    # Remove y ticks
    ax.set_yticks([])
    # Relabel the axis as "Frequency"
    ax.set_ylabel("对应潜力客户档案数")
    # Calculate percentiles
    percentiles = []
    for i in range(9):
        percentiles.append([data.quantile((i + 1) / 10), "D" + str(i + 1)])
    # Plot the lines with a loop
    for percentile in percentiles:
        ax.axvline(percentile[0], linestyle=":")
        ax.text(percentile[0], ax.get_ylim()[1] * 0.95, int(percentile[0]))
        ax.text(percentile[0], ax.get_ylim()[1], percentile[1])

    plt.show()
