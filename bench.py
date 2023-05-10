import sys
import argparse
import re

import engine

STARTPOS = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
TWOMOVES = 'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1'

# Check if FEN string is valid
def is_valid_fen(fen):
    t,c=s.split("/"),s.count;P=p=9;o=0
    for x in"pqrnb":p-=max(0,c(x)-o);P-=max(0,c(x.upper())-o);o+=o<2
    v=8==len(t)and all(8==sum(int(x)for x in re.sub("[A-z]","1",p))for p in t)and p>0<P and c('k')==c('K')==1
    return v

# Convert string to boolean
def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

# Preprocess FEN string
def str2fen(v):
    if v == 'startpos':
        return STARTPOS
    if is_valid_fen(v):
        return v
    else:
        raise argparse.ArgumentTypeError('FEN value expected.')

if __name__ == '__main__':
    # Parse input arguments
    p = argparse.ArgumentParser(description='Stockfish benchmark', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    p.add_argument('-ln', '--lognum',       required=True,              type=int,       help='Log file number')
    p.add_argument('-p', '--position',      required=True,              type=str2fen,   help='Position (in FEN format)')
    p.add_argument('-sm', '--search_mode',  required=True,              type=str,       help='Search mode', choices=['depth','nodes','movetime'])
    p.add_argument('-sv', '--search_value', required=True,              type=int,       help='Search value')
    p.add_argument('-d', '--default',       default=False, const=True,  type=str2bool,  help='Use default benchmark', nargs='?')
    p.add_argument('-hd', '--header',       default=True, const=True,   type=str2bool,  help='Use result header', nargs='?')

    global args
    args = p.parse_args()

    # enable analysis mode
    ops = [('UCI_AnalyseMode', 'True')]

    # create engine
    e = engine.Engine('{}'.format(args.lognum), './Stockfish/src/stockfish', def_bench=args.default, li_options_uci=ops, log=True)

    if not args.default:
        # print header
        if args.header:
            print('Search strategy:\tdepth\tseldepth\tscore\tnodes\t\ttime\tbestmove\tpv')

        # set position string


        # set search string
        search = '{} {}'.format(args.search_mode, args.search_value)

        # start new game
        e.uci_newgame()

        # set position
        if e.ready_ok() and e.position(STARTPOS):

            # do search
            resp = e.go(search, timeout=100000)

            # parse response
            split = resp[-2].split(' ')
            depth = int(split[split.index('depth') + 1])
            seldepth = int(split[split.index('seldepth') + 1])
            score = int(split[split.index('score') + 2])
            total_nodes = int(split[split.index('nodes') + 1])
            total_time = int(split[split.index('time') + 1])
            bestmove = split[split.index('pv') + 1]
            pv = ' '.join(split[split.index('pv') + 1:])

            print('{}:\t\t{}\t{}\t\t{}\t{}\t\t{}\t{}\t\t{}'.format(search, depth, seldepth, score, total_nodes, total_time, bestmove, pv))