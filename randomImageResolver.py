# Tanner Bohn
# RandomImageResolver

from __future__ import print_function

from PIL import Image, ImageFilter

import random
import numpy as np
import math
import colorsys
from Tkinter import Tk, Scale, Label, Button, HORIZONTAL, FLAT, Entry, Toplevel, Canvas
import tkcolorpicker


class ColourSetter:

	def __init__(self, parent):
		self.parent = parent

		self.root = self.parent.root
		

		self.size = (1, 1)
		self.colours = [(0, 0, 255)]
		
		self.colour_cells = []

		self.draw(init=True)

		return

	def draw(self, init=False):

		if init:
			self.canvas_width, self.canvas_height = 0, 0
			self.canvas = Canvas(self.root, bg="black")
			self.colour_cells = []

		# update colour cells

		while self.colour_cells != []:
			#print('killing...')
			self.colour_cells[0].unbind("<Button-1>")
			self.colour_cells[0].destroy()
			del self.colour_cells[0]


		self.button_index_dict = dict()

		nb_colours = self.size[0]*self.size[1]
		pos = 0
		for ix in range(self.size[0]):
			for iy in range(self.size[1]):
				colour = self.colours[pos]

				# create the new cell
				colour_cell = Button(self.canvas, bg=toHex([v/255. for v in colour]), activebackground=toHex([v/255. for v in colour]))
				colour_cell.bind("<Button-1>", self.handleColourSelector)


				# place the cell
				cell_width = self.canvas_width/self.size[0]
				cell_height = self.canvas_height/self.size[1]

				cell_width = min(cell_width, cell_height)
				cell_height = min(cell_width, cell_height)

				x = ix * cell_width
				y = iy * cell_height
				colour_cell.place(x = x, y = y, width = cell_width, height=cell_height)

				self.button_index_dict[colour_cell] = pos
				self.colour_cells.append(colour_cell)

				pos += 1

	def handleColourSelector(self, event=[]):

		#print("SELECTOR:", event)
		#print(dir(event))

		btn_pos = self.button_index_dict[event.widget]

		#event.widget.configure(bg="black")
		new_colour_rgb, new_colour_hex = tkcolorpicker.askcolor(color=self.colours[btn_pos])

		if new_colour_rgb == None:
			print("No colour selected.")
			return


		
		self.colours[btn_pos] = new_colour_rgb
		self.draw()

		return


	def place(self, x, y, width, height):

		self.canvas_width = width
		self.canvas_height = height

		self.canvas.place(x=x, y=y, width=width, height=height)

		return

	def setGridSize(self, size):

		

		self.size = size

		nb_colours = self.size[0] * self.size[1]

		# need to make sure there are the proper number of colours
		self.colours = self.colours[:nb_colours]
		if len(self.colours) < nb_colours:
			for _ in range(nb_colours - len(self.colours)):
				self.colours.append(self.colours[-1])

		self.draw()

	def randomize(self):

		nb_colours = self.size[0] * self.size[1]

		new_seed_colours = []
		for _ in range(nb_colours):
			c = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
			new_seed_colours.append(c)

		self.colours = new_seed_colours

		self.draw()


		return

	def getSeed(self):

		# return the seed image with specified colours

		N1 = Image.new('RGB', self.size, "white")
		pix1 = N1.load()
		pos = 0
		for x in range(N1.size[0]):
			for y in range(N1.size[1]):

				r, g, b = self.colours[pos]
				pix1[x,y] = (r, g, b)

				pos += 1

		return N1

class MyDialog:
	def __init__(self, parent):

		top = self.top = Toplevel(parent)

		Label(top, text="Enter filename (+.png):").pack()

		self.e = Entry(top)
		self.e.pack(padx=5)

		b = Button(top, text="OK", command=self.ok)
		b.pack(pady=5)
		self.value = ""

	def ok(self):

		self.value = self.e.get()

		self.top.destroy()

class ResolverInterface:

	def __init__(self):

		self.window_width = 800
		self.window_height = 10*40

		self.root = Tk()

		self.colourSetter = ColourSetter(self)

		self.draw(init=True)

		self.root.mainloop()

		return

	def draw(self, init=False):


		self.root.geometry("%dx%d" % (self.window_width, self.window_height))
		self.root.title("RandomImageResolver")

		# set colours
		self.root.configure(background="black")

		self.tk_iters_scale = Scale(self.root)
		self.tk_iters_scale_label = Label(self.root, text="Iters")

		self.tk_width_scale = Scale(self.root, command=self.handleGridSizeChange)
		self.tk_width_scale_label = Label(self.root, text="Width")

		self.tk_height_scale = Scale(self.root, command=self.handleGridSizeChange)
		self.tk_height_scale_label = Label(self.root, text="Height")

		self.tk_hueStd_scale = Scale(self.root)
		self.tk_hueStd_scale_label = Label(self.root, text="HueStd")

		self.tk_saturStd_scale = Scale(self.root)
		self.tk_saturStd_scale_label = Label(self.root, text="SaturStd")

		self.tk_valueStd_scale = Scale(self.root)
		self.tk_valueStd_scale_label = Label(self.root, text="ValueStd")

		self.tk_stdDecay_scale = Scale(self.root)
		self.tk_stdDecay_scale_label = Label(self.root, text="StdDecay")

		self.tk_parentNoise_scale = Scale(self.root)
		self.tk_parentNoise_scale_label = Label(self.root, text="ParentPosNoise")

		self.tk_parentNoiseDecay_scale = Scale(self.root)
		self.tk_parentNoiseDecay_scale_label = Label(self.root, text="ParentPosNoiseDecay")

		# start width, start height, hue shift std, saturation std, value std

		self.tk_randomize = Button(self.root, text="Randomize", command=self.handleRandomize)
		self.tk_generate = Button(self.root, text="Generate", command=self.handleGenerate)
		self.tk_expand = Button(self.root, text="Expand", command=self.handleExpand)
		self.tk_save = Button(self.root, text="Save", command=self.handleSave)

		self.tk_iters_scale.configure(bd=0, from_=1, to=10, orient=HORIZONTAL, sliderrelief=FLAT, resolution=1)
		self.tk_iters_scale.set(8)

		self.tk_width_scale.configure(bd=0, from_=1, to=10, orient=HORIZONTAL, sliderrelief=FLAT, resolution=1)
		self.tk_width_scale.set(2)

		self.tk_height_scale.configure(bd=0, from_=1, to=10, orient=HORIZONTAL, sliderrelief=FLAT, resolution=1)
		self.tk_height_scale.set(2)

		self.tk_hueStd_scale.configure(bd=0, from_=0, to=0.1, orient=HORIZONTAL, sliderrelief=FLAT, resolution=0.005)
		self.tk_hueStd_scale.set(0.01)

		self.tk_saturStd_scale.configure(bd=0, from_=0, to=0.4, orient=HORIZONTAL, sliderrelief=FLAT, resolution=0.01)
		self.tk_saturStd_scale.set(0.07)

		self.tk_valueStd_scale.configure(bd=0, from_=0, to=0.4, orient=HORIZONTAL, sliderrelief=FLAT, resolution=0.01)
		self.tk_valueStd_scale.set(0.07)

		self.tk_stdDecay_scale.configure(bd=0, from_=0, to=1., orient=HORIZONTAL, sliderrelief=FLAT, resolution=0.1)
		self.tk_stdDecay_scale.set(0.)

		self.tk_parentNoise_scale.configure(bd=0, from_=0, to=1, orient=HORIZONTAL, sliderrelief=FLAT, resolution=0.05)
		self.tk_parentNoise_scale.set(0.15)

		self.tk_parentNoiseDecay_scale.configure(bd=0, from_=0, to=1, orient=HORIZONTAL, sliderrelief=FLAT, resolution=0.1)
		self.tk_parentNoiseDecay_scale.set(0.)

		self.root.bind("<Configure>", self.resize)


		# make sure colourSetter size is synced to default
		self.colourSetter.setGridSize((self.tk_width_scale.get(), self.tk_height_scale.get()))
		self.colourSetter.randomize()

		return

	def handleRandomize(self, event=[]):

		# generate a new random set of colours
		start_width = self.tk_width_scale.get()
		start_height = self.tk_height_scale.get()

		self.colourSetter.setGridSize((start_width, start_height))
		self.colourSetter.randomize()		

		return

	def handleGenerate(self, event=[]):

		'''
		iters = self.tk_iters_scale.get()
		start_width = self.tk_width_scale.get()
		start_height = self.tk_height_scale.get()
		hueStd = self.tk_hueStd_scale.get()
		staurStd = self.tk_saturStd_scale.get()
		valueStd = self.tk_valueStd_scale.get()
		std_decay = self.tk_stdDecay_scale.get()
		parent_pos_noise = self.tk_parentNoise_scale.get()

		self.IMGS = newImage(start_size=(start_width, start_height), iters=iters, hsv_std = (hueStd, staurStd, valueStd), std_decay=std_decay, parent_pos_noise=parent_pos_noise)
		self.IMGS[-1].show()
		'''

		iters = self.tk_iters_scale.get()
		hueStd = self.tk_hueStd_scale.get()
		staurStd = self.tk_saturStd_scale.get()
		valueStd = self.tk_valueStd_scale.get()
		std_decay = self.tk_stdDecay_scale.get()
		parent_pos_noise = self.tk_parentNoise_scale.get()
		parent_pos_noise_decay = self.tk_parentNoiseDecay_scale.get()
		seed = self.colourSetter.getSeed()

		self.IMGS = newImage(seed=seed, iters=iters, hsv_std = (hueStd, staurStd, valueStd), std_decay=std_decay, parent_pos_noise=parent_pos_noise, parent_pos_noise_decay=parent_pos_noise_decay)
		self.IMGS[-1].show()

		return

	def handleExpand(self, event=[]):

		hueStd = self.tk_hueStd_scale.get()
		staurStd = self.tk_saturStd_scale.get()
		valueStd = self.tk_valueStd_scale.get()
		std_decay = self.tk_stdDecay_scale.get()
		parent_pos_noise = self.tk_parentNoise_scale.get()
		parent_pos_noise_decay = self.tk_parentNoiseDecay_scale.get()

		new_imgs = newImage(seed=self.IMGS[-1], iters=1, hsv_std = (hueStd, staurStd, valueStd), std_decay=std_decay, parent_pos_noise=parent_pos_noise, parent_pos_noise_decay=parent_pos_noise_decay, inum_offset=len(self.IMGS))
		self.IMGS.append(new_imgs[-1])
		self.IMGS[-1].show()
 
		return

	def handleSave(self, event=[]):
		# save the current image with prompt for name

		#self.tk_entry.focus()

		d = MyDialog(self.root)
		self.root.wait_window(d.top)
		#print("You said: ", d.value)
		fname = d.value.strip()

		try:
			if '.png' not in fname:
				fname = fname+".png"
			self.IMGS[-1].save(fname)
			print("Saved.")
		except:
			#print("Error: Have not generated image yet.")
			print("Error: Nothing saved")

	def handleGridSizeChange(self, event=[]):

		self.colourSetter.setGridSize((self.tk_width_scale.get(), self.tk_height_scale.get()))

		return



	def resize(self, event=[]):
		pixelX=self.root.winfo_width()
		pixelY=self.root.winfo_height()

		self.window_width = pixelX
		self.window_height = pixelY

		nb_scales = 9

		colourSetterWidth = 200
		label_width = 150
		button_width = 75
		scale_height = self.window_height/nb_scales

		cur_height = 0
		scale_width = self.window_width - label_width - button_width - colourSetterWidth
		scale_x = label_width+colourSetterWidth
		self.tk_iters_scale.place(x=scale_x, y=cur_height, width = scale_width, height = scale_height)
		self.tk_iters_scale_label.place(x=colourSetterWidth, y=cur_height, width = label_width, height = scale_height)
		
		cur_height += scale_height
		self.tk_width_scale.place(x=scale_x, y=cur_height, width = scale_width, height = scale_height)
		self.tk_width_scale_label.place(x=colourSetterWidth, y=cur_height, width = label_width, height = scale_height)

		cur_height += scale_height
		self.tk_height_scale.place(x=scale_x, y=cur_height, width = scale_width, height = scale_height)
		self.tk_height_scale_label.place(x=colourSetterWidth, y=cur_height, width = label_width, height = scale_height)

		cur_height += scale_height
		self.tk_hueStd_scale.place(x=scale_x, y=cur_height, width = scale_width, height = scale_height)
		self.tk_hueStd_scale_label.place(x=colourSetterWidth, y=cur_height, width = label_width, height = scale_height)

		cur_height += scale_height
		self.tk_saturStd_scale.place(x=scale_x, y=cur_height, width = scale_width, height = scale_height)
		self.tk_saturStd_scale_label.place(x=colourSetterWidth, y=cur_height, width = label_width, height = scale_height)

		cur_height += scale_height
		self.tk_valueStd_scale.place(x=scale_x, y=cur_height, width = scale_width, height = scale_height)
		self.tk_valueStd_scale_label.place(x=colourSetterWidth, y=cur_height, width = label_width, height = scale_height)

		cur_height += scale_height
		self.tk_stdDecay_scale.place(x=scale_x, y=cur_height, width = scale_width, height = scale_height)
		self.tk_stdDecay_scale_label.place(x=colourSetterWidth, y=cur_height, width = label_width, height = scale_height)

		cur_height += scale_height
		self.tk_parentNoise_scale.place(x=scale_x, y=cur_height, width = scale_width, height = scale_height)
		self.tk_parentNoise_scale_label.place(x=colourSetterWidth, y=cur_height, width = label_width, height = scale_height)

		cur_height += scale_height
		self.tk_parentNoiseDecay_scale.place(x=scale_x, y=cur_height, width = scale_width, height = scale_height)
		self.tk_parentNoiseDecay_scale_label.place(x=colourSetterWidth, y=cur_height, width = label_width, height = scale_height)


		randomize_height = int(round(self.window_height*0.3))
		generate_height = int(round(self.window_height*0.3))
		expand_height = int(round(self.window_height*0.2))
		save_height = int(round(self.window_height*0.2))

		button_cur_ypos = 0.
		self.tk_randomize.place(x=self.window_width-button_width, y=button_cur_ypos, width=button_width, height=randomize_height)
		button_cur_ypos += randomize_height

		self.tk_generate.place(x=self.window_width-button_width, y=button_cur_ypos, width=button_width, height=generate_height)
		button_cur_ypos += generate_height

		self.tk_expand.place(x=self.window_width-button_width, y=button_cur_ypos, width=button_width, height= expand_height)
		button_cur_ypos += expand_height

		self.tk_save.place(x=self.window_width-button_width, y=button_cur_ypos, width=button_width, height= save_height)
		button_cur_ypos += save_height

		self.colourSetter.place(x=0, y=0, width = colourSetterWidth, height = self.window_height)


def bound(m, M, a):
	return min(max(a, m), M)

def toHex(cvec):
	rgb = tuple([int(255*v) for v in cvec])
	return '#%02x%02x%02x' % rgb

def weighted_choice(choices):
	total = sum(w for c, w in choices)
	r = random.uniform(0, total)
	upto = 0
	for c, w in choices:
		if upto + w >= r:
			return c
		upto += w
	assert False, "Shouldn't get here"

def modifyColour(parent_colour, hsv_std):
	# take parent colour and generate child colour
	#r, g, b = parent_colour


	h_std, s_std, v_std = hsv_std

	h, s, v = colorsys.rgb_to_hsv(*[val/255. for val in parent_colour])

	#hue_shift_choices = [0, 0, 0, 0]+[random.choice([-90, 90])] + [180]

	#base_hsv = (rand(0, 1), rand(0.25, 1), rand(0.5, 1))

	#V = 36
	# hue
	hue_shift = np.random.normal(loc=0., scale=h_std*360)

	new_h = ((int(h*360) + hue_shift)%360)/360.
	new_s = bound(0, 1, s+np.random.normal(0., s_std))  # saturation
	new_v = bound(0, 1, v+np.random.normal(0., v_std))  # lighter or darker

	c = (new_h, new_s, new_v)


	r, g, b = colorsys.hsv_to_rgb(*c)
	r = int(r*255.)
	g = int(g*255.)
	b = int(b*255.)

	return (r, g, b)

def newImage(start_size=(2,2), seed=None, iters=6, hsv_std=(0.1, 0.1, 0.1), std_decay=0., parent_pos_noise=0., parent_pos_noise_decay=0., inum_offset=0):

	IMGS = []
	PIX = []

	# if no seed image, start with noise

	if seed == None:
		N1 = Image.new('RGB', start_size, "white")
		pix1 = N1.load()
		for x in range(N1.size[0]):
			for y in range(N1.size[1]):

				r, g, b = colorsys.hsv_to_rgb(random.random(), #bound(0, 1, np.random.normal(start_satur, 0.5)), 
								np.random.uniform(0, 1.),
								random.random())
				r = int(r*255.)
				g = int(g*255.)
				b = int(b*255.)
				pix1[x,y] = (r, g, b)

		IMGS.append(N1)
		PIX.append(pix1)
	else:
		# if given seed, rescale it to start size

		IMGS.append(seed)
		PIX.append(seed.load())



	for inum in range(iters):

		prevSize = IMGS[inum].size

		N2 = Image.new('RGB', (prevSize[0]*2,prevSize[1]*2), "white")
		pix2 = N2.load()

		# for each pixel in new image, locate parent pixel in previous image and get colour
		for xi in range(N2.size[0]):
			for yi in range(N2.size[1]):
				parent_loc = (xi/2, yi/2)
				parent_colour = PIX[inum][parent_loc[0], parent_loc[1]]
				# with small probability, instead choose pixel near the parent
				#neighbor_prob = parent_pos_noise
				# add decay to pos noise
				neighbor_prob = parent_pos_noise/(1. + parent_pos_noise_decay*(inum+inum_offset))

				if neighbor_prob > random.random():
					try:
						parent_colour = PIX[inum][parent_loc[0]+random.choice([-1, 0, 1]), parent_loc[1]+random.choice([-1, 0, 1])]
					except:
						pass
				hsv_std_mod = [v/(1. + std_decay*(inum+inum_offset)) for v in hsv_std]
				child_colour = modifyColour(parent_colour, hsv_std=hsv_std_mod)
				pix2[xi, yi] = child_colour

		IMGS.append(N2)
		PIX.append(pix2)

		print("Done ",inum)


	return IMGS


RI = ResolverInterface()