import os

import time

import psutil
import sys
import subprocess

class Engine(object):
    def __init__(self, name, exe, def_bench=False, li_options_uci=None, num_multipv=0, args=None, log=True):
        self.log = log
        self.name = name
        self.def_bench = def_bench

        self.is_white = True

        self.uci_ok = False
        self.pid = None

        self.uci_lines = []

        if not os.path.isfile(exe):
            return

        # Set up executable
        self.exe = exe = os.path.abspath(exe)
        direxe = os.path.dirname(exe)
        xargs = ["./%s" % os.path.basename(exe)]
        if self.def_bench:
            xargs.append("bench")
        if args:
            xargs.extend(args)

        # Run executable in subprocess
        curdir = os.path.abspath(os.curdir)
        os.chdir(direxe)
        self.process = subprocess.Popen(xargs, stdout=subprocess.PIPE, stdin=subprocess.PIPE, startupinfo=None)

        if self.def_bench:
            for line in self.process.stdout:
                if isinstance(line, bytes):
                    continue
                elif isinstance(line, str):
                    # print(line[-1], end='') # process line here
                    continue

        if not self.def_bench:
            os.chdir(curdir)

            self.pid = self.process.pid

            # Map subprocess's stdin/out
            self.stdout = self.process.stdout
            self.stdin = self.process.stdin

            # Init UCI protocol
            self.orden_uci()

            # Load custom options
            setoptions = False
            if li_options_uci:
                for option, valor in li_options_uci:
                    if type(valor) == bool:
                        valor = str(valor).lower()
                    self.set_option(option, valor)
                    setoptions = True
            if self.log:
                self.set_option("Debug Log File", direxe + "/{}.log".format(self.name))

            # Check ready
            if setoptions:
                self.ready_ok()

    # UCI protocol console functions

    def put_line(self, line):
        self.stdin.write(line.encode("utf-8") + b"\n")
        self.stdin.flush()

    def pwait_list(self, orden, txt_busca, maxtime):
        self.put_line(orden)
        ini = time.time()
        li = []
        while time.time() - ini < maxtime:
            line = self.stdout.readline().decode("utf-8", errors="ignore")
            li.append(line.strip())
            if line.startswith(txt_busca):
                return li, True
        return li, False

    # UCI protocol instruction functions

    def orden_uci(self):
        li, self.uci_ok = self.pwait_list("uci", "uciok", 10000)
        self.uci_lines = [x for x in li if x.startswith("id ") or x.startswith("option name")] if self.uci_ok else []

    def ready_ok(self):
        li, readyok = self.pwait_list("isready", "readyok", 10000)
        return readyok

    def set_option(self, name, value):
        if value:
            self.put_line("setoption name %s value %s" % (name, value))
        else:
            self.put_line("setoption name %s" % name)

    def uci_newgame(self):
        self.put_line("ucinewgame")

    # def test_nodes(self):
    #     self.put_line("position r1bq1rk1/ppp1nppp/3pp3/2b1P3/2B2BQP/2P2N2/PP3PP1/R3K2R w KQ - 0 12")
    #     li, ok = self.pwait_list("go nodes 50", "bestmove", 1000)
    #     return li

    def work_ok(self, orden):
        self.put_line(orden)
        return self.ready_ok()

    def position(self, fen=None):
        if fen:
            return self.work_ok("position fen %s" % fen)
            self.is_white = is_white = "w" in fen
        else:
            return self.work_ok("position startpos")

    def go(self, ops, timeout=100000):
        li_resp, result = self.pwait_list("go {}".format(ops), "bestmove", timeout)
        if not result:
            return None
        return li_resp

    def bestmove_fen(self, fen, max_time=None, max_depth=None):
        self.work_ok("position fen %s" % fen)
        self.is_white = is_white = "w" in fen
        return self._mejorMov(max_time, max_depth)

    def _mejorMov(self, max_time, max_depth):
        env = "go"
        if max_depth:
            env += " depth %d" % max_depth
        elif max_time:
            env += " movetime %d" % max_time

        msTiempo = 10000
        if max_time:
            msTiempo = max_time
        elif max_depth:
            msTiempo = int(max_depth * msTiempo / 3.0)

        li_resp, result = self.pwait_list(env, "bestmove", msTiempo)

        if not result:
            return None

        return li_resp

    def close(self):
        if self.pid:
            if self.process.poll() is None:
                self.put_line("quit")
                wtime = 40  # wait for it, wait for it...
                while self.process.poll() is None and wtime > 0:
                    time.sleep(0.05)
                    wtime -= 1

                if self.process.poll() is None:  # nope, no luck
                    sys.stderr.write("INFO X CLOSE525: the engine %s won't close properly.\n" % self.exe)
                    self.process.kill()
                    self.process.terminate()

            self.pid = None