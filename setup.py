from setuptools import setup, find_packages

setup(
	name='CSImportResources',
	version='0.3',
	py_modules=['CSImportResources'],
	packages=find_packages(),
	install_requires=['cloudshell_automation_api',],
	author="graboskyc",
	author_email="chris@grabosky.net",
	entry_points='''
		[console_scripts]
		CSImportResources=CSImportResources:cli
	''',
)
