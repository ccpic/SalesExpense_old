from pyecharts.charts import Line, Pie, Bar, Geo, Scatter, TreeMap, Page
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
import numpy as np
import json
from django.http import HttpResponse


def response_as_json(data):
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str,
        content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, code=200):
    data = {
        "code": code,
        "msg": "success",
        "data": data,
    }
    return response_as_json(data)


def json_error(error_string="error", code=500, **kwargs):
    data = {
        "code": code,
        "msg": error_string,
        "data": {}
    }
    data.update(kwargs)
    return response_as_json(data)


def line(df, datatype='ABS'):
    axislabel_format = '{value}'
    if datatype in ['SHARE', 'GR']:
        df = df.multiply(100).round(2)
        axislabel_format = '{value}%'
    if df.empty is False:
        line = (
            Line()  # init_opts=opts.InitOpts(width="1200px", height="700px")
                .add_xaxis(df.index.strftime("%Y-%m").tolist())
                .set_global_opts(
                # title_opts=opts.TitleOpts(title='Trend', pos_left='center'),
                legend_opts=opts.LegendOpts(pos_top='5%', pos_left='10%', pos_right='60%'),
                toolbox_opts=opts.ToolboxOpts(is_show=True),
                tooltip_opts=opts.TooltipOpts(trigger='axis',
                                              axis_pointer_type='cross',
                                              ),
                xaxis_opts=opts.AxisOpts(type_='category',
                                         boundary_gap=False,
                                         splitline_opts=opts.SplitLineOpts(is_show=True,
                                                                           linestyle_opts=opts.LineStyleOpts(
                                                                               type_='dotted',
                                                                               opacity=0.5,
                                                                           )
                                                                           )
                                         ),
                yaxis_opts=opts.AxisOpts(type_="value",
                                         axislabel_opts=opts.LabelOpts(formatter=axislabel_format),
                                         # axistick_opts=opts.AxisTickOpts(is_show=True),
                                         splitline_opts=opts.SplitLineOpts(is_show=True,
                                                                           linestyle_opts=opts.LineStyleOpts(
                                                                               type_='dotted',
                                                                               opacity=0.5,
                                                                           )
                                                                           )
                                         ),
            )
        )
        for i, item in enumerate(df.columns):
            line.add_yaxis(item,
                           df[item],
                           # symbol='circle',
                           symbol_size=8,
                           label_opts=opts.LabelOpts(is_show=False),
                           linestyle_opts=opts.LineStyleOpts(width=3),
                           itemstyle_opts=opts.ItemStyleOpts(border_width=1, border_color='', border_color0='white'),
                           )
    else:
        line = (
            Line()
        )

    return line


def stackarea(df, datatype='ABS'):
    axislabel_format = '{value}'
    if datatype in ['SHARE', 'GR']:
        df = df.multiply(100).round(2)
        axislabel_format = '{value}%'

    if df.empty is False:
        stackarea = (
            Line()
                .add_xaxis(df.index.strftime("%Y-%m").tolist())
                .set_global_opts(
                # title_opts=opts.TitleOpts(title='Trend', pos_left='center'),
                legend_opts=opts.LegendOpts(pos_top='5%', pos_left='10%', pos_right='60%'),
                toolbox_opts=opts.ToolboxOpts(is_show=True),
                tooltip_opts=opts.TooltipOpts(trigger='axis',
                                              axis_pointer_type='cross',
                                              ),
                xaxis_opts=opts.AxisOpts(type_='category',
                                         boundary_gap=False,
                                         splitline_opts=opts.SplitLineOpts(is_show=True,
                                                                           linestyle_opts=opts.LineStyleOpts(
                                                                               type_='dotted',
                                                                               opacity=0.5,
                                                                           )
                                                                           )
                                         ),
                yaxis_opts=opts.AxisOpts(type_="value",
                                         max_=df.sum(axis=1).max(),
                                         axislabel_opts=opts.LabelOpts(formatter=axislabel_format),
                                         # axistick_opts=opts.AxisTickOpts(is_show=True),
                                         splitline_opts=opts.SplitLineOpts(is_show=True,
                                                                           linestyle_opts=opts.LineStyleOpts(
                                                                               type_='dotted',
                                                                               opacity=0.5,
                                                                           )
                                                                           )
                                         ),
            )
        )
        for i, item in enumerate(df.columns):
            stackarea.add_yaxis(series_name=item,
                                stack='总量',
                                y_axis=df[item],
                                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                                # symbol_size=8,
                                label_opts=opts.LabelOpts(is_show=False),
                                linestyle_opts=opts.LineStyleOpts(width=3),
                                itemstyle_opts=opts.ItemStyleOpts(border_width=1, border_color='',
                                                                  border_color0='white'),
                                )

    else:
        stackarea = (
            Line()
        )

    return stackarea


def stackarea100(df, datatype='ABS'):
    axislabel_format = '{value}'
    if datatype in ['SHARE', 'GR']:
        df = df.multiply(100).round(2)
        axislabel_format = '{value}%'

    if df.empty is False:
        stackarea = (
            Line()
                .add_xaxis(df.index.strftime("%Y-%m").tolist())
                .set_global_opts(
                # title_opts=opts.TitleOpts(title='Trend', pos_left='center'),
                legend_opts=opts.LegendOpts(pos_top='5%', pos_left='10%', pos_right='60%'),
                toolbox_opts=opts.ToolboxOpts(is_show=True),
                tooltip_opts=opts.TooltipOpts(trigger='axis',
                                              axis_pointer_type='cross',
                                              ),
                xaxis_opts=opts.AxisOpts(type_='category',
                                         boundary_gap=False,
                                         splitline_opts=opts.SplitLineOpts(is_show=True,
                                                                           linestyle_opts=opts.LineStyleOpts(
                                                                               type_='dotted',
                                                                               opacity=0.5,
                                                                           )
                                                                           )
                                         ),
                yaxis_opts=opts.AxisOpts(type_="value",
                                         max_=100,
                                         axislabel_opts=opts.LabelOpts(formatter=axislabel_format),
                                         # axistick_opts=opts.AxisTickOpts(is_show=True),
                                         splitline_opts=opts.SplitLineOpts(is_show=True,
                                                                           linestyle_opts=opts.LineStyleOpts(
                                                                               type_='dotted',
                                                                               opacity=0.5,
                                                                           )
                                                                           )
                                         ),
            )
        )
        for i, item in enumerate(df.columns):
            stackarea.add_yaxis(series_name=item,
                                stack='总量',
                                y_axis=df[item],
                                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                                # symbol_size=8,
                                label_opts=opts.LabelOpts(is_show=False),
                                linestyle_opts=opts.LineStyleOpts(width=3),
                                itemstyle_opts=opts.ItemStyleOpts(border_width=1, border_color='',
                                                                  border_color0='white'),
                                )

    else:
        stackarea = (
            Line()
        )

    return stackarea


def pie_radius(df) -> Pie:
    if df.empty is False:
        x_data = df.index.tolist()
        y_data = df.tolist()
        data_pair = [list(z) for z in zip(x_data, y_data)]
        pie = (
            Pie(init_opts=opts.InitOpts())
                .add(
                series_name="所在科室",
                data_pair=data_pair,
                radius=["50%", "70%"],
                label_opts=opts.LabelOpts(is_show=False, position="center"),
            )
                .set_global_opts(legend_opts=opts.LegendOpts(is_show=False),
                                 toolbox_opts=opts.ToolboxOpts(is_show=True),
                                 )
                .set_series_opts(
                tooltip_opts=opts.TooltipOpts(
                    trigger="item", formatter="{a} <br/>{b}: {c} ({d}%)"
                ),
                label_opts=opts.LabelOpts(is_show=True,
                                          formatter="{b}: {d}%"),
            )
        )
    else:
        pie = (Pie())
    return pie


def bar(df, datatype='ABS', show_label=False, label_rotate=90) -> Bar:
    axislabel_format = '{value}'
    if datatype in ['SHARE', 'GR']:
        df = df.multiply(100).round(2)
        axislabel_format = '{value}%'
    if df.empty is False:
        bar = (
            Bar()
                .add_xaxis(df.index.tolist())
        )
        for i, item in enumerate(df.columns):
            bar.add_yaxis(item,
                          df[item].values.tolist(),
                          label_opts=opts.LabelOpts(is_show=show_label),
                          )
        bar.set_global_opts(
            # title_opts=opts.TitleOpts(title='Trend', pos_left='center'),
            legend_opts=opts.LegendOpts(pos_top='5%', pos_left='10%', pos_right='60%'),
            toolbox_opts=opts.ToolboxOpts(is_show=True),
            tooltip_opts=opts.TooltipOpts(trigger='axis',
                                          axis_pointer_type='cross',
                                          ),
            xaxis_opts=opts.AxisOpts(type_='category',
                                     boundary_gap=True,
                                     axislabel_opts=opts.LabelOpts(rotate=label_rotate),
                                     splitline_opts=opts.SplitLineOpts(is_show=False,
                                                                       linestyle_opts=opts.LineStyleOpts(
                                                                           type_='dotted',
                                                                           opacity=0.5,
                                                                       )
                                                                       )
                                     ),
            yaxis_opts=opts.AxisOpts(type_="value",
                                     axislabel_opts=opts.LabelOpts(formatter=axislabel_format),
                                     # axistick_opts=opts.AxisTickOpts(is_show=True),
                                     splitline_opts=opts.SplitLineOpts(is_show=True,
                                                                       linestyle_opts=opts.LineStyleOpts(
                                                                           type_='dotted',
                                                                           opacity=0.5,
                                                                       )
                                                                       )
                                     ),
        )
    else:
        bar = (Bar())

    return bar


def stackbar(df, df_gr=None, datatype='ABS') -> Bar:
    axislabel_format = '{value}'
    max = df[df > 0].sum(axis=1).max()
    min = df[df <= 0].sum(axis=1).min()
    if datatype in ['SHARE', 'GR']:
        df = df.multiply(100).round(2)
        axislabel_format = '{value}%'
        max = 100
        min = 0
    if df_gr is not None:
        df_gr = df_gr.multiply(100).round(2)
    if df.empty is False:
        stackbar = (
            Bar()
                .add_xaxis(df.index.tolist())
        )
        for i, item in enumerate(df.columns):
            stackbar.add_yaxis(item,
                               df[item].values.tolist(),
                               stack='总量',
                               label_opts=opts.LabelOpts(is_show=False),
                               )
            # .add_yaxis(series_name=df.index[-5].strftime("%Y-%m"),
            #            yaxis_data=df_ya.values.tolist(),
            #            stack='总量',
            #            label_opts=opts.LabelOpts(is_show=False)
            #            )
            # .add_yaxis(series_name=df.index[-1].strftime("%Y-%m")+' vs '+df.index[-5].strftime("%Y-%m"),
            #            yaxis_data=df_diff.values.tolist(),
            #            stack='总量',
            #            label_opts=opts.LabelOpts(is_show=False)
            #            )
        if df_gr is not None:
            stackbar.extend_axis(
                yaxis=opts.AxisOpts(
                    name="同比增长率",
                    type_="value",
                    axislabel_opts=opts.LabelOpts(formatter="{value}%"),
                )
            )
        stackbar.set_global_opts(
            # title_opts=opts.TitleOpts(title='Trend', pos_left='center'),
            legend_opts=opts.LegendOpts(pos_top='5%', pos_left='10%', pos_right='60%'),
            toolbox_opts=opts.ToolboxOpts(is_show=True),
            tooltip_opts=opts.TooltipOpts(trigger='axis',
                                          axis_pointer_type='cross',
                                          ),
            xaxis_opts=opts.AxisOpts(type_='category',
                                     boundary_gap=True,
                                     axislabel_opts=opts.LabelOpts(rotate=90),
                                     splitline_opts=opts.SplitLineOpts(is_show=False,
                                                                       linestyle_opts=opts.LineStyleOpts(
                                                                           type_='dotted',
                                                                           opacity=0.5,
                                                                       )
                                                                       )
                                     ),
            yaxis_opts=opts.AxisOpts(max_=max,
                                     min_=min,
                                     type_="value",
                                     axislabel_opts=opts.LabelOpts(formatter=axislabel_format),
                                     # axistick_opts=opts.AxisTickOpts(is_show=True),
                                     splitline_opts=opts.SplitLineOpts(is_show=True,
                                                                       linestyle_opts=opts.LineStyleOpts(
                                                                           type_='dotted',
                                                                           opacity=0.5,
                                                                       )
                                                                       )
                                     ),
        )
        if df_gr is not None:
            line = (
                Line()
                    .add_xaxis(xaxis_data=df_gr.index.tolist())
                    .add_yaxis(
                    series_name="同比增长率",
                    yaxis_index=1,
                    y_axis=df_gr.values.tolist(),
                    label_opts=opts.LabelOpts(is_show=False),
                    linestyle_opts=opts.LineStyleOpts(width=3),
                    symbol_size=8,
                    itemstyle_opts=opts.ItemStyleOpts(border_width=1, border_color='', border_color0='white'),
                )
            )
    else:
        stackbar = (Bar())

    if df_gr is not None:
        return stackbar.overlap(line)
    else:
        return stackbar


def scatter(df) -> Scatter:
    if df.empty is False:
        scatter = (
            Scatter()
                .add_xaxis(xaxis_data=df['当前月处方量'])
                .add_yaxis(
                series_name=df.index.tolist(),
                y_axis=df['月累计相关病人数'],
                symbol_size=10,
                label_opts=opts.LabelOpts(is_show=False),
            )

        )
        scatter.set_series_opts()
        scatter.set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="value", splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True),
            title_opts=opts.TitleOpts(title="Scatter-基本示例")
        )
    else:
        scatter = (Scatter())
    return scatter


def geo_scatter(df) -> Geo:
    if df.empty is False:
        index = df.max() / df.mean() / 50
        geo = (
            Geo()
                .add_schema(maptype="china")
        )
        for item in df.index:
            l = [[item, df.loc[item]]]
            geo.add(series_name=item,
                    data_pair=l,
                    symbol_size=df.loc[item] / df.mean() / index,
                    )
        geo.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        geo.set_global_opts(toolbox_opts=opts.ToolboxOpts(is_show=True),
                            legend_opts=opts.LegendOpts(is_show=False),
                            tooltip_opts=opts.TooltipOpts(axis_pointer_type='cross'),
                            # visualmap_opts=opts.VisualMapOpts(),
                            # title_opts=opts.TitleOpts(title="Geo-基本示例"),
                            )
    else:
        geo = (
            Geo()
                .add_schema(maptype="china")
        )
    return geo


def bubble(df, yavg=None, symbol_size=1, show_label=True, formatter_y='{value}') -> Scatter:
    if df.empty is False:
        if formatter_y=='{value}%':
            df.iloc[:, 0] = df.iloc[:, 0].multiply(100).round(2)
        index = df.iloc[:, 2].max() / df.iloc[:, 2].mean() / 50

        bubble = (Scatter()
            .add_xaxis(df.iloc[:, 1].values.tolist())
            .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="value",
                name=df.columns[1],
                splitline_opts=opts.SplitLineOpts(is_show=True,
                                                  linestyle_opts=opts.LineStyleOpts(
                                                      type_='dotted',
                                                      opacity=0.5,
                                                  )
                                                  )
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name=df.columns[0],
                axistick_opts=opts.AxisTickOpts(is_show=True),
                axislabel_opts=opts.LabelOpts(formatter=formatter_y),
                splitline_opts=opts.SplitLineOpts(is_show=True,
                                                  linestyle_opts=opts.LineStyleOpts(
                                                      type_='dotted',
                                                      opacity=0.5,
                                                  )
                                                  )
            ),
            toolbox_opts=opts.ToolboxOpts(is_show=True),
            legend_opts=opts.LegendOpts(is_show=False),
            tooltip_opts=opts.TooltipOpts(axis_pointer_type='cross',
                                          formatter='{a}: {c}',
                                          ),
        )
        )
        for i, item in enumerate(df.index):
            l = [np.nan] * i
            l.append(df.ix[item, 0])
            bubble.add_yaxis(series_name=item,
                             y_axis=l,
                             symbol_size=df.ix[item, 2] / df.iloc[:, 2].mean() / index * symbol_size
                             )
        bubble.set_series_opts(label_opts=opts.LabelOpts(is_show=show_label,
                                                         formatter='{a}',
                                                         ),
                               )
        if yavg is not None:
            bubble.set_series_opts(markline_opts=opts.MarkLineOpts(
                is_silent=True,
                symbol=None,
                data=[
                    {"yAxis": yavg},
                ],
                label_opts=opts.LabelOpts(position="end",
                                          formatter='平均'),
            )
            )
    else:
        bubble = (Scatter())

    return bubble


def treemap(d, series_name):
    c = (
        TreeMap()
            .add(series_name, d)
            .set_series_opts(
            label_opts=opts.LabelOpts(position="inside",
                                      font_size=11,
                                      font_weight='lighter',
                                      formatter='{b}\n{c}'
                                      ),
        )
            .set_global_opts(toolbox_opts=opts.ToolboxOpts(is_show=True),
                             legend_opts=opts.LegendOpts(is_show=False),
                             )
    )
    return c
