import tkinter as tk
from tkinter import messagebox
import random
import os
from PIL import Image, ImageTk
from playsound import playsound
from special_level import special_level_game
import threading
import json
import bcrypt



#definit le repertoire pour les images et les sons
script_dir = os.path.dirname(os.path.abspath(__file__))
users_file = os.path.join(script_dir, "users.json")

#les chemins pour les sons et les images

sounds_dir = os.path.join(script_dir, "sounds")

win_sound_path = os.path.join(script_dir, "sounds", "win_sound.wav")

lose_sound_path = os.path.join(script_dir, "sounds", "lose_sound.wav")
flip_card_sound_path = os.path.join(script_dir, "sounds", "flip_card.mp3")
# chemin pour enregistrer les score et le chemin pour les images aussi 
scores_file = os.path.join(script_dir, "game_scores.json")
image_folder = os.path.abspath(os.path.join(script_dir, "images"))

# chemin pour le fichier utilisateurs
users_file = os.path.join(script_dir, "users.json")
def init_users_db():
    if not os.path.exists(users_file):
        with open(users_file, "w") as file:
            json.dump([], file)

init_users_db() 
print(f"Image folder path: {image_folder}")

# les backgrounds en fct du temps 
backgrounds = {
    "Morning": r"c:\Users\nv\Desktop\pairgamefinal\Pair Games\images\day1.png",
    
     "Daytime": r"c:\Users\nv\Desktop\pairgamefinal\Pair Games\images\day2.png",
     "Sunset": r"c:\Users\nv\Desktop\pairgamefinal\Pair Games\images\day3.png",
    "Night": r"c:\Users\nv\Desktop\pairgamefinal\Pair Games\images\day4.png",
}

# fonction pour initialiser le fichier JSON des utilisateurs
def init_users_db():
    if not os.path.exists(users_file):
        with open(users_file, "w") as file:
            json.dump([], file)

# la focntion d inscription
def signup(username, password):
    try:
         # Ouvre le fichierJSON contenant les utilisateurs enregistre
        with open(users_file, "r") as file:
            users = json.load(file)
            # Verifie si lutilisateur existe deja
        for user in users:
            if user["username"] == username:
                return "Username already exists."
           # Hash le mot de passe et ajoute lutilisateur 
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        users.append({"username": username, "password": hashed_password})
        with open(users_file, "w") as file:
            json.dump(users, file, indent=4)
        return "Signup successful."
    # Gestion des erreurs
    except Exception as e:
        return f"Error during signup: {e}"
    
# Fonction pour la connexion
def login(username, password):
    try:
        # Ouvre le fichier JSON contenant les utilisateurs enregistrés
        with open(users_file, "r") as file:
            users = json.load(file)

        for user in users:
            # Vérifie si l'utilisateur existe et si le mot de passe est correct
            if user["username"] == username and bcrypt.checkpw(password.encode(), user["password"].encode()):
                global player_name, current_level_label
                player_name = username
                current_level = user.get("current_level", 1)  # Récupère le niveau actuel ou 1 par défaut
                
                # Met à jour le message et affiche le niveau actuel sous la difficulté
                current_level_label.config(text=f"Your Current Level: {current_level}")
                messagebox.showinfo("Login Successful", f"Welcome, {username}! Your current level is: {current_level}")
                return "Login successful."

        # Retourne un message d'erreur si le mot de passe est incorrect
        return "Invalid username or password."
    except Exception as e:
        return f"Error during login: {e}"


    
#fonction pour mettre a jour le fond d ecran selon le temp qui reste
def change_background_ontime():
   
    global bg_label
    # Determine the background based on the remaining time
    if time_remaining > 135:
        new_bg = backgrounds["Morning"]
    elif time_remaining > 90:
        
        new_bg = backgrounds["Daytime"]
    elif time_remaining > 45:
        
        new_bg = backgrounds["Sunset"]
    else:
        new_bg = backgrounds["Night"]

     # mise a jour dynamique de la taille de la fenetre
    window.update_idletasks()  
    window_width = window.winfo_width()
    window_height = window.winfo_height()


    #Dimensions par defaut si la fenêtre na pas encore ete mise a jour
    if window_width == 0:
        
          window_width = 800
        
    if window_height == 0:
        window_height = 900

     # Chargement et redimensionnement du background
    imag = Image.open(new_bg)
    
    imag = imag.resize((window_width, window_height), Image.Resampling.LANCZOS)
    
    new_bg_image = ImageTk.PhotoImage(imag)

     # mise ajour du label de fond
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    bg_label.config(image=new_bg_image)
    
    bg_label.image = new_bg_image

# fonction pour sauvegarder le score du joueur avec le fichier JSON
def save_score(player_name, score, difficulty, time_spent):
    try:
        if os.path.exists(scores_file):
            with open(scores_file, "r") as file:
                
                
                scores = json.load(file)
        else:
            scores = []
# ajout de nouvelles donnes au tableau des scores
        scores.append({
            "player_name": player_name,
            "score": score,
            "difficulty": difficulty,
            "time_spent": time_spent
            
            
        })
# ecrire  les scores  dans le fichier
        with open(scores_file, "w") as file:
            
            json.dump(scores, file, indent=4)

    except Exception as e:
        print(f"Error when saving the score {e}")

# fonctions pour jouer les differents sons
def play_win_sound():
    threading.Thread(target=playsound, args=(win_sound_path,), daemon=True).start()
def play_lose_sound():
    threading.Thread(target=playsound, args=(lose_sound_path,), daemon=True).start()

def play_flip_card_sound():
    threading.Thread(target=playsound, args=(flip_card_sound_path,), daemon=True).start()

#fct pour ameliorer l affichage de difficulte (en cours)
def update_difficulty_highlight(selected):
    for rb in difficulty_frame.winfo_children():
        if isinstance(rb, tk.Radiobutton):
            rb.config(bg="#2e3f4f" if rb.cget("value") != selected else "#FFD700")

# variables globales pour suivre l etat du jeu ; boutons,images,score ...
selected_buttons = []
selected_images = []
score = 0
found_pairs = 0
buttons = []
time_remaining = 180
timer_running = False
grid_size = (4, 5)
player_name = ""
card_images = []
total_pairs = 0

excluded_images = ["background_image.jpg", "day1.png", "day2.png", "day3.png", "day4.png"]
#images valides pour le jeu
valid_images = [
    f for f in os.listdir(image_folder)
    if f.endswith((".png", ".jpg", ".jpeg")) and f != "card_back.png" and f not in excluded_images
]
# fct pour recuperer les images pour le jeu
def load_images(num_pairs):
    
    global card_images
    #efface les images precedamment chargees
    card_images.clear()

    # Verifier si le nombre d'images valides est suffisant(gestion des  erreurs)
    if len(valid_images) < num_pairs:
        
        raise ValueError("Not enough  images for the selected difficulty.")

      # Choix aleatoire des images pour le jeu
    chosen_images = random.sample(valid_images, num_pairs)
    
      # Calcul des dimensions des boutons en fonction de la taille de la fenetre et de la grille
    window_width = window.winfo_width()
    window_height = window.winfo_height()
        # Defini les dimensions de la grille en fonction du niveau de difficulte

    if num_pairs == 6:  # simple
        rows, cols = 2, 6
    elif num_pairs == 9:  # Intermediate level
        rows, cols = 3, 6
    elif num_pairs == 12:  # difficile
        rows, cols = 4, 6  

      ## dt la taille des boutons en pixels avec des limite maximale
    button_width = min(120, (window_width - 100) // cols)
    button_height = min(150, (window_height - 300) // rows)

    # Charger et redimensionner les images
    images = []
    for file in chosen_images:
        imag = Image.open(os.path.join(image_folder, file))
        imag = imag.resize((button_width, button_height), Image.Resampling.LANCZOS)
        
        images.append(ImageTk.PhotoImage(imag))

    ## dupliquer chaque image pour creer des paires et mélanger la liste
    card_images = images + images
    random.shuffle(card_images)

    return card_images

##  initialiser le jeu
def start_game():
    global player_name, grid_size, total_pairs, time_remaining

    # Recuperer le nom du joueur
   
    message_label.config(text=f"Welcome {player_name}!Good luck!", bg="#2e3f4f")

    ## Df la taille de la grille et le nombre de paires en fonction  de difficulté
    level = difficulty_var.get()
    if level == "Easy":
        total_pairs = 6
        
        grid_size = (2, 3)
    elif level == "Intermediate":
        total_pairs = 9
        grid_size = (3, 6)
    elif level == "Hard":
         total_pairs = 12  # 12 paires  = 24 cards
         grid_size = (4, 6)  # 4 ligne x 6 colonnes

    # Initialiser  le temps restant 3 minutes
    time_remaining = 180

    ## Définit le backgound initial pour le jeu morning
    set_gameplay_background("Morning")

    ### Change l  ecran vers le jeu
    start_frame.grid_remove()
    game_frame.grid(row=0, column=0, sticky="nsew")
    create_game_ui(total_pairs)

# Signup Window
def show_signup():
    signup_window = tk.Toplevel(window)
    signup_window.title("Signup")
    signup_window.geometry("400x300")  # Set the window size to 400x300
    tk.Label(signup_window, text="Username:", font=("Helvetica", 14)).pack(pady=10)
    username_entry = tk.Entry(signup_window, font=("Helvetica", 12))
    username_entry.pack(pady=5)
    tk.Label(signup_window, text="Password:", font=("Helvetica", 14)).pack(pady=10)
    password_entry = tk.Entry(signup_window, show="*", font=("Helvetica", 12))
    password_entry.pack(pady=5)
    def signup_action():
        username = username_entry.get()
        password = password_entry.get()
        message = signup(username, password)
        messagebox.showinfo("Signup", message)
        if "successful" in message:
            signup_window.destroy()
    tk.Button(signup_window, text="Signup", command=signup_action, font=("Helvetica", 14), bg=BUTTON_BG, fg=BUTTON_FG).pack(pady=20)

# Login Window
def show_login():
    login_window = tk.Toplevel(window)
    login_window.title("Login")
    login_window.geometry("400x300")  # Set the window size to 400x300
    tk.Label(login_window, text="Username:", font=("Helvetica", 14)).pack(pady=10)
    username_entry = tk.Entry(login_window, font=("Helvetica", 12))
    username_entry.pack(pady=5)
    tk.Label(login_window, text="Password:", font=("Helvetica", 14)).pack(pady=10)
    password_entry = tk.Entry(login_window, show="*", font=("Helvetica", 12))
    password_entry.pack(pady=5)
    def login_action():
      username = username_entry.get()
      password = username_entry.get()  # Update this to retrieve the correct password field value
      message = login(username, password)
      if "successful" in message:
        global player_name
        player_name = username
        messagebox.showinfo("Login", message)
        login_window.destroy()
        
        # affice le bouton special level
        # 
        tk.Button(
            start_frame,
            text="Special Level",
            command=lambda: special_level_game(player_name, 1),  # Pass appropriate level
            font=("Helvetica", 16),
            bg=BUTTON_BG,
            fg=BUTTON_FG,
        ).place(relx=0.5, rely=0.3, anchor="center") # Position the button in the center of the screen
      else:
        messagebox.showerror("Login Failed", message)

    tk.Button(login_window, text="Login", command=login_action, font=("Helvetica", 14), bg=BUTTON_BG, fg=BUTTON_FG).pack(pady=20)

##creer le fenetre pricipale de l app
window = tk.Tk()
window.title("Memory Card Game")
window.geometry("800x900")
window.configure(bg="#2e3f4f")
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

card_back_image = ImageTk.PhotoImage(Image.open(os.path.join(image_folder, "card_back.png")).resize((150, 150)))

BUTTON_BG = "#4CAF50"
BUTTON_FG = "#ffffff"
HIGHLIGHT_BG = "#FFD700"
CARD_BACK_COLOR = "#1e293b"


# Load and resize the background image for start_frame
background_image_path = os.path.join(image_folder, "background_image.jpg")  # Replace with your actual image path
bg_start_image = Image.open(background_image_path).resize((800, 900), Image.Resampling.LANCZOS)
bg_start_photo = ImageTk.PhotoImage(bg_start_image)

start_frame = tk.Frame(window)
start_frame.grid(row=0, column=0, sticky="nsew")
start_frame.grid_rowconfigure(0, weight=1)
start_frame.grid_columnconfigure(0, weight=1)

bg_start_label = tk.Label(start_frame)
bg_start_label.place(relx=0, rely=0, relwidth=1, relheight=1)

game_frame = tk.Frame(window, bg="#2e3f4f")
game_frame.grid(row=0, column=0, sticky="nsew")
game_frame.grid_rowconfigure(0, weight=1)
game_frame.grid_columnconfigure(0, weight=1)


bg_label = tk.Label(game_frame)
new_bg = backgrounds["Morning"]
bg_image = ImageTk.PhotoImage(Image.open(new_bg).resize((800, 900)))
bg_label.config(image=bg_image)
bg_label.image = bg_image
bg_label.place(relwidth=1, relheight=1)  


game_frame.grid_remove()  #
start_frame.grid()        # 

#  titre de l app
title_label = tk.Label(
    start_frame,
    
    text="Memory Card Game",
    font=("Helvetica", 36, "bold"),
    bg="#2e3f4f",  # 
    
    fg="#FFD700"
)
title_label.place(relx=0.5, rely=0.1, anchor="center")  
# boutons pour login et signup
tk.Button(start_frame,
          text="Login",
          command=show_login,
          font=("Helvetica", 16),
          bg=BUTTON_BG, fg=BUTTON_FG).place(relx=0.4,
                                            rely=0.3, anchor="center")
tk.Button(start_frame, text="Signup", command=show_signup, font=("Helvetica", 16), bg=BUTTON_BG, fg=BUTTON_FG).place(relx=0.6, rely=0.3, anchor="center")




## pour la difficulte dans l ecran pricip
difficulty_var = tk.StringVar(value="Intermediate")  # 
difficulty_frame = tk.Frame(start_frame, bg="#2e3f4f")  # 
difficulty_frame.place(relx=0.5, rely=0.5, anchor="center")
tk.Label(
    difficulty_frame,
    text="Select difficulty:",
    font=("Helvetica", 18),
    bg="#2e3f4f",
    fg="#ffffff"
).grid(row=0, column=0, padx=10, pady=10)
tk.Radiobutton(
    difficulty_frame,
    text="Easy",
    variable=difficulty_var,  # 
    value="Easy",
    font=("Helvetica", 14),
    bg="#2e3f4f",
    fg="#ffffff",
    selectcolor="#3b4754"
).grid(row=0, column=1)
tk.Radiobutton(
    difficulty_frame,
    text="Intermediate",
    variable=difficulty_var,  
    value="Intermediate",
    font=("Helvetica", 14),
    bg="#2e3f4f",
    fg="#ffffff",
    selectcolor="#3b4754"
).grid(row=1, column=1)
tk.Radiobutton(
    difficulty_frame,
    text="Hard",
    variable=difficulty_var,  
    value="Hard",
    font=("Helvetica", 14),
    bg="#2e3f4f",
    fg="#ffffff",
    selectcolor="#3b4754"
).grid(row=2, column=1)

# Start button
start_button = tk.Button(
    start_frame,
    text="Start Game",
    command=start_game,
    font=("Helvetica", 16),
    bg=BUTTON_BG,
    fg=BUTTON_FG,
    relief="solid",
    bd=0,
    width=20
)
# pour afficher le niveau actuel
current_level_label = tk.Label(
    difficulty_frame,
    text="Your Current Level: ",
    font=("Helvetica", 14),
    bg="#2e3f4f",
    fg="#ffffff"
)
current_level_label.grid(row=3, column=0, columnspan=2, pady=10)

##positionnement du bouton
start_button.place(relx=0.5, rely=0.7, anchor="center")  

message_label = tk.Label(start_frame, text="", font=("Helvetica", 18), fg="#ffffff", bg="#2e3f4f", wraplength=700, justify="center")
message_label.place(relx=0.5, rely=0.8, anchor="center")  



## poour le temps et le score
score_label = tk.Label(game_frame, text="Score: 0", font=("Helvetica", 18, "bold"), bg="#4CAF50", fg="#ffffff", width=15)
timer_label = tk.Label(game_frame, text="Time: 3:00", font=("Helvetica", 18, "bold"), bg="#FF5722", fg="#ffffff", width=15)

grid_frame = tk.Frame(game_frame, bg="#2e3f4f")
restart_button = None
##ajuste l'image d'arrière-plan en fonction de la taille actuelle de la fenêtre.
def setup_background():
    global bg_start_photo
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    if window_width == 1: 
        window_width = 800
    if window_height == 1:
        window_height = 900
    bg_image = Image.open(background_image_path)
    bg_image = bg_image.resize((window_width, window_height), Image.Resampling.LANCZOS)
    bg_start_photo = ImageTk.PhotoImage(bg_image)
    bg_start_label.configure(image=bg_start_photo)
    bg_start_label.image = bg_start_photo

def on_window_resize(event):
    if event.widget == window:
        setup_background()

window.bind('<Configure>', on_window_resize)

def set_initial_background():
    global bg_label

    # day1.png
    new_bg = backgrounds["Morning"]  # day1.png chemin
    initial_bg_image = ImageTk.PhotoImage(Image.open(new_bg).resize((800, 900)))
    bg_label.config(image=initial_bg_image)
    bg_label.image = initial_bg_image  ## pour garbage collection


###Change le background en fonction du moment de la partie day-evening-night.
def set_gameplay_background(background_key):
    global bg_label
    new_bg = backgrounds[background_key]
    
    # Get the window size
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    
    # size par defaut si la fenetre n apas encore ete redimensionnee
    if window_width == 0:
        window_width = 800
        
        
    if window_height == 0:
        window_height = 900
    
             # chargement et redimensionnement de l'image de fond
    imag = Image.open(new_bg)
    
    imag = imag.resize((window_width, window_height), Image.Resampling.LANCZOS)
    gameplay_bg_image = ImageTk.PhotoImage(imag)
    
    
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    bg_label.config(image=gameplay_bg_image)
    
    bg_label.image = gameplay_bg_image


set_gameplay_background("Morning")  # definit day1.png






def create_game_ui(total_pairs):
    #  initialisation des variable globales
    global buttons, score, found_pairs, restart_button

### reinitialise les variables de jeu
    buttons.clear()
    score = 0
    found_pairs = 0
    #placement des labels et bouton
    score_label.grid(row=2, column=0, pady=10)
    
    timer_label.grid(row=3, column=0, pady=10)
    grid_frame.grid(row=4, column=0, pady=10)
    #verifie si le bouton restart existe deja
    if restart_button:
        restart_button.grid_remove()
        #  cree un bouton pour redemarrer le jeu
    restart_button = tk.Button(
        game_frame,
        text="Restart",
        command=reset_game,
        font=("Helvetica", 14),
        bg="#FFA500",
        fg="#ffffff",
        relief="solid",
        bd=0
    )
    restart_button.grid(row=5, column=0, pady=10)
    # Crée un nouveau bouton "Home" pour revenir à l'écran d'accueil
    if not hasattr(game_frame, "home_button"):
        home_button = tk.Button(
            game_frame,
            text="Home",
            command=go_to_home,
            font=("Helvetica", 14),
            bg="#FF5722",
            fg="#ffffff",
            relief="solid",
            bd=0
        )
        home_button.grid(row=6, column=0, pady=10)
        game_frame.home_button = home_button
    else:
        game_frame.home_button.grid(row=6, column=0, pady=10)

    game_images = load_images(total_pairs)
    ## Boucle pour creer les boutons representant les cartes
    for idx, image in enumerate(game_images):
        row = idx // 6
        
        col = idx % 6
        ## cree un boutonpour chaque carte avec une image de dos par defaut
        button = tk.Button(grid_frame, image=card_back_image, relief="solid", bd=2,
                           highlightbackground=HIGHLIGHT_BG,
                           command=lambda idx=idx: on_button_click(idx), width=150, height=150)

        button.grid(row=row, column=col, padx=10, pady=10)
        buttons.append((button, image))
    #demarre le timer
    start_timer()
    


def on_button_click(index):
    global selected_buttons, selected_images, found_pairs, total_pairs

    # empeche de retourner plus de deux carte  lorsque le jeu est terminé
    if len(selected_buttons) == 2 or not timer_running:
        return
     ## recuperer le bouton et l image associee
    button, image = buttons[index]



    # empeche de retourner une carte deja retourne
    if button in [b for b, _ in selected_buttons] or button["state"] == "disabled":
        return

    play_flip_card_sound()  # flip sound

    # flip card animation
    def smooth_card_flip(button, new_image):
        # fonction pour reduire la taille du bouton et changer l image
        def shrink():
            for scale in range(150, 0, -15):  # 
                button.config(width=scale)
                
                window.update_idletasks()
                window.after(30)  # 
                ##change l image de la carte
            button.config(image=new_image)  

            # # # Augmente la largeur de la carte progressivement pour completer l animation
            for scale in range(0, 150, 15):  
                button.config(width=scale)
                window.update_idletasks()
                window.after(30)  # Pause 
            button.config(width=150)  

        
        shrink()

    # flip  card
    smooth_card_flip(button, image)

    # ajoute le bouton et l image a la liste des cartes retournees
    selected_buttons.append((button, image))
    selected_images.append(image)

    #  Verifie si deux cartes ont ete retournees
    if len(selected_buttons) == 2:
        window.after(500, check_pair)  ## retarde la verification de la paire de 500ms

def check_pair():
    global selected_buttons, selected_images, found_pairs, total_pairs, score

    if selected_images[0] == selected_images[1]:  # match
        found_pairs += 1
        score += 10  
        score_label.config(text=f"Score: {score}")

        # 
        for button, _ in selected_buttons:
            button.config(state="disabled")
            
            
    else:  # No match # si les cartes ne correspondent pas
        for button, _ in selected_buttons:
            button.config(image=card_back_image)

    # clear 
    selected_buttons.clear()
    selected_images.clear()

    # verif si le jeu est terminé
    if found_pairs == total_pairs:
        stop_timer()
        play_win_sound()
        end_game(f"Congratulations!You won with a score of {score}!")
# pour cacher les cartes
def hide_cards():
    
    for button, _ in selected_buttons:
        
        button.config(image=card_back_image)
    selected_buttons.clear()
    selected_images.clear()

def start_timer():
    global timer_running
    timer_running = True
    update_timer()
    
    
##fonction pour mettre a jour le timer
def update_timer():
    global time_remaining, timer_running

    if timer_running and time_remaining > 0:
        minutes, seconds = divmod(time_remaining, 60)
        timer_label.config(text=f"Time: {minutes}:{seconds:02d}")
        time_remaining -= 1

        # update  background
        change_background_ontime()

        #  next timer update
        window.after(1000, update_timer)
    elif time_remaining <= 0:
        timer_running = False
        
        play_lose_sound()
        end_game("Time s up :( !Click restart to try again.")
##pour afficher les scores dans end_game
def display_leaderboard(frame, scores):
    for idx, score_entry in enumerate(scores, start=1):
        tk.Label(frame, text=f"{idx}.", font=("Helvetica", 12, "bold")).grid(row=idx, column=0, padx=5)
        tk.Label(frame, text=score_entry['player_name'], font=("Helvetica", 12)).grid(row=idx, column=1, padx=5)
        tk.Label(frame, text=f"{score_entry['score']} pts", font=("Helvetica", 12)).grid(row=idx, column=2, padx=5)
        tk.Label(frame, text=f"{score_entry['difficulty']}", font=("Helvetica", 12)).grid(row=idx, column=3, padx=5)
        tk.Label(frame, text=f"{score_entry['time_spent']}s", font=("Helvetica", 12)).grid(row=idx, column=4, padx=5)
##pour la fin du jeu game over et congrats
def end_game(message):
     # Calcule le temps passé pendant la partie
    time_spent = 180 - time_remaining
    ##recupere le score et la difficulte et sauvegarde le score
    difficulty = difficulty_var.get()
    save_score(player_name, score, difficulty, time_spent)

## creer une fenetre pour la fin du jeu
    end_game_window = tk.Toplevel()
    end_game_window.title("Game Over")

    tk.Label(end_game_window, text=message, font=("Helvetica", 16)).pack(pady=10)
    tk.Label(end_game_window, text=f"Your Score: {score}", font=("Helvetica", 14)).pack(pady=5)
##pour afficher le tableau des scores dans la fenetre de fin de jeu
    leaderboard_frame = tk.Frame(end_game_window)
    leaderboard_frame.pack(pady=10)
# Crée un menu déroulant pour filtrer les scores par niveau de difficulté
    tk.Label(end_game_window, text="Leaderboard", font=("Helvetica", 16, "bold")).pack(pady=5)
    difficulty_dropdown = tk.StringVar(value="All")
    dropdown = tk.OptionMenu(end_game_window, difficulty_dropdown, "Easy", "Intermediate", "Hard", command=lambda diff: update_leaderboard(leaderboard_frame, diff))
    dropdown.pack()
##afficher les scores en fonction de la difficulte
    high_scores = get_high_scores_by_difficulty(difficulty)
    display_leaderboard(leaderboard_frame, high_scores)

    tk.Button(end_game_window, text="Restart Game", command=reset_game, font=("Helvetica", 12)).pack(pady=5)
    tk.Button(end_game_window, text="Close", command=end_game_window.destroy, font=("Helvetica", 12)).pack(pady=5)

def update_score(points=10):
    global score
    score += points
    score_label.config(text=f"Score: {score}")

def stop_timer():
    global timer_running
    timer_running = False

def disable_buttons():
    for button, _ in buttons:
        button.config(state="disabled")

##pour le bouton restart
def reset_game():
    global timer_running, time_remaining, score, found_pairs
    timer_running = False
    time_remaining = 180
    score = 0
    found_pairs = 0
    selected_buttons.clear()
    selected_images.clear()

    score_label.config(text=f"Score: {score}")
    timer_label.config(text="Time: 3:00")

    for button, _ in buttons:
        button.destroy()
    buttons.clear()
    game_frame.grid_remove()
    start_game()

###pour le bouton home
def go_to_home():
    global timer_running, time_remaining, score, found_pairs, selected_buttons, selected_images

    # Reset game variables
    timer_running = False
    time_remaining = 180
    score = 0
    found_pairs = 0
    selected_buttons.clear()
    selected_images.clear()

    # enlever les boutons 
    for button, _ in buttons:
        button.destroy()
    buttons.clear()

    # enlever le frame du jeu
    for widget in game_frame.winfo_children():
        widget.grid_forget()

    # cacher le frame du jeu et afficher le frame de d acceuil
    game_frame.grid_forget()
    start_frame.grid(row=0, column=0, sticky="nsew")

    
    setup_background()

    #  mettre a jour le fond d ecran
    window.update_idletasks()





def create_db():
    ##creer un fichier JSON pour les scores
    if not os.path.exists(scores_file):
        with open(scores_file, "w") as file:
            json.dump([], file, indent=4)

def get_high_scores(limit=5):
    try:
        if os.path.exists(scores_file):
            with open(scores_file, "r") as file:
                scores = json.load(file) ##recuperer les scores depuis le fichier json
        else:
            return []
        ##trie les scores par ordre decroissant et retourne les 5 premiers
        return sorted(scores, key=lambda x: x["score"], reverse=True)[:limit]
    except Exception as e:
        print(f"Error reading scores: {e}")
        return []

def show_scores():
    ##creer une fenetre pour afficher les scores
    scores_window = tk.Toplevel()
    scores_window.title("Scores")
    scores_window.geometry("400x300")
    
    ##creer un canvas pour afficher les scores
    canvas = tk.Canvas(scores_window)
    scrollbar = tk.Scrollbar(scores_window, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    ##recuperer les scores et les afficher
    high_scores = get_high_scores()
    if not high_scores:
        tk.Label(frame, text="No scores available.", font=("Arial", 12)).pack(pady=10)
    else:
        for idx, score in enumerate(high_scores, start=1):
            ##afficher les scores dans la fenetre
            tk.Label(
                frame,
                text=f"{idx}. {score['player_name']} - Score: {score['score']} - "
                     f"Difficulty: {score['difficulty']} - Time: {score['time_spent']}s",
                font=("Arial", 10)
            ).pack(anchor="w", padx=10, pady=5)

def get_high_scores_by_difficulty(difficulty, limit=5):
    try:
        if os.path.exists(scores_file):
            with open(scores_file, "r") as file:
                scores = json.load(file)
        else:
            return []
         # Filtre les scores par niveau de difficulté
        filtered_scores = [s for s in scores if s['difficulty'] == difficulty]
        
        return sorted(filtered_scores, key=lambda x: x["score"], reverse=True)[:limit]
         # Trie les scores filtrés par ordre décroissant
    except Exception as e:
        print(f"Error reading scores: {e}")
        return []

def update_leaderboard(frame, difficulty):
    for widget in frame.winfo_children():
        widget.destroy()
    high_scores = get_high_scores_by_difficulty(difficulty)
    # Affiche les scores dans le cadre
    display_leaderboard(frame, high_scores)

create_db()


setup_background()
window.mainloop()