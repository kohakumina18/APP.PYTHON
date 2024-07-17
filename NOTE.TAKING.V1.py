import tkinter as tk
from tkinter import font, filedialog, scrolledtext, colorchooser, messagebox
import threading
import time
import enchant


class NoteTakingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Note-Taking App")
        
        # Create a Text widget
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Times New Roman", 12))
        self.text_area.pack(expand=True, fill='both')
        
        # Create a menu bar
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)
        
        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=self.cut_text)
        edit_menu.add_command(label="Copy", command=self.copy_text)
        edit_menu.add_command(label="Paste", command=self.paste_text)
        
        # Toolbar for formatting options
        self.toolbar = tk.Frame(root, bd=1, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        self.bold_btn = tk.Button(self.toolbar, text="Bold", command=self.make_bold)
        self.bold_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.italic_btn = tk.Button(self.toolbar, text="Italic", command=self.make_italic)
        self.italic_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.underline_btn = tk.Button(self.toolbar, text="Underline", command=self.make_underline)
        self.underline_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.strikethrough_btn = tk.Button(self.toolbar, text="Strikethrough", command=self.make_strikethrough)
        self.strikethrough_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.font_family_var = tk.StringVar(value="Times New Roman")
        self.font_size_var = tk.IntVar(value=12)
        
        self.font_family_menu = tk.OptionMenu(self.toolbar, self.font_family_var, *font.families(), command=self.change_font)
        self.font_family_menu.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.font_size_menu = tk.OptionMenu(self.toolbar, self.font_size_var, *list(range(8, 72)), command=self.change_font)
        self.font_size_menu.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.color_btn = tk.Button(self.toolbar, text="Text Color", command=self.change_text_color)
        self.color_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.highlight_btn = tk.Button(self.toolbar, text="Highlight", command=self.highlight_text)
        self.highlight_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.night_mode_var = tk.BooleanVar(value=False)
        self.night_mode_btn = tk.Checkbutton(self.toolbar, text="Night Mode", variable=self.night_mode_var, command=self.toggle_night_mode)
        self.night_mode_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.spell_check_btn = tk.Button(self.toolbar, text="Spell Check", command=self.spell_check)
        self.spell_check_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.word_count_label = tk.Label(self.toolbar, text="Words: 0 Characters: 0")
        self.word_count_label.pack(side=tk.RIGHT, padx=2, pady=2)
        
        self.text_area.bind("<KeyRelease>", self.update_word_count)
        
        self.start_autosave()
        
    def make_bold(self):
        self.toggle_tag("bold")
        
    def make_italic(self):
        self.toggle_tag("italic")
        
    def make_underline(self):
        self.toggle_tag("underline")
        
    def make_strikethrough(self):
        self.toggle_tag("strikethrough")
        
    def toggle_tag(self, tag):
        try:
            current_tags = self.text_area.tag_names(tk.SEL_FIRST)
            if tag in current_tags:
                self.text_area.tag_remove(tag, tk.SEL_FIRST, tk.SEL_LAST)
            else:
                self.text_area.tag_add(tag, tk.SEL_FIRST, tk.SEL_LAST)
                font_style = font.Font(self.text_area, self.text_area.cget("font"))
                if tag == "bold":
                    font_style.configure(weight="bold")
                elif tag == "italic":
                    font_style.configure(slant="italic")
                elif tag == "underline":
                    font_style.configure(underline=True)
                elif tag == "strikethrough":
                    font_style.configure(overstrike=True)
                self.text_area.tag_configure(tag, font=font_style)
        except tk.TclError:
            pass  # No text selected
        
    def change_font(self, *args):
        current_font = font.Font(self.text_area, self.text_area.cget("font"))
        current_font.configure(family=self.font_family_var.get(), size=self.font_size_var.get())
        self.text_area.configure(font=current_font)
        
    def change_text_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            try:
                self.text_area.tag_add("color", tk.SEL_FIRST, tk.SEL_LAST)
                self.text_area.tag_configure("color", foreground=color)
            except tk.TclError:
                pass  # No text selected
        
    def highlight_text(self):
        color = colorchooser.askcolor()[1]
        if color:
            try:
                self.text_area.tag_add("highlight", tk.SEL_FIRST, tk.SEL_LAST)
                self.text_area.tag_configure("highlight", background=color)
            except tk.TclError:
                pass  # No text selected
        
    def toggle_night_mode(self):
        if self.night_mode_var.get():
            self.text_area.config(bg="black", fg="white", insertbackground="white")
        else:
            self.text_area.config(bg="white", fg="black", insertbackground="black")
        
    def spell_check(self):
        d = enchant.Dict("en_US")
        text = self.text_area.get("1.0", tk.END)
        words = text.split()
        misspelled = [word for word in words if not d.check(word)]
        
        if misspelled:
            messagebox.showinfo("Spell Check", "Misspelled words:\n" + ", ".join(misspelled))
        else:
            messagebox.showinfo("Spell Check", "No misspelled words found.")
        
    def autosave(self):
        while True:
            self.save_file()
            time.sleep(300)  # Autosave:5 minutes

    def start_autosave(self):
        autosave_thread = threading.Thread(target=self.autosave)
        autosave_thread.daemon = True
        autosave_thread.start()

    def search_notes(self):
        search_window = tk.Toplevel(self.root)
        search_window.title("Search Notes")
        search_label = tk.Label(search_window, text="Search for:")
        search_label.pack(side=tk.LEFT)
        search_entry = tk.Entry(search_window)
        search_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        search_button = tk.Button(search_window, text="Search", command=lambda: self.search_text(search_entry.get()))
        search_button.pack(side=tk.RIGHT)

    def search_text(self, query):
        self.text_area.tag_remove('search', '1.0', tk.END)
        start_pos = '1.0'
        while True:
            start_pos = self.text_area.search(query, start_pos, stopindex=tk.END)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(query)}c"
            self.text_area.tag_add('search', start_pos, end_pos)
            start_pos = end_pos
        self.text_area.tag_config('search', background='yellow', foreground='black')

    def new_file(self):
        self.text_area.delete(1.0, tk.END)
    
    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r') as file:
                self.text_area.insert(tk.INSERT, file.read())
    
    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.text_area.get(1.0, tk.END))
    
    def cut_text(self):
        self.text_area.event_generate("<<Cut>>")
    
    def copy_text(self):
        self.text_area.event_generate("<<Copy>>")
    
    def paste_text(self):
        self.text_area.event_generate("<<Paste>>")
        
    def update_word_count(self, event=None):
        text = self.text_area.get("1.0", tk.END)
        words = len(text.split())
        characters = len(text) - 1  # Subtract 1 to ignore the ending newline character
        self.word_count_label.config(text=f"Words: {words} Characters: {characters}")


if __name__ == "__main__":
    root = tk.Tk()
    app = NoteTakingApp(root)
    root.mainloop()
