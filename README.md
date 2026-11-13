#  2048 AI Solver

An AI-powered implementation of the classic **2048 puzzle game** using **Expectimax search** and a heuristic evaluation function.

The project models 2048 as a search problem where the player makes deterministic moves while the environment introduces random tiles.

---

##  Project Objective

The objective of this project is to build an AI agent that can play 2048 automatically by:

- Representing the board as a state
- Generating legal successor states
- Evaluating board states using a heuristic function
- Searching future states using **Expectimax**
- Handling random tile generation using **chance nodes**
- Selecting the move with the highest expected value

The approach is based on concepts from **Adversarial Search / Game Playing in Artificial Intelligence**, including:

- State-space search
- Depth-limited search
- Evaluation functions
- Chance nodes
- Expected utility
- Expectimax

---

##  Game Overview

2048 is played on a **4 × 4 grid**.

The player can move all tiles in four directions:

-  Up
-  Down
-  Left
-  Right

When two tiles with the same value collide, they merge into a tile with twice their value.

After every successful move, a new random tile is added to an empty position:

- `2` with probability **0.9**
- `4` with probability **0.1**

The objective is to create the **2048 tile** while achieving the highest possible score.

---

#  AI Approach

The game is represented as a search problem.

## State

A state is the current **4 × 4 board configuration**.

For example:

```text
2   4   8   0
0   2   4   0
0   0   2   0
0   0   0   0
```

Each different board configuration represents a different state.

---

## Actions

The AI can choose from four possible actions:

```text
LEFT
RIGHT
UP
DOWN
```

Only moves that actually change the board are considered legal moves.

---

## Successor Function

For each legal action, the resulting board is generated.

For example:

```text
Current State
      ↓
   Move Left
      ↓
New Board State
```

The AI evaluates these possible successor states to determine which move is most promising.

---

## Terminal Test

A state is considered terminal when there are **no legal moves remaining**.

At this point, the game is over.

---

#  Expectimax Search

2048 is different from deterministic games such as Chess because the environment introduces randomness.

After the AI makes a move, a random tile is placed on the board.

Therefore, the search tree contains both:

- **MAX nodes**
- **CHANCE nodes**

---

## MAX Node

At a MAX node, the AI chooses the action with the highest evaluation.

```text
              MAX
          /    |    |    \
       LEFT   UP  RIGHT  DOWN
```

The AI assumes that it can choose the best available action.

---

## CHANCE Node

After the AI makes a move, the environment randomly places a tile.

The chance node considers the possible random outcomes.

```text
                    CHANCE
                 /     |     \
              Cell 1  Cell 2  Cell 3
                |        |       |
              2 / 4    2 / 4   2 / 4
```

For each empty cell:

```text
P(2) = 0.9
P(4) = 0.1
```

The expected value of the chance node is calculated from these probabilities.

---

## Expectimax Flow

The overall search can be represented as:

```text
              Current Board
                    │
                    ▼
                  MAX
          ┌─────────┼─────────┐
          ▼         ▼         ▼
        Move 1    Move 2    Move 3
          │         │         │
          ▼         ▼         ▼
       CHANCE    CHANCE    CHANCE
          │         │         │
          ▼         ▼         ▼
     Random Tile Random Tile Random Tile
          │         │         │
          └─────────┼─────────┘
                    ▼
              Evaluate States
                    │
                    ▼
              Expected Value
                    │
                    ▼
              Select Best Move
```

---

#  Heuristic Evaluation Function

Searching until the end of the game is computationally expensive.

Therefore, the AI searches to a fixed depth and evaluates the resulting board states using a heuristic function.

The current heuristic considers:

- Empty cells
- Smoothness
- Monotonicity
- Merge potential
- Maximum tile
- Corner placement of the maximum tile

The evaluation is a weighted combination of these features.

---

## Current Evaluation Function

The current implementation uses:

```text
Evaluation =
    270 × Empty Cells
  + 18 × Smoothness
  + 8 × Monotonicity
  + 32 × Merge Potential
  + 14 × Maximum Tile
  + Corner Bonus
```

The maximum tile is represented using:

```text
log2(max_tile)
```

If the maximum tile is located in a corner, an additional corner bonus is applied.

---

## Current Heuristic Weights

| Feature | Weight |
|---|---:|
| Empty cells | 270 |
| Smoothness | 18 |
| Monotonicity | 8 |
| Merge potential | 32 |
| Maximum tile | 14 |
| Corner bonus | `2.5 × max_log` |

These weights are **problem-specific** and are not universal optimal values.

They can be improved through systematic experimentation.

---

#  Heuristic Features

## 1. Empty Cells

The number of empty cells is rewarded because having more empty positions gives the AI more space to make future moves.

```text
More empty cells
       ↓
More available moves
       ↓
Lower probability of getting stuck
```

---

## 2. Smoothness

Smoothness measures how similar neighboring tile values are.

A smoother board generally makes it easier to combine tiles.

---

## 3. Monotonicity

Monotonicity measures whether tile values generally increase or decrease along rows or columns.

This encourages organized board structures.

---

## 4. Merge Potential

This feature rewards boards where tiles have opportunities to merge.

A board with many possible merges can provide more useful future moves.

---

## 5. Maximum Tile

The largest tile on the board is also considered by the evaluation function.

The implementation uses:

```text
log2(max_tile)
```

instead of directly using the raw tile value.

---

## 6. Corner Bonus

The AI gives an additional bonus when the largest tile is positioned in a corner.

This encourages keeping the largest tile in a stable position.

---

#  Search Depth

The current AI uses:

```python
ai_depth = 3
```

The search depth controls how far the AI looks ahead.

A larger depth can potentially improve decision-making, but it also increases computational cost because the AI must consider many possible random tile placements.

The current implementation therefore uses a fixed-depth search.

---

#  Algorithm Flow

```text
Start Game
     │
     ▼
Create 4 × 4 Board
     │
     ▼
Add Two Random Tiles
     │
     ▼
Check Legal Moves
     │
     ▼
Generate Possible Player Moves
     │
     ▼
Run Expectimax
     │
     ├── MAX Node
     │      │
     │      └── Generate legal moves
     │
     └── CHANCE Node
            │
            ├── Find empty cells
            ├── Generate 2 with probability 0.9
            └── Generate 4 with probability 0.1
     │
     ▼
Evaluate Leaf States
     │
     ▼
Calculate Expected Values
     │
     ▼
Select Best Move
     │
     ▼
Execute Move
     │
     ▼
Generate Random Tile
     │
     ▼
Check Win / Game Over
     │
     └──────────────► Repeat
```

---

#  Main Components

| Function / Class | Purpose |
|---|---|
| `new_board()` | Creates an empty 4 × 4 board |
| `add_random_tile()` | Adds a random `2` or `4` |
| `compress_and_merge()` | Performs tile compression and merging |
| `move_board()` | Generates the board after a move |
| `available_moves()` | Finds all legal moves |
| `board_heuristic()` | Calculates the heuristic evaluation |
| `expectimax()` | Performs Expectimax search |
| `choose_best_move()` | Selects the best move |
| `Game2048` | Handles game state, AI control and GUI |

---

#  User Interface

The game includes a graphical interface implemented using **Pygame**.

The interface displays:

- Current score
- Highest tile
- Number of moves
- Search depth
- Last AI move
- Current game status
- 2048 board

---

## Controls

| Control | Action |
|---|---|
| `↑` | Move Up |
| `↓` | Move Down |
| `←` | Move Left |
| `→` | Move Right |

The interface also provides:

| Button | Function |
|---|---|
| **Start AI** | Starts automatic AI gameplay |
| **Step** | Performs one AI move |
| **Restart** | Starts a new game |

---

#  AI Concepts Demonstrated

This project demonstrates several important Artificial Intelligence concepts:

- State representation
- State-space search
- Successor generation
- Game playing
- Depth-limited search
- Cutoff evaluation
- Heuristic evaluation
- Weighted evaluation functions
- Chance nodes
- Probability
- Expected utility
- Expectimax search
- Stochastic environments

The overall concept is:

```text
State
  ↓
Generate Actions
  ↓
Generate Successor States
  ↓
Search
  ↓
Handle Random Outcomes
  ↓
Evaluate States
  ↓
Calculate Expected Values
  ↓
Choose Best Action
```

---

#  Requirements

The project requires:

- Python 3.x
- Pygame

Install Pygame using:

```bash
pip install pygame
```

---

#  How to Run

Clone or download the project.

Then run:

```bash
python 2048_ai_solver.py
```

The Pygame window will open.

You can either:

1. Play the game manually using the arrow keys.
2. Start the AI using the **Start AI** button.
3. Use **Step** to allow the AI to make one move at a time.

---

#  Project Structure

```text
2048-AI-Solver/
│
├── 2048_ai_solver.py
└── README.md
```

---

#  Performance Evaluation

Because 2048 contains randomness, the AI can produce different results in different games.

Therefore, evaluating the AI using only one game is not sufficient.

A better evaluation method is to run multiple independent games and measure:

- Win rate
- Average score
- Maximum tile achieved
- Average number of moves
- Average computation time per move

For example:

```text
Run 100 Games
      │
      ├── Win Rate
      ├── Average Score
      ├── Maximum Tile
      ├── Average Moves
      └── Average Time / Move
```

This provides a more reliable measure of AI performance.

---

#  Future Improvements

The current implementation provides a foundation for further experimentation.

## 1. Heuristic Weight Optimization

The current heuristic weights can be experimentally optimized.

Instead of assuming that the current weights are optimal:

```text
Generate Weight Set
        ↓
Run Multiple Games
        ↓
Measure Performance
        ↓
Keep Better Weights
        ↓
Generate New Candidates
        ↓
Repeat
```

Possible evaluation metrics include:

- Win rate
- Average score
- Average maximum tile

---

## 2. Additional Evaluation Features

The heuristic can be extended with additional features such as:

- Positional board weighting
- Snake-like tile arrangement
- Mobility
- Additional merge opportunities
- Dangerous board configurations
- Edge concentration

These features should be tested experimentally to determine whether they actually improve performance.

---

## 3. Adaptive Search Depth

Instead of always using depth 3, the search depth could depend on the current board.

For example:

```text
Many empty cells
       ↓
Shallower search

Few empty cells
       ↓
Deeper search
```

This allows more computation to be used when the board becomes more difficult.

---

## 4. Move Ordering

Moves could first be evaluated using a shallow search.

The most promising moves could then be searched more deeply.

This can potentially reduce unnecessary computation.

---

## 5. Experimental Comparison

Different versions of the AI can be compared:

```text
Version 1
Basic Expectimax
        ↓
Version 2
Optimized Heuristic Weights
        ↓
Version 3
Additional Evaluation Features
        ↓
Version 4
Adaptive Search Depth
        ↓
Version 5
Improved Search + Optimized Heuristic
```

Each version can be evaluated over multiple independent games.

---

#  Limitations

The current AI does **not guarantee** that it will always reach 2048.

The main reasons are:

1. Tile generation is random.
2. The search is depth-limited.
3. The heuristic is only an approximation of board quality.
4. The current weights are not guaranteed to be optimal.
5. Deeper Expectimax searches increase computational cost significantly.

Therefore, the objective is to maximize the probability of achieving strong game states rather than guaranteeing a win for every possible random sequence.

---

#  Relation to Adversarial Search

The project follows the general game-playing framework:

```text
State
  ↓
Actions
  ↓
Successor States
  ↓
Search
  ↓
Evaluation
```

For deterministic games, algorithms such as **Minimax** can be used.

When random events are introduced, **chance nodes** can be incorporated into the search tree.

For 2048:

```text
Player Action
      ↓
     MAX
      ↓
Random Tile
      ↓
    CHANCE
      ↓
New Board
      ↓
     MAX
      ↓
    ...
```

This makes 2048 a practical example of search in a **stochastic environment**.

---

#  Project Goal

The long-term goal of this project is to investigate how different:

- Heuristic features
- Feature weights
- Search depths
- Search strategies

affect the performance of an AI playing 2048.

Rather than assuming that one heuristic or one set of weights is optimal, the project can be extended into a systematic experimental study.

---
