---
layout: default
title: Proposal
---

### Project Summary
For our project, we are essentially training a Malmo Agent to be Shepherd. The agent will be dropped into an initially flat world and will be faced with a variable amount of sheep to herd. The agent will do this by luring the sheep into a specially designed enclosure. Our AI will take in information about sheep positions and a destination (the corral), and produce a series of actions to bring as many sheep as possible into the corral.

### AI/ML Algorithms
In this project, we are going to try multiple ways to implement the agent policy. Methods including traditional path finding, reinforcement learning, and deep learning will be used in this project. The traditional method can be simply designed as shortest path graph problem. For the reinforcement learning method, the reward will be given when the agent successfully attract sheep and direct sheep to the fence area.

### Evaluation Plan
We will evaluate the quantitative success of our project by counting the number of sheep herded at the final run of the AI, given an initial starting number of sheep and a time limit. The metrics being measured are the number of sheep that remain inside our corral at the end of the run and the amount of time that has passed. The baselines are the sheep, the agent, and the corral/fence holding the sheep. We expect our approach to improve herding by at least 50%. Being able to herd at least 50% of the sheep within our time constraint would be our expected minimum, while the moonshot case would be herding all 100% of the sheep.

The qualitative analysis we will use to verify that our project works will be to see if our agent is able to successfully find sheep and herd it into the corral with direction. It should not be chasing/leading sheep around aimlessly, and after it has herded its last sheep, it should go immediately to find the next sheep instead of walking around randomly. We will visualize the inner workings of our algorithm by starting off with smaller test cases first (ie. large amounts of sheep first to simplify search, simple terrain, large enough corral), and increasing the difficulty once we ensure that our algorithm is doing its job.

<br/><br/>
Appointment with Instructor: Thursday October 24, 5:10pm @ DBH 4204
