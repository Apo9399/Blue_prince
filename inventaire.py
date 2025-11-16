#inventaire.py
class Inventaire:
    """
    Représente l'inventaire complet du joueur.
    Il est divisé en deux parties :
    1. Les consommables (ressources comme les pas, l'or...).
    2. Les objets portés (permanents comme la pelle, ou autres comme la nourriture).
    """
    
    def __init__(self):
        """
        Initialise l'inventaire avec les valeurs de départ du PDF.
        """
        # --- 1. OBJETS CONSOMMABLES (Ressources) ---
        
        self.__pas = 70         # [cite: 47]
        self.__pieces_or = 1    # [cite: 48]
        self.__gemmes = 2       # [cite: 49]
        self.__cles = 1         # [cite: 50]
        self.__des = 1          # [cite: 51]
        
        # objet food
        self.__apple = 0
        self.__carrot = 0
        self.__meat = 0
        
        # --- 2. OBJETS PERMANENTS / AUTRES (Items) ---
        self.__lockpick = 0
        self.__rabbit_foot = 0
        self.__metal_detector = 0

        # Cette liste contiendra les *objets* (Pelle, Marteau, Pomme...)
        # que le joueur ramassera.
        self.__objets_portes = [] 

    
    # ==========================================================
    # --- PARTIE 1 : GESTION DES OBJETS CONSOMMABLES ---
    # ==========================================================

    # --- Pas ---
    @property
    def pas(self):
        return self.__pas
        
    def perdre_pas(self, quantite=1): # [cite: 47]
        self.__pas -= quantite
        if self.__pas < 0:
            self.__pas = 0

    def gagner_pas(self, quantite): # [cite: 72, 73, 74, 75, 76]
        self.__pas += quantite

    # --- Pièces d'Or ---
    @property
    def pieces_or(self):
        return self.__pieces_or
    
    def gagner_pieces(self, quantite): # [cite: 48]
        self.__pieces_or += quantite

    def depenser_pieces(self, quantite): # [cite: 48]
        if self.__pieces_or >= quantite:
            self.__pieces_or -= quantite
            return True
        else:
            return False 

    # --- Gemmes ---
    @property
    def gemmes(self):
        return self.__gemmes
    
    def gagner_gemmes(self, quantite): # [cite: 49]
        self.__gemmes += quantite

    def depenser_gemmes(self, quantite): # [cite: 49]
        if self.__gemmes >= quantite:
            self.__gemmes -= quantite
            return True
        else:
            return False

    # --- Clés ---
    @property
    def cles(self):
        return self.__cles
    
    def gagner_cles(self, quantite): # [cite: 50]
        self.__cles += quantite

    def depenser_cles(self, quantite=1): # [cite: 50]
        if self.__cles >= quantite:
            self.__cles -= quantite
            return True
        else:
            return False
            
    # --- Dés ---
    @property
    def des(self):
        return self.__des
    
    def gagner_des(self, quantite): # [cite: 51]
        self.__des += quantite

    def depenser_des(self, quantite=1): # [cite: 51]
        if self.__des >= quantite:
            self.__des -= quantite
            return True
        else:
            return False
        
    # --- Apple ---
    @property
    def apple(self):
        return self.__apple

    def gagner_apple(self, qty=1):
        self.__apple += qty

    def utiliser_apple(self):
        if self.__apple > 0:
            self.__apple -= 1
            self.gagner_pas(3)  # apple = +3 pas
            return True
        return False


    # --- Carrot ---
    @property
    def carrot(self):
        return self.__carrot

    def gagner_carrot(self, qty=1):
        self.__carrot += qty

    def utiliser_carrot(self):
        if self.__carrot > 0:
            self.__carrot -= 1
            self.gagner_pas(5)
            return True
        return False


    # --- Meat ---
    @property
    def meat(self):
        return self.__meat

    def gagner_meat(self, qty=1):
        self.__meat += qty

    def utiliser_meat(self):
        if self.__meat > 0:
            self.__meat -= 1
            self.gagner_pas(10)
            return True
        return False


    # --- Lockpick ---
    @property
    def lockpick(self):
        return self.__lockpick

    def gagner_lockpick(self, qty=1):
        self.__lockpick += qty


    # --- Rabbit Foot ---
    @property
    def rabbit_foot(self):
        return self.__rabbit_foot

    def gagner_rabbit_foot(self, qty=1):
        self.__rabbit_foot += qty


    # --- Metal Detector ---
    @property
    def metal_detector(self):
        return self.__metal_detector

    def gagner_metal_detector(self, qty=1):
        self.__metal_detector += qty

    # ==========================================================
    # --- PARTIE 2 : GESTION DES OBJETS PERMANENTS / AUTRES ---
    # ==========================================================

    @property
    def objets_portes(self):
        """ Getter pour obtenir la liste de tous les objets portés. """
        return self.__objets_portes

    def ajouter_objet(self, objet):
        """
        Appelé quand le joueur ramasse un objet (Pelle, Pomme...).
        'objet' sera une instance d'une classe (ex : Pelle()).
        """
        self.__objets_portes.append(objet)

    def a_objet(self, objet_name):
        """
        Vérifie si le joueur possède un objet.
        Supporte :
        - objets sous forme de string ("lockpick")
        - objets sous forme de classe (ex: Pelle())
        """
        for objet in self.__objets_portes:

            # 1) Cas où les objets sont des strings
            if isinstance(objet, str) and objet == objet_name:
                return True

            # 2) Cas où les objets sont des instances de classe
            if objet.__class__.__name__ == objet_name:
                return True
        
        return False


    def utiliser_objet(self, nom_classe_objet):
        """
        Trouve un objet consommable (comme "Pomme") et le supprime
        de la liste après utilisation.
        Retourne l'objet si trouvé, ou None sinon.
        """
        for objet in self.__objets_portes:
            if objet.__class__.__name__ == nom_classe_objet:
                self.__objets_portes.remove(objet) # On le consommer
                return objet
        return None
