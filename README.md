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
Evade is a spin on the conventional Wordle game. Here, Nerdle uses its solver to hide the final answer for as long as possible. Nerdle doesn't choose an answer before the game starts - instead it presents you with a score that results in maximal ambiguity for as long as possible. You'll always get there in the end, but the game might take a while. 😈


## Algorithm
Nerdle uses a [minimax](https://en.wikipedia.org/wiki/Minimax) algorithm to solve the game. The algorithm:
- is still a work in progress
- is subject to change
- has plenty of scope for improvement (see below!)

## Coming soon
- Add an `explain` feature to show what the solver is thinking
- An improved UI (console based) for evade
  - The user needs an interactive keyboard to remember what they've already played
- Proper setup of CI/CD and containerisation
  - To check deployment on UNIX based systems
- Optional search-depth arguments for deep-dive searches
  - Performance needs to be assessed.
  - Hopefully results in interesting pairs of moves.
- More algorithms for solving (DNNs or RL)
- MVC architecture
