##
## coding: UTF-8
## Subversion for Sublime Text 2
## @version 0.2
## @author Timmy Sjöstedt
## @author Patrik Ring
## @license GPL
##

import sublime, sublime_plugin, subprocess

class SubversionCommand(sublime_plugin.TextCommand):
	settings = sublime.load_settings('subversion')

	def run(self, edit, cmd):
		if cmd == "togglefolders": # Toggle the use of folders
			newbool = not self.settings.get('usefolder')
			self.settings.set('usefolder', newbool)
			if newbool:
				sublime.status_message("SVN: Using folders")
			else:
				sublime.status_message("SVN: Not using folders")
			return

		filename = self.view.file_name()
		folders = self.view.window().folders()
		path = filename

		if filename == None:
			sublime.error_message("File is not saved")
			return
		
		if self.settings.get('usefolder') == True: # Should we use a folder?
			for folder in folders:
				if filename.find(folder) != -1:
					path = folder
					break

		if cmd == "commit":
			#### COMMIT ####
			self.prepare_commit(path)
		elif cmd == "update":
			#### UPDATE ####
			self.do_update(path)
		elif cmd == "add":
			#### ADD FILES ####
			self.do_add(path)
		elif cmd == 'commitandadd':
			#### ADD AND COMMIT ####
			self.do_add(path)
			self.prepare_commit(path)

	def prepare_commit(self,path):
		diff = self.execute(["svn", "diff", path], False)
		if diff['stderr'] != "":
			sublime.error_message(diff['stderr'])
			return
		elif diff['stdout'] == "":
			sublime.status_message("SVN: Nothing to commit!")
			return

		if self.settings.get("commitmessage") == None:
			self.settings.set("commitmessage", "")
		
		self.view.window().show_input_panel(
			"Commit Message:",
			self.settings.get("commitmessage"),
			lambda s: self.do_commit(path, s),
			None,
			None
		)

	def do_commit(self, path, message):
		self.settings.set("commitmessage", message)
		ret = self.execute(["svn", "commit", path, "--non-interactive", "-m", message])

		self.print_in_new_file(ret['stderr'] + ret['stdout'])
	
	def do_update(self, path):
		ret = self.execute(["svn", "update", path])

		self.print_in_new_file(ret['stderr'] + ret['stdout'])

	def do_add(self,path):
		ret = self.execute(['svn st ' + path + ' | grep ^? | sed s/?// | xargs -r svn add $1'],True,True)
		if ret.get('stdout') == '':
			sublime.status_message("SVN: No files added")
			
	def execute(self, command, showoutput = True,use_shell = False):
		p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=use_shell)
		stderr = p.stderr.read()
		stdout = p.stdout.read()
		stdout_oneline = stdout.replace("\n", " ")

		if showoutput:
			sublime.status_message("SVN: " + stdout_oneline)

		if showoutput and stderr != "":
			sublime.error_message(stderr)
		
		return {"stdout":stdout, "stdout_oneline":stdout_oneline, "stderr":stderr}
	
	def print_in_new_file(self, text):
		new = self.view.window().new_file()
		edit = new.begin_edit()
		new.insert(edit, 0, text)
		new.end_edit(edit)
		new.set_scratch(True)
