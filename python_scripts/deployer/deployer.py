import subprocess

def compile_cpp_project():
    subprocess.run(["./compile.sh"], check=True)

def deploy_to_mcu():
    subprocess.run(["./deploy.sh"], check=True)
