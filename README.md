# Stockfish Benchmark

## Compiling Stockfish

```
cd Stockfish/src
make -j build ARCH=x86-64-modern
```

## How to run the benchmark

Usage: 

```
bench.py [-h] -ln LOGNUM -p POSITION -sm {depth,nodes,movetime} -sv SEARCH_VALUE [-d [DEFAULT]] [-hd [HEADER]]
```

Arguments: 
- `-ln/--lognum`*: The number of the log file to use (e.g. "1", "2", or "3")
- `-p/--position`*: The position to use (e.g. "startpos", or a FEN string like "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
- `-sm/--search_mode`*: The search mode to use (e.g. "depth", "nodes", or "movetime")
- `-sv/--search_value`*: The search value to use (e.g. "10", "1000000", or "1000")
- `-d/--default`: This flag indicates that the default benchmark should be run (e.g. "True" or "False")
- `-hd/--header`: This flag indicates that the header should be printed (e.g. "True" or "False")
- `-h/--help`: Show the help message and exit

*Required arguments

Examples:

```
python bench.py -ln 1 -p startpos -sm depth -sv 10
```

```
python bench.py -ln 2 -p rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR -sm nodes -sv 1000000
```

## How Stockfish runs a single iteration

1. Tell the engine to switch to UCI mode
    ```
    uci
    ```
    Engine should respond with
    ```
    id name <name>
    option name <options>
    .
    .
    .
    uciok
    ```

1. Use log file
    ```
    setoption name Debug Log File value "<log-file-name>"
    ```

1. Enable analysis mode
    ```
    setoption name UCI_AnalyseMode value true
    ```

1. Check if engine is ready
    ```
    isready
    ```
    Engine should respond with
    ```
    readyok
    ```
    
1. Create new game
    ```
    ucinewgame
    ```

1. Tell the engine to set the board to the given `<fen-string>`
    ```
    position fen <fen-string>
    ```

1. Search for the next best move up to a certain `<depth-level>`
    ```
    go depth <depth-level>
    ```

1. The engine has finished searching and is sending the bestmove command
    ```
    bestmove g1f3 ponder d8f6
    ```