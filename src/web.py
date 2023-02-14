from flask import Flask, render_template
import os, json
from markupsafe import escape
# from strategy_function.elo_winrate_calculation_handler_by_each_step import EloWinrateCalculationHandlerByEachStep
from strategy_function.win_sum_handler_by_each_step_and_single_agent_in_train import WinSumHandlerByEachStepAndSingleAgentInTrain
from strategy_function.win_rate_handler_by_each_step_in_train import WinSumHandlerByEachStepInTrain
from strategy_function.win_sum_handler_by_each_step_and_single_agent import WinSumHandlerByEachStepAndSingleAgent
from strategy_function.win_sum_handler_by_each_step import WinSumHandlerByEachStep
from strategy_function.win_sum_handler_by_selfplay_agent_iter import WinSumHandlerBySelfplayAgentIter
from strategy_function.win_sum_handler_by_selfplay_agent_iter_elo_value import WinSumHandlerBySelfplayAgentIterEloValue
from strategy_function.win_sum_handler_by_single_agent import WinSumHandlerBySingleAgent
from strategy_function.win_sum_handler import WinSumHandler
from strategy_function.win_sum_handler_by_phase import WinSumHandlerByPhase
from strategy_function.win_sum_handler_winrate import WinSumHandlerWinrate

app = Flask(__name__)
hash_maps = {}

@app.route('/json/<name>')
def func_json(name):
    name = escape(name)
    j = hash_maps[name]
    del hash_maps[name]
    return j

@app.route('/')
def hello_world():
    info = {}
    info["title"] = "测试title"
    info["list"] = []
    info["list"].extend(all_stratepy([]))
    return render_template('template.html', info=info)

@app.route('/data/<name>')
def hello_worlds(name):
    info = {}
    info["title"] = name
    info["list"] = []
    if name == "win_sum_handler_by_single_agent":
        info["list"].extend(WinSumHandlerBySingleAgent().handleRequest(hash_maps))
    # if name == "":

    # info["list"].extend(all_stratepy([]))
    return render_template('template.html', info=info)

def all_stratepy(l):
    # l.extend(WinSumHandlerByPhase().handleRequest(hash_maps))

    # l.extend(WinSumHandler().handleRequest(hash_maps))
    # l.extend(WinSumHandlerWinrate().handleRequest(hash_maps))
    # l.extend(WinSumHandlerBySingleAgent().handleRequest(hash_maps))
    # l.extend(WinSumHandlerBySelfplayAgentIter().handleRequest(hash_maps))
    # l.extend(WinSumHandlerBySelfplayAgentIterEloValue().handleRequest(hash_maps))
    
    # l.extend(WinSumHandlerByEachStep().handleRequest(hash_maps))
    # l.extend(WinSumHandlerByEachStepAndSingleAgent().handleRequest(hash_maps))

    # l.extend(WinSumHandlerByEachStepInTrain().handleRequest(hash_maps))
    
    # l.extend(WinSumHandlerByEachStepAndSingleAgentInTrain().handleRequest(hash_maps))
    
    # l.extend(EloWinrateCalculationHandlerByEachStep().handleRequest(hash_maps))
    return l

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)