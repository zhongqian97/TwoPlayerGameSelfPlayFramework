import demjson, json

def data_json(name="", data=[]) -> dict:
    info = r"""
    {
        name: 'Search Engine',
        type: 'line',
        label: {
            show: true,
            position: 'top'
        },
        areaStyle: {},
        emphasis: {
            focus: 'series'
        },
        data: [820, 932, 901, 934, 1290, 1330, 1320]
    }
    """
    # info = r"""
    # {
    #     name: 'Search Engine',
    #     type: 'line',
    #     stack: 'Total',
    #     label: {
    #         show: true,
    #         position: 'top'
    #     },
    #     areaStyle: {},
    #     emphasis: {
    #         focus: 'series'
    #     },
    #     data: [820, 932, 901, 934, 1290, 1330, 1320]
    # }
    # """
    info = demjson.decode(info)
    info["name"] = name
    info["data"] = data
    return info


def stacked_area_chart(title: str, xAxis: list, agent_name_list: list, data: list, yMin = 0, yMax = 400) -> json:
    info = r"""
            {
            title: {
                text: 'Stacked Area Chart'
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                type: 'cross',
                label: {
                    backgroundColor: '#6a7985'
                }
                }
            },
            legend: {
                data: ['Email', 'Union Ads', 'Video Ads', 'Direct', 'Search Engine']
            },
            toolbox: {
                feature: {
                saveAsImage: {}
                }
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: [
                {
                type: 'category',
                boundaryGap: false,
                data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                }
            ],
            yAxis: [
                {
                type: 'value'
                }
            ],
            series: []
            }
        """
    info = demjson.decode(info)
    info["title"]["text"] = title
    info["xAxis"][0]["data"] = xAxis
    info["legend"]["data"] = agent_name_list

    # info["yAxis"][0]["min"] = yMin
    # info["yAxis"][0]["max"] = yMax

    data_list = []
    for i in range(len(agent_name_list)):
        data_list.append(data_json(name=agent_name_list[i], data=data[i]))

    info["series"] = data_list
    return demjson.encode(info)