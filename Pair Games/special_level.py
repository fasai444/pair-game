import tkinter as tk
from tkinter import messagebox
import random
import os
from PIL import Image, ImageTk
from playsound import playsound
import threading
import json
import bcrypt

##definition des variables globales
script_dir = os.path.dirname(os.path.abspath(__file__))
users_file = os.path.join(script_dir, "users.json")
sounds_dir = os.path.join(script_dir, "sounds")
win_sound_path = os.path.join(sounds_dir, "win_sound.wav")
lose_sound_path = os.path.join(sounds_dir, "lose_sound.wav")
flip_card_sound_path = os.path.join(sounds_dir, "flip_card.mp3")
scores_file = os.path.join(script_dir, "game_scores.json")
image_folder = os.path.join(script_dir, "images")
card_back_path = os.path.join(image_folder, "card_back.png")

## Variables globales pour le jeu
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
card_back_image = None

# arrieere plan dynamique
backgrounds = {
    "Morning": os.path.join(image_folder, "day1.png"),
    "Daytime": os.path.join(image_folder, "day2.png"),
    "Sunset": os.path.join(image_folder, "day3.png"),
    "Night": os.path.join(image_folder, "day4.png"),
}

## pour creer le fichier json des utilisateurs
def init_users_db():
    if not os.path.exists(users_file):
        with open(users_file, "w") as file:
            json.dump([], file)

def load_users():
    ### Charge les utilisateurs à partir du fichier JSON
    if os.path.exists(users_file):
        with open(users_file, "r") as file:
            return json.load(file)
    return []

def save_users(users):
    ## # Sauvegarde les utilisateurs dans le fichier JSON
    with open(users_file, "w") as file:
        json.dump(users, file, indent=4)

##recherche un utilisateur dans le fichier json
def find_user(username):
    users = load_users()
    for user in users:
        if user["username"] == username:
            return user
    return None

def update_user_level(username, level):
    ## # Met à jour le niveau de l'utilisateur
    users = load_users()
    for user in users:
        if user["username"] == username:
            user["current_level"] = level
    save_users(users)

def save_score(player_name, score, difficulty, time_spent):
    try:
        scores = []
        if os.path.exists(scores_file):
            with open(scores_file, "r") as file:
                scores = json.load(file)
              ##  # Ajoute un nouveau score
        scores.append({
            "player_name": player_name,
            "score": score,
            "difficulty": difficulty,
            "time_spent": time_spent
        })
        ### Sauvegarde dans le fichier JSON
        with open(scores_file, "w") as file:
            json.dump(scores, file, indent=4)
    except Exception as e:
        print(f"Error saving score: {e}")

# 
def play_win_sound():
    ## Joue le son de victoire dans un thread
    threading.Thread(target=playsound, args=(win_sound_path,), daemon=True).start()

def play_lose_sound():
    threading.Thread(target=playsound, args=(lose_sound_path,), daemon=True).start()

def play_flip_card_sound():
    threading.Thread(target=playsound, args=(flip_card_sound_path,), daemon=True).start()

# pour charger les images la meme methode dans le fichier pairgame avec qq changements
def load_images(num_pairs):
    valid_images = [f for f in os.listdir(image_folder) if f.endswith((".png", ".jpg", ".jpeg"))]
    if len(valid_images) < num_pairs:
        raise ValueError("Not enough images for the selected difficulty.")

    chosen_images = random.sample(valid_images, num_pairs)
    images = []
    for file in chosen_images:
        image = Image.open(os.path.join(image_folder, file)).resize((150, 150), Image.Resampling.LANCZOS)
        images.append(ImageTk.PhotoImage(image))
        
    # Duplique les images pour les paires et les mélange

    card_images = images + images
    random.shuffle(card_images)
    return card_images

# 
def load_card_back_image():
    global card_back_image
    if os.path.exists(card_back_path):
        image = Image.open(card_back_path).resize((150, 150), Image.Resampling.LANCZOS)
        card_back_image = ImageTk.PhotoImage(image)
    else:
        raise FileNotFoundError(f"Card back image not found at {card_back_path}")

def update_background(game_frame, timer_label, grid_frame):
    global time_remaining
    if time_remaining > 135:
        bg_path = backgrounds["Morning"]
    elif time_remaining > 90:
        bg_path = backgrounds["Daytime"]
    elif time_remaining > 45:
        bg_path = backgrounds["Sunset"]
    else:
        bg_path = backgrounds["Night"]

    # 
    bg_image = ImageTk.PhotoImage(Image.open(bg_path).resize((800, 600), Image.Resampling.LANCZOS))
    bg_label = tk.Label(game_frame, image=bg_image)
    bg_label.image = bg_image
    bg_label.place(relwidth=1, relheight=1)

  
    grid_frame.lift()  
    if timer_label: 
        timer_label.lift()




def smooth_card_flip(button, new_image):
    def flip_animation():
        for scale in range(150, 0, -30):  
            button.config(width=scale)
            button.update_idletasks()
            button.after(10)  
        button.config(image=new_image)
        for scale in range(0, 150, 30):  
            button.config(width=scale)
            button.update_idletasks()
            button.after(10) 
        button.config(width=150)
    flip_animation()





def special_level_game(username, level):
    global card_images, total_pairs, found_pairs, score, time_remaining

    
    load_card_back_image()

    
    user = find_user(username)
    if not user:
        messagebox.showerror("Error", "User not found")
        return

    # 
    current_level = user.get("current_level", level)  # Default to provided level if not set
    num_pairs = {1: 6, 2: 8, 3: 12}.get(current_level, 6)  # Default to 6 pairs

    
    try:
        card_images = load_images(num_pairs)
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return

  
    total_pairs = num_pairs

    found_pairs = 0
    score = 0
    time_remaining = 180

   
    create_ui(current_level, username)


def create_ui(current_level, username):
    global buttons, found_pairs, score, time_remaining, bg_label  # Declare global variables
    buttons.clear()
    found_pairs = 0
    score = 0
    time_remaining = 180

   
    game_frame = tk.Toplevel()
    game_frame.title(f"Level {current_level} - Special Level")
    game_frame.geometry("800x900")

   
    bg_label = tk.Label(game_frame)
    bg_label.place(relwidth=1, relheight=1)

    def resize_background(event=None):
        """Dynamically resize the background image to fit the screen."""
        if time_remaining > 135:
            bg_path = backgrounds["Morning"]
        elif time_remaining > 90:
            bg_path = backgrounds["Daytime"]
        elif time_remaining > 45:
            bg_path = backgrounds["Sunset"]
        else:
            bg_path = backgrounds["Night"]

        width = game_frame.winfo_width()
        height = game_frame.winfo_height()

       
        bg_image = Image.open(bg_path).resize((width, height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(bg_image)

      
        bg_label.configure(image=photo)
        bg_label.image = photo

  
    game_frame.bind("<Configure>", resize_background)

   
    score_label = tk.Label(
        game_frame,
        text="Score: 0",
        font=("Helvetica", 18, "bold"),
        bg="#4CAF50",
        fg="#ffffff",
        width=15
    )
    
    score_label.pack_forget()

    timer_label = tk.Label(
        game_frame,
        text="Time: 3:00",
        font=("Helvetica", 18, "bold"),
        bg="#FF5722",
        fg="#ffffff",
        width=15
    )
    timer_label.pack(pady=5)

    
    grid_frame = tk.Frame(game_frame, bg="#2e3f4f")
    grid_frame.pack(expand=True, padx=20, pady=20)

    
    restart_button = tk.Button(
        game_frame,
        text="Restart",
        command=lambda: restart_level(game_frame, current_level, username),
        font=("Helvetica", 14),
        bg="#FFA500",
        fg="#ffffff",
        relief="solid",
        bd=0
    )
    restart_button.pack(pady=5)

    home_button = tk.Button(
        game_frame,
        text="Home",
        command=game_frame.destroy,
        font=("Helvetica", 14),
        bg="#FF5722",
        fg="#ffffff",
        relief="solid",
        bd=0
    )
    home_button.pack(pady=5)

    
    for idx, img in enumerate(card_images):
        row, col = divmod(idx, 6)
        button = tk.Button(
            grid_frame,
            image=card_back_image,
            relief="solid",
            bd=2,
            highlightbackground="#FFD700",
            command=lambda idx=idx: on_card_click(idx, score_label, current_level, username),
            width=150,
            height=150
        )
        button.grid(row=row, column=col, padx=10, pady=10)
        buttons.append((button, img))

    def update_timer():
        """Updates the timer dynamically."""
        global time_remaining
        if time_remaining > 0:
            minutes, seconds = divmod(time_remaining, 60)
            timer_label.config(text=f"Time: {minutes}:{seconds:02d}")
            resize_background()  
            time_remaining -= 1
            game_frame.after(1000, update_timer)
        else:
            play_lose_sound()
            messagebox.showinfo("Time's Up", "Game Over!")
            game_frame.destroy()

    def on_card_click(index, score_label, current_level, username):
        """Handles card click events."""
        global found_pairs, score, selected_buttons, selected_images

       
        if len(selected_buttons) == 2:
            return

        button, image = buttons[index]
        if button in [b[0] for b in selected_buttons] or button.cget("state") == "disabled":
            return

        play_flip_card_sound()
        smooth_card_flip(button, image)

       
        selected_buttons.append((button, image))
        selected_images.append(image)

        if len(selected_buttons) == 2:
           
            if selected_images[0] == selected_images[1]:
                found_pairs += 1
                score += 10
                score_label.config(text=f"Score: {score}")

               
                for btn, _ in selected_buttons:
                    btn.config(state="disabled")

               
                selected_buttons.clear()
                selected_images.clear()

                
                if found_pairs == total_pairs:
                    play_win_sound()
                    if current_level == 3:
                        
                        messagebox.showinfo("Special Level Completed", "Congratulations! You have completed the special level!")
                        game_frame.destroy()
                    else:
                        messagebox.showinfo("Congratulations", f"Level {current_level} completed!")
                        update_user_level(username, current_level + 1)
                        game_frame.destroy()
                        special_level_game(username, current_level + 1)
            else:
                
                game_frame.after(1000, reset_selected_buttons)


    def reset_selected_buttons():
        """Resets unmatched card buttons."""
        global selected_buttons, selected_images

        for button, _ in selected_buttons:
            button.config(image=card_back_image)  
        selected_buttons.clear()
        selected_images.clear()

    def restart_level(game_frame, current_level, username):
        """Restarts the level."""
        game_frame.destroy()
        special_level_game(username, current_level)

    update_timer()





# 
def main():
   ##initialisation de la base de donnees des utilis
    init_users_db()

    # Cree la fenetre principale
    root = tk.Tk()
    root.withdraw() # Cache la fenetre principale 

   # Charge limage de dos des cartes
    load_card_back_image()

  # Lance le niveau spécial pour un utilisateur
    username = "test_user"
    special_level_game(username, 1)

   
    root.mainloop()

