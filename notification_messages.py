import enum
class English(enum.Enum):
    start = "Ride {0} has started"
    end = "Ride {0} has ended"
    pickup = "Pickup for ride {0} coming up"
    dropoff = "Dropoff for ride {0} coming up"
    save25 = "Save 25% when using the promocode {0} on your next ride"
    save50 = "Thank you for using swvl. Save 50% when using the promocode {0} on your next ride"

class French(enum.Enum):
    start = "Le voyage {0} a commencé"
    end = "Le voyage {0} est terminé"
    pickup = "Prise en charge pour le voyage {0} à venir"
    dropoff = "Retour pour le voyage {0} à venir"
    save25 = "Économisez 20% en utilisant le code promotionnel {0} lors de votre prochain voyage"
    save50 = "Merci d'utiliser swvl. Économisez 50% en utilisant le code promotionnel {0} lors de votre prochain voyage"
