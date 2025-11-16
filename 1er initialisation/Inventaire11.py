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
        
        [cite_start]self.__pas = 70         # [cite: 47]
        [cite_start]self.__pieces_or = 0    # [cite: 48]
        [cite_start]self.__gemmes = 2       # [cite: 49]
        [cite_start]self.__cles = 0         # [cite: 50]
        [cite_start]self.__des = 0          # [cite: 51]
        
        # --- 2. OBJETS PERMANENTS / AUTRES (Items) ---
        
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
        
    [cite_start]def perdre_pas(self, quantite=1): # [cite: 47]
        self.__pas -= quantite
        if self.__pas < 0:
            self.__pas = 0

    [cite_start]def gagner_pas(self, quantite): # [cite: 72, 73, 74, 75, 76]
        self.__pas += quantite

    # --- Pièces d'Or ---
    @property
    def pieces_or(self):
        return self.__pieces_or
    
    [cite_start]def gagner_pieces(self, quantite): # [cite: 48]
        self.__pieces_or += quantite

    [cite_start]def depenser_pieces(self, quantite): # [cite: 48]
        if self.__pieces_or >= quantite:
            self.__pieces_or -= quantite
            return True
        else:
            return False 

    # --- Gemmes ---
    @property
    def gemmes(self):
        return self.__gemmes
    
    [cite_start]def gagner_gemmes(self, quantite): # [cite: 49]
        self.__gemmes += quantite

    [cite_start]def depenser_gemmes(self, quantite): # [cite: 49]
        if self.__gemmes >= quantite:
            self.__gemmes -= quantite
            return True
        else:
            return False

    # --- Clés ---
    @property
    def cles(self):
        return self.__cles
    
    [cite_start]def gagner_cles(self, quantite): # [cite: 50]
        self.__cles += quantite

    [cite_start]def depenser_cles(self, quantite=1): # [cite: 50]
        if self.__cles >= quantite:
            self.__cles -= quantite
            return True
        else:
            return False
            
    # --- Dés ---
    @property
    def des(self):
        return self.__des
    
    [cite_start]def gagner_des(self, quantite): # [cite: 51]
        self.__des += quantite

    [cite_start]def depenser_des(self, quantite=1): # [cite: 51]
        if self.__des >= quantite:
            self.__des -= quantite
            return True
        else:
            return False

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
        'objet' sera une instance d'une classe (ex: Pelle()).
        """
        self.__objets_portes.append(objet)

    def a_objet(self, nom_classe_objet):
        """
        Vérifie si le joueur possède un objet permanent.
        Exemple d'utilisation : if inventaire.a_objet("Pelle"): ...
        
        (Fonctionne pour la Pelle, Marteau, Kit de crochetage, etc.)
        [cite_start][cite: 53, 54, 55, 56, 57]
        """
        for objet in self.__objets_portes:
            # On vérifie le nom de la classe de l'objet
            if objet.__class__.__name__ == nom_classe_objet:
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
                self.__objets_portes.remove(objet) # On le consomme
                return objet
        return None
