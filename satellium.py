# Initialisation des modules nécessaires à notre jeu (bah ouais sinon ça marche pas sans ça)
import pygame
import sys
import random
import time

# On initialise pygame pour pouvoir jouer
pygame.init()

# Configuration de la fenêtre de jeu (paye ta résolution pas terrible néanmoins si t'as un écran 144hz t'en profiteras)!
largeur_fenetre = 1440
hauteur_fenetre = 900
fps = 144
blanc = (255, 255, 255)
noir = (0, 0, 0)
fenetre = pygame.display.set_mode((largeur_fenetre, hauteur_fenetre))
pygame.display.set_caption("Satellium")

# Attribution d'un logo spécial à la fenêtre de jeu (Oui le logo de Pygame craint sérieusement...)
logo = pygame.image.load("satellium.png")
pygame.display.set_icon(logo)

# Chargement des images utilisées dans le jeu (techniquement on va faire bouger des images sur une image... ça aurait pu être un cours de PAO avec des calques png xD)
fond_image = pygame.image.load("fond.png")
avion_image = pygame.image.load("avion.png")
alien_image = pygame.image.load("alien.png")
tir_image = pygame.image.load("tir.png")
missile_image = pygame.image.load("missile.png")
splash_image = pygame.image.load("Splash.png")
boom_image = pygame.image.load("Boom.png")
acceleration_image = pygame.image.load("acceleration.png")

# Initialisation du module de mixage audio pour les effets sonores (qui bug des fois et on a testé beaucoup de choses mais au bout de 3 sons simultantés eeeee c'est pas fou pygame il comprend plus ou alors on sait pas faire !)
pygame.mixer.init()
son_monstre_hurt = pygame.mixer.Sound("monstre_hurt.mp3")
son_blaster = pygame.mixer.Sound("blaster.mp3")
son_explosion = pygame.mixer.Sound("explosion.mp3")
son_powerup = pygame.mixer.Sound("powerup.mp3")
son_powerup.play()
son_powerup.set_volume(0.5)
#Son de l'afterburner de l'avion + mixage du volume (C'était trop fort mais flemme de réduire tout ça avec Audacity. Pourquoi se fatiguer quand Python peut nous aider?)
son_afterburner = pygame.mixer.Sound("afterburner.mp3")
son_afterburner.set_volume(0.4)

# Redimensionnement des images pour un affichage dans des normes normalement normées (Il fallait que l'alien soit énorme par rapport à l'avion dans nos normes).
fond_image = pygame.transform.scale(fond_image, (largeur_fenetre, hauteur_fenetre))
avion_image = pygame.transform.scale(avion_image, (50, 50))
alien_image = pygame.transform.scale(alien_image, (50, 50))
missile_image = pygame.transform.scale(missile_image, (20, 20))
splash_image = pygame.transform.scale(splash_image, (50, 50))
tir_image = pygame.transform.scale(tir_image, (40, 40))
boom_image = pygame.transform.scale(boom_image, (50, 50))
acceleration_image = pygame.transform.scale(acceleration_image, (50, 50))

# Fonction pour afficher l'avion à une position donnée (histoire qu'il s'affiche pas n'importe où)
def afficher_avion(x, y):
    fenetre.blit(avion_image, (x, y))

# Tout pareil mais pour l'alien et ainsi de suite pour les commentaires qui vont suivre
def afficher_alien(x, y):
    fenetre.blit(alien_image, (x, y))

# The same pour le missile
def afficher_missile(x, y):
    fenetre.blit(missile_image, (x, y))

# ...Le splash (oui on savait pas comment appeller la tâche de sang)
def afficher_splash(x, y):
    fenetre.blit(splash_image, (x, y))

# ...Le tir infligé par l'alien
def afficher_tir(x, y):
    fenetre.blit(tir_image, (x, y))

# ... Le "boom" (là c'est pas un manque d'inspiration on vous jure c'est juste qu'explosion.mp3 existe et pour éviter des confusions bah on a choisi boom)
def afficher_boom(x, y):
    fenetre.blit(boom_image, (x, y))

# ... L'effet d'accélération (On s'est dit que les flammes de kéké c'était pas mal jusqu'à ce que ça commence à être bien galère à gérer au niveau de l'affichage)
def afficher_acceleration(x, y):
    fenetre.blit(acceleration_image, (x, y))

# ... Le score pas très design (mais fait son job)
def afficher_score(score):
    police = pygame.font.Font(None, 36)
    texte_score = police.render(f"Score: {score}", True, blanc)
    fenetre.blit(texte_score, (largeur_fenetre - 150, 10))

# Ici c'est différent car on initialise les variables pour les mouvements de l'alien
direction_alien = random.choice([-1, 1])  # -1 pour gauche, 1 pour droite
etat_alien = "descente"

# Initialisation de l'état du boom comme invisible par défaut sinon il s'afficherait en permanence
boom_etat = "invisible"
acceleration_etat = False

# Et voilà le plat de résistance... la boucle principale du jeu que l'on défini
def jeu():
    global direction_alien, etat_alien, boom_etat, acceleration_etat  # Déclaration de variables globales
    clock = pygame.time.Clock()

    # Position initiale de l'avion
    avion_x = largeur_fenetre // 2 - 25
    avion_y = hauteur_fenetre - 100
    avion_vitesse = 5

    # Position initiale de l'alien
    alien_x = random.randint(0, largeur_fenetre - 50)
    alien_y = 50
    alien_vitesse = 1.5  

    # Position initiale du missile (pareil faut pas voir le splash en permanence mais que quand le missile touche l'alien donc on le rend invible)
    missile_x = 0
    missile_y = 0
    missile_vitesse = 10
    missile_etat = "pret"
    splash_etat = "invisible"

    # Position initiale du tir
    tir_vitesse = 7
    tir_x = alien_x + 10
    tir_y = alien_y + 30

    # Là on set les compteurs de temps à 0 et on fixe la durée d'invisibilité à 1 seconde
    temps_explosion = 0
    temps_pause = 0
    temps_reapparition = 0
    temps_invisibilite = 0
    duree_invisibilite = 1
    temps_splash = 0
    temps_boom = 0
    score = 0

    # Et maintenant que la boucle est définie bah on la lance (faut bien s'amuser un jour)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Comme on doit pouvoir faire bouger l'avion bah on lui attribue des touches
        touches = pygame.key.get_pressed()
        if touches[pygame.K_LEFT] and avion_x > 0:
            avion_x -= avion_vitesse
            son_afterburner.play()
        if touches[pygame.K_RIGHT] and avion_x < largeur_fenetre - 50:
            avion_x += avion_vitesse
            son_afterburner.play()
        if touches[pygame.K_UP] and avion_y > 0:
            avion_y -= avion_vitesse
            son_afterburner.play()
        if touches[pygame.K_DOWN] and avion_y < hauteur_fenetre - 100:
            avion_y += avion_vitesse
            son_afterburner.play()

        # Là c'est le truc bien chiant pour le son de l'effet d'accélération (car il doit être joué dans certaines conditions bien spécifiques)
        if (
            not touches[pygame.K_LEFT]
            and not touches[pygame.K_RIGHT]
            and not touches[pygame.K_UP]
            and not touches[pygame.K_DOWN]
        ):
            son_afterburner.stop()

        # Condition pour déclencher un son blaster lorsque le missile est tiré (bah ouais logique un missile avec un son de blaster c'est nouveau). On spécifie encore l'état de certains png pour qu'il s'affiche correctement et pas en permanence.
        if touches[pygame.K_SPACE] and missile_etat == "pret":
            missile_x = avion_x + 15
            missile_y = avion_y - 20
            missile_etat = "en_vol"
            splash_etat = "invisible"
            son_blaster.play()

        # Bon là c'est une condition qu'on aurait pu "concaténer" avec l'effet sonore de l'accélération mais ça sert à afficher l'image d'accélération et on a préféré scindé le tout car en fait ça buggait de base...
        if touches[pygame.K_UP]:
            acceleration_etat = True
        else:
            acceleration_etat = False

        # Complexité nous y voilà... l'alien était un peu trop statique et facile à touché donc on a randomisé ses déplacements en fonction de son état (c'est pas parfait mais il a l'air moins bête maintenant)
        if etat_alien == "descente":
            alien_y += alien_vitesse
            if alien_y >= hauteur_fenetre // 4:
                etat_alien = "random"

        elif etat_alien == "random":
            if random.random() < 0.02:  # Jouons avec les probabilités pour changer la direction de l'alien à chaque itération (vous aviez raison c'est des maths de dev un jeu...) 
                direction_alien = random.choice(["haut", "bas", "gauche", "droite"])

            if direction_alien == "haut" and alien_y > 0:
                alien_y -= alien_vitesse
            elif direction_alien == "bas" and alien_y < hauteur_fenetre - 50:
                alien_y += alien_vitesse
            elif direction_alien == "gauche" and alien_x > 0:
                alien_x -= alien_vitesse
            elif direction_alien == "droite" and alien_x < largeur_fenetre - 50:
                alien_x += alien_vitesse

        if alien_y <= 0 or alien_y >= hauteur_fenetre - 50:
            alien_y = max(0, min(alien_y, hauteur_fenetre - 50))

        # Voici un bidouillage pour rendre l'alien invisible pendant un certain temps une fois qu'il est touché avant de réapparaître (il faut simuler le décès)
        if (
            temps_invisibilite > 0
            and time.time() - temps_invisibilite <= duree_invisibilite
        ):
            afficher_alien(-100, -100)

        # Voici de quoi donner au missile un comportement de missile
        if missile_etat == "en_vol":
            missile_y -= missile_vitesse
            if missile_y < 0:
                missile_etat = "pret"

        # Gérons les collisions avec l'alien (encore des maths... et pour le coup merci à chatgpt)
        if (
            alien_x < missile_x < alien_x + 50
            and alien_y < missile_y < alien_y + 50
            and missile_etat == "en_vol"
        ):
            son_monstre_hurt.play()
            splash_etat = "visible"
            missile_etat = "pret"
            alien_y = 50
            alien_x = random.randint(0, largeur_fenetre - 50)
            temps_explosion = time.time()
            temps_pause = time.time()
            temps_invisibilite = time.time()
            score += 10 # +10 points pour Gryffondor(à savoir nous) si on touche l'alien
            temps_splash = time.time()
            boom_etat = "visible"

        # Gestion des collisions du tir avec l'avion (toujours des maths)
        if (
            avion_x < tir_x < avion_x + 50
            and avion_y < tir_y < avion_y + 50
        ):
            son_explosion.play()  # Là c'est pour que le son d'explosion soit joué lorsqu'un tir d'alien touche l'avion et que l'effet d'explosion apparaisse
            tir_y = alien_y + 30
            tir_x = alien_x + 10
            score -= 3 # -3 points pour Gryffondor qui sont dérober par Serpentard (notre alien est un Malfoy)
            temps_boom = time.time()
            boom_etat = "visible"

        # Gestion du tir de l'alien (pareil c'était un peu casse tête à implémenter)
        if time.time() - temps_pause >= 1:
            tir_y += tir_vitesse
        if tir_y > hauteur_fenetre:
            tir_y = alien_y + 30
            tir_x = alien_x + 10
        
        # Affichage du sang pendant 1 seconde lorsque l'alien se fait touché
        if splash_etat == "visible" and time.time() - temps_explosion >= 1:
            splash_etat = "invisible"

        # Ici pareil pour l'effet d'explosion quand l'avion se fait touché par un tir d'alien
        if boom_etat == "visible" and time.time() - temps_boom >= 1:
            boom_etat = "invisible"

        # Affichage du fond pour chaque frame (techniquement là on demande à ce que notre fond soit affiché 144 fois par seconde chaque seconde pour avoir une impression d'un fond statique et ça se défini de la sorte)
        fenetre.blit(fond_image, (0, 0))

        # Affichage des éléments du jeu (là on demande l'affichage de nos png dans notre fenêtre pygame sinon on aurait pas nos images sur notre fond)
        afficher_avion(avion_x, avion_y)
        afficher_alien(alien_x, alien_y)
        afficher_tir(tir_x, tir_y)
        if missile_etat == "en_vol":
            afficher_missile(missile_x, missile_y)
        if splash_etat == "visible" and time.time() - temps_splash < 1:
            afficher_splash(alien_x, alien_y)
        if boom_etat == "visible" and time.time() - temps_boom < 1:
            afficher_boom(avion_x, avion_y)
        if acceleration_etat:
            afficher_acceleration(avion_x, avion_y + 50)

        # Affichage du score (car faut se l'avouer sans ça on pas vraiment de but ni d'objectif à se fixer)
        afficher_score(score)

        # Rafraîchissement de l'écran à une fréquence constante (encore une histoire de Hz heureusement on a pas de filtre antialiasing à devoir implémenter)
        pygame.display.flip()
        clock.tick(fps)

# Et ça c'est le déclencheur magique pour que le jeu se lance quand on exécute tout ce gros script!
if __name__ == "__main__":
    jeu()
