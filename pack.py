import csv
import os
import shutil
import subprocess

assemblyrelpath = 'sdk/bin'
clibrelpath = 'sdk/lib'
localartifactpath = 'original_packages'
nugetpackagepath = 'nuget_packages'
		
def copysdklocally(path, packagename, version, config):
	# copy all assemblies, and anything else in the bin folder of the FBT/FDT package
	binpath = os.path.join(path, assemblyrelpath, config)
	localbinpath = os.path.join(localartifactpath, packagename, version, assemblyrelpath, config)
	shutil.copytree(binpath, localbinpath, ignore=shutil.ignore_patterns('*.pdb'))
	
	# copy lib files, for an easy way to later check whether a dll is a .net assembly or not
	libpath = os.path.join(path, clibrelpath, config)
	if(os.path.exists(libpath)):
		locallibpath = os.path.join(localartifactpath, packagename, version, clibrelpath, config)
		shutil.copytree(libpath, locallibpath)
	
def determinereferences(packagename, version, config):
	binpath = os.path.join(localartifactpath, packagename, version, assemblyrelpath, config)
	references = ''
		
	for file in os.listdir(binpath):
		if(file.endswith(".dll")):
			csharpassembly = True
			libpath = os.path.join(localartifactpath, packagename, version, clibrelpath, config)
			if os.path.exists(libpath):				
				libfile = os.path.join(libpath, os.path.splitext(file)[0]+'.lib')
				if(os.path.isfile(libfile)):
					csharpassembly = False
			if csharpassembly:
				references += '\t\t<reference file="{0}" />\n'.format(file)
	return references.strip()
					
def createnuspecfile(packagename, version, references):
	template = None
	with open('template.nuspec', 'r') as file:
		template = file.read()
		
	template = template.replace('$references$', references)
	
	with open(os.path.join(localartifactpath, packagename, version, packagename + '.nuspec'), 'w') as file:
		file.write(template)
		
def createtargetsfile(packagename, version):
	shutil.copy('template.targets', os.path.join(localartifactpath, packagename, version, packagename + '.targets'))
		
def packnugetpackage(packagename, version, config):
	if not os.path.exists(nugetpackagepath):
		os.makedirs(nugetpackagepath)

	basepath = os.path.join(localartifactpath, packagename, version)
	nuspecfile = os.path.join(basepath, packagename + '.nuspec')
	properties = 'id={0};version={1};configuration={2}'.format(packagename, version, config)
	subprocess.call(['nuget', 'pack', nuspecfile, '-OutputDirectory', nugetpackagepath, '-properties', properties, '-BasePath', basepath])

with open('initial_packages.csv') as csvfile:
	packagereader = csv.reader(csvfile, delimiter=',')
	for row in packagereader:
		packagename = row[0]
		version = row[1]
		originalpackagepath = row[2]
		config = row[3]
		
		copysdklocally(originalpackagepath, packagename, version, config)
		references = determinereferences(packagename, version, config)
		createnuspecfile(packagename, version, references)
		createtargetsfile(packagename, version)
		packnugetpackage(packagename, version, config)
					
		print '{0:25}DONE'.format(row[0])