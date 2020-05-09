import re
import urllib.parse

class GFlareRobots:
	def __init__(self, robots_txt):
		self.robots_txt = robots_txt
		self.disallows = []
		self.allows = []
		self.allow_lines = None
		self.disallow_lines = None
		if self.robots_txt:
			self.parse_rules()
			self.allows = self.process_rules(self.allows)
			self.disallows = self.process_rules(self.disallows)

	def remove_spaces(self, inp):
		return " ".join(inp.split(" "))

	def set_robots_txt(self, robots_txt):
		self.robots_txt = robots_txt
		self.parse_rules()
		self.allows = self.process_rules(self.allows)
		self.disallows = self.process_rules(self.disallows)

	def parse_rules(self):
		exp_disallow_rule = re.compile(r"\s*Disallow:\s*(.*)", re.IGNORECASE)
		exp_allow_rule = re.compile(r"\s*Allow:\s*(.*)", re.IGNORECASE)

		for row in self.robots_txt.splitlines():
			row = self.remove_spaces(row)
			if d_match:= re.match(exp_disallow_rule, row): self.disallows.append(d_match.group(1))
			if a_match:= re.match(exp_allow_rule, row): self.allows.append(a_match.group(1))

		self.allow_lines = self.allows.copy()
		self.disallow_lines = self.disallows.copy()

	def process_rules(self, rules):
		rules = [re.escape(l).replace("\*", ".*").replace("\$", "$") for l in rules]
		for i, r in enumerate(rules):
			if not re.match(r"^\.\*.*", r): rules[i] = f"^{r}"
			if not re.match(r".*\$|.*\.\*$", r): rules[i] = f"{r}.*"
		return "|".join([f"({r})" for r in rules])

	def is_allowed(self, url):
		scheme, netloc, path, query, frag = urllib.parse.urlsplit(url)
		url = str(urllib.parse.urlunsplit(("", "", path, query, "")))
		allow = None
		disallow = None

		if self.allow_lines:
			if a_match:= re.match(self.allows, url):
				group = 0
				for m in a_match.groups():
					group += 1
					if m: break
				allow = self.allow_lines[group -1]
		if self.disallow_lines:
			if d_match:= re.match(self.disallows, url):
				group = 0
				for m in d_match.groups():
					group += 1
					if m: break
				disallow = self.disallow_lines[group -1]

		if allow and not disallow: return True
		if not allow and disallow: return False
		if allow and disallow: return len(allow) >= len(disallow)
		return True