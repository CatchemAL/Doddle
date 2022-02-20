<img src="https://i.imgur.com/eLnkxkp.png" width="420">


## Features
- **Run** the solver to see how the game is optimally played
- **Solve** a game in realtime using Doddle's solver
- Play a variation of the game where the solver attempts to **hide** the answer from you for as long as possible (inspired by [Absurdle](https://qntm.org/files/absurdle/absurdle.html))
- Play using words of length 4-9 (inclusive) by adding the optional `--size` argument (default is 5).
- Choose your solver using the `--solver=ENTROPY` `--solver=MINIMAX` argument (default is minimax)
- Run deep searches using the depth argument (default is 1)

## Install
![example workflow](https://github.com/CatchemAl/Doddle/actions/workflows/python-app.yml/badge.svg)

`pip install doddle`

## Commands
### Run

```ruby
doddle run --answer=SALTY
doddle run --answer=SPEED --guess=SOLVE
doddle run --answer=FABULOUS --guess=SOLUTION --solver=ENTROPY
doddle run --answer=DEEP --guess=MIND --solver=ENTROPY --depth=2
```

Run a simulation with an answer of your choosing to see how Doddle solves the problem. You can optionally provide your own starting `guess` to see how the game plays out. With every guess, Doddle acquires more information and prunes the list of possible solutions. The output (far right column) shows you how many possible solutions still exist at each step of the solve.

Doddle provides multiple ways to solve the game. You can choose between a **minimax** `solver` (the default), or an **entropy** reduction approach. An entropy based approach optimises for best average play; a minimax approach tries to avoid worst-case scenarios and never goes above 5 moves.

Doddle supports deep searches for all of its solvers 🧠🧠🧠. These are slower, more exhaustive searches for those that want to go deeper. By default, Doddle plays the move that will yield the 'best' outcome on its next turn. In the case of minimax, that means playing the move that will result in the fewest number of possible words to search in the worst-case scenario (it choose a word that **mini**mises the outcome that provides **max**imum uncertainty). In the case of `--solver=ENTROPY`, it plays the move that results in the greatest expected reduction in [Shannon entropy](https://en.wikipedia.org/wiki/Entropy_(information_theory)). With deep searches, it thinks `n` steps ahead. So for `--depth=2`, the minimax solver plays the word that minimses the number of possible solutions in the worst case scenario on the turn after next taking into consideration ***all*** sensible first moves. The performance is still decent - a few seconds per game - but it is noticably slower as the search space explodes exponentially with depth.

<img src="https://i.imgur.com/Al2ucap.png" width="400">

### Solve

```ruby
doddle solve
doddle solve --size=7
doddle solve --guess=RAISE
doddle solve --guess=MIND --solver=ENTROPY
doddle solve --guess=MIND --solver=MINIMAX --depth=2
```

Work smarter not harder. Use Doddle's solver to solve Wordle as fast as possible. If you're playing Wordle and need some... ahem... *divine inspiration*, fire up Doddle's solver. Doddle will give you the optimal word to use. Type the response back into Wordle to generate the next guess. Doddle represents answers as ternary numbers! Doddle uses `2` for exact matches, `1` for partial matches and `0` for unmatched letters (e.g. `10202`).

```
>>> doddle solve --guess=TORCH
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

Half way through a game and just want to know the next best move? Doddle's got you covered. With `solve`, you're not forced to play the move Doddle suggests. Doddle accepts two syntaxes when entering a score: 1) just a score (as above e.g. `20101`); or 2) a `WORD=SCORE` pair (`SNAKE=20100`). If you're half way through and need the best move, fill in what you've done so far using the second input method and let Doddle take over from there.


```
The best guess is SNAIL
Enter score for SNAIL:
>>> SNAKE=20100

The best guess is SALTY
...
```

### Hide
```ruby
doddle hide --guess=SALTY
```
Hide is a spin on the conventional Wordle game. Here, Doddle uses its solver to hide the final answer for as long as possible. Doddle doesn't choose an answer before the game starts - instead it always presents you with the score that results in maximum ambiguity. You'll get there in the end, but the game might take a while. 😈

<img src="https://i.imgur.com/JrMj21n.png" width="350">

Similar to the original Wordle game, a keyboard is rendered to display what characters have been guessed so far.

## Algorithm
Doddle uses a [minimax](https://en.wikipedia.org/wiki/Minimax) algorithm to solve the game. The algorithm:
- is still a work in progress
- is subject to change
- has plenty of scope for improvement (see below!)

## Coming soon
- An `explain` feature to show what the solver is thinking
- A facade layer - for those who want to call a simple API in their code
- Best pair mode - Find the best pair of moves for those who like to take it easy
- Rate my guess - see how your guess compares against the optimal move
- Proper setup of CI/CD and containerisation to check deployment on UNIX based systems
- More algorithms for solving (DNNs or RL)
- Documentation
- More views! For snazzy reporting. e.g.:

Wordle 242 3/6

⬜🟩⬜⬜⬜

⬜🟨⬜⬜⬜

🟩🟩🟩🟩🟩

