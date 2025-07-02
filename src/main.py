import atspi_backend
import speech_backend
import input_listener

def main():
    print("[NVDA-Linux] Démarrage du prototype...")
    atspi_backend.print_accessible_tree()
    speech_backend.say("Bienvenue sur NVDA-Linux !")
    input_listener.listen_keys()

if __name__ == "__main__":
    main() 