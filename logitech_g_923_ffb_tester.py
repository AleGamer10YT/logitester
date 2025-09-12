import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import platform
import sys

# Le librerie verranno importate solo quando necessario

class LogitechFFB:
    def __init__(self):
        self.controller = None
        self.connected = None
        self.dll_path = None
        self.logidrivepy_module = None

    def initialize(self):
        if self.controller is not None and self.connected is not None:
            return self.connected
        try:
            if not self.logidrivepy_module:
                from logidrivepy import LogitechController
                self.logidrivepy_module = LogitechController
            
            if self.dll_path:
                self.controller = self.logidrivepy_module(dll_path=self.dll_path)
            else:
                self.controller = self.logidrivepy_module()
            
            self.connected = self.controller.is_connected(0)
            if not self.connected:
                 messagebox.showwarning("Logitech", "Volante non rilevato da logidrivepy.")
            return self.connected
        except ImportError:
            messagebox.showerror("Errore", "logidrivepy non installato. Esegui: pip install logidrivepy")
            self.connected = False
            return False
        except Exception as e:
            messagebox.showerror(
                "Errore logidrivepy", 
                f"Impossibile inizializzare la DLL Logitech:\n{e}\n\n"
                "Possibili cause:\n"
                "1. G HUB non è in esecuzione.\n"
                "2. La DLL selezionata non è corretta (deve essere di G HUB, 64-bit).\n"
                "3. Esegui lo script come Amministratore.\n"
                "4. Il G923 potrebbe non essere supportato da questa libreria."
            )
            self.controller = None
            self.connected = False
            return False

    def move_to_angle(self, angle):
        if not self.initialize(): return
        if self.connected:
            try:
                force = int(max(min(angle / 4.5, 100), -100))
                self.controller.constant_force(force)
            except Exception as e:
                messagebox.showerror("Errore FFB", f"Errore durante l'invio del comando FFB:\n{e}")
                self.connected = False # Disabilita FFB se fallisce

    def stop_all(self):
        if not self.initialize(): return
        if self.connected:
            try:
                self.controller.stop_all()
            except Exception as e:
                messagebox.showerror("Errore FFB", f"Errore durante l'invio del comando STOP:\n{e}")
                self.connected = False # Disabilita FFB se fallisce

class App:
    def __init__(self, root):
        self.root = root
        self.controller = LogitechFFB()
        self.pygame_module = None
        self.selected_joystick_index = None

        self.root.title("Logitech G Input Tester")
        self.root.geometry("520x400")

        # --- Sezione rilevamento input ---
        frame_input = ttk.LabelFrame(root, text="Rilevamento dispositivi (DirectInput)")
        frame_input.pack(fill="x", padx=10, pady=8)

        self.status = tk.StringVar(value="Nessun dispositivo selezionato")
        self.label_status = ttk.Label(frame_input, textvariable=self.status)
        self.label_status.pack(pady=5)

        self.btn_detect = ttk.Button(frame_input, text="Rileva e seleziona dispositivo", command=self.detect_joysticks, state="disabled")
        self.btn_detect.pack(pady=2)

        self.btn_diagnostics = ttk.Button(frame_input, text="Diagnostica Ambiente", command=self.run_diagnostics)
        self.btn_diagnostics.pack(pady=2)

        # --- Sezione controlli force feedback ---
        frame_ffb = ttk.LabelFrame(root, text="Controlli Force Feedback (Logitech DLL)")
        frame_ffb.pack(fill="x", padx=10, pady=8)

        self.ffb_status = tk.StringVar(value="FFB non inizializzato")
        self.label_ffb_status = ttk.Label(frame_ffb, textvariable=self.ffb_status)
        self.label_ffb_status.pack(pady=5)

        self.btn_init_ffb = ttk.Button(frame_ffb, text="Inizializza Logitech FFB", command=self.initialize_ffb)
        self.btn_init_ffb.pack(pady=5)

        self.btn_load_dll = ttk.Button(frame_ffb, text="Seleziona DLL...", command=self.load_dll)
        self.btn_load_dll.pack(pady=2)

        self.angle_label = ttk.Label(frame_ffb, text="Angolo volante (-450° / +450°):")
        self.angle_label.pack(pady=5)
        self.slider = ttk.Scale(frame_ffb, from_=-450, to=450, orient="horizontal", length=350, command=self.set_angle, state="disabled")
        self.slider.set(0)
        self.slider.pack(pady=10)
        self.last_angle = 0

        self.btn_stop = ttk.Button(frame_ffb, text="STOP ALL", command=self.controller.stop_all, state="disabled")
        self.btn_stop.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Inizializza Pygame automaticamente all'avvio
        self.initialize_pygame()

    def initialize_pygame(self):
        try:
            import pygame
            self.pygame_module = pygame
            self.pygame_module.init()
            self.btn_detect.config(state="normal")
        except ImportError:
            messagebox.showerror("Errore", "pygame non installato. Esegui: pip install pygame")
        except Exception as e:
            messagebox.showerror("Errore Pygame", f"Errore durante l'inizializzazione di Pygame:\n{e}")

    def initialize_ffb(self):
        if self.controller.initialize():
            self.ffb_status.set("Volante Rilevato da logidrivepy ✅")
            messagebox.showinfo("Successo", "Logitech FFB inizializzato. Ora puoi usare i controlli.")
            self.btn_init_ffb.config(state="disabled", text="Logitech FFB Inizializzato")
            self.slider.config(state="normal")
            self.btn_stop.config(state="normal")
        else:
            self.ffb_status.set("Volante NON Rilevato da logidrivepy ❌")
            messagebox.showerror("Fallito", "Inizializzazione Logitech FFB fallita. Controlla i suggerimenti nel messaggio di errore.")

    def run_diagnostics(self):
        py_arch = platform.architecture()[0]
        dll_path = self.controller.dll_path or "Nessuna DLL selezionata"
        
        info_message = (
            f"Architettura Python: {py_arch}\n"
            f"Versione Python: {sys.version.split(' ')[0]}\n"
            f"DLL Selezionata: {dll_path}\n\n"
            "Assicurati che la DLL sia della stessa architettura di Python (es. 64-bit per Python 64-bit).\n"
            "La DLL si trova solitamente in:\n"
            "C:\\Program Files\\LGHUB\\sdk_legacy\\bin\\x64\\LogitechSteeringWheelEnginesWrapper.dll"
        )
        messagebox.showinfo("Diagnostica", info_message)

    def load_dll(self):
        path = filedialog.askopenfilename(title="Seleziona LogitechSteeringWheelEnginesWrapper.dll", filetypes=[("DLL files", "*.dll")])
        if path:
            self.controller.dll_path = path
            self.controller.controller = None # Forza la re-inizializzazione
            self.controller.connected = None  # Forza la re-inizializzazione
            messagebox.showinfo("DLL Selezionata", f"DLL selezionata:\n{path}\nL'FFB verrà reinizializzato al prossimo comando.")

    def set_angle(self, val):
        angle = int(float(val))
        if -5 < angle < 5:
            angle = 0
            self.slider.set(0)
        if angle != self.last_angle:
            self.controller.move_to_angle(angle)
            self.last_angle = angle
        self.angle_label.config(text=f"Angolo volante: {angle}°")

    def detect_joysticks(self):
        if not self.pygame_module: return
        self.pygame_module.joystick.init()
        count = self.pygame_module.joystick.get_count()
        if count == 0:
            messagebox.showinfo("DirectInput", "Nessun dispositivo rilevato.")
        else:
            names = [f"{i}: {self.pygame_module.joystick.Joystick(i).get_name()}" for i in range(count)]
            sel = self.select_joystick_popup(names)
            if sel is not None:
                self.selected_joystick_index = sel
                self.status.set(f"Selezionato: {names[sel]}")
        self.pygame_module.joystick.quit()

    def select_joystick_popup(self, names):
        popup = tk.Toplevel(self.root)
        popup.title("Seleziona dispositivo")
        var = tk.IntVar(value=0)
        for idx, name in enumerate(names):
            tk.Radiobutton(popup, text=name, variable=var, value=idx).pack(anchor="w")
        result = {'value': None}
        def confirm():
            result['value'] = var.get()
            popup.destroy()
        btn = tk.Button(popup, text="Conferma", command=confirm)
        btn.pack(pady=5)
        popup.transient(self.root)
        popup.grab_set()
        self.root.wait_window(popup)
        return result['value']

    def on_close(self):
        self.controller.stop_all()
        if self.pygame_module:
            self.pygame_module.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
