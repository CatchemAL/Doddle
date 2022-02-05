# Nerdle -  _a nerd's approach to solving Wordle_

![alt text](https://github.com/CatchemAl/Nerdle/blob/main/images/Nerdle.png?raw=true)

## Build
![example workflow](https://github.com/CatchemAl/Nerdle/actions/workflows/python-app.yml/badge.svg)

## Features
- **Run** the solver to see how the game is optimally played
- **Solve** the game in realtime using Nerdle's solver
- **Evade** - a variation of the game where the solver attempts to dodge your guesses (inspired by Absurdle)

## Install
- `pip install git+https://github.com/CatchemAl/Nerdle.git`

## Commands
- `nerdle solve --guess=SOARE` (with an optional starting guess)
- `nerdle simulate --solution=BRAIN` (see how the pros solve it)
- `nerdle evade --size=6` (play a devilishly hard game with 6 letters inspired by absurdle)

## Algorithm
- Based on min-max
- Subject to change
- Can be improved
- Is work in progress

## Coming soon
- Change guess in realtime
- **Explain** feature to show what the solver is thinking
- An improved UI (console based) for evade
- Proper setup of CI/CD and containerisation
- Optional search-depth arguments for deep-dive searches
- More algorithms for solving
- MVC architecture
