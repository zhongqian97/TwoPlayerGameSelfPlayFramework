pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# pip install -e ./Entity/Env/gym_fightingice
pip install -e ./Entity/Env/myenv
# pip install -e ./

pip install ray==1.7.1 dm-tree==0.1.6 ray[rllib]==1.7.1 aiohttp==3.7.4

pip install gym===0.15.3 py4j==0.10.9.5 port-for==0.6.2 opencv-python==4.2.0.34
pip install ipython==7.32.0 joblib==1.1.0
pip install matplotlib==3.1.1 numpy==1.21.5 pandas==1.3.5 pytest==7.1.1 psutil==5.9.0 
pip install scipy==1.7.3 seaborn==0.8.1 tensorflow==1.15 tqdm==4.63.0 torch==1.3.1

pip install opencv-python-headless==4.2.0.34
pip install aioredis==1.3.1

pip install flask demjson
export RAY_OBJECT_STORE_ALLOW_SLOW_STORAGE=1
