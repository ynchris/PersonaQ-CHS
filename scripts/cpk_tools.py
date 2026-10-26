"""Keep verbose CRI progress bars in local logs, with errors surfaced clearly."""
import subprocess

def run_logged(args,cwd,log_name):
    log=cwd/log_name
    with log.open('wb') as stream:
        result=subprocess.run([str(x) for x in args],cwd=cwd,stdout=stream,stderr=subprocess.STDOUT)
    if result.returncode:
        tail=log.read_bytes()[-3000:].decode('utf-8',errors='replace')
        raise RuntimeError(f'CPK tool failed ({result.returncode}); {log}\n{tail}')
    print(f'CPK tool completed; log: {log.name}',flush=True)
