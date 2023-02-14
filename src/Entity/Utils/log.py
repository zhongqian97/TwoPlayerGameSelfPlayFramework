import csv
import os
class Logger():

    def __init__(self, csv_file_path, csv_str):
        self.csv_file_path = csv_file_path
        self.csv_str = csv_str

    def exists(self):
        return os.path.exists(self.csv_file_path)

    def log_append(self, csv_str):
        f = open(self.csv_file_path, 'a')
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(csv_str)
        f.close()

    def log(self, maps=None, mode='a'):
        """maps为空为初始化，mode默认为追加写入
        """
        if maps == None:
            if self.exists():
                return
            f = open(self.csv_file_path, 'w')
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow(self.csv_str)
            f.close()
            return
        
        f = open(self.csv_file_path, mode)
        writer = csv.writer(f, lineterminator='\n')
        csv_list = []
        for key in self.csv_str:
            try:
                csv_list.append(maps[key])
            except Exception:
                csv_list.append(None)
        writer.writerow(csv_list)
        f.close()
        pass

    def list_log(self, lists=None, mode='a'):
        for maps in lists:
            self.log(maps=maps, mode=mode)
        pass