# Nerdle -  _a nerd's approach to solving Wordle_

<img src="https://github.com/CatchemAl/Nerdle/blob/main/images/Nerdle.png" width="360">

## Build
![example workflow](https://github.com/CatchemAl/Nerdle/actions/workflows/python-app.yml/badge.svg)

## Features
- **Run** the solver to see how the game is optimally played
- **Solve** a game in realtime using Nerdle's solver
- Play a variation of the game where the solver attempts to **evade** your every guess (inspired by [Absurdle](https://qntm.org/files/absurdle/absurdle.html))

## Install
`pip install git+https://github.com/CatchemAl/Nerdle.git`

## Commands
### Run

```ruby
nerdle run --answer=SALTY
nerdle run --answer=SALTY --guess=TORCH
```

Run a simulation with an answer of your choosing to see how Nerdle solves the problem. You can optionally provide your own starting `--guess` to see how the game plays out. With every guess in the game, Nerdle acquires more information and prunes the list of possible solutions. The output shows you how many possible solutions still exist.

<img src="https://github.com/CatchemAl/Nerdle/blob/main/images/Simulate.png" width="510">

### Solve

```ruby
nerdle solve --size=5
nerdle solve --guess=RAISE
```

Work smarter not harder. Use Nerdle's solver to solve Wordle as fast as possible. If you're playing Wordle and need some... ahem... *divine inspiration*, fire up Nerdle's solver. Nerdle will give you the optimal word to use. Type the response back into Wordle to generate the next guess. Nerdle represents answers as ternary numbers! Nerdle uses `2` for exact matches, `1` for partial matches and `0` for unmatched letters (e.g. `10202`).

### Evade
```ruby
nerdle evade --guess=SALTY
```

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
