import argparse
import cairo
import regex as re
import Bioinfo


parser = argparse.ArgumentParser()
def getArgs():
	parser.add_argument(
		"-f", help="input fasta file containing reads from genes", type=str, required=True
	)
	parser.add_argument(
		"-m", help="input file containing motifs of interest and their associated sequences", type=str, required=True
	)
	return parser.parse_args()

args = getArgs()

f_in = args.f
m_in = args.m

nt_dict = {
"W":["A","T"], "S":["C","G"], 'M':["A","C"], "K":["G","T"], "R":["A","G"], "Y":["C","T"], "B":["C","G","T"], "D":["A","G","T"], "H":["A","C","T"], "V":["A","C","G"], "N":["A","C","G","T"]
}

class reads:
	'''
	This class represents motifs
	'''

	def __init__(self,read,nt_dict):
		self.read = read
		self.nt_dict = nt_dict

	def create_re(read,nt_dict):
		new = ""
    
    	for ch in read:
        	if ch in nt_dict.keys():
            	new+=nt_dict[ch]
        	else:
            	new+=ch
    	return(new)
	
	def detect_exton(read):
		matches = re.finditer(r'[A-Z]+', gene)

		for x in matches:
    		print(x.span())

	

reads = []

with open(f_in, 'r') as f_in:
	Bioinfo.oneline_fasta(f_in, f_1l)

with open(m_in, 'r') as m_in, open(f1l, 'r') as f:
	while True:
		header = f.readline
		read = f.readline

		if header or read == "":
			break

		reads += (header, read)

	for line in motif:
		line = line.strip()

