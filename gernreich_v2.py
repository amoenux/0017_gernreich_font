import cairo
from dataclasses import dataclass
import random
from math import pi,tau, sqrt
import sys

@dataclass
class listset:
    L=[]
    S=set()
    
    def __init__(self, items):
        for item in items:
            self.add(item)
            
    def add(self,item):
        self.L.append(item)
        self.S.add(item)
    
    def pop(self):
        item=self.L.pop()
        self.S.remove(item)
    
    def __contains__(self, item):
        return item in self.S
    
    def __getitem__(self, idx):
        return self.L[idx]
    
    def __repr__(self):
        return str(self.L)

    def __sizeof__(self):
        return len(self.L)
    
    def __len__(self):
        return len(self.L)
    
def get_moves(encoded_moves):
    li=[]
    invli=[]
    for m in encoded_moves:
        match m:
            case "+":
                li.append(1)
                invli.append(-1)
            case "-":
                li.append(-1)
                invli.append(1)
            case "0":
                li.append(0)
                invli.append(0)
    return [((li[0],li[1]),(li[2],li[3])), ((invli[2],invli[3]),(invli[0],invli[1]))]
    

letters_moves={}
with open("gernreich_mod.txt", "r") as f:
    for symbol, moves in map(str.split,f.readlines()):
        letters_moves[symbol]=get_moves(moves)

def get_new_corner(current, delta):
    return (current[0]+delta[0],current[1]+delta[1])

def shuffle_letter_moves():
    global letters_moves
    for a in letters_moves:
        random.shuffle(letters_moves[a]) 

# Function to find all valid paths
def findPath(idx, replaced_text, path, result):
    
    # If destination is reached, store the path
    if idx==len(replaced_text):
        result.append(path.L.copy())
        print(result[-1])
        return
    
    # This is so it only finds one solution
    if result:
        return
    
    # Mark current cell as visited
    idx+=1

    for i in range(2):
        deltas=letters_moves[replaced_text[idx-1]][i]
        new_corner0=get_new_corner(path[-1],deltas[0])
        if new_corner0 not in path:
            new_corner1=get_new_corner(new_corner0,deltas[1])
            if new_corner1 not in path:
                path.add(new_corner0)
                path.add(new_corner1)
                
                # Move to the next cell recursively
                findPath(idx,replaced_text, path, result)
                
                # Backtrack
                path.pop()
                path.pop()
    
    # Unmark current cell
    idx-= 1

def get_drawing(text,random_seed=None):
    random.seed(random_seed)
    shuffle_letter_moves()
    x=0
    y=0
    
    idx=0
    replaced_text=''.join(ch for ch in text if ch in set("abcdefghijklmnopqrstuvwxyzñß"))
    path=listset([(x,y)])
    result = []

    findPath(idx, replaced_text, path, result)

    # Sort results lexicographically
    result.sort()
    
    # return only one result, for now
    positions=result[0]
    
    return positions


def draw(text,file_format='png',file_name="output",line_width=0.1,circle_radius=0.15,resolution=16, random_seed=None):
    text=text.lower()
    
    valid_symbols=set("abcdefghijklmnopqrstuvwxyzñß ,.?")
    text=''.join(ch for ch in text if ch in valid_symbols)
    sys.setrecursionlimit(len(text)+10)
    positions=get_drawing(text,random_seed=random_seed)
    
    xs=[pos[0] for pos in positions]
    ys=[pos[1] for pos in positions]
    minx=min(xs)
    maxx=max(xs)
    miny=min(ys)
    maxy=max(ys)
    rows=maxy-miny+2
    cols=maxx-minx+2
    #print(minx,maxx,miny,maxy)
    
    # Set up the image surface (width, height)
    if file_format == 'svg':
        # SVG surface for SVG output
        width, height = resolution*cols,resolution*rows
        surface = cairo.SVGSurface(file_name+".svg", width, height)
    else:
        # PNG surface for PNG output (default)
        width, height = resolution*cols,resolution*rows
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    
    ctx = cairo.Context(surface)
    
    # Fill background
    ctx.set_source_rgb(1,1,1)  # RGB for white
    ctx.rectangle(0, 0, width, height)  # Full canvas
    ctx.fill()
    
    
    # Prepare to draw lines
    ctx.set_line_width(line_width)
    ctx.set_source_rgb(0,0,0)  # Set color for the circles (black)
    
    # Draw lines
    ctx.scale(resolution,resolution)
    ctx.translate(-minx+1,-miny+1)
    ctx.move_to(0,0)
    idx=1
    dots={" ":circle_radius,",":circle_radius*sqrt(2),".":circle_radius*sqrt(3),"?":circle_radius*sqrt(3)}
    for symbol in text:
        if symbol in dots:
            ctx.stroke()
            # set color here
            ctx.arc(positions[idx-1][0],positions[idx-1][1],dots[symbol],0,tau)
            if symbol=="?":
                ctx.stroke()
            else:
                ctx.fill()
            ctx.move_to(positions[idx-1][0],positions[idx-1][1])
        
        else:
            #print(symbol, idx, positions[idx])
            ctx.line_to(positions[idx][0],positions[idx][1])
            idx+=1
            ctx.line_to(positions[idx][0],positions[idx][1])
            idx+=1
    ctx.stroke()
    
    # Save the output based on the chosen file format
    if file_format == 'svg':
        print(f"SVG saved as '{file_name}.svg'")
    else:
        surface.write_to_png(file_name+".png")
        print(f"PNG saved as '{file_name}.png'")


text="""The quick brown fox jumps over the lazy dog."""
draw(text,file_format="svg", random_seed=0)