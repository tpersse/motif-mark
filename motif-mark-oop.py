import argparse
import cairo
import random
import regex as re
import math


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

# print(f_in)
# new title for image created
title = f_in.split("/")[-1].split(".")[0] + ".png"
# print(title)


class Reads:
	'''
	This class represents motifs
	'''

	def __init__(self, read, nt_dict):
		self.read = read
		self.nt_dict = nt_dict

	def create_re(self, read, nt_dict):
		'''
		Function that creates regex characters to replace ambiguous nucleotides
		'''

		new = ""
    
		for ch in read:
			if ch.upper() in nt_dict.keys():
				new+=nt_dict[ch.upper()]
			else:
				new+=ch.upper()
		return(new)
	
	def detect_exon(self, read, longest):
		''' 
		Function that detects exons within a read and returns their positions within
		'''
        
		matches = re.finditer(r'[A-Z]+', read)

		for x in matches:
			newspan = []
			for val in x.span():
				val = int((val / longest) * 1000) + 100
				newspan.append(val)
			return([newspan, ((1,1,1, .8))])

	def detect_motifs(self, motifs, read, longest, colors_dict):
		'''
		Function that detects motifs within a read and returns their positions within the read
		'''

		y = []
		matches = []
		# motifs_upper = [m.upper() for m in motifs]
		# colors = dict.fromkeys(motifs_upper)
		colors = {}
        
		for motif in motifs:
			# print(motif)
			# red = random.random()
			# green = random.random()
			# blue = random.random()
			# colors[motif[0].upper()] = [motif[1], (red, green, blue, .5)]
			# matches[motif[1]] = re.finditer(fr'(?=({motif[0]}))', read, re.IGNORECASE)

			matches = re.finditer(fr'(?=({motif[0]}))', read, re.IGNORECASE)
			for x in matches:
				s = int((x.start(1) / longest) * 1000) + 100
				e = int((x.end(1) / longest) * 1000) + 100
				color = colors_dict[motif[0].upper()]
				y += [[[s, e], color]] ## do i need the motif here?


		return([y, colors])

nt_dict = {
"W":"[AT]", "S":"[CG]", 'M':"[AC]", "K":"[GT]", "R":"[AG]", "Y":"[CT]", "B":"[CGT]", "D":"[AGT]", "H":"[ACT]", "V":"[ACG]", "N":"[ACGT]"
}

cairo_dict = {}
motifs = []

## initializing variables for converting fasta to dictionary
head_ct = 0
first = True
seq = ""
seqs_dict = {}
longest = 0

def create_colors(motifs):
	colors_dict = {}
	for motif in motifs:
		red = random.random()
		green = random.random()
		blue = random.random()
		colors_dict[motif[0].upper()] = [motif[1], (red, green, blue, .5)]
	return(colors_dict)

## reading fasta file in line by line, then converting to a dictionary with header as key and sequence as value
with open(f_in, 'r') as f:
	while True:
		line = f.readline().strip()
		# print(line)
		if line == "":
			if len(seq) > longest:
				longest = len(seq)
			seqs_dict[header] = [seq, len(seq)]
			break
		if line.startswith(">"):
			head_ct += 1
			if first == True:
				header=line
				first = False
			else:
				if len(seq) > longest:
					longest = len(seq)
				seqs_dict[header] = [seq, len(seq)]
				seq = ""
			header = line
		else:
			seq += line

# print(seqs_dict)

with open(m_in, 'r') as motif:

## read in motifs

	for line in motif:
		line = line.strip()
		orig_motif = line
		m = Reads(line, nt_dict)
		re_m = m.create_re(line, nt_dict)
		motifs.append([re_m, orig_motif])

	colors_dict = create_colors(motifs)

## determine locations of exons, add to pycairo dict	
	for fa in seqs_dict.keys():
		# print(fa)
		# print('this is the seqs_dict', seqs_dict)
		# print(seqs_dict[fa][0])
		cairo_dict[fa] = {'exon':[], 'motif':[], 'length':0}
		# print(cairo_dict)
		# create read object for each fasta read
		r = Reads(seqs_dict[fa][0], nt_dict)
		cairo_dict[fa]['exon'] = [r.detect_exon(seqs_dict[fa][0], longest)] #adds coordinates of exon to first position in dictionary
		
		cairo_dict[fa]['motif'] = r.detect_motifs(motifs, seqs_dict[fa][0], longest, colors_dict)[0] #adds coordinates of motifs to second position in dictionary
		cairo_dict[fa]['length'] = int((seqs_dict[fa][1] / longest) * 1000)

# print(motifs)
# print(seqs_dict)
# print('this is the cairo dict', cairo_dict)
# print('this is the colors dict', colors_dict)


## When looping through the fasta lines, make sure to keep length of longest fasta line
# use it to standardize width of regions in output image
# make height of motifs dynamic too? divide by max number of motifs in a given fasta line

# print("THE FOLLOWING IS CAIRO DEBUGGING PRINT STATEMENTS")

### CAIRO PORTION ###
def plotCairo(cairo_dict:dict, title:str):
	# make height of figure dynamic
	height = (100 * math.ceil(len(motifs)/2)) + (head_ct * 200)
	line_start = (100 * math.ceil(len(motifs)/2)) + 100

	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1200, height)
	# create context
	c = cairo.Context(surface)

	# create legend
	i = 0
	up = 25
	side = 25
	for motif in colors_dict.keys():
		colors = colors_dict[motif][1]
		if i % 2 == 0:

			c.set_source_rgba(colors[0], colors[1], colors[2], colors[3])
			c.rectangle(side, up, 25, 25)
			c.fill()

			c.set_source_rgb(1,1,1)
			c.select_font_face("Courier", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
			c.move_to(side + 50, up + 20)
			c.set_font_size(30)

			c.show_text(colors_dict[motif][0].upper())

			side += 600

		if i % 2 == 1: 
			c.set_source_rgba(colors[0], colors[1], colors[2], colors[3])
			c.rectangle(side, up, 25, 25)
			c.fill()

			c.set_source_rgb(1,1,1)
			c.select_font_face("Courier", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
			c.move_to(side + 50, up + 20)
			c.set_font_size(30)

			c.show_text(colors_dict[motif][0].upper())

			up += 100
			side += (-600)
		i += 1



	# create line and exon/motif details for each gene via loop
	for gene in cairo_dict.keys():
		
		# write gene name
		c.move_to(50, line_start - 75)
		c.set_source_rgb(1,1,1)
		c.select_font_face("Courier", cairo.FONT_SLANT_NORMAL)
		c.set_font_size(25)
		c.show_text(gene)


		# draw line for whole gene
		gene_len = cairo_dict[gene]['length']
		c.set_line_width(5)
		c.set_source_rgba(1,1,1, .8)

		c.move_to(100, line_start)
		c.line_to(gene_len + 100, line_start)
		c.stroke()

		# exon = cairo_dict[gene]['exon']
		# print(exon)
		# exon_start = exon[0][0]
		# exon_stop = exon[0][1]

		for exon in cairo_dict[gene]['exon']:
			# print(exon)
			# print(exon[0])

			exon_start = exon[0][0]
			exon_stop = exon[0][1]
			exon_color = exon[1]
			# print(exon_color[0])
			c.set_source_rgba(exon_color[0], exon_color[1], exon_color[2], exon_color[3])
			c.move_to(100, line_start)
			c.rectangle(exon_start, (line_start - 50), (exon_stop - exon_start), 100)
			c.fill()
			c.stroke()

		for motif in cairo_dict[gene]['motif']:
			# print(motif)
			motif_start = motif[0][0]
			motif_stop = motif[0][1]
			motif_color = motif[1][1]
			# print(motif_color)
			c.set_source_rgba(motif_color[0], motif_color[1], motif_color[2], motif_color[3])
			c.move_to(100, line_start)
			c.rectangle(motif_start, (line_start - 30), (motif_stop - motif_start), 60)
			c.fill()
			c.stroke()
		line_start += 200
		

	surface.write_to_png(title)


plotCairo(cairo_dict, title)


