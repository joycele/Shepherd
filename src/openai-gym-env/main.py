import gym
from SheepHerder import SheepHerderEnvironment

env = SheepHerderEnvironment()
env.reset()

for _ in range(6000):
	env.render()
	env.step(env.action_space.sample())

env.close()