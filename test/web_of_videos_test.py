import os
import unittest
import metapy
import string
import shutil

class TestDataset(unittest.TestCase):
	def setUp(self):

		self.prev_dir = os.getcwd()
		os.chdir("..")
		if os.path.exists("dir"):
			shutil.rmtree("idx", ignore_errors=False, onerror=None)
		#os.remove("idx/*")
		#os.rmdir("idx")
		self.idx = None
		self.idx = metapy.index.make_inverted_index('config.toml')
		
	def test_title(self):
		#printset = set(string.printable)
		#isprintable = set(self.idx.metadata(0).get("title")).issubset(printset)
		print(self.idx.num_docs())
		print(self.idx.unique_terms())
		
		print(self.idx.metadata(0).get("title"))
		print(self.idx.metadata(0).get("path"))
		print(self.idx.metadata(0).get("url"))
		print(self.idx.metadata(0).get("description"))

if __name__ == '__main__':
	unittest.main()