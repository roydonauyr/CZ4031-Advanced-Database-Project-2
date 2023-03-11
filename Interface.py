from pathlib import Path
from math import floor

# from types import NoneType
NoneType = type(None)

from typing import Tuple, Union
from preprocessing import *
from annotation import *

# from tkinter import *
# Explicit imports to satisfy Flake8
import tkinter as tk
from tkinter import font
from tkinter import messagebox


# from tkinter.ttk import *

# Functions for the appication

def countLeafNodes(node: PlanNode):
	leafNodesNum = 0
	queue = [node]
	while (len(queue) > 0):
		curNode = queue.pop()
		if (len(curNode.children) > 0):
			for node in curNode.children:
				queue.append(node)
		else:
			leafNodesNum += 1
	return leafNodesNum


class DisplayNode():
	def __init__(self) -> None:
		self.children: list[DisplayNode] = []
		self.text = ""
		self.annotations = ""
		self.depth: int = 0
		self.left_bound: int = 0
		self.right_bound: int = 0


def createDisplayNode(root: PlanNode):
	maxBound = countLeafNodes(root)
	rootDisplay = DisplayNode()
	rootDisplay.left_bound = 0
	rootDisplay.right_bound = maxBound
	rootDisplay.text = root.attributes['Node Type']
	rootDisplay.annotations = root.annotations
	nodeQueue: list[Tuple[DisplayNode, PlanNode, Tuple[int, int]]] = []  # tuple of (displayNode parent, node child)
	if (len(root.children) == 1):
		nodeQueue.append((rootDisplay, root.children[0], (0, maxBound)))
	elif (len(root.children) == 2):
		nodeQueue.append((rootDisplay, root.children[0], (0, countLeafNodes(root.children[0]))))
		nodeQueue.append((rootDisplay, root.children[1], (countLeafNodes(root.children[0]), maxBound)))
	while (len(nodeQueue) > 0):
		curNode = nodeQueue.pop(0)
		newChild = DisplayNode()
		newChild.left_bound = curNode[2][0]
		newChild.right_bound = curNode[2][1]
		newChild.text = curNode[1].attributes['Node Type']
		newChild.annotations = curNode[1].annotations
		newChild.depth = curNode[0].depth + 1
		# append to parent
		curNode[0].children.append(newChild)
		if (len(curNode[1].children) == 1):
			nodeQueue.append((newChild, curNode[1].children[0], (newChild.left_bound, newChild.right_bound)))
		elif (len(curNode[1].children) == 2):
			nodeQueue.append((newChild, curNode[1].children[0],
							  (newChild.left_bound, newChild.left_bound + countLeafNodes(curNode[1].children[0]))))
			nodeQueue.append((newChild, curNode[1].children[1],
							  (newChild.left_bound + countLeafNodes(curNode[1].children[0]), newChild.right_bound)))
	return rootDisplay


class projectWindow(tk.Tk):
	def createLoginDetails(self):
		# Labelling frames
		ipFrame = tk.Frame(self.sqlLabelFrame)
		ipFrame.pack(anchor=tk.W)
		portFrame = tk.Frame(self.sqlLabelFrame)
		portFrame.pack(anchor=tk.W)
		dbNameFrame = tk.Frame(self.sqlLabelFrame)
		dbNameFrame.pack(anchor=tk.W)
		userFrame = tk.Frame(self.sqlLabelFrame)
		userFrame.pack(anchor=tk.W)
		pwdFrame = tk.Frame(self.sqlLabelFrame)
		pwdFrame.pack(anchor=tk.W)

		# Auto filling certain labels
		ipLabel = tk.Label(ipFrame, text="IP address: ")
		ipLabel.pack(side=tk.LEFT)
		self.ipEntry = tk.Entry(ipFrame)
		self.ipEntry.insert(0, "127.0.0.1")
		self.ipEntry.pack(side=tk.RIGHT)

		portLabel = tk.Label(portFrame, text="Port: ")
		portLabel.pack(side=tk.LEFT)
		self.portEntry = tk.Entry(portFrame)
		self.portEntry.insert(0, "5432")
		self.portEntry.pack(side=tk.RIGHT)

		userLabel = tk.Label(userFrame, text="Username: ")
		userLabel.pack(side=tk.LEFT)
		self.userEntry = tk.Entry(userFrame)
		self.userEntry.insert(0, "postgres")
		self.userEntry.pack(side=tk.RIGHT)

		pwdLabel = tk.Label(pwdFrame, text="Password: ")
		pwdLabel.pack(side=tk.LEFT)
		self.pwdEntry = tk.Entry(pwdFrame)
		self.pwdEntry.pack(side=tk.RIGHT)

		dbNameLabel = tk.Label(dbNameFrame, text="Database name: ")
		dbNameLabel.pack(side=tk.LEFT)
		self.dbNameEntry = tk.Entry(dbNameFrame)
		self.dbNameEntry.pack(side=tk.RIGHT)

		loginBtn = tk.Button(self.sqlLabelFrame, text="LOGIN", command=self.processLogin)
		loginBtn.pack()

	def scroll_move(self, event):
		self.planCanvas.scan_dragto(event.x, event.y, gain=1)

	def scroll_start(self, event):
		self.planCanvas.scan_mark(event.x, event.y)

	def onObjectClick(self, event):
		x = event.widget.canvasx(event.x)
		y = event.widget.canvasy(event.y)
		self.annoStr.set(self.dictExtraToID[event.widget.find_closest(x, y)[0]])
		if (self.dictExtraToID[event.widget.find_closest(x, y)[0]] != ""):
			self.open_popup(self.dictExtraToID[event.widget.find_closest(x, y)[0]])

	# self.annoStr.set(self.dictExtraToID[event.widget.find_closest(event.x, event.y)[0]])
	# if(self.dictExtraToID[event.widget.find_closest(event.x, event.y)[0]] != ""):
	#     self.open_popup(self.dictExtraToID[event.widget.find_closest(event.x, event.y)[0]])

	def createTextRectangle(self, text: str, canvas: tk.Canvas, x0: int, y0: int):
		rectangle = canvas.create_rectangle(x0, y0, x0 + 100, y0 + 50, fill="#FFFFFF")
		textline = canvas.create_text(x0 + 50, y0 + 25, text=text, justify='center')
		self.textBoxes.append(textline)
		self.planCanvas.tag_bind(rectangle, '<ButtonPress-1>', self.onObjectClick)
		self.planCanvas.tag_bind(textline, '<ButtonPress-1>', self.onObjectClick)
		return (rectangle, textline)

	def open_popup(self, text: str):
		top = tk.Toplevel(self)
		top.title("Annotation")
		lbl = tk.Label(top, text=text, font=('Arial', 12, ''), wraplength=300)
		lbl.pack()
		btn = tk.Button(top, text="Close", command=top.destroy)
		btn.pack()

	def drawCanvasPlan(self, root: PlanNode):
		self.planCanvas.delete("all")
		self.dictExtraToID = {}
		self.scale = 0
		self.textBoxes = []

		rootD = createDisplayNode(root)

		drawQueue: list[Tuple[DisplayNode, Union[DisplayNode, NoneType]]] = [(rootD, None)]
		while (len(drawQueue) > 0):
			curTup = drawQueue.pop(0)
			curNode = curTup[0]
			for child in curNode.children:
				drawQueue.append((child, curNode))
			x = (curNode.left_bound * 200 + curNode.right_bound * 200) / 2 - 50
			y = curNode.depth * 100 + 50 - 25
			(rect, line) = self.createTextRectangle(curNode.text, self.planCanvas, x, y)
			self.dictExtraToID[rect] = curNode.annotations
			self.dictExtraToID[line] = curNode.annotations
			if (curTup[1] != None):
				self.planCanvas.create_line((curNode.left_bound * 200 + curNode.right_bound * 200) / 2,
											curNode.depth * 100 + 50 - 25,
											(curTup[1].left_bound * 200 + curTup[1].right_bound * 200) / 2,
											(curNode.depth - 1) * 100 + 50 + 25)

	def processQuery(self):
		# with open('query3.txt', 'r') as file:
		#     data = file.read().replace('\n', ' ')
		# query = data

		# Check if user logged in correctly

		if not self.connect.verify:
			messagebox.showerror(
				title="Warning", message="User is not Logged In. Try Again")
			return

		# User logged in correctly
		print("query entered: ", self.queryTextBox.get(1.0, "end-1c"))
		self.connect.getAllQueryPlans(self.queryTextBox.get(1.0, "end-1c"))

		# SQL Statement is wrong
		if (self.connect.queryError):
			print("Please check your sql statements")
			messagebox.showerror(
				title="Warning", message="Please check your sql statement entered.")
			return

		# Clear query
		self.queryTextBox.delete(1.0, "end")

		print(self.connect.query_plans['chosen_plan'][1].print_tree())

		annotation = Annotation()
		annotation.traverseTree(self.connect.query_plans['chosen_plan'][1])

		# Draw optimal query tree
		self.drawCanvasPlan(self.connect.query_plans['chosen_plan'][1])

	def processLogin(self):
		# Checking if entry labels are empty in case user did not enter
		typesOfEntry = []
		typesOfEntry.extend([self.ipEntry, self.portEntry,
							 self.userEntry, self.pwdEntry, self.dbNameEntry])
		isEmpty = False
		for i in typesOfEntry:
			if len(i.get()) == 0:
				isEmpty = True
		if isEmpty:
			messagebox.showerror(
				title="Warning", message="Please fill All Empty Fields")
			return

		# Establishing connection
		self.connect = SetUp(self.ipEntry.get(), self.portEntry.get(), self.dbNameEntry.get(), self.userEntry.get(),
							 self.pwdEntry.get())

		# Checking if login credentials are correct

		if not self.connect.verify:
			messagebox.showerror(
				title="Warning", message="User is not Logged In. Credentials are wrong. Try Again")
			return

		messagebox.showinfo(
			title="Success", message="User is logged in!!")

		# query = "SELECT * FROM customer"

		# print("-------------------Best plan operator tree--------------")
		# print(self.connect.query_plans['chosen_plan'][1].print_tree())
		print("IP:", self.ipEntry.get())
		print("PORT:", self.portEntry.get())
		print("USER:", self.userEntry.get())
		print("PWD:", self.pwdEntry.get())
		print("DB NAME:", self.dbNameEntry.get())

	def centreCanvas(self):
		self.planCanvas.scale("all", 0, 0, pow(0.8, self.scale), pow(0.8, self.scale))
		self.planCanvas.xview_moveto(0.5)
		self.planCanvas.yview_moveto(0)
		writingFont = font.nametofont("TkDefaultFont").copy()
		for text in self.textBoxes:
			self.planCanvas.itemconfig(text, font=writingFont)

		self.scale = 0

	def zoomIn(self):
		self.scale += 1
		self.planCanvas.scale("all", 0, 0, 1.25, 1.25)
		writingFont = font.nametofont("TkDefaultFont").copy()
		writingFont.config(size=floor(writingFont.cget("size") * pow(1.1, self.scale)))
		for text in self.textBoxes:
			self.planCanvas.itemconfig(text, font=writingFont)

	def zoomOut(self):
		self.scale -= 1
		self.planCanvas.scale("all", 0, 0, 0.8, 0.8)
		writingFont = font.nametofont("TkDefaultFont").copy()
		writingFont.config(size=floor(writingFont.cget("size") * pow(1.1, self.scale)))
		for text in self.textBoxes:
			self.planCanvas.itemconfig(text, font=writingFont)

	def __init__(self):
		super().__init__()
		self.scale = 0
		self.dictExtraToID = {}
		self.textBoxes = []
		self.title("CZ4031 Database Project 2")

		inputFrame = tk.Frame(self)
		inputFrame.pack(side=tk.LEFT)

		planFrame = tk.Frame(self)
		planFrame.pack(side=tk.RIGHT)

		planInfoFrame = tk.Frame(planFrame)
		planInfoFrame.pack()
		planLabel = tk.Label(planInfoFrame, text="Query:")
		planLabel.pack(side=tk.LEFT)
		centreBtn = tk.Button(planInfoFrame, text="RESET VIEW", command=self.centreCanvas)
		centreBtn.pack(side=tk.RIGHT)
		zoomFrame = tk.Frame(planFrame)
		zoomFrame.pack()

		zoomInBtn = tk.Button(zoomFrame, text="Zoom In", command=self.zoomIn)
		zoomInBtn.pack(side=tk.LEFT)
		zoomOutBtn = tk.Button(zoomFrame, text="Zoom Out", command=self.zoomOut)
		zoomOutBtn.pack(side=tk.RIGHT)

		self.planCanvas = tk.Canvas(planFrame, height=600, width=600, bg="#FFFFFF")
		self.planCanvas.pack()

		self.planCanvas.bind("<ButtonPress-1>", self.scroll_start)
		self.planCanvas.bind("<B1-Motion>", self.scroll_move)

		self.sqlLabelFrame = tk.LabelFrame(inputFrame, text="PostgreSQL login")
		self.sqlLabelFrame.pack(fill="both", expand="yes")

		self.createLoginDetails()

		queryLabel = tk.Label(inputFrame, text="Query:")
		queryLabel.pack(anchor=tk.W)

		self.queryTextBox = tk.Text(inputFrame, height=4, width=20)
		self.queryTextBox.pack()

		processBtn = tk.Button(inputFrame, text="Process query", command=self.processQuery)
		processBtn.pack()

		annoLabel = tk.Label(inputFrame, text="Annotation:")
		annoLabel.pack()
		self.annoStr = tk.StringVar()
		annoMsg = tk.Label(inputFrame, textvariable=self.annoStr, wraplength=150)
		annoMsg.pack()
		self.resizable(False, False)

# if __name__ == "__main__":
#     app = projectWindow()
#     app.mainloop()
