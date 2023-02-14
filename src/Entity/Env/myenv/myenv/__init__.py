from gym.envs.registration import register

register(
    id = "FightingiceEnv-v0",
    entry_point = "myenv.envs.fightingice_env:FightingiceEnv"
)