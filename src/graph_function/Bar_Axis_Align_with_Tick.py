import demjson, json
def Axis_Align_with_Tick(title: str, xAxis: list, data: list, bar_or_line_type: bool, yMin = 0, yMax = 400) -> json:
    info = r"""
            {
            "title": {
                "text": "ECharts 入门示例"
            },
            "tooltip": {
                "trigger": 'axis',
                "axisPointer": {
                "type": 'shadow'
                }
            },
            "grid": {
                "left": '3%',
                "right": '4%',
                "bottom": '3%',
                "containLabel": "true"
            },
            "xAxis": [
                {
                "type": 'category',
                "data": ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                "axisTick": {
                    "alignWithLabel": "true"
                }
                }
            ],
            "yAxis": [
                {
                "type": 'value',
                min: 0,
                max: 400,
                }
            ],
            "series": [
                {
                "name": 'Direct',
                "type": 'bar',
                "barWidth": '60%',
                "data": [10, 52, 200, 334, 390, 330, 220]
                }
            ]
            }
    """

    info = demjson.decode(info)
    info["title"]["text"] = title
    info["xAxis"][0]["data"] = xAxis

    info["yAxis"][0]["min"] = yMin
    info["yAxis"][0]["max"] = yMax

    info["series"][0]["data"] = data
    info["series"][0]["type"] = "bar" if bar_or_line_type else "line"
    return demjson.encode(info)

Axis_Align_with_Tick("", [], [], True)