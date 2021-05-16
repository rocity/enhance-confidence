# Enhancing Simulator with fancy result plotting

This code simulates accessory enhancing without crons.
It saves how many successful/failed attempts happened for each level.

# Stack

- Python3
- Sqlite3

## How to use

In `main.py`:

1. Run the simulation by uncommenting the line with `runner.simulate(100)`. Change the `100` to a number you want. This is how many simulations the code will run.

2. After the simulation finishes, you can view the results by **commenting** the `runner.simulate(100)` line and **uncommenting** the `runner.analyze()` line.

*note: the simulator saves the result data into a `.sqlite3` file that serves as the database for the program.
