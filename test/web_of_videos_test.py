import os
import unittest
import metapy
import string
import shutil

class TestDataset(unittest.TestCase):
    def setUp(self):
        self.prev_dir = os.getcwd()
        os.chdir("..")
        if os.path.exists("idx"):
            shutil.rmtree("idx", ignore_errors=False, onerror=None)

        print(os.getcwd())
        idx = metapy.index.make_inverted_index('config.toml')
        os.chdir(self.prev_dir)
        self.assertIsNotNone(idx)
        self.idx = idx
    
    def test_idx(self):
        #self.assertNotEqual(self.idx.num_docs(), 0)
        #self.assertNotEqual(self.idx.unique_terms(), 0)
        print(self.idx.num_docs())
        print(self.idx.unique_terms())
        
    def test_metadata(self):
        # title
#        try:
#            self.idx.metadata(0).get('title').encode('ascii')
#        except:
#            print("Title contains non-ascii characters")
        self.idx.metadata(0).get('title').encode('ascii')
        print(self.idx.metadata(0).get("title"))
        
        # path
        #printset = set(string.printable)
        #isprintable = set(self.idx.metadata(0).get("path")).issubset(printset)
        #self.assertTrue(isprintable)
        self.idx.metadata(0).get('path').encode('ascii')
        print(self.idx.metadata(0).get("path"))
        
        # description
        self.idx.metadata(0).get('description').encode('ascii')
        print(self.idx.metadata(0).get("description"))

        # url
        self.idx.metadata(0).get('url').encode('ascii')
        print(self.idx.metadata(0).get("url"))

        
if __name__ == '__main__':
	unittest.main()