from indiceval.core import sandbox
def test_correct_wrong_and_early_exit():
    tests="def check(f):\n    assert f(2)==4"
    assert sandbox("def double(x): return x*2",tests,"double")[0]
    assert not sandbox("def double(x): return x+1",tests,"double")[0]
    assert not sandbox("import sys;sys.exit(0)",tests,"double")[0]
def test_sandbox_blocks_network():
    code="import socket\ns=socket.socket()\ns.settimeout(.2)\ns.connect(('1.1.1.1',80))\ndef f(x): return x"
    assert not sandbox(code,"def check(f): assert f(1)==1","f")[0]
