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

Run a simulation with an answer of your choosing to see how Nerdle solves the problem. You can optionally provide your own starting `guess` to see how the game plays out. With every guess, Nerdle acquires more information and prunes the list of possible solutions. The output shows you how many possible solutions still exist.

<img src="https://github.com/CatchemAl/Nerdle/blob/main/images/Run.png" width="400">

### Solve

```ruby
nerdle solve --size=5
nerdle solve --guess=RAISE
```

Work smarter not harder. Use Nerdle's solver to solve Wordle as fast as possible. If you're playing Wordle and need some... ahem... *divine inspiration*, fire up Nerdle's solver. Nerdle will give you the optimal word to use. Type the response back into Wordle to generate the next guess. Nerdle represents answers as ternary numbers! Nerdle uses `2` for exact matches, `1` for partial matches and `0` for unmatched letters (e.g. `10202`).

```
>>> nerdle solve --guess=TORCH
Enter score for TORCH:
>>> 10000

The best guess is SNAIL
Enter score for SNAIL:
>>> 20101

The best guess is SALTY
Enter score for SALTY:
>>> 22222

Great success! ✨ 🔮 ✨
```

Half way through a game and just want to know the next best move? Nerdle's got you covered. With `solve`, you're not forced to play the move Nerdle suggests. Nerdle accepts two syntaxes when entering a score: 1) as score (as above e.g. `20101`); or 2) a `WORD=SCORE` pair (`SNAKE=20100`). If you're half way through and need the best move, fill in what you've done so far using the second input method and let Nerdle take over from there.


```
The best guess is SNAIL
Enter score for SNAIL:
>>> SNAKE=20100

The best guess is SALTY
...
```

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
