# Q1: Ce programme permet de faire une division entière entre deux nombre x et y. (x diviser par y).
# Q2: Voici un exemple avec 2 valeurs x=20 et y=4:
def divEntier(x: int, y: int) -> int:
    if x < y:
        return 0
    else:
        x = x - y
        return divEntier(x, y) + 1
print(divEntier(20,4))

#Exercice 1
if __name__ == '__main__':
    x = int(input("x: "))
    y = int(input("y: "))
    print(divEntier(x,y))

#Exercice 2
if __name__ == '__main__':
    try:
        x = int(input("x: "))
        y = int(input("y: "))
    except ValueError:
        print("Enter a int")
    else:
        print(divEntier(x,y))

#Exercice 2.a
#On doit gérer cette erreur car, les 2 nombres doivent être entier.

#Exercice 3.a 
#Une erreur est générée car le programme tourne en boucle.

#Exercice 3.b 
if __name__ == '__main__':
    x = int(input("x: "))
    y = int(input("y: "))
    try:
        print(divEntier(x,y))
    except RecursionError:
        print("Enter a positif number, there is endless loop")

#Exercice 4.a 
def divEntier(x: int, y: int) -> int:
    if (x or y) < 0:
        raise ValueError("It’s not a positive number")
    if x < y:
        return 0
    else:
        x = x - y
        return divEntier(x, y) + 1

#Exercice 4.b
def divEntier(x: int, y: int) -> int:
    if y == 0:
        raise ValueError("The value of 'y' need to be strictly superior to 0")
    if x < y:
        return 0
    else:
        x = x - y
        return divEntier(x, y) + 1