# exercice 1
def lecture1(x:str):
    try:
        f=open(x ,'r')
    except FileNotFoundError:
        print("The file didn't exist") 
    except PermissionError:
        print("You haven't the permission to read this file") 
    except IOError:
        print("There is an issue on output/input of this file")
    except FileExistsError:
        print("This file already exist")
    else:
        a = f.read()
        print(a)
        f.close
    finally:
        print("This function is terminated")


# exercice 2
def lecture2(x:str):
    try:
        with open(x ,'r') as f:
            a = f.read()
    except FileNotFoundError:
        print("The file didn't exist") 
    except PermissionError:
        print("You haven't the permission to read this file") 
    except IOError:
        print("There is an issue on output/input of this file")
    except FileExistsError:
        print("This file already exist")
    else:
        print(a)
        
    finally:
        print("This function is terminated")
lecture1("Desktop\ex1.py")