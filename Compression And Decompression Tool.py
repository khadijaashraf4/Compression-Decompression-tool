import heapq  # Used to build a priority queue (min-heap) for Huffman tree
import os  # Used for file path and size handling
from tkinter import *  # GUI library for building the interface
from tkinter import filedialog, messagebox  # For file dialogs and alerts


# ---------- HUFFMAN NODE CLASS ----------
class Node:
    def __init__(self, char, freq):
        self.char = char      # Character stored in node
        self.freq = freq      # Frequency of the character
        self.left = None      # Left child
        self.right = None     # Right child

    def __lt__(self, other):
        # Allows heapq to compare nodes based on frequency
        return self.freq < other.freq


# ---------- BUILD HUFFMAN TREE ----------
def make_codes(node, current_code, codes):
    """Recursive function to assign binary codes to each character."""
    if node is None:
        return
    # If a leaf node is reached (actual character)
    if node.char is not None:
        codes[node.char] = current_code
        return
    # Recurse left with '0' and right with '1'
    make_codes(node.left, current_code + "0", codes)
    make_codes(node.right, current_code + "1", codes)


def build_huffman_tree(text):
    """Build Huffman tree and return root + character codes."""
    if not text:
        return None, {}

    # Step 1: Calculate frequency of each character
    freq = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1

    # Step 2: Create a priority queue (min-heap) of nodes
    heap = [Node(ch, fr) for ch, fr in freq.items()]
    heapq.heapify(heap)

    # Step 3: Build tree by merging two lowest-frequency nodes repeatedly
    while len(heap) > 1:
        n1 = heapq.heappop(heap)  # Remove smallest node
        n2 = heapq.heappop(heap)  # Remove next smallest
        merged = Node(None, n1.freq + n2.freq)  # Create parent node
        merged.left, merged.right = n1, n2  # Assign children
        heapq.heappush(heap, merged)  # Push merged node back into heap

    # Step 4: Generate Huffman codes by traversing tree
    root = heap[0]
    codes = {}
    make_codes(root, "", codes)
    return root, codes


# ---------- ENCODE AND DECODE ----------
def huffman_encode(text, codes):
    """Encode text using Huffman codes."""
    return ''.join(codes[ch] for ch in text)


def huffman_decode(encoded_text, root):
    """Decode encoded binary string using Huffman tree."""
    decoded = ""
    node = root
    for bit in encoded_text:
        node = node.left if bit == "0" else node.right
        # If a leaf node is reached, append the character
        if node.char is not None:
            decoded += node.char
            node = root  # Restart from root for next symbol
    return decoded


# ---------- TKINTER GUI SETUP ----------
root_win = Tk()
root_win.title(" Huffman Compression Tool")
root_win.geometry("600x520")
root_win.config(bg="#f5f6fa")

# Title label
Label(root_win, text="Huffman Compression Tool", font=("Arial", 18, "bold"), bg="#f5f6fa", fg="#2f3640").pack(pady=10)

# Text area for displaying or typing input text
text_box = Text(root_win, width=70, height=10, wrap=WORD, font=("Arial", 11))
text_box.pack(pady=10)

# ---------- INFORMATION LABELS ----------
file_label = Label(root_win, text="No file loaded.", bg="#f5f6fa", fg="#353b48", font=("Arial", 10))
file_label.pack()

size_label = Label(root_win, text="", bg="#f5f6fa", fg="#273c75", font=("Arial", 10, "bold"))
size_label.pack(pady=5)

result_label = Label(root_win, text="", bg="#f5f6fa", fg="#44bd32", font=("Arial", 11, "bold"))
result_label.pack(pady=5)

status_label = Label(root_win, text="", bg="#f5f6fa", fg="#0097e6", font=("Arial", 11, "bold"))
status_label.pack(pady=5)


# ---------- FILE & COMPRESSION FUNCTIONS ----------
def load_file():
    """Load a text file into the text box."""
    global original_size, file_path
    path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if path:
        with open(path, "r", encoding="utf-8") as file:
            data = file.read()
            text_box.delete(1.0, END)
            text_box.insert(END, data)
        original_size = os.path.getsize(path)
        file_path = path
        file_label.config(text=f"Loaded File: {os.path.basename(path)}")
        size_label.config(text=f"Original File Size: {original_size} bytes")
        result_label.config(text="")
        status_label.config(text="")
        messagebox.showinfo("Loaded", f"Loaded: {os.path.basename(path)}")


def compress_text():
    """Compress text using Huffman coding and save .bin file."""
    global tree_root, codes, encoded_text, compressed_size
    text = text_box.get(1.0, END).strip()
    if not text:
        messagebox.showwarning("Error", "Please enter or load some text!")
        return

    # Step 1: Build Huffman tree and generate codes
    tree_root, codes = build_huffman_tree(text)
    encoded_text = huffman_encode(text, codes)

    # Step 2: Save compressed text to .bin file in same folder
    if 'file_path' in globals():
        folder = os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        compressed_file_path = os.path.join(folder, f"{base_name}_compressed.bin")
        with open(compressed_file_path, "w", encoding="utf-8") as comp_file:
            comp_file.write(encoded_text)
        messagebox.showinfo("File Saved", f"Compressed file saved as:\n{compressed_file_path}")
    else:
        messagebox.showwarning("Warning", "No original file loaded, compressed file not saved.")

    # Step 3: Update text box and calculate compression ratio
    text_box.delete(1.0, END)
    text_box.insert(END, text)

    original_bits = len(text.encode("utf-8")) * 8
    compressed_bits = len(encoded_text)
    compressed_size = compressed_bits / 8  # Convert bits → bytes
    ratio = (compressed_size / (original_bits / 8)) * 100

    result_label.config(
        text=f"File: {os.path.basename(file_path)}\nCompressed Size: {int(compressed_size)} bytes | Compression Ratio: {ratio:.2f}%"
    )
    status_label.config(text=" Compression Done Successfully!")


def decompress_text():
    """Decompress the encoded text and restore the original content."""
    global encoded_text
    if 'encoded_text' not in globals() or not encoded_text:
        messagebox.showwarning("Error", "No compressed data available for decompression!")
        return

    try:
        decoded = huffman_decode(encoded_text, tree_root)
        text_box.delete(1.0, END)
        text_box.insert(END, decoded)
        status_label.config(text="Decompression Done Successfully!")

        # Save decompressed text back to a file
        if 'file_path' in globals():
            folder = os.path.dirname(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            decompressed_path = os.path.join(folder, f"{base_name}_decompressed.txt")
            with open(decompressed_path, "w", encoding="utf-8") as dec_file:
                dec_file.write(decoded)
            messagebox.showinfo("File Saved", f"Decompressed file saved as:\n{decompressed_path}")
        else:
            messagebox.showwarning("Warning", "No original file loaded, decompressed file not saved.")

    except Exception as e:
        messagebox.showerror("Error", f"Invalid compressed data!\n{e}")


def show_codes():
    """Display generated Huffman codes in a new window."""
    if 'codes' not in globals() or not codes:
        messagebox.showwarning("Info", "No codes generated yet!")
        return
    code_win = Toplevel(root_win)
    code_win.title("Huffman Codes")
    code_win.config(bg="white")
    Label(code_win, text="Character : Code", font=("Arial", 12, "bold"), bg="white").pack(pady=5)
    for ch, code in codes.items():
        Label(code_win, text=f"'{ch}' : {code}", bg="white", font=("Arial", 11)).pack(anchor="w")


def view_bits():
    """Preview first 1000 bits of the compressed binary text."""
    if 'encoded_text' not in globals() or not encoded_text:
        messagebox.showwarning("Warning", "Cannot view bits before compression!")
        return

    bit_win = Toplevel(root_win)
    bit_win.title("Compressed Bits Preview")
    bit_win.config(bg="white")
    Label(bit_win, text="Compressed Bits Preview", font=("Arial", 12, "bold"), bg="white").pack(pady=5)

    preview = encoded_text[:1000] + ("..." if len(encoded_text) > 1000 else "")
    text_area = Text(bit_win, wrap=WORD, width=80, height=20, font=("Consolas", 10))
    text_area.insert(END, preview)
    text_area.pack(padx=10, pady=10)


# ---------- GUI BUTTONS ----------
Button(root_win, text=" Load File", width=15, command=load_file, bg="#00a8ff", fg="white",
       font=("Arial", 10, "bold")).pack(pady=5)
Button(root_win, text=" Compress", width=15, command=compress_text, bg="#44bd32", fg="white",
       font=("Arial", 10, "bold")).pack(pady=5)
Button(root_win, text=" Decompress", width=15, command=decompress_text, bg="#e1b12c", fg="white",
       font=("Arial", 10, "bold")).pack(pady=5)
Button(root_win, text=" View Bits", width=15, command=view_bits, bg="#9b59b6", fg="white",
       font=("Arial", 10, "bold")).pack(pady=5)
Button(root_win, text=" View Huffman Codes", width=20, command=show_codes, bg="#8c7ae6", fg="white",
       font=("Arial", 10, "bold")).pack(pady=5)

# ---------- RUN MAIN GUI LOOP ----------
root_win.mainloop()
