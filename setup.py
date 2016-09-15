from setuptools import setup

files = [
    "ansible/module_utils",
    "ansible/modules/dcos",
]

setup(name='ansible-modules-dcos',
      version='0.1',
      description='DCOS Ansible Modules',
      url='https://github.webapps.rr.com/ApplicationServices/ansible-modules-dcos',
      author='Kevin Wood',
      author_email='kevin.wood1@charter.com',
      license='MIT',
      packages=files,
      )
