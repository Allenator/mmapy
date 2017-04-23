#!/usr/local/bin/python3

### Import ###

import os # for file operations
import configparser # for parsing config
import hashlib # for hashing
import subprocess # for calling subprocess
import signal # for calling kill signal
import psutil # for force-killing
import atexit # for atexit event register
import warnings # for warnings
import glob # for wildcard file removal
from IPython.display import Math # for 'td' flag typesetting
from IPython.display import Image # for image export
from sympy.parsing import mathematica as M # for MMA parsing

### Core function ###

# Core Component
def core(flag, inparams):
    
    # Get raw command
    cmd = [MMAapp, '-script', socket_path]
    
    # Convert parameters
    params = str(inparams)
    
    # Hash
    cmdhash = str(hashlib.md5(params.encode('utf-8')).hexdigest())
    
    # Write file
    with open(os.path.join(tempdir, cmdhash), 'w+') as f:
        f.write(params)
    
    # Generate execution command
    execcmd = cmd + [cmdhash, flag]
    # print(execcmd)
    
    # Run and fetch output / print hash
    proc = subprocess.Popen(execcmd, env=mma_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # Open child process
    global child_pid # initialize child_pid variable
    child_pid = proc.pid
    (returnhash, returnerror) = proc.communicate()
    returnhash = returnhash.strip().decode('utf-8')
    returnerror = returnerror.strip().decode('utf-8')
    if returnerror:
        warnings.warn(' '.join(['[COMMS WARNING]', returnerror])) # show communication error
        
    # Read message file
    msg = readprint(flag, tempdir, returnhash[64:96])
    
    # Read print file
    pnt = readprint(flag, tempdir, returnhash[32:64])
    
    # Read output file
    ret = readout(flag, tempdir, returnhash[0:32])
     
    # Clean "cmdhash" and "returnhash" files
    #os.remove(os.path.join(tempdir, cmdhash))
    #os.remove(os.path.join(tempdir, returnhash[0:32]))
    #os.remove(os.path.join(tempdir, returnhash[32:64]))
    #os.remove(os.path.join(tempdir, returnhash[64:96]))
    
    # Print and return results
    if msg:
        for line in msg:
            warnings.warn(' '.join(['[MMA WARNING]', line])) # show MMA error
    if pnt:
        for line in pnt:
            print(line) # print "print" file
    return ret # return results

### Export Functions ###

# readprint
def readprint(flag, tempdir, returnhash):
    pnt = []
    with open(os.path.join(tempdir, returnhash), 'r') as f:
        for line in f.readlines():
            pnt.append(line.strip())
    return pnt

# readout
def readout(flag, tempdir, returnhash):
    if (flag == 't') or (flag == 'n'):
        with open(os.path.join(tempdir, returnhash), 'r') as f:
            ret = f.read()
        return ret
    elif flag == 'p':
        with open(os.path.join(tempdir, returnhash), 'r') as f:
            ret = f.read()
        return M.mathematica(ret)
    elif flag == 'g':
        ret = Image(os.path.join(tempdir, returnhash), format='png')
        return ret
    else:
        raise Exception('Flag must be one of (\'t\', \'n\', \'p\', \'g\').')

### Formatting ###

# TeX format
def t(inparams):
    return core('t', inparams)

# TeX display wrapper
def td(inparams):
    return Math(t(inparams))

# N/A (plain text) format
def n(inparams):
    return core('n', inparams)

# Python compatible format
def p(inparams):
    return core('p', inparams)

# Graphics format
def g(inparams):
    return core('g', inparams)

### Utilities ###

# Clean temp directory
def clean():
    for f in glob.glob(os.path.join(tempdir, '*')):
        os.remove(f)
        
# Kill child process
def _kill_child():
    if child_pid is None:
        pass
    else:
        os.kill(child_pid, signal.SIGKILL)

# Force-kill all WolframKernel Processes
def force_killall():
    for proc in psutil.process_iter():
        if proc.name() == 'WolframKernel':
            proc.kill()

# Warning: ignore everything except the message
def _custom_warning(msg, *a):  
     return str(msg) + '\n'

### Initialization ###

# Get absolute path of "mmapy-socket"
script_dir = os.path.dirname(__file__)
socket_name = 'mmapy-socket.wl'
config_name = 'mmapy-config'
socket_path = os.path.join(script_dir, socket_name)
config_path = os.path.join(script_dir, config_name)

# Read config
cnfpsr = configparser.RawConfigParser()
cnfpsr.read(config_path)
disp = cnfpsr.get('Basic mmapy Configuration', 'Display')
MMAapp = cnfpsr.get('Basic mmapy Configuration', 'MathematicaApp')

tempdir = r'/tmp/mmapy-cache'

# Create temp directory
if not os.path.exists(tempdir):
    os.makedirs(tempdir)

# Customize warning
warnings.formatwarning = _custom_warning

# Set display for graphics export
mma_env = dict(os.environ)
mma_env['DISPLAY'] = disp

# Check display validity
try:
    subprocess.check_output(" ".join(['xdpyinfo', '-display', disp, '>', '/dev/null', '2>&1']), shell=True)
except subprocess.CalledProcessError:
    warnings.warn(' '.join(['[ENV WARNING]', 'Selected DISPLAY', disp, 'is not available. Graphical operations may not work as intended.'])) # show environment error

# Register kill_child at exit
atexit.register(_kill_child)