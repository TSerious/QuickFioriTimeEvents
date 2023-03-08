import pkg_resources
from subprocess import call

call("pip install --upgrade pip")
packages = [dist.project_name for dist in pkg_resources.working_set]
call("pip install --upgrade " + ' '.join(packages), shell=True)