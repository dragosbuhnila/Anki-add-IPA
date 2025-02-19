# Warning: completely o3-mini generated

def configure_config():
    import tkinter as tk
    from tkinter import simpledialog, messagebox, ttk

    # Import current configuration from config.py
    try:
        from config import DECKS, deck_id, DECK_NAME, LANGUAGE, VOCAB_FIELD
    except ImportError as e:
        messagebox.showerror("Error", f"Could not load config.py: {e}")
        return

    # Copy DECKS so we can modify it locally
    decks = DECKS.copy()

    # Create the main window
    root = tk.Tk()
    root.title("Configure Decks")
    root.geometry("700x400")

    # Create a Treeview to display the current decks with four columns
    columns = ('id', 'deck_name', 'lang', 'vocab_field')
    tree = ttk.Treeview(root, columns=columns, show='headings')
    tree.heading('id', text='ID')
    tree.heading('deck_name', text='Deck Name')
    tree.heading('lang', text='Language')
    tree.heading('vocab_field', text='Vocab Field')
    tree.pack(fill=tk.BOTH, expand=True)

    # Add some explanatory text with text wrapping
    label = tk.Label(root, text="If you only wish to edit the language/deck on which the program should be run on, just click on the `Save Config` button and select the deck you wish to use.", 
                    wraplength=450)  # Set wrap length slightly less than window width
    label.pack(pady=5)  # Add some padding above and below the label


    def refresh_tree():
        tree.delete(*tree.get_children())
        sorted_items = sorted(decks.items(), key=lambda x: x[0])
        for did, data in sorted_items:
            tree.insert('', 'end', iid=did, values=(did, data['deck_name'], data['lang'], data['vocab_field']))

    refresh_tree()

    # Function to update the underlying decks dictionary when a cell is edited
    def update_decks(item, col, new_value):
        current_values = tree.item(item, 'values')
        # Column indices: 0 = id, 1 = deck_name, 2 = lang, 3 = vocab_field
        if col == 0:
            old_id = current_values[0]
            # Update dictionary: change key from old_id to new_value
            data = decks.pop(old_id)
            decks[new_value] = data
            # Remove and reinsert the item with new iid
            tree.delete(item)
            tree.insert('', 'end', iid=new_value, values=(new_value, current_values[1], current_values[2], current_values[3]))
        elif col == 1:
            deck_key = current_values[0]
            decks[deck_key]['deck_name'] = new_value
        elif col == 2:
            deck_key = current_values[0]
            decks[deck_key]['lang'] = new_value
        elif col == 3:
            deck_key = current_values[0]
            decks[deck_key]['vocab_field'] = new_value
        
        refresh_tree()

    # Function to make a cell editable
    def edit_cell(event):
        # Identify the item and column
        item = tree.identify_row(event.y)
        column = tree.identify_column(event.x)
        if not item or not column:
            return
        col_index = int(column.replace('#', '')) - 1  # convert column id (#1, #2, etc.) to index (0, 1, etc.)
        x, y, width, height = tree.bbox(item, column)
        # Get the current value
        current_value = tree.item(item, 'values')[col_index]
        # Create an Entry widget to overlay the cell
        entry = tk.Entry(root)
        entry.place(x=x, y=y + tree.winfo_y(), width=width, height=height)
        entry.insert(0, current_value)
        entry.focus_set()

        # When the user finishes editing (Return key or focus out)
        def finish_edit(event):
            new_value = entry.get()
            entry.destroy()
            # Update the Treeview cell
            current_values = list(tree.item(item, 'values'))
            current_values[col_index] = new_value
            tree.item(item, values=tuple(current_values))
            # Update the underlying decks dictionary
            update_decks(item, col_index, new_value)
        entry.bind("<Return>", finish_edit)
        entry.bind("<FocusOut>", finish_edit)

    # Bind double-click and right-click events to edit the cell
    tree.bind("<Double-1>", edit_cell)
    tree.bind("<Button-3>", edit_cell)

    # Create a frame for additional buttons
    frame = tk.Frame(root)
    frame.pack(pady=10)

    def add_deck():
        did = simpledialog.askstring("Add Deck", "Enter deck ID:")
        if not did:
            return
        if did in decks:
            messagebox.showerror("Error", "Deck ID already exists!")
            return
        dname = simpledialog.askstring("Add Deck", "Enter deck name:", initialvalue=f"Languages::{did.capitalize()}")
        lang = simpledialog.askstring("Add Deck", "Enter language:", initialvalue=did)
        vocab = simpledialog.askstring("Add Deck", "Enter vocab field:", initialvalue="Front")
        decks[did] = {'deck_name': dname, 'lang': lang, 'vocab_field': vocab}
        refresh_tree()

    def remove_deck():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a deck to remove")
            return
        did = selected[0]
        if messagebox.askyesno("Confirm", f"Remove deck '{did}'?"):
            del decks[did]
            refresh_tree()
            
    def save_config():
        # Create a dialog for selecting the default deck
        if not decks:
            messagebox.showerror("Error", "No decks available!")
            return
        
        dialog = tk.Toplevel(root)
        dialog.title("Select Deck")
        dialog.geometry("300x150")
        dialog.transient(root)  # Make dialog modal
        dialog.grab_set()  # Make dialog modal
        
        # Center the dialog on the main window
        dialog.geometry("+%d+%d" % (
            root.winfo_x() + root.winfo_width()/2 - 150,
            root.winfo_y() + root.winfo_height()/2 - 75))

        # Create and pack a label
        tk.Label(dialog, text="Select the default deck:").pack(pady=10)
        
        # Create the combobox with deck IDs
        default_var = tk.StringVar()
        combo = ttk.Combobox(dialog, textvariable=default_var, state='readonly')  # Added state='readonly'
        combo['values'] = sorted(decks.keys())
        combo.set(list(decks.keys())[0])  # Set default value
        combo.pack(pady=10)
        
        def on_ok():
            nonlocal default
            default = combo.get()
            dialog.destroy()
        
        def on_cancel():
            nonlocal default
            default = None
            dialog.destroy()
        
        # Create and pack OK/Cancel buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="OK", command=on_ok).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
        
        default = None
        dialog.wait_window()  # Wait for the dialog to close
        
        if not default:
            return
        
        # write the dictionary in a readable manner
        decks_str = "{\n"
        for did, data in decks.items():
            decks_str += f"\t{did!r}:"
            decks_str += " {\n"
            for key, value in data.items():
                decks_str += f"\t\t'{key}': '{value}',\n"
            decks_str += "\t},\n"
        decks_str += "}\n"

        config_content = f"""\
from multiprocessing import cpu_count

DECKS = {decks_str}
deck_id = '{default}'
DECK_NAME = DECKS[deck_id]['deck_name']
LANGUAGE = DECKS[deck_id]['lang']
VOCAB_FIELD = DECKS[deck_id]['vocab_field']

N_CORES = cpu_count()
N_JOBS_EXTRACT = 5 * N_CORES
N_JOBS_UPDATE = 4 * N_CORES

OUTPUT_DIRECTORY = './outputs'
ANKI_CONNECT_URL = 'http://localhost:8765'
DATE_FORMAT = r'%Y%m%d-%H%M%S'
"""
        try:
            with open("config.py", "w", encoding="utf-8") as f:
                f.write(config_content)
            messagebox.showinfo("Success", "Configuration saved to config.py!")
            root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config.py: {e}")

    btn_add = tk.Button(frame, text="Add Deck", command=add_deck)
    btn_remove = tk.Button(frame, text="Remove Deck", command=remove_deck)
    btn_save = tk.Button(frame, text="Save Config", command=save_config)
    btn_add.pack(side=tk.LEFT, padx=5)
    btn_remove.pack(side=tk.LEFT, padx=5)
    btn_save.pack(side=tk.LEFT, padx=5)

    root.mainloop()