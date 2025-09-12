import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox

def diagnose(path):
    try:
        logi = ctypes.WinDLL(path)
    except Exception as e:
        messagebox.showerror("Errore", f"Impossibile caricare DLL:\n{e}")
        return

    if not logi.LogiSteeringInitialize(False):
        messagebox.showerror("Errore", "Impossibile inizializzare l'SDK Logitech")
        return

    logi.LogiUpdate()

    results = []
    for i in range(5):
        connected = logi.LogiIsConnected(i)
        results.append(f"Device index {i}: {connected}")

    logi.LogiSteeringShutdown()

    msg = "\n".join(results)
    if not any("True" in line for line in results):
        msg += "\n⚠ Nessun dispositivo rilevato!"
    messagebox.showinfo("Risultato Diagnostica", msg)


def select_dll():
    path = filedialog.askopenfilename(
        title="Seleziona LogitechSteeringWheelEnginesWrapper.dll",
        filetypes=[("DLL files", "*.dll")]
    )
    if path:
        diagnose(path)


root = tk.Tk()
root.title("Diagnostica Logitech G923")
root.geometry("400x150")

label = tk.Label(root, text="Seleziona il DLL Logitech per la diagnosi")
label.pack(pady=20)

button = tk.Button(root, text="Scegli DLL...", command=select_dll)
button.pack(pady=10)

root.mainloop()