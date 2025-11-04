import tkinter as tk
from tkinter import messagebox
import sqlite3

# ===================== BASE DE DONNÉES =====================
def init_db():
    conn = sqlite3.connect("banque.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS client(
                    id_client TEXT PRIMARY KEY,
                    nom TEXT,
                    prenom TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS compte(
                    id_compte TEXT PRIMARY KEY,
                    id_client TEXT,
                    solde REAL DEFAULT 0,
                    FOREIGN KEY(id_client) REFERENCES client(id_client))''')

    c.execute('''CREATE TABLE IF NOT EXISTS transactions(
                    id_trans INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_compte TEXT,
                    type TEXT,
                    montant REAL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(id_compte) REFERENCES compte(id_compte))''')

    conn.commit()
    conn.close()

# ===================== FONCTIONS CLIENT =====================
def ajouter_client():
    idc = entry_id_client.get()
    nom = entry_nom.get()
    prenom = entry_prenom.get()
    if not idc or not nom or not prenom:
        messagebox.showwarning("Erreur", "Tous les champs sont obligatoires.")
        return

    conn = sqlite3.connect("banque.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO client VALUES (?,?,?)", (idc, nom, prenom))
        conn.commit()
        messagebox.showinfo("Succès", "Client ajouté avec succès.")
        afficher_clients()
    except sqlite3.IntegrityError:
        messagebox.showerror("Erreur", "ID client déjà existant.")
    conn.close()

def afficher_clients():
    listbox_clients.delete(0, tk.END)
    conn = sqlite3.connect("banque.db")
    c = conn.cursor()
    c.execute("SELECT id_client, nom, prenom FROM client")
    for row in c.fetchall():
        listbox_clients.insert(tk.END, f"{row[0]} - {row[1]} {row[2]}")
    conn.close()

# ===================== FONCTIONS COMPTE =====================
def creer_compte():
    id_compte = entry_id_compte.get()
    id_client = entry_client_compte.get()
    solde = float(entry_solde_init.get() or 0)

    conn = sqlite3.connect("banque.db")
    c = conn.cursor()
    c.execute("SELECT * FROM client WHERE id_client=?", (id_client,))
    if not c.fetchone():
        messagebox.showerror("Erreur", "Client introuvable.")
        conn.close()
        return

    try:
        c.execute("INSERT INTO compte VALUES (?,?,?)", (id_compte, id_client, solde))
        conn.commit()
        messagebox.showinfo("Succès", "Compte créé avec succès.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Erreur", "ID compte déjà existant.")
    conn.close()

def consulter_solde():
    id_compte = entry_id_solde.get()
    conn = sqlite3.connect("banque.db")
    c = conn.cursor()
    c.execute("SELECT solde FROM compte WHERE id_compte=?", (id_compte,))
    data = c.fetchone()
    conn.close()

    if data:
        messagebox.showinfo("Solde", f"Le solde du compte {id_compte} est de {data[0]:.2f} DH")
    else:
        messagebox.showerror("Erreur", "Compte introuvable.")

# ===================== FONCTIONS TRANSACTION =====================
def effectuer_transaction(type_op):
    id_compte = entry_id_compte_trans.get()
    montant = float(entry_montant.get() or 0)

    conn = sqlite3.connect("banque.db")
    c = conn.cursor()
    c.execute("SELECT solde FROM compte WHERE id_compte=?", (id_compte,))
    data = c.fetchone()

    if not data:
        messagebox.showerror("Erreur", "Compte introuvable.")
        conn.close()
        return

    solde = data[0]
    if type_op == "retrait" and solde < montant:
        messagebox.showwarning("Erreur", "Solde insuffisant pour le retrait.")
        conn.close()
        return

    nouveau_solde = solde + montant if type_op == "depot" else solde - montant
    c.execute("UPDATE compte SET solde=? WHERE id_compte=?", (nouveau_solde, id_compte))
    c.execute("INSERT INTO transactions (id_compte, type, montant) VALUES (?,?,?)",
              (id_compte, type_op, montant))
    conn.commit()
    conn.close()
    messagebox.showinfo("Succès", f"{type_op.capitalize()} effectué avec succès.")

# ===================== CHANGEMENT DE PAGE =====================
def show_frame(frame_func):
    for widget in content_frame.winfo_children():
        widget.destroy()
    frame_func()

# ===================== PAGES =====================
def accueil_page():
    tk.Label(content_frame, text=" Bienvenue dans le système bancaire",
             font=("Arial", 16, "bold"), bg="#f4fdff").pack(pady=40)
    tk.Label(content_frame, text="Utilisez le menu à gauche pour naviguer.",
             font=("Arial", 12), bg="#f4fdff").pack()

def clients_page():
    global entry_id_client, entry_nom, entry_prenom, listbox_clients
    tk.Label(content_frame, text="Gestion des Clients", font=("Arial", 14, "bold"), bg="#f4fdff").pack(pady=10)
    entry_id_client = tk.Entry(content_frame, width=30)
    entry_nom = tk.Entry(content_frame, width=30)
    entry_prenom = tk.Entry(content_frame, width=30)

    for label_text, entry in [("ID Client", entry_id_client),
                              ("Nom", entry_nom),
                              ("Prénom", entry_prenom)]:
        tk.Label(content_frame, text=label_text, bg="#f4fdff").pack()
        entry.pack(pady=3)

    tk.Button(content_frame, text="Ajouter Client", bg="#0078d7", fg="white",
              command=ajouter_client).pack(pady=8)
    listbox_clients = tk.Listbox(content_frame, width=45)
    listbox_clients.pack(pady=10)
    afficher_clients()

def comptes_page():
    global entry_id_compte, entry_client_compte, entry_solde_init, entry_id_solde
    tk.Label(content_frame, text="Gestion des Comptes", font=("Arial", 14, "bold"), bg="#f4fdff").pack(pady=10)

    entry_id_compte = tk.Entry(content_frame, width=30)
    entry_client_compte = tk.Entry(content_frame, width=30)
    entry_solde_init = tk.Entry(content_frame, width=30)

    for label_text, entry in [("ID Compte", entry_id_compte),
                              ("ID Client", entry_client_compte),
                              ("Solde Initial", entry_solde_init)]:
        tk.Label(content_frame, text=label_text, bg="#f4fdff").pack()
        entry.pack(pady=3)

    tk.Button(content_frame, text="Créer Compte", bg="#0078d7", fg="white",
              command=creer_compte).pack(pady=10)

    tk.Label(content_frame, text="ID Compte à consulter", bg="#f4fdff").pack()
    entry_id_solde = tk.Entry(content_frame, width=30)
    entry_id_solde.pack()
    tk.Button(content_frame, text="Consulter Solde", bg="#0078d7", fg="white",
              command=consulter_solde).pack(pady=10)

def transactions_page():
    global entry_id_compte_trans, entry_montant
    tk.Label(content_frame, text="Transactions", font=("Arial", 14, "bold"), bg="#f4fdff").pack(pady=10)

    tk.Label(content_frame, text="ID Compte", bg="#f4fdff").pack()
    entry_id_compte_trans = tk.Entry(content_frame, width=30)
    entry_id_compte_trans.pack(pady=3)

    tk.Label(content_frame, text="Montant", bg="#f4fdff").pack()
    entry_montant = tk.Entry(content_frame, width=30)
    entry_montant.pack(pady=3)

    tk.Button(content_frame, text="Dépôt", bg="#28a745", fg="white",
              command=lambda: effectuer_transaction("depot")).pack(pady=5)
    tk.Button(content_frame, text="Retrait", bg="#dc3545", fg="white",
              command=lambda: effectuer_transaction("retrait")).pack(pady=5)

# ===================== INTERFACE PRINCIPALE =====================
root = tk.Tk()
root.title("Système Bancaire")
root.geometry("800x500")
root.config(bg="#e7f2f8")
root.resizable(False, False)

init_db()

# --- MENU LATÉRAL ---
menu_frame = tk.Frame(root, bg="#0078d7", width=180)
menu_frame.pack(side="left", fill="y")

tk.Label(menu_frame, text="MENU", bg="#0078d7", fg="white",
         font=("Arial", 14, "bold")).pack(pady=20)

for text, func in [("Accueil", accueil_page),
                   ("Clients", clients_page),
                   ("Comptes", comptes_page),
                   ("Transactions", transactions_page)]:
    tk.Button(menu_frame, text=text, bg="#0094ff", fg="white",
              width=18, height=2, relief="flat",
              command=lambda f=func: show_frame(f)).pack(pady=8)

tk.Button(menu_frame, text="Quitter", bg="#ff4444", fg="white",
          width=18, height=2, relief="flat", command=root.quit).pack(side="bottom", pady=20)

# --- ZONE DE CONTENU ---
content_frame = tk.Frame(root, bg="#f4fdff")
content_frame.pack(expand=True, fill="both")

accueil_page()  # page d’accueil par défaut

root.mainloop()