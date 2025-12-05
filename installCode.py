import glob
import os
import re
import shutil
import subprocess
import sys

ccpnmr_major = 2
ccpnmr_minor = 4
ccpnmr_version = '%d.%d' % (ccpnmr_major, ccpnmr_minor)

api_distribution = 'api'
format_distribution = 'format'
analysis_distribution = 'analysis'
extend_nmr_distribution = 'extendNmr'

backup_suffix = '.bak'

distributions = (api_distribution, format_distribution, analysis_distribution, extend_nmr_distribution)

top_dir = os.getcwd()
distribution = 'analysis'
program_name = None

program_names = { \
  api_distribution: 'Api',
  format_distribution: 'Format Converter',
  analysis_distribution: 'Analysis',
  extend_nmr_distribution: 'ExtendNmr',
}

tcl_tk_platform = 'unix' # needed for Tcl/Tk

bin_rel_dir = 'bin'

ccpnmr_rel_dir = 'ccpnmr%s' % ccpnmr_version

#tcltk_version = '8.3'
#tcltk_release = '8.3.4'
#tcltk_version = '8.4'
#tcltk_release = '8.4.14'
#tcltk_version = '8.5'
#tcltk_release = '8.5.4'
#tcltk_release = '8.5.8'
tcltk_version = '8.6'
tcltk_release = '8.6.3'

tcl_rel_dir = 'tcl%s' % tcltk_version
tcl_tar_dir = 'tcl%s' % tcltk_release
tcl_tar_file = tcl_tar_dir + '.tar'
tcl_tar_file_gz = tcl_tar_file + '.gz'

tk_rel_dir = 'tk%s' % tcltk_version
tk_tar_dir = 'tk%s' % tcltk_release
tk_tar_file = tk_tar_dir + '.tar'
tk_tar_file_gz = tk_tar_file + '.gz'

tix_version = '8.4'
tix_release = '8.4.3'
tix_rel_dir = 'tix%s' % tix_version
tix_tar_dir = 'Tix%s' % tix_release
tix_tar_file = tix_tar_dir + '.tar'
tix_tar_file_gz = tix_tar_file + '.gz'

#min_python_version = '2.2'
min_python_version = '2.4'
#python_version = '2.2'
#python_release = '2.2.3'
#python_version = '2.4'
#python_release = '2.4.2'
#python_version = '2.5'
#python_release = '2.5.2'
#python_version = '2.6'
#python_release = '2.6.5'
python_version = '2.7'
python_release = '2.7.9'
python_rel_dir = 'python%s' % python_version
python_tar_dir = 'Python-%s' % python_release
python_tar_file = python_tar_dir + '.tar'
python_tar_file_gz = python_tar_dir + '.tgz'

element_tree_rel_dir = 'elementTree'
element_tree_tar_dir = 'elementtree-1.2.6-20050316'
element_tree_tar_file = element_tree_tar_dir + '.tar'
element_tree_tar_file_gz = element_tree_tar_file + '.gz'

#numpy_version = '1.2'
#numpy_release = '1.2.1'
#numpy_version = '1.4'
#numpy_release = '1.4.1'
numpy_version = '1.9'
numpy_release = '1.9.2'
numpy_rel_dir = 'numpy%s' % numpy_version
numpy_tar_dir = 'numpy-%s' % numpy_release
numpy_tar_file = numpy_tar_dir + '.tar'
numpy_tar_file_gz = numpy_tar_file + '.gz'

mesa_version = '6.0'
mesa_release = '6.0'
mesa_rel_dir = 'mesa%s' % mesa_version
mesa_prefix = 'Mesa'
mesa_tar_dir = '%s-%s' % (mesa_prefix, mesa_release)
mesa_tar_file1 = '%sLib-%s.tar' % (mesa_prefix, mesa_release)
mesa_tar_file1_gz = mesa_tar_file1 + '.gz'
mesa_tar_file2 = '%sDemos-%s.tar' % (mesa_prefix, mesa_release)
mesa_tar_file2_gz = mesa_tar_file2 + '.gz'

possible_platforms = ('linux', 'irix', 'sunos', 'darwin')

# too many choices for irix and sunos to make a guess
comp_arch_guess = { \
  'linux': ('linux-x86', 'Linux on a PC'),
  'darwin': ('darwin', 'Mac OSX'),
}

mesa_comp_arch_msg = """
aix                   for AIX systems with xlc
aix-sl                for AIX systems, make shared libs
aix-gcc               for AIX sytems with gcc
beos-r4               for BeOS R4
cygnus                for Win95/NT using Cygnus-Win32
cygnus-linux          for Win95/NT using Cygnus-Win32 under Linux
darwin                for Darwin - Mac OS X
freebsd               for FreeBSD systems with GCC
freebsd-386           for FreeBSD systems with GCC, w/ Intel assembly
gcc-sl                for a generic system with GCC for shared libs
hpux9                 for HP systems with HPUX 9.x
hpux9-sl              for HP systems with HPUX 9.x, make shared libs
hpux9-gcc             for HP systems with HPUX 9.x using GCC
hpux9-gcc-sl          for HP systems with HPUX 9.x, GCC, make shared libs
hpux10                for HP systems with HPUX 10.x and 11.x
hpux10-sl             for HP systems with HPUX 10.x and 11.x, shared libs
hpux10-gcc            for HP systems with HPUX 10.x w/ GCC
hpux10-gcc-sl         for HP systems with HPUX 10.x w/ GCC, shared libs
irix6-o32             for SGI systems with IRIX 6.x, make o32-bit libs
irix6-o32-dso         for SGI systems with IRIX 6.x, make o32-bit DSOs
irix6-n32             for SGI systems with IRIX 6.x, make n32-bit libs
irix6-n32-dso         for SGI systems with IRIX 6.x, make n32-bit DSOs
irix6-gcc-n32-sl      for SGI systems with IRIX 6.x, GCC, make n32 DSOs
irix6-64              for SGI systems with IRIX 6.x, make 64-bit libs
irix6-64-dso          for SGI systems with IRIX 6.x, make 64-bit DSOs
linux                 for Linux
linux-x86             for Linux with x86 optimizations
linux-ggi             for Linux with libggi driver
linux-x86-ggi         for Linux with libggi driver and x86 optimizations
linux-glide           for Linux with 3Dfx Glide driver
linux-x86-glide       for Linux with 3Dfx Glide driver and x86 opts
linux-alpha           for Linux with Alpha optimizations
linux-alpha-static    for Linux with Alpha opts, make static libs
linux-ppc             for Linux with PowerPC opts
linux-ppc-static      for Linux with PowerPC opts, make static libs
linux-sparc           for Linux with Sparc optimzations
linux-sparc5          for Linux with Sparc5 optimizations
linux-sparc-ultra     for Linux with UltraSparc optimizations
linux-osmesa16        for 16-bit/channel OSMesa
linux-osmesa16-static for 16-bit/channel OSMesa, make static libs
linux-osmesa32        for 32-bit/channel OSMesa
linux-solo            for Linux standalone with DRI drivers
linux-icc             for Linux with the Intel C/C++ compiler
lynxos                for LynxOS systems with GCC
mklinux               for Linux on Power Macintosh
netbsd                for NetBSD 1.0 systems with GCC
openbsd               for OpenBSD systems
openstep              for OpenStep/MacOSX Server systems
osf1                  for DEC Alpha systems with OSF/1
qnx                   for QNX V4 systems with Watcom compiler
solaris-x86           for PCs with Solaris
solaris-x86-gcc       for PCs with Solaris using GCC
sunos4                for Suns with SunOS 4.x
sunos4-sl             for Suns with SunOS 4.x, make shared libs
sunos4-gcc            for Suns with SunOS 4.x and GCC
sunos4-gcc-sl         for Suns with SunOS 4.x, GCC, make shared libs
sunos5                for Suns with SunOS 5.x
sunos5-smp            for Suns with SunOS 5.x, SMP optimization
sunos5-gcc            for Suns with SunOS 5.x and GCC
sunos5-gcc-debug      for Suns with SunOS 5.x and GCC
ultrix-gcc            for DEC systems with Ultrix and GCC
unixware              for PCs running UnixWare
unixware-shared       for PCs running UnixWare, shared libs
"""
mesa_comp_arch = []
s = mesa_comp_arch_msg.split('\n')[1:-1]
for x in s:
  mesa_comp_arch.append(x.split()[0])

format_program = 'formatConverter'
data_shifter_program = 'dataShifter'
analysis_program = 'analysis'
eci_program = 'eci'
deposition_program = 'depositionFileImporter'
extend_nmr_program = 'extendNmr'
dangle_program = 'dangle'
pipe2azara_program = 'pipe2azara'
xeasy2azara_program = 'xeasy2azara'
updateCode_program = 'updateCheck'
updateAuto_program = 'updateAll'

python_program = 'python'

share_suffix = 'so'

fp_log = None

def runCmds(cmds):
 
  cmd = ';'.join(cmds)
  #print 'COMMAND =', cmd
  os.system(cmd)

def writeLog(message):

  if (fp_log):
    fp_log.write('%s\n' % message)

def doPrint(message):

  print(message)
  writeLog(message)

def getInput(prompt, doLower = 1, default = None):
 
  s = ''
  while (not s):
    s = input(prompt + ' ')
    s = s.strip()
    if (not s and default is not None):
        s = default
 
  writeLog('%s %s' % (prompt, s))

  if (doLower):
    s = s.lower()
 
  return s

def getPlatform():

  platform = sys.platform
 
  flag = 0
  for p in possible_platforms:
    if (platform.find(p) >= 0):
      platform = p
      doPrint('Assuming your platform is %s' % platform)
      flag = 1
      break

  if (not flag):
    s = getInput('Cannot figure out your platform, is it one of %s (y or n)?' % (possible_platforms,))
    if (s == 'y'):
      while (platform not in possible_platforms):
        platform = getInput('Which platform (%s)?:' % (possible_platforms,))
    else:
      #doPrint('Unknown platform, there will probably be problems')
      platform = None

  return platform

def getShell():

  shell = 'sh'
  for dir in ('/bin', '/usr/bin'):
    ss = '%s/%s' % (dir, shell)
    if os.path.exists(ss):
      break
  else:
    shell = os.environ.get('SHELL')
    if shell:
      n = shell.rfind('/')
      if n >= 0:
        shell = shell[n+1:]
    else:
      shell = 'csh'  # hopefully always exists if sh does not

  return shell

def setStandardCodeDict(codeDict, directory, version = None):

  codeDict['directory'] = directory
  if version:
    codeDict['version'] = version
    for key in ('include', 'lib'):
      codeDict[key] = key

def haveTclTarFile():

  return os.path.exists(os.path.join(tcl_rel_dir, tcl_tar_file_gz)) \
       or os.path.exists(os.path.join(tcl_rel_dir, tcl_tar_file))

def haveTclFiles():

  # checks that platform code directory exists, nothing else
  if os.path.exists(os.path.join(tcl_rel_dir, tcl_tar_dir, tcl_tk_platform)):
    return True
  else:
    return False

def unpackTcl():

  os.chdir(tcl_rel_dir)

  cmds = []
  if os.path.exists(tcl_tar_dir):
    cmds.append('rm -rf %s' % tcl_tar_dir)

  for dir in ('bin', 'include', 'lib', 'man'):
    if (os.path.exists(dir)):
      cmds.append('rm -rf %s' % dir)

  if (os.path.exists(tcl_tar_file_gz)):
    cmds.append('gunzip %s' % tcl_tar_file_gz)
  # else assume it has already been gunzipped
  cmds.append('tar xvf %s' % tcl_tar_file)
  cmds.append('gzip %s' % tcl_tar_file)

  runCmds(cmds)

  #os.chdir('..')
  os.chdir(top_dir)

def compileTcl():

  os.chdir(os.path.join(tcl_rel_dir, tcl_tar_dir, tcl_tk_platform))

  platform = getPlatform()
  flags = ''
  if platform == 'darwin':
    flags = ' --enable-threads --enable-shared --disable-corefoundation'
    n = int(os.uname()[2].split('.')[0])
    if n >= 10:  # OSX >= 10.6 (Snow Leopard)
      flags += ' --enable-64bit'
    
  cmds = []
  cmds.append('./configure --prefix=%s/%s%s' % (top_dir, tcl_rel_dir, flags))
  cmds.append('make')
  cmds.append('make install')

  runCmds(cmds)

  #os.chdir('../../..')
  os.chdir(top_dir)

def haveTkTarFile():

  return os.path.exists(os.path.join(tk_rel_dir, tk_tar_file_gz)) \
       or os.path.exists(os.path.join(tk_rel_dir, tk_tar_file))

def haveTkFiles():

  # checks that platform code directory exists, nothing else
  if os.path.exists(os.path.join(tk_rel_dir, tk_tar_dir, tcl_tk_platform)):
    return True
  else:
    return False

def unpackTk():

  os.chdir(tk_rel_dir)

  cmds = []
  if (os.path.exists(tk_tar_dir)):
    cmds.append('rm -rf %s' % tk_tar_dir)

  for dir in ('bin', 'include', 'lib', 'man'):
    if (os.path.exists(dir)):
      cmds.append('rm -rf %s' % dir)

  if (os.path.exists(tk_tar_file_gz)):
    cmds.append('gunzip %s' % tk_tar_file_gz)
  # else assume it has already been gunzipped
  cmds.append('tar xvf %s' % tk_tar_file)
  cmds.append('gzip %s' % tk_tar_file)

  runCmds(cmds)

  #os.chdir('..')
  os.chdir(top_dir)

def compileTk(tcl_lib_dir):

  os.chdir(os.path.join(tk_rel_dir, tk_tar_dir, tcl_tk_platform))

  platform = getPlatform()
  flags = ''
  if platform == 'darwin':
    flags = ' --enable-threads --enable-shared --disable-corefoundation'
    n = int(os.uname()[2].split('.')[0])
    if n >= 10:  # OSX >= 10.6 (Snow Leopard)
      flags += ' --enable-64bit'

  cmds = []
  cmds.append('./configure --prefix=%s/%s --with-tcl=%s%s' % (top_dir, tk_rel_dir, tcl_lib_dir, flags))
  cmds.append('make')
  cmds.append('make install')

  runCmds(cmds)

  #os.chdir('../../..')
  os.chdir(top_dir)

def haveTixTarFile():

  return os.path.exists(os.path.join(tix_rel_dir, tix_tar_file_gz)) \
       or os.path.exists(os.path.join(tix_rel_dir, tix_tar_file))

def haveTixFiles():

  if os.path.exists(os.path.join(tix_rel_dir, tix_tar_dir)):
    return True
  else:
    return False

def unpackTix():

  os.chdir(tix_rel_dir)

  cmds = []
  if os.path.exists(tix_tar_dir):
    cmds.append('rm -rf %s' % tix_tar_dir)

  if (os.path.exists(tix_tar_file_gz)):
    cmds.append('gunzip %s' % tix_tar_file_gz)
  # else assume it has already been gunzipped
  cmds.append('tar xvf %s' % tix_tar_file)
  cmds.append('gzip %s' % tix_tar_file)

  runCmds(cmds)

  os.chdir(top_dir)

def compileTix(softwareDict):

  x11CodeDict = softwareDict['X11']
  x11_abs_dir  = x11CodeDict.get('directory')
  x11_inc_dir = x11CodeDict['include']
  x11_inc_dir = os.path.join(x11_abs_dir, x11_inc_dir)
  x11_lib_dir = x11CodeDict['lib']
  x11_lib_dir = os.path.join(x11_abs_dir, x11_lib_dir)

  tclCodeDict = softwareDict['Tcl']
  tcl_abs_dir  = tclCodeDict.get('directory')
  tcl_lib_dir = tclCodeDict['lib']
  tcl_lib_dir = os.path.join(tcl_abs_dir, tcl_lib_dir)
  tcltk_version = tclCodeDict['version']

  tkCodeDict = softwareDict['Tk']
  tk_abs_dir  = tkCodeDict.get('directory')
  tk_lib_dir = tkCodeDict['lib']
  tk_lib_dir = os.path.join(tk_abs_dir, tk_lib_dir)

  os.chdir(os.path.join(tix_rel_dir, tix_tar_dir))

  platform = getPlatform()
  flags = ''
  if platform == 'darwin':
    flags = ' --enable-threads --enable-shared --disable-corefoundation'
    n = int(os.uname()[2].split('.')[0])
    if n >= 10:  # OSX >= 10.6 (Snow Leopard)
      flags += ' --enable-64bit'
    
  if tcltk_version == '8.6':
    flags += ' CC="gcc -DUSE_INTERP_RESULT -DUSE_INTERP_ERRORLINE"'

  cmds = []
  cmds.append('./configure --prefix=%s/%s --with-tcl=%s --with-tk=%s --x-includes=%s --x-libraries=%s %s' % (top_dir, tix_rel_dir, tcl_lib_dir, tk_lib_dir, x11_inc_dir, x11_lib_dir, flags))
  cmds.append('make')
  cmds.append('make install')

  runCmds(cmds)

  os.chdir(top_dir)

def havePythonTarFile():

  return os.path.exists(os.path.join(python_rel_dir, python_tar_file_gz)) \
       or os.path.exists(os.path.join(python_rel_dir, python_tar_file))

def havePythonFiles():

  # checks that code directory exists, nothing else
  if os.path.exists(os.path.join(python_rel_dir, python_tar_dir)):
    return True
  else:
    return False

def unpackPython():

  os.chdir(python_rel_dir)

  cmds = []
  if (os.path.exists(python_tar_dir)):
    cmds.append('rm -rf %s' % python_tar_dir)

  for dir in ('bin', 'include', 'lib', 'man'):
    if (os.path.exists(dir)):
      cmds.append('rm -rf %s' % dir)

  if (os.path.exists(python_tar_file_gz)):
    cmds.append('gunzip %s' % python_tar_file_gz)
  # else assume it has already been gunzipped
  cmds.append('tar xvf %s' % python_tar_file)

  cmds.append('gzip %s' % python_tar_file)
  cmds.append('mv %s.gz %s' % (python_tar_file, python_tar_file_gz))

  runCmds(cmds)

  #os.chdir('..')
  os.chdir(top_dir)

def findFile(directory, pattern):

  pattern = os.path.join(directory, pattern)

  result = glob.glob(pattern)
  if result:
    result = '/' + os.path.basename(os.path.dirname(result[0]))
  else:
    result = ''

  return result

def compilePython(softwareDict):

  os.chdir(python_rel_dir + '/' + python_tar_dir)

  codeDict = softwareDict['X11']
  x11_abs_dir  = codeDict.get('directory')

  platform = getPlatform()
  bits = softwareDict['bits']
  built_by = os.environ.get('USER', 'unknown')

  if x11_abs_dir:

    # need to create Modules/Setup so that our Tcl/Tk found

    x11_inc_dir = codeDict['include']
    x11_lib_dir = codeDict['lib']
    codeDict = softwareDict['Tcl']
    tcl_abs_dir  = codeDict.get('directory')
    tcl_inc_dir = codeDict['include']
    tcl_lib_dir = codeDict['lib']
    tcltk_version = codeDict['version']
    codeDict = softwareDict['Tk']
    tk_abs_dir  = codeDict.get('directory')
    tk_inc_dir = codeDict['include']
    tk_lib_dir = codeDict['lib']
    codeDict = softwareDict['Tix']
    tix_abs_dir = codeDict.get('directory', '')
    tix_lib_dir = codeDict.get('lib', '')
    if tix_abs_dir and tix_lib_dir:
      tix_stuff = '-L%s \\\n\t-DWITH_TIX -lTix%s \\\n\t' % (os.path.join(tix_abs_dir, tix_lib_dir), tix_release)
    else:
      tix_stuff = ''

    fp = open('Modules/Setup.dist')
    lines = fp.readlines()
    fp.close()

    fp = open('Modules/Setup.dist', 'w')
    s = '# The _tkinter module.'
    t = '#SSL=/usr/local/ssl'
    n = len(s)
    m = len(t)
    for line in lines:
      fp.write(line)
      if (line[:n] == s):
        fp.write('''
# lines below added in by CcpNmr installation script
 _tkinter _tkinter.c tkappinit.c -DWITH_APPINIT \\
	-L%s/%s -L%s/%s -L%s/%s \\
	-I%s/%s -I%s/%s -I%s/%s \\
	%s-ltcl%s -ltk%s -lX11
# lines above added in by CcpNmr installation script
''' % (tcl_abs_dir, tcl_lib_dir, tk_abs_dir, tk_lib_dir, x11_abs_dir, x11_lib_dir,
       tcl_abs_dir, tcl_inc_dir, tk_abs_dir, tk_inc_dir, x11_abs_dir, x11_inc_dir,
       tix_stuff, tcltk_version, tcltk_version))
      elif (platform == 'linux') and (bits == 64) and (built_by == 'wb104') and (line[:m] == t): # 2015 Feb 24 hack to get ssl compilation to work on hydra (also needed to edit out SSL2 stuff from Python source code: see http://blog.schmichael.com/2012/05/29/building-python-2-6-8-on-ubuntu-12-04/, although 2.6.5 is somewhat different)
        fp.write('''
# lines below added in by CcpNmr installation script
SSL=/usr
_ssl _ssl.c \
       -DUSE_SSL -I$(SSL)/include -I$(SSL)/include/openssl \
       -L$(SSL)/lib -lssl -lcrypto

_hashlib _hashopenssl.c
''')
    fp.close()

  # now compile and install code

  flags = ''
  if platform == 'darwin':
    flags = ' --enable-threads --disable-toolbox-glue --disable-framework'

  cmds = []
  cmds.append('./configure --prefix=%s/%s%s' % (top_dir, python_rel_dir, flags))
  cmds.append('make')
  cmds.append('make install')
  runCmds(cmds)

  #os.chdir('../..')
  os.chdir(top_dir)

def haveElementTreeTarFile():

  return os.path.exists(os.path.join(element_tree_rel_dir, element_tree_tar_file_gz)) \
       or os.path.exists(os.path.join(element_tree_rel_dir, element_tree_tar_file))

def unpackElementTree():

  os.chdir(element_tree_rel_dir)

  cmds = []
  if (os.path.exists(element_tree_tar_dir)):
    cmds.append('rm -rf %s' % element_tree_tar_dir)

  if (os.path.exists(element_tree_tar_file_gz)):
    cmds.append('gunzip %s' % element_tree_tar_file_gz)
  # else assume it has already been gunzipped
  cmds.append('tar xvf %s' % element_tree_tar_file)

  cmds.append('gzip %s' % element_tree_tar_file)

  runCmds(cmds)

  #os.chdir('..')
  os.chdir(top_dir)

def haveNumpyTarFile():

  return os.path.exists(os.path.join(numpy_rel_dir, numpy_tar_file_gz)) \
       or os.path.exists(os.path.join(numpy_rel_dir, numpy_tar_file))

def haveNumpyFiles():

  # checks that platform code directory exists, nothing else
  if os.path.exists(os.path.join(numpy_rel_dir, numpy_tar_dir)):
    return True
  else:
    return False

def unpackNumpy():

  os.chdir(numpy_rel_dir)

  cmds = []
  if (os.path.exists(numpy_tar_dir)):
    cmds.append('rm -rf %s' % numpy_tar_dir)

  if (os.path.exists(numpy_tar_file_gz)):
    cmds.append('gunzip %s' % numpy_tar_file_gz)
  # else assume it has already been gunzipped
  cmds.append('tar xvf %s' % numpy_tar_file)

  cmds.append('gzip %s' % numpy_tar_file)

  runCmds(cmds)

  #os.chdir('..')
  os.chdir(top_dir)

def compileNumpy(python_bin_dir, py_version):

  os.chdir(os.path.join(numpy_rel_dir, numpy_tar_dir))

  python_exe = '%s/bin/python%s' % (python_bin_dir, py_version)
  if not os.path.exists(python_exe):
    python_exe = '%s/bin/python' % python_bin_dir
    if not os.path.exists(python_exe):
      doPrint('Could not find "%s%s" nor "%s" so giving up trying to compile numpy' % (python_exe, py_version, python_exe))

  cmds = []
  cmds.append('%s setup.py install' % python_exe)

  runCmds(cmds)

  #os.chdir('../..')
  os.chdir(top_dir)

def haveMesaTarFiles():

  return (os.path.exists(os.path.join(mesa_rel_dir, mesa_tar_file1_gz))
       or os.path.exists(os.path.join(mesa_rel_dir, mesa_tar_file1))) \
       and (os.path.exists(os.path.join(mesa_rel_dir, mesa_tar_file2_gz)) \
       or os.path.exists(os.path.join(mesa_rel_dir, mesa_tar_file2)))

def haveMesaFiles():

  # checks that code directory exists, nothing else
  if os.path.exists(os.path.join(mesa_rel_dir, mesa_tar_dir)):
    return True
  else:
    return False

def unpackMesa():

  os.chdir(mesa_rel_dir)

  cmds = []
  if (os.path.exists(mesa_tar_dir)):
    cmds.append('rm -rf %s' % mesa_tar_dir)

  for dir in ('etc', 'include', 'lib'):
    if (os.path.exists(dir)):
      cmds.append('rm -rf %s' % dir)

  if (os.path.exists(mesa_tar_file1_gz)):
    cmds.append('gunzip %s' % mesa_tar_file1_gz)
  # else assume it has already been gunzipped
  cmds.append('tar xvf %s' % mesa_tar_file1)
  if (os.path.exists(mesa_tar_file2_gz)):
    cmds.append('gunzip %s' % mesa_tar_file2_gz)
  # else assume it has already been gunzipped
  cmds.append('tar xvf %s' % mesa_tar_file2)

  cmds.append('gzip %s' % mesa_tar_file1)
  cmds.append('gzip %s' % mesa_tar_file2)

  runCmds(cmds)

  #os.chdir('..')
  os.chdir(top_dir)

def getCompArch(platform):

  if (platform):
    (comp_arch, comp_msg) = comp_arch_guess.get(platform, '')
  else:
    comp_arch = ''

  if (comp_arch):
    s = getInput('Is your computer %s (%s) (y or n)?' % (comp_arch, comp_msg))
  else:
    s = 'n'
  if (s[0] == 'n'):
    doPrint('Possible Mesa architecture compilations:')
    doPrint(mesa_comp_arch_msg)
    comp_arch = getInput('Which is the most appropriate architecture for your computer?', doLower=0)
    while (comp_arch not in mesa_comp_arch):
      doPrint('That architecture not on list, try again')
      comp_arch = getInput('Which is the most appropriate architecture for your computer?', doLower=0)

  return comp_arch

def compileMesa(comp_arch):

  os.chdir(mesa_rel_dir + '/' + mesa_tar_dir)

  # Mesa compilation changed between v4.0 and v6.0
  cmds = []
  #cmds.append('./configure --prefix=%s/%s' % (top_dir, mesa_rel_dir))
  #cmds.append('make')
  #cmds.append('make install')
  cmds.append('make %s' % comp_arch)
  runCmds(cmds)

  os.chdir('..')

  for dir in ('include', 'lib'):
    os.symlink('%s/%s' % (mesa_tar_dir, dir), dir)

  #os.chdir('..')
  os.chdir(top_dir)

def createEnvironmentFile(platform, softwareDict, doOpenGL,
                          needGlutInit, useFrameworkGlut,  usePic, useOpenmp):
 
  bits = softwareDict['bits']

  codeDict = softwareDict['Tcl']
  tcl_abs_dir = codeDict.get('directory', '')
  tcl_inc_dir = codeDict.get('include', '')
  tcl_lib_dir = codeDict.get('lib', '')
  tcl_version = tk_version = codeDict.get('version', '')

  codeDict = softwareDict['Tk']
  tk_abs_dir = codeDict.get('directory', '')
  tk_inc_dir = codeDict.get('include', '')
  tk_lib_dir = codeDict.get('lib', '')

  codeDict = softwareDict['Python']
  python_abs_dir = codeDict.get('directory', '')
  python_inc_dir = codeDict.get('include', '')
  python_lib_dir = os.path.join(python_abs_dir, codeDict.get('lib', ''))
  py_version = codeDict.get('version', '')

  codeDict = softwareDict['ElementTree']
  element_tree_abs_dir = codeDict.get('directory', '')
  element_tree_inc_dir = codeDict.get('elementtree', '')

  codeDict = softwareDict['X11']
  x11_abs_dir = codeDict.get('directory', '')
  x11_inc_dir = codeDict.get('include', '')
  x11_lib_dir = codeDict.get('lib', '')

  codeDict = softwareDict['OpenGL']
  mesa_abs_dir = codeDict.get('directory', '')
  mesa_inc_dir = codeDict.get('include', '')
  mesa_lib_dir = codeDict.get('lib', '')

  codeDict = softwareDict['glut']
  glut_abs_dir = codeDict.get('directory', '')
  glut_inc_dir = codeDict.get('include', '')
  glut_lib_dir = codeDict.get('lib', '')

  env_file = '%s/c/environment.txt' % ccpnmr_rel_dir

  if not platform:
    doPrint('Unknown platform, %s installation procedure will probably fail and you will need to edit %s by hand, continuing anyway using linux options' % (program_name, env_file))
    platform = 'linux'

  if platform == 'windows':
    mallocFlag = ''
  else:
    # other platforms seem not to need this now
    mallocFlag = '-DDO_NOT_HAVE_MALLOC'

  if usePic:
    picFlag = '-fPIC'
  else:
    picFlag = ''

  if useOpenmp:
    openmpComment = ''
  else:
    openmpComment = '#'

  if platform == 'sunos':
    xorFlag = '-DXOR_IS_EQUIV'
  else:
    xorFlag = ''

  if doOpenGL:
    ignoreGL = ''
    glCom = ''
  else:
    ignoreGL = '-DIGNORE_GL'
    glCom = '#'

  if platform == 'linux':
    glFlag = '-DUSE_GL_FALSE'
  else:
    glFlag = '-DUSE_GL_TRUE'

  if platform == 'linux' and bits == 32:
    bigFileFlag = '-D_FILE_OFFSET_BITS=64'
  else:
    bigFileFlag = ''

  if needGlutInit:
    glutNeedInit = '-DNEED_GLUT_INIT'
  else:
    glutNeedInit = ''

  if platform == 'sunos':
    sharedFlag = '-G'
  elif platform == 'darwin':
    sharedFlag = '-L%s -bundle -bundle_loader %s/bin/python%s' % (python_lib_dir, python_abs_dir, py_version)
  else:
    sharedFlag = '-shared'

  pythonLib = ''
  if platform == 'darwin' and py_version >= '2.6':
    try:
      n = int(os.uname()[2].split('.')[0])
      if n >= 10:  # OSX >= 10.6 (Snow Leopard)
        pythonLib = '\nPYTHON_LIB = -L$(PYTHON_DIR)/lib/python%s/config -lpython%s' % (py_version, py_version)

    except:
      pass
    
  if useFrameworkGlut:
    glLibs = '-framework GLUT -lGLU -lGL'
    extraGlIncludeFlag = '-I/System/Library/Frameworks/GLUT.framework/Headers'
    extraGlLibFlag = '-framework GLUT'
    glutNotInGl = '-DGLUT_IN_OWN_DIR'

    try:
      n = int(os.uname()[2].split('.')[0])
      if n >= 9:  # OSX >= 10.5 (Leopard)
        extraGlLibFlag = extraGlLibFlag + ' -Wl,-dylib_file,/System/Library/Frameworks/OpenGL.framework/Versions/A/Libraries/libGL.dylib:/System/Library/Frameworks/OpenGL.framework/Versions/A/Libraries/libGL.dylib'

    except:
      pass
    
  else:
    glLibs = '-lglut -lGLU -lGL'
    if glut_abs_dir:
      extraGlIncludeFlag = '-I%s/%s' % (glut_abs_dir, glut_inc_dir)
      extraGlLibFlag = '-L%s/%s' % (glut_abs_dir, glut_lib_dir)
    else:
      extraGlIncludeFlag = ''
      extraGlLibFlag = ''
    glutNotInGl = ''

  home = '../../../..' # relative to where C source code is
 
  if os.path.exists(env_file):
    env_backup = '%s/c/environment%s' % (ccpnmr_rel_dir, backup_suffix)
    if (os.path.exists(env_backup)):
      os.remove(env_backup)
    doPrint('Backing up %s to %s' % (env_file, env_backup))
    os.rename(env_file, env_backup)

  fp = open('%s/c/environment.txt' % ccpnmr_rel_dir, 'w')
  fp.write('''
# should work if suitably edited for Linux, Irix, Solaris, OSX

# the C compiler and associated things

# use below for everything except Windows
CC = cc
LINK = $(CC)
MAKE = make
CO_NAME = -c $<
OUT_NAME = -o $@
OBJ_SUFFIX = o
DYLIB_SUFFIX = so
RM = rm -f

# use below for Windows
#CC = cl
#LINK = $(CC) /LD
#MAKE = nmake
#CO_NAME = -c $**
#OUT_NAME = /Fe$@
#OBJ_SUFFIX = obj
#DYLIB_SUFFIX = pyd
#RM = rm -f

# compiler flags

# Windows specific flag
# use below for everything except Windows
WIN_FLAG =
# use below for Windows
#WIN_FLAG = /DWIN32 /MD

MALLOC_FLAG = %s
# use below for everything with malloc.h
#MALLOC_FLAG = 
# use below for everything without malloc.h (e.g. OSX)
#MALLOC_FLAG = -DDO_NOT_HAVE_MALLOC

FPIC_FLAG = %s
# use below for everything with -fPIC option (e.g. gcc)
#FPIC_FLAG = -fPIC
# use below for everything without -fPIC option
#FPIC_FLAG = 

XOR_FLAG = %s
# use below for everything where Tk xor behaves normally
#XOR_FLAG =
# use below for everything (e.g. Solaris) where xor is equiv
#XOR_FLAG = -DXOR_IS_EQUIV

# optimisation flag
# use below for everything except Windows
OPT_FLAG = -O2
# use below for Windows
#OPT_FLAG = /Ox

# file flag needed for 32-bit Linux to be able to read > 2Gb files
BIGFILE_FLAG = %s
# use below for everything except 32-bit Linux
#BIGFILE_FLAG = 
# use below for 32-bit Linux
#BIGFILE_FLAG = -D_FILE_OFFSET_BITS=64

# Some functions utilise OpenMP for multi-cpu optimisation
# use below if you have more than one cpu
# (these flags for GNU CC, Intel CC differs)
%sOPENMP_FLAGS = -fopenmp
%sOPENMP_LIB  = -lgomp
# use below for Windows (note: after VS 2010 VCOMP.LIB is a paid upgrade,
# but is available for free in VS 2008)
#OPENMP_FLAGS = /OPENMP
#OPENMP_LIB  = VCOMP.LIB

CC_FLAGS = $(WIN_FLAG) $(OPT_FLAG) $(FPIC_FLAG) $(MALLOC_FLAG) $(XOR_FLAG) $(BIGFILE_FLAG)
LINK_FLAGS = $(WIN_FLAG) $(OPT_FLAG) $(FPIC_FLAG)

# linking command for C libraries into Python world
# (used for everything except Windows)
LINK_LIBRARIES = sh linkSharedObjs

# copying command for C libraries into Python world
# (used only for Windows)
COPY_LIBRARIES = sh copySharedObjs
''' % (mallocFlag, picFlag, xorFlag, bigFileFlag, openmpComment, openmpComment))
 
  fp.write('''

# specify whether or not you want to compile GL
IGNORE_GL_FLAG = %s
# use below if you want to compile GL
#IGNORE_GL_FLAG =
# use below if you want to ignore GL
#IGNORE_GL_FLAG = -DIGNORE_GL

# special GL flag, should have either USE_GL_TRUE or USE_GL_FALSE
# (-D means this gets defined by the compiler so can be checked in source code)
# (this relates to glXCreateContext() call in ccpnmr/global/gl_handler.c)
# if have problems with USE_GL_TRUE then try GL_FALSE, or vice versa
GL_FLAG = %s
# use below for Linux?
#GL_FLAG = -DUSE_GL_FALSE
# use below for everything else?
#GL_FLAG = -DUSE_GL_TRUE

GLUT_NEED_INIT = %s
# use below if your glut does not need to be explicitly initialised
#GLUT_NEED_INIT =
# use below if your glut needs to be explicitly initialised
#GLUT_NEED_INIT = -DNEED_GLUT_INIT

GLUT_NOT_IN_GL = %s
# whether glut.h is GL/glut.h (normal case) or just glut.h (OSX)
# use below if glut.h is in GL directory
#GLUT_NOT_IN_GL =
# use below if glut.h is not in GL directory (e.g. OSX)
#GLUT_NOT_IN_GL = -DGLUT_IN_OWN_DIR

# special glut flag
GLUT_FLAG = $(GLUT_NEED_INIT) $(GLUT_NOT_IN_GL)
''' % (ignoreGL, glFlag, glutNeedInit, glutNotInGl))

  fp.write('''

# shared library flags
SHARED_FLAGS = %s
# use below for Linux or Irix
#SHARED_FLAGS = -shared
# use below for OSX (assuming python executable is /sw/bin/python)
#SHARED_FLAGS = -L/sw/lib -bundle -bundle_loader /sw/bin/python
# use below for Solaris
#SHARED_FLAGS = -G
''' % sharedFlag)

  fp.write('''

# math
MATH_LIB = -lm
''')
 
  fp.write('''

# X11
X11_DIR = %s
# use below for everything but Irix
#X11_DIR = /usr/X11R6
# use below for Irix
#X11_DIR = /usr
X11_LIB = -lX11 -lXext
X11_INCLUDE_FLAGS = -I$(X11_DIR)/%s
X11_LIB_FLAGS = -L$(X11_DIR)/%s
# use below for 32 bit except on Irix
#X11_LIB_FLAGS = -L$(X11_DIR)/lib
# use below for 32 bit on Irix
#X11_LIB_FLAGS = -L$(X11_DIR)/lib32
# use below for 64 bit (not OSX?)
#X11_LIB_FLAGS = -L$(X11_DIR)/lib64
''' % (x11_abs_dir, x11_inc_dir, x11_lib_dir))

  fp.write('''

# Tcl
TCL_DIR = %s
TCL_LIB = -ltcl%s
TCL_INCLUDE_FLAGS = -I$(TCL_DIR)/%s
TCL_LIB_FLAGS = -L$(TCL_DIR)/%s
''' % (tcl_abs_dir, tcl_version, tcl_inc_dir, tcl_lib_dir))
 
  fp.write('''

# Tk
TK_DIR = %s
TK_LIB = -ltk%s
TK_INCLUDE_FLAGS = -I$(TK_DIR)/%s
TK_LIB_FLAGS = -L$(TK_DIR)/%s
''' % (tk_abs_dir, tk_version, tk_inc_dir, tk_lib_dir))
 
  fp.write('''

# Python
PYTHON_DIR = %s
PYTHON_INCLUDE_FLAGS = -I$(PYTHON_DIR)/%s/python%s%s
''' % (python_abs_dir, python_inc_dir, py_version, pythonLib))
 
  fp.write('''

# GL
%sGL_DIR = %s
%sGL_LIB = %s
# use below if compiling GL, except on OSX
#GL_LIB = -lglut -lGLU -lGL
# use below if compiling GL on OSX
#GL_LIB = -framework GLUT -lGLU -lGL
# use below if not compiling GL (or comment out GL_LIB line)
#GL_LIB =
# set GL_INCLUDE_FLAGS and GL_LIB_FLAGS if compiling GL
%sGL_INCLUDE_FLAGS = -I$(GL_DIR)/%s %s
%sGL_LIB_FLAGS = -L$(GL_DIR)/%s %s
# use below if compiling GL, except on OSX
#GL_INCLUDE_FLAGS = -I$(GL_DIR)/include
# use below if compiling GL on OSX
#GL_INCLUDE_FLAGS = -I$(GL_DIR)/include -I/System/Library/Frameworks/GLUT.framework/Headers
# use below if not compiling GL
#GL_INCLUDE_FLAGS =
# use below if compiling GL for everything 32 bit but Irix and OSX
#GL_LIB_FLAGS = -L$(GL_DIR)/lib
# use below for OSX
#GL_LIB_FLAGS = -L$(GL_DIR)/lib -framework GLUT
# use below for 32 bit Irix
#GL_LIB_FLAGS = -L$(GL_DIR)/lib32
# use below for 64 bit (not on OSX?)
#GL_LIB_FLAGS = -L$(GL_DIR)/lib64
# use below if not compiling GL (or comment out GL_LIB_FLAGS line)
#GL_LIB_FLAGS =
''' % (glCom, mesa_abs_dir,
       glCom, glLibs,
       glCom, mesa_inc_dir, extraGlIncludeFlag,
       glCom, mesa_lib_dir, extraGlLibFlag))

  fp.close()

def compileAnalysis(softwareDict):
 
  codeDict = softwareDict['Python']
  python_abs_dir = codeDict['directory']

  # need to make sure picking up correct Python before compiling Analysis
  path = os.environ.get('PATH')
  if path:
    path = '%s:%s' % (python_abs_dir, path)
  else:
    path = python_abs_dir
  os.environ['PATH'] = path

  os.chdir('%s/c' % ccpnmr_rel_dir)
  cmds = ['make']
  runCmds(cmds)
  #os.chdir('../..')
  os.chdir(top_dir)

# below currently works for Analysis only
# (and is only really needed for that, because of pre-compiled releases)
def addInfoToVersion(softwareDict):
 
  platform = softwareDict['platform']
  bits = softwareDict['bits']
  try:
    arch = subprocess.Popen(['uname', '-m'],stdout=subprocess.PIPE).communicate()[0].strip()
  except:
    arch = 'unknown'
  built_by =  os.environ.get('USER', 'unknown')
  if built_by in ('wb104',):  # hack
    built_by = 'ccpn'
    category = 'all-compiled'
  else:
    category = 'user-compiled'

  versionFile = os.path.join(ccpnmr_rel_dir, 'python/ccpnmr/analysis/Version.py')
  try:
    fp = open(versionFile, 'a')
    fp.write("platform = '%s'\n" % platform)
    fp.write("bits = %d\n" % bits)
    fp.write("arch = '%s'\n" % arch)
    fp.write("built_by = '%s'\n" % built_by)
    fp.write("category = '%s'\n" % category)
    fp.close()
  except:
    pass

def createSymbolicLinks():
 
  script = './linkSharedObjs'
  cmds = ['chmod u+x %s' % script, script]

  os.chdir('%s/python' % ccpnmr_rel_dir)

  for dir in ('memops/c', 'ccp/c', 'ccpnmr/c', 'cambridge/c'):
    os.chdir(dir)
    runCmds(cmds)
    os.chdir('../..')
 
  #os.chdir('../..')
  os.chdir(top_dir)

def writeShellCommand(fp, shell):

  for dir in ('/bin', '/usr/bin'):
    ss = '%s/%s' % (dir, shell)
    if os.path.exists(ss):
      break
  else:
    return

  if shell == 'csh':
    ss += ' -f'
  fp.write('#!%s\n\n' % ss)

def writeEnvString(fp, key, value, useExport):

  if useExport:
    fp.write('export %s="%s"\n' % (key, value))
  else:
    fp.write('setenv %s "%s"\n' % (key, value))

def replaceTopDir(path):

  if path == top_dir or path.startswith(top_dir + '/'):
    path = path.replace(top_dir, '${CCPNMR_TOP_DIR}')

  return path

def writeEnvVars(fp, softwareDict, useExport):

  platform = softwareDict['platform']

  tcl_lib_path = tk_lib_path = ''
  lib_paths = []
  keys = ('Tcl', 'Tk', 'Tix')
  if platform != 'darwin':
    keys = ('X11',) + keys + ('OpenGL', 'glut')

  for key in keys:
    codeDict = softwareDict[key]
    abs_dir = codeDict.get('directory', '')
    lib_dir = codeDict.get('lib', '')
    if abs_dir and lib_dir:
      lib_path = os.path.join(abs_dir, lib_dir)
      if key == 'Tcl':
        tcl_lib_path = lib_path
        tcl_version = tk_version = codeDict.get('version', '')
      elif key == 'Tk':
        tk_lib_path = lib_path
      if lib_path not in lib_paths:
        lib_paths.append(lib_path)

  lib_paths = [replaceTopDir(lib_path) for lib_path in lib_paths]

  python_paths = ['.', '${CCPNMR_TOP_DIR}/%s/python' % ccpnmr_rel_dir]
  codeDict = softwareDict['ElementTree']
  element_tree_abs_dir = codeDict.get('directory', '')
  if element_tree_abs_dir:
    python_paths.append(element_tree_abs_dir)
  python_paths = [replaceTopDir(python_path) for python_path in python_paths]

  #writeEnvString(fp, 'CCPNMR_TOP_DIR', top_dir, useExport)
  if useExport:
    # IFS - internal field separator - so we can open analysis if on path including spaces
    #fp.write( 'IFS=$(echo "\\n\\b")\n' )
    writeEnvString(fp, 'CCPNMR_TOP_DIR', '$(dirname $(cd $(dirname "$0"); pwd))', useExport)
  else:
    writeEnvString(fp, 'CCPNMR_BIN_DIR', '`dirname "$0"`', useExport)
    writeEnvString(fp, 'CCPNMR_BIN_DIR', '`cd ${CCPNMR_BIN_DIR}; pwd`', useExport)
    writeEnvString(fp, 'CCPNMR_TOP_DIR', '`dirname "${CCPNMR_BIN_DIR}"`', useExport)
  writeEnvString(fp, 'PYTHONPATH', ':'.join(python_paths), useExport)

  if lib_paths:
    lib_paths_string = ':'.join(lib_paths)
    writeEnvString(fp, 'LD_LIBRARY_PATH', lib_paths_string, useExport)
    if platform == 'darwin':
      codeDict = softwareDict['Python']
      python_bin_dir = codeDict['directory']
      # DYLD_LIBRARY_PATH does not work with Fink python because get error:
      #  ImportError: Failure linking new module: ...: Symbol not found: __cg_jpeg_save_markers
      #  Referenced from: /System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/ImageIO.framework/Versions/A/ImageIO
      #  Expected in: /sw/lib/libJPEG.dylib
      if not python_bin_dir.startswith('/sw'):
        writeEnvString(fp, 'DYLD_LIBRARY_PATH', lib_paths_string, useExport)

  if tcl_lib_path:
    tcl_lib_path = replaceTopDir(tcl_lib_path)
    writeEnvString(fp, 'TCL_LIBRARY', '%s/tcl%s' % (tcl_lib_path, tcl_version), useExport)
    tk_lib_path = replaceTopDir(tk_lib_path)
    writeEnvString(fp, 'TK_LIBRARY', '%s/tk%s' % (tk_lib_path, tk_version), useExport)

def uncommentFutureImport():

  os.chdir(ccpnmr_rel_dir)

  directory = 'python/memops/format/compatibility'
  for file in ('Converters.py', 'part2/Converters2.py'):
    fullfile = os.path.join(directory, file)
    doPrint('Uncommenting future import in %s' % file)
    fp = open(fullfile)
    data = fp.read()
    fp.close()
    data = data.replace('#from __future__', 'from __future__')
    fp = open(fullfile, 'w')
    fp.write(data)
    fp.close()

  os.chdir(top_dir)

def backupProgram(program):

  # this is because of old v1 analysis scripts

  if os.path.exists(program):
    fp = open(program)
    data = fp.read()
    fp.close()
    if 'ccpnmr1.0' in data:
      program_backup = '%s1' % program
      if os.path.exists(program_backup):
        program_backup = '%s%s' % (program_backup, backup_suffix)
      if not os.path.exists(program_backup):
        doPrint('Moving %s to %s' % (program, program_backup))
        os.rename(program, program_backup)
    else:
      os.remove(program)

def createProgram(program, script, softwareDict, useExport, shell):

    # create programX.Y script

    program_version = '%s%s' % (program, ccpnmr_version)
    if os.path.exists(program_version):
      os.remove(program_version)

    fp = open(program_version, 'w')
    writeShellCommand(fp, shell)
    writeEnvVars(fp, softwareDict, useExport)
    script = replaceTopDir(script)
    fp.write('%s $*\n' % script)
    fp.close()
    os.chmod(program_version, 0o755)  # Python 3: octal literal

    # link programX --> programX.Y

    program_major = '%s%d' % (program, ccpnmr_major)
    if os.path.exists(program_major):
      os.remove(program_major)

    try:  # not sure if works on Windows
      os.symlink(program_version, program_major)
    except:
      shutil.copyfile(program_version, program_major)

    # link program --> programX

    backupProgram(program)

    try:  # not sure if works on Windows
      os.symlink(program_major, program)
    except:
      shutil.copyfile(program_major, program)

def createBin(softwareDict, useExport, shell):
 
  # shell introduced because otherwise scripts do not work on stan
  # but there even though tcsh is the shell scripts do not run with that
  # but instead need csh (not sure what is going on at all with this)
  # so below is just trying to play safe (but it could fail I guess)
  """ 4 Oct 2010: getShell() hopefully working now
  if useExport:
    shell = 'bash'
  else:
    shell = 'csh'
"""

  ##if (os.path.exists(bin_rel_dir)):
  ##  cmds = [ 'rm -rf %s' % bin_rel_dir ]
  ##  runCmds(cmds)
     
  if not os.path.exists(bin_rel_dir):
    os.mkdir(bin_rel_dir)

  os.chdir(bin_rel_dir)
 
  codeDict = softwareDict['Python']
  python_bin_dir = codeDict['directory']
  py_version = codeDict['version']
  python_exe = '%s/bin/python%s' % (python_bin_dir, py_version)
  if not os.path.exists(python_exe):
    python_exe = '%s/bin/python' % python_bin_dir
    if not os.path.exists(python_exe):
      doPrint('Could not find "%s%s" nor "%s" so assuming python executable is latter for now' % (python_exe, py_version, python_exe))
      doPrint('You will probably need to edit scripts in %s/%s' % (top_dir, ))
  
  # make python script
  script = '%s -O' % python_exe
  createProgram('pythonCcpn', script, softwareDict, useExport, shell)
 
  if distribution != api_distribution:
    # make format converter program
    script = '%s -O ${CCPNMR_TOP_DIR}/%s/python/ccpnmr/format/gui/FormatConverter.py' % (python_exe, ccpnmr_rel_dir)
    createProgram(format_program, script, softwareDict, useExport, shell)
 
    # make data shifter program
    script = '%s -O ${CCPNMR_TOP_DIR}/%s/python/ccpnmr/format/gui/DataShifter.py' % (python_exe, ccpnmr_rel_dir)
    createProgram(data_shifter_program, script, softwareDict, useExport, shell)

    # make eci program
    script = '%s -O ${CCPNMR_TOP_DIR}/%s/python/ccpnmr/eci/EntryCompletionGui.py' % (python_exe, ccpnmr_rel_dir)
    createProgram(eci_program, script, softwareDict, useExport, shell)
 
    # make deposition program
    script = '%s -O ${CCPNMR_TOP_DIR}/%s/python/pdbe/deposition/dataFileImport/dataFileImportGui.py' % (python_exe, ccpnmr_rel_dir)
    createProgram(deposition_program, script, softwareDict, useExport, shell)
 
  if distribution in (analysis_distribution, extend_nmr_distribution):
    # make analysis program
    script = '%s -i -O ${CCPNMR_TOP_DIR}/%s/python/ccpnmr/analysis/AnalysisGui.py' % (python_exe, ccpnmr_rel_dir)
    createProgram(analysis_program, script, softwareDict, useExport, shell)
 
    # make dangle program
    script = '%s -O ${CCPNMR_TOP_DIR}/%s/python/cambridge/dangle/DangleGui.py' % (python_exe, ccpnmr_rel_dir)
    createProgram(dangle_program, script, softwareDict, useExport, shell)
 
    # make updateCode program
    script = '%s -O ${CCPNMR_TOP_DIR}/%s/python/ccpnmr/update/UpdatePopup.py' % (python_exe, ccpnmr_rel_dir)
    createProgram(updateCode_program, script, softwareDict, useExport, shell)

    # make updateAuto program
    script = '%s -O ${CCPNMR_TOP_DIR}/%s/python/ccpnmr/update/UpdateAuto.py' % (python_exe, ccpnmr_rel_dir)
    createProgram(updateAuto_program, script, softwareDict, useExport, shell)

    # make pipe2azara program
    script = '%s -O ${CCPNMR_TOP_DIR}/%s/python/ccp/format/spectra/params/NmrPipeData.py' % (python_exe, ccpnmr_rel_dir)
    createProgram(pipe2azara_program, script, softwareDict, useExport, shell)

    # make xeasy2azara program
    script = '%s -O ${CCPNMR_TOP_DIR}/%s/python/ccp/format/spectra/params/XeasyData.py' % (python_exe, ccpnmr_rel_dir)
    createProgram(xeasy2azara_program, script, softwareDict, useExport, shell)

    ###if distribution == extend_nmr_distribution:
    # make extendNmr program
    script = '%s -i -O ${CCPNMR_TOP_DIR}/%s/python/extendNmr/ExtendNmrGui.py' % (python_exe, ccpnmr_rel_dir)
    createProgram(extend_nmr_program, script, softwareDict, useExport, shell)


  # make python symbolic link
  # not sure os.symlink works on Windows
  #os.symlink('%s/bin/%s' % (python_bin_dir, python_program), python_program)
 
  #os.chdir('..')
  os.chdir(top_dir)

def runProgram(program):

  cmds = [ os.path.join(bin_rel_dir, program) ]
  runCmds(cmds)

def dirContainsFile(code, codeDict, directory, subdir, file, key):

  result = ''
  cwd = os.getcwd()

  try:
    os.chdir(directory)
  except:
    return False

  try:
    ff = glob.glob(os.path.join(subdir, file))
    if ff:
      result = ff[0]  # arbitrarily pick first hit
    else: # if direct hit fails try one level down
      ff = glob.glob(os.path.join(subdir, '*', file))
      if ff:
        result = ff[0]  # arbitrarily pick first hit
  finally:
    os.chdir(cwd)
 
  if result:
    doPrint('Found %s %s match: %s' % (code, key, os.path.join(directory, result)))
    n = file.count('/') + 1
    for i in range(n):
      result = os.path.dirname(result)
    codeDict[key] = result
    return True

  return False

def dirContainsFiles(code, codeDict, directory, files):

  for (prefix, file) in files:

    if type(prefix) == type(()):
      key = prefix[-1]
      for subdir in prefix:
        if dirContainsFile(code, codeDict, directory, subdir, file, key):
          break
      else:
        return False
    else:
      subdir = key = prefix
      if not dirContainsFile(code, codeDict, directory, subdir, file, key):
        return False

  return True

def getRepr(reqd):

  if type(reqd[0]) == type(()):
    r = reqd[0][-1] + '*'
  else:
    r = reqd[0]

  if reqd[1]:
    s = '*/' + reqd[1]
  else:
    s = ''

  return r + '/' + s

def determineCodeDir(codeDict, code, dirsToCheck, reqdFiles):

  for dir in dirsToCheck:
    if dirContainsFiles(code, codeDict, dir, reqdFiles):
      break
  else:
    dir = ''

  if dir:
    t = ', and as seen, %s does' % dir
  else:
    t = ''

  doPrint('Need to know where %s directory is, in order to compile %s' % (code, program_name))

  ss = [getRepr(rr) for rr in reqdFiles]
  doPrint('This directory should contain [%s]%s' % (', '.join(ss), t))
  if dir:
    s = getInput('Guess %s dir = "%s", is this correct (y or n)?' % (code, dir))
    if s == 'y':
      codeDict['directory'] = dir
      return
    else:
      dir = getInput('Where is the %s dir? [%s]' % (code, dir), doLower=0, default=dir)
  else:
    dir = getInput('Where is the %s dir?' % code, doLower=0)

  while not dirContainsFiles(code, codeDict, dir, reqdFiles):
    doPrint('Could not find required files %s in %s' % (reqdFiles, dir))
    dir = getInput('Where is the %s dir?' % code, doLower=0)

  codeDict['directory'] = dir

def determineVersion(codeDict, code, prefix, minimal_version):

  pattern = prefix + '*'
  result = glob.glob(pattern)
  result = [x[len(prefix):] for x in result]
  c = re.compile('^(\d\.\d)')
  versions = [c.match(x).group(1) for x in result if c.match(x)]
  versions = [x for x in versions if x >= minimal_version]
  versions.sort()
  versions.reverse()

  if versions:
    version = versions[0]
    s = getInput('Guess %s version = %s (by looking), is this ok (y or n) (reply y unless sure otherwise)?' % (code, version))
  else:
    s = 'n'

  if s != 'y':
    version = getInput('What %s version do you have (found %s) (minimal acceptable %s)?' % (code, versions, minimal_version), doLower=0)
    if version not in versions:
      doPrint('Warning: %s version set to %s, something might go wrong')

  codeDict['version'] = version

def main(log_file = None):

  global fp_log

  # used to store information about where third-party code lives
  softwareDict = {}
  for key in ('X11', 'Tcl', 'Tk', 'Python', 'ElementTree', 'OpenGL', 'glut', 'Tix'):
    softwareDict[key] = {}

  if (log_file):
    fp_log = open(log_file, 'w')
  else:
    fp_log = None

  platform = getPlatform()
  softwareDict['platform'] = platform

  if platform == 'darwin':
    sysDirs = ('/sw', )
  else:
    sysDirs = ('/usr', '/usr/local')

  libDirs = []
  if distribution != api_distribution:
    bits = 64
    if platform != 'darwin':
      s = getInput('Are you using 64 bit libraries? (answer n unless you know otherwise) (y or n))?')
      if s[0] == 'y':
        libDirs.append('lib64')
      else:
        bits = 32
        libDirs.append('lib32')
    libDirs.append('lib')
    libDirs = tuple(libDirs)
    softwareDict['bits'] = bits
            
    # Analysis X11

    if distribution in (analysis_distribution, extend_nmr_distribution):
      codeDict = softwareDict['X11']
      dirsToCheck = ('/usr/X11R6', '/usr')
      reqdFiles = ( \
        ('include', 'X11/Xlib.h'),
        (libDirs, 'libX11.*'),
      )
      determineCodeDir(codeDict, 'X11', dirsToCheck, reqdFiles)

    # Tcl

    flag = 1
    haveTar = haveTclTarFile()
    codeDict = softwareDict['Tcl']
    setStandardCodeDict(codeDict, os.path.join(top_dir, tcl_rel_dir), tcltk_version)
    if haveTar:
      doPrint('You have choice of installing provided Tcl%s or using already installed Tcl.' % tcltk_version)
      s = getInput('Unpack Tcl%s (y or n)?' % tcltk_version)
      if s[0] == 'y':
        unpackTcl()
      if haveTclFiles():
        s = getInput('Compile and install Tcl%s (y or n)?' % tcltk_version)
        if s[0] == 'y':
          compileTcl()
          flag = 0
    else:
      doPrint('CCPN Tcl gzipped tar file not found, assuming using existing Tcl')
    if flag:
      dirsToCheck = (os.path.join(top_dir, tcl_rel_dir),) + sysDirs
      reqdFiles = ( \
        ('include', 'tcl.h'),
        (libDirs, 'tclConfig.sh'),
      )
      determineCodeDir(codeDict, 'Tcl', dirsToCheck, reqdFiles)
      prefix = os.path.join(codeDict['directory'], codeDict['lib'], 'libtcl')
      determineVersion(codeDict, 'Tcl', prefix, '8.2')

    # Tk

    flag = 1
    haveTar = haveTkTarFile()
    using_tcl_dir = codeDict['directory']
    using_tcl_lib = os.path.join(using_tcl_dir, codeDict['lib'])
    using_tcl_version = codeDict['version']
    codeDict = softwareDict['Tk']
    setStandardCodeDict(codeDict, os.path.join(top_dir, tk_rel_dir), tcltk_version)
    if haveTar and using_tcl_version == tcltk_version and using_tcl_dir == '%s/%s' % (top_dir, tcl_rel_dir):
      doPrint('You have choice of installing provided Tk%s or using already installed Tk.' % tcltk_version)
      s = getInput('Unpack Tk%s (y or n)?' % tcltk_version)
      if s[0] == 'y':
        unpackTk()
      if haveTkFiles():
        s = getInput('Compile and install Tk%s (y or n)?' % tcltk_version)
        if s[0] == 'y':
          tcl_lib_dir = os.path.join(using_tcl_dir, codeDict['lib'])
          x11_dir = softwareDict['X11']['directory']
          compileTk(using_tcl_lib)
          flag = 0
    elif haveTar:
      doPrint('CCPN Tk gzipped tar file found, but does not match Tcl, so ssuming using existing Tk')
    else:
      doPrint('CCPN Tk gzipped tar file not found, assuming using existing Tk')

    if flag:
      dirsToCheck = (using_tcl_dir, os.path.join(top_dir, tk_rel_dir)) + sysDirs
      reqdFiles = ( \
        ('include', 'tk.h'),
        (libDirs, 'tkConfig.sh'),
      )
      determineCodeDir(codeDict, 'Tk', dirsToCheck, reqdFiles)
      doPrint('Assuming Tk version is also %s' % using_tcl_version)

  # Tix
  if distribution in (analysis_distribution, extend_nmr_distribution):
    # only do if have CCPN versions of Tcl/Tk and Tix code
    tclCodeDict = softwareDict['Tcl']
    tcl_abs_dir  = tclCodeDict.get('directory')
    tcl_lib_dir  = tclCodeDict.get('lib')
    tkCodeDict = softwareDict['Tk']
    tk_abs_dir  = tkCodeDict.get('directory')
    if tcl_abs_dir == os.path.join(top_dir, tcl_rel_dir) and \
       tk_abs_dir == os.path.join(top_dir, tk_rel_dir):  # Tcl/Tk is CCPN
      haveTar = haveTixTarFile()
      codeDict = softwareDict['Tix']
      setStandardCodeDict(codeDict, os.path.join(top_dir, tix_rel_dir), tix_version)
      if haveTar:
        s = getInput('Unpack Tix%s (y or n)?' % tix_version)
        if s[0] == 'y':
          unpackTix()
        if haveTixFiles():
          s = getInput('Compile and install Tix%s (y or n)?' % tix_version)
          if s[0] == 'y':
            compileTix(softwareDict)

      tix_dir = 'Tix%s' % tix_release
      tix_lib_dir = os.path.join(tcl_lib_dir, tix_dir)
      if os.path.exists(os.path.join(tcl_abs_dir, tix_lib_dir)):
        # Note this is absolute, not relative like the other lib dirs
        codeDict['directory'] = tcl_abs_dir
        codeDict['lib'] = tix_lib_dir
      else:
        codeDict['directory'] = codeDict['lib'] = ''
        print('Do not have Tix so will not be able to use Aria in extendNmr script')

  # Python

  flag = 1
  haveTar = havePythonTarFile()
  codeDict = softwareDict['Python']
  setStandardCodeDict(codeDict, '%s/%s' % (top_dir, python_rel_dir), python_version)
  if haveTar:
    doPrint('You have choice of installing provided Python%s or using already installed Python.' % python_version)
    doPrint('It must be %s or higher, and it must have Tcl/Tk compiled in (latter not checked here).' % min_python_version)
    s = getInput('Unpack Python%s (y or n)?' % python_version)
    if s[0] == 'y':
      unpackPython()
    if havePythonFiles():
      s = getInput('Compile and install Python%s (y or n)?' % python_version)
      if s[0] == 'y':
        # Format Converter X11
        if distribution == format_distribution:
          xcodeDict = softwareDict['X11']
          dirsToCheck = ('/usr/X11R6', '/usr')
          reqdFiles = ( \
            ('include', 'X11/Xlib.h'),
            (libDirs, 'libX11.*'),
          )
          determineCodeDir(xcodeDict, 'X11', dirsToCheck, reqdFiles)

        compilePython(softwareDict)
        flag = 0
  else:
    doPrint('CCPN Python gzipped tar file not found, assuming using existing Python')

  if flag:
    dir = python_rel_dir[:-1] + '*'
    dirsToCheck = (os.path.join(top_dir, python_rel_dir),) + sysDirs
    reqdFiles = ( \
      ('include', dir),
      (libDirs, dir),
    )
    determineCodeDir(codeDict, 'Python', dirsToCheck, reqdFiles)
    prefix = os.path.join(codeDict['directory'], codeDict['include'], 'python')
    determineVersion(codeDict, 'Python', prefix, min_python_version)

  py_version = codeDict['version']

  # ElementTree

  element_tree_abs_dir = ''
  if py_version == '2.4':
    element_tree_abs_dir = os.path.join(top_dir, element_tree_rel_dir, element_tree_tar_dir)
    flag = 1
    haveTar = haveElementTreeTarFile()
    codeDict = softwareDict['ElementTree']
    setStandardCodeDict(codeDict, element_tree_abs_dir)
    if haveTar:
      doPrint('You have choice of installing provided ElementTree or using already installed Python.')
      s = getInput('Unpack ElementTree (y or n)?')
      if s[0] == 'y':
        unpackElementTree()
        flag = 0
    else:
      doPrint('CCPN ElementTree gzipped tar file not found, assuming using existing ElementTree')

    if flag:
      dirsToCheck = (element_tree_abs_dir,) + sysDirs
      reqdFiles = ( \
        ('elementtree', ''),
      )
      determineCodeDir(codeDict, 'ElementTree', dirsToCheck, reqdFiles)
    
  if distribution in (analysis_distribution, extend_nmr_distribution):

    # Numpy

    codeDict = softwareDict['Python']
    directory = codeDict['directory']
    doNumpy = False
    if directory == '%s/%s' % (top_dir, python_rel_dir):
      s = getInput('Do you want numpy used in Analysis (y or n) (n means some functionality not available)?')
      if s[0] == 'y':
        doNumpy = True

    if doNumpy:
      numpy_abs_dir = os.path.join(top_dir, numpy_rel_dir)
      flag = 1
      haveTar = haveNumpyTarFile()
      if haveTar:
        s = getInput('Unpack numpy%s (y or n)?' % numpy_version)
        if s[0] == 'y':
          unpackNumpy()
        if haveNumpyFiles():
          s = getInput('Compile and install numpy%s (y or n)?' % numpy_version)
          if s[0] == 'y':
            py_version = codeDict['version']
            compileNumpy(directory, py_version)
            flag = 0
      else:
        doPrint('CCPN numpy gzipped tar files not found, so not using numpy')

    # OpenGL

    s = getInput('Do you want OpenGL used in Analysis (y or n) (n means only get Tk)?')
    if s[0] == 'y':
      doOpenGL = True
    else:
      doOpenGL = False

    useFrameworkGlut = False
    if doOpenGL:
      mesa_abs_dir = os.path.join(top_dir, mesa_rel_dir)
      flag = 1
      haveTar = haveMesaTarFiles()
      codeDict = softwareDict['OpenGL']
      setStandardCodeDict(codeDict, os.path.join(top_dir, mesa_rel_dir), mesa_version)
      if haveTar:
        doPrint('You have choice of installing provided Mesa%s or using already installed OpenGL or Mesa.' % mesa_version)
        s = getInput('Unpack Mesa%s (y or n)?' % mesa_version)
        if s[0] == 'y':
          unpackMesa()
        if haveMesaFiles():
          s = getInput('Compile and install Mesa%s (y or n)?' % mesa_version)
          if s[0] == 'y':
            comp_arch = getCompArch(platform)
            compileMesa(comp_arch)
            flag = 0
      else:
        doPrint('CCPN Mesa gzipped tar files not found, assuming using existing Mesa or alternative OpenGL')

      if flag:
        if platform == 'darwin':
          s = getInput('Do you want to use OSX framework version of glut (y or n) (answer y unless you know otherwise)?')
          if s[0] == 'y':
            useFrameworkGlut = True
  
        x11_dir = softwareDict['X11']['directory']
        dirsToCheck = (os.path.join(top_dir, mesa_rel_dir),) + (x11_dir, '/usr/X11R6', '/usr')
        reqdFiles = ( \
          ('include', 'GL/gl.h'),
          (libDirs, 'libGL.*'),
        )
        determineCodeDir(codeDict, 'OpenGL', dirsToCheck, reqdFiles)

        open_gl_dir = codeDict['directory']
        codeDict = softwareDict['glut']
        reqdFiles = ( \
          ('include', 'glut.h'),
          (libDirs, 'libGL.*'),
        )
        if not useFrameworkGlut and \
            not dirContainsFiles('glut', codeDict, open_gl_dir, reqdFiles):
          dirsToCheck = (os.path.join(top_dir, mesa_rel_dir),) + (x11_dir, '/usr/X11R6', '/usr')
          determineCodeDir(codeDict, 'glut', dirsToCheck, reqdFiles)

    s = getInput('Compile and install %s code (y or n)?' % program_name)
    if s[0] == 'y':
      doPrint('You can create environment file from scratch (this does not copy it from environment_default.txt)')
      doPrint('If you have already created it and edited it by hand you probably do not want to create it again here.')
      s = getInput('Create environment file (y or n) (answer y unless you know otherwise)?')
      if s[0] == 'y':
        needGlutInit = 0
        if doOpenGL:
          s = getInput('Does your glut need explicit initialisation (OSX and freeglut probably y, ordinary glut probably n) (y or n)?')
          if s[0] == 'y':
            needGlutInit = 1
        s = getInput('Use -fPIC compiler flag (y or n) (if gcc compiler y, otherwise n; answer y unless you know otherwise)?')
        if s[0] == 'y':
          usePic = 1
        else:
          usePic = 0

        s = getInput('Use OPENMP compiler flags (y or n) (if gcc compiler >= 4.3 y, otherwise n; answer n unless you know otherwise; y allows Bayes peak separator code to use multi-processors)?')
        if s[0] == 'y':
          useOpenmp = 1
        else:
          useOpenmp = 0

        createEnvironmentFile(platform, softwareDict, doOpenGL,
                              needGlutInit, useFrameworkGlut,  usePic, useOpenmp)
      compileAnalysis(softwareDict)
      addInfoToVersion(softwareDict)
    createSymbolicLinks()

  if py_version in ('2.5', '2.6', '2.7'):
    uncommentFutureImport()

  if distribution != api_distribution:
    s = getInput('Do you want to create a bin directory (answer y unless you know otherwise) (y or n)?')
    if s[0] == 'y':
      shell = getShell()
      if shell in ('bash', 'sh'):
        useExport = 1
      elif shell in ('csh', 'tcsh'):
        useExport = 0
      else:
        s = getInput('Does your shell use export (rather than setenv) (bash y,  tcsh and csh n, not sure about others) (y or n)?')
        if s[0] == 'y':
          useExport = 1
        else:
          useExport = 0

      doPrint('Creating the bin directory')
      createBin(softwareDict, useExport, shell)

  if distribution == format_distribution:

    s = getInput('Run FormatConverter (as test) (y or n)?')
    if s[0] == 'y':
      runProgram(format_program)

  elif distribution == analysis_distribution:

    s = getInput('Install latest updates (from server) (y or n)?')
    if s[0] == 'y':
      print('Getting latest updates from server')
      runProgram(updateAuto_program)

    s = getInput('Run Analysis (as test) (y or n)?')
    if s[0] == 'y':
      runProgram(analysis_program)

  elif distribution == extend_nmr_distribution:

    """ TBD: comment out for now until done properly
    s = getInput('Install latest updates (from server) (y or n)?')
    if s[0] == 'y':
      print('Getting latest updates from server')
      runProgram(updateAuto_program)
"""

    s = getInput('Run ExtendNmr (as test) (y or n)?')
    if s[0] == 'y':
      runProgram(extend_nmr_program)

  doPrint('Finished installation script')

  if fp_log:
    fp_log.close()

if __name__ == '__main__':

  import sys

  top_dir = os.getcwd()

  if len(sys.argv) >= 2:
    distribution = sys.argv[1].lower()
    
  if distribution not in distributions:
    print('Error: require one argument: distribution')
    print('where distribution = one of %s' % str(distributions))
    sys.exit(1)

  program_name = program_names[distribution]

  n = 1
  log_file = 'log_%s_%d.txt' % (program_name, n)
  while os.path.exists(log_file):
    n = n + 1
    log_file = 'log_%s_%d.txt' % (program_name, n)
    
  print('Messages will be logged in "%s"' % log_file)
  main(log_file)
