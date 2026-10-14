"""Tkinter window for converting a folder of .SPA files into one CSV."""
import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from converter import convert_folder, find_spa_files


class SpaToCsvApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SPA to CSV converter")
        self.root.minsize(640, 480)

        self.folder_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.mode_var = tk.StringVar(value='auto')
        self.start_var = tk.StringVar(value='4000.188')
        self.end_var = tk.StringVar(value='649.90')
        self.workers_var = tk.IntVar(value=os.cpu_count() or 1)

        self.messages = queue.Queue()
        self.stop_event = threading.Event()
        self.worker = None

        self._build_widgets()
        self._toggle_manual_fields()
        self.root.after(100, self._poll_messages)

    # ---------- layout ----------

    def _build_widgets(self):
        pad = {'padx': 8, 'pady': 4}
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill='both', expand=True)
        main.columnconfigure(1, weight=1)

        # 1. Input folder
        ttk.Label(main, text="Folder with .SPA files:").grid(row=0, column=0, sticky='w', **pad)
        ttk.Entry(main, textvariable=self.folder_var).grid(row=0, column=1, sticky='ew', **pad)
        ttk.Button(main, text="Browse...", command=self._choose_folder).grid(row=0, column=2, **pad)

        # 2. Output file
        ttk.Label(main, text="Save CSV as:").grid(row=1, column=0, sticky='w', **pad)
        ttk.Entry(main, textvariable=self.output_var).grid(row=1, column=1, sticky='ew', **pad)
        ttk.Button(main, text="Browse...", command=self._choose_output).grid(row=1, column=2, **pad)

        # 3. Wavenumber options
        wn = ttk.LabelFrame(main, text="Wavenumbers", padding=8)
        wn.grid(row=2, column=0, columnspan=3, sticky='ew', **pad)
        ttk.Radiobutton(
            wn, text="Read from the .SPA files (recommended)",
            variable=self.mode_var, value='auto', command=self._toggle_manual_fields,
        ).grid(row=0, column=0, columnspan=4, sticky='w')
        ttk.Radiobutton(
            wn, text="Manual range (number of points is detected automatically):",
            variable=self.mode_var, value='manual', command=self._toggle_manual_fields,
        ).grid(row=1, column=0, columnspan=4, sticky='w')
        ttk.Label(wn, text="Start (cm-1):").grid(row=2, column=0, sticky='e', padx=(24, 4))
        self.start_entry = ttk.Entry(wn, textvariable=self.start_var, width=12)
        self.start_entry.grid(row=2, column=1, sticky='w')
        ttk.Label(wn, text="End (cm-1):").grid(row=2, column=2, sticky='e', padx=(16, 4))
        self.end_entry = ttk.Entry(wn, textvariable=self.end_var, width=12)
        self.end_entry.grid(row=2, column=3, sticky='w')

        # 4. Advanced
        adv = ttk.Frame(main)
        adv.grid(row=3, column=0, columnspan=3, sticky='w', **pad)
        ttk.Label(adv, text="Parallel workers:").pack(side='left')
        ttk.Spinbox(adv, from_=1, to=max(1, os.cpu_count() or 1), textvariable=self.workers_var,
                    width=5).pack(side='left', padx=4)

        # 5. Buttons + progress
        buttons = ttk.Frame(main)
        buttons.grid(row=4, column=0, columnspan=3, sticky='ew', **pad)
        self.convert_btn = ttk.Button(buttons, text="Convert", command=self._start)
        self.convert_btn.pack(side='left')
        self.cancel_btn = ttk.Button(buttons, text="Cancel", command=self._cancel, state='disabled')
        self.cancel_btn.pack(side='left', padx=6)
        self.progress = ttk.Progressbar(buttons, mode='determinate')
        self.progress.pack(side='left', fill='x', expand=True, padx=6)

        # 6. Log
        main.rowconfigure(5, weight=1)
        log_frame = ttk.Frame(main)
        log_frame.grid(row=5, column=0, columnspan=3, sticky='nsew', **pad)
        self.log_text = tk.Text(log_frame, height=12, wrap='word', state='disabled')
        scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        self.log_text.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')

    # ---------- callbacks ----------

    def _choose_folder(self):
        folder = filedialog.askdirectory(title="Select the folder containing the .SPA files")
        if not folder:
            return
        self.folder_var.set(folder)
        if not self.output_var.get():
            self.output_var.set(os.path.join(folder, os.path.basename(os.path.normpath(folder)) + '.csv'))
        self._log(f"{len(find_spa_files(folder))} .SPA files found in {folder}")

    def _choose_output(self):
        initial = self.output_var.get()
        path = filedialog.asksaveasfilename(
            title="Save combined CSV as",
            defaultextension='.csv',
            filetypes=[("CSV files", "*.csv")],
            initialdir=os.path.dirname(initial) if initial else self.folder_var.get() or None,
            initialfile=os.path.basename(initial) if initial else 'combined_spectra.csv',
        )
        if path:
            self.output_var.set(path)

    def _toggle_manual_fields(self):
        state = 'normal' if self.mode_var.get() == 'manual' else 'disabled'
        self.start_entry.configure(state=state)
        self.end_entry.configure(state=state)

    def _start(self):
        folder = self.folder_var.get().strip()
        output = self.output_var.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Missing folder", "Please select a valid folder with .SPA files.")
            return
        if not output:
            messagebox.showerror("Missing output", "Please choose where to save the CSV file.")
            return
        if os.path.exists(output) and not messagebox.askyesno(
                "Overwrite?", f"{output}\nalready exists. Overwrite it?"):
            return

        manual_range = None
        if self.mode_var.get() == 'manual':
            try:
                manual_range = (float(self.start_var.get()), float(self.end_var.get()))
            except ValueError:
                messagebox.showerror("Invalid range", "Start and end wavenumbers must be numbers.")
                return

        try:
            workers = max(1, int(self.workers_var.get()))
        except (ValueError, tk.TclError):
            workers = os.cpu_count() or 1

        self.stop_event.clear()
        self.progress['value'] = 0
        self.convert_btn.configure(state='disabled')
        self.cancel_btn.configure(state='normal')
        self.worker = threading.Thread(
            target=self._run, args=(folder, output, manual_range, workers), daemon=True)
        self.worker.start()

    def _cancel(self):
        self.stop_event.set()
        self._log("Cancelling... (waiting for running files to finish)")

    # ---------- background work ----------

    def _run(self, folder, output, manual_range, workers):
        try:
            path = convert_folder(
                folder, output, manual_range=manual_range, max_workers=workers,
                log=lambda msg: self.messages.put(('log', msg)),
                progress=lambda i, n: self.messages.put(('progress', (i, n))),
                should_stop=self.stop_event.is_set,
            )
            self.messages.put(('done', path))
        except InterruptedError:
            self.messages.put(('cancelled', None))
        except Exception as e:
            self.messages.put(('error', str(e)))

    def _poll_messages(self):
        """Apply updates sent from the worker thread (Tk is not thread-safe)."""
        try:
            while True:
                kind, payload = self.messages.get_nowait()
                if kind == 'log':
                    self._log(payload)
                elif kind == 'progress':
                    i, n = payload
                    self.progress.configure(maximum=n, value=i)
                elif kind == 'done':
                    self._finish()
                    messagebox.showinfo("Done", f"CSV saved at:\n{payload}")
                elif kind == 'cancelled':
                    self._log("Conversion cancelled.")
                    self._finish()
                elif kind == 'error':
                    self._log(f"ERROR: {payload}")
                    self._finish()
                    messagebox.showerror("Error", payload)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_messages)

    def _finish(self):
        self.convert_btn.configure(state='normal')
        self.cancel_btn.configure(state='disabled')

    def _log(self, msg):
        self.log_text.configure(state='normal')
        self.log_text.insert('end', msg + '\n')
        self.log_text.see('end')
        self.log_text.configure(state='disabled')


def main():
    root = tk.Tk()
    SpaToCsvApp(root)
    root.mainloop()
