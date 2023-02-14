from abc import abstractmethod, ABCMeta
import os
import csv
from collections import OrderedDict
import re
def agent_name_sorted(s1):
    try:
        s = re.findall("\d+",s1)
        return int(s[-1])
    except Exception:
        return 0
class StrategyHandler(metaclass=ABCMeta):

    def find(self, request_name, agent_data_list):
        request_agent_data_list = []
        for agent_data in agent_data_list:
            try:
                agent_data.index(request_name) # 查找失败会直接跳Exception
                request_agent_data_list.append(agent_data)
            except Exception as e:
                pass

        return request_agent_data_list

    def getDataDict(self, path, file_name):
        """*.csv 加载器
        """
        test_data_dict = OrderedDict()
        # path = "./" + "temp/NoSFEloTest(20220423_Original_Version)" + "/"
        dir_list = os.listdir(path)
        dir_list = sorted(dir_list, key=agent_name_sorted)
        for dir_name in dir_list:
            if dir_name != ".git":
                csv_file_path = path + dir_name + '/' + file_name
                if os.path.exists(csv_file_path) == False:
                    continue
                with open(csv_file_path) as f:
                    f_csv = csv.reader(f)
                    f_csv = list(f_csv)
                    test_data_dict[dir_name] = f_csv
                
        return test_data_dict

    def getTrainDataDict(self, path):
        """game_in_fighting_data.csv 加载器
        """
        test_data_dict = OrderedDict()
        # path = "./" + "temp/NoSFEloTest(20220423_Original_Version)" + "/"
        dir_list = os.listdir(path)
        dir_list = sorted(dir_list, key=agent_name_sorted)
        for dir_name in dir_list:
            if dir_name != ".git":
                csv_file_path = path + dir_name + '/game_in_fighting_data.csv'
                if os.path.exists(csv_file_path) == False:
                    continue
                with open(csv_file_path) as f:
                    f_csv = csv.reader(f)
                    f_csv = list(f_csv)
                    test_data_dict[dir_name] = f_csv
                
        return test_data_dict

    def getTestDataDict(self, path):
        """game_in_testing_fighting_data.csv 加载器
        """
        test_data_dict = OrderedDict()
        # path = "./" + "temp/NoSFEloTest(20220423_Original_Version)" + "/"
        dir_list = os.listdir(path)
        dir_list = sorted(dir_list, key=agent_name_sorted)
        for dir_name in dir_list:
            if dir_name != ".git":
                csv_file_path = path + dir_name + '/game_in_testing_fighting_data.csv'
                if os.path.exists(csv_file_path) == False:
                    continue
                with open(csv_file_path) as f:
                    f_csv = csv.reader(f)
                    f_csv = list(f_csv)
                    test_data_dict[dir_name] = f_csv
                
        return test_data_dict

    def getTestDataDictList(self, path_name_list):
        """game_in_testing_fighting_data.csv 加载器
        """
        test_data_dict = OrderedDict()

        for i in range(len(path_name_list)):
            path = "./" + path_name_list[i] + "/"
            dir_list = os.listdir(path)
            dir_list = sorted(dir_list, key=agent_name_sorted)
            for dir_name in dir_list:
                if dir_name != ".git":
                    csv_file_path = path + dir_name + '/game_in_testing_fighting_data.csv'
                    if os.path.exists(csv_file_path) == False:
                        continue
                    with open(csv_file_path) as f:
                        f_csv = csv.reader(f)
                        f_csv = list(f_csv)
                        test_data_dict[dir_name] = f_csv
                
        return test_data_dict

    

    @abstractmethod
    def handleRequest(self, store_dict, request_name="StrategyHandler"):
        pass