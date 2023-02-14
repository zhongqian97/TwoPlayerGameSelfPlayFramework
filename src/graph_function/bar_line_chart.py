import demjson, json

def bar_line_chart(title: str, xAxis: list, data: list, bar_or_line_type: bool) -> json:
    info = r"""
            {
            "title": {
                "text": "ECharts 入门示例"
            },
            "xAxis": {
                "type": "category",
                "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            },
            "yAxis": {
                "type": "value"
            },
            "series": [
                {
                "data": [150, 230, 224, 218, 135, 147, 260],
                "type": "bar"
                }
            ]
            }
        """
    info = json.loads(info)
    info["title"]["text"] = title
    info["xAxis"]["data"] = xAxis
    info["series"][0]["data"] = data
    info["series"][0]["type"] = "bar" if bar_or_line_type else "line"
    return json.dumps(info)