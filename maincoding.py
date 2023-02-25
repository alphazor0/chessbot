import discord
import os
from fentoboardimage import fenToImage, loadPiecesFolder
import asyncio
import io
import nest_asyncio 
from PIL import Image
import numpy as np
import random
nest_asyncio.apply()
import constant

#Manipulation des images
def get_concat_h_resize(im1, im2, resample=Image.BICUBIC, resize_big_image=True):
    if im1.height == im2.height:
        _im1 = im1
        _im2 = im2
    elif (((im1.height > im2.height) and resize_big_image) or
          ((im1.height < im2.height) and not resize_big_image)):
        _im1 = im1.resize((int(im1.width * im2.height / im1.height), im2.height), resample=resample)
        _im2 = im2
    else:
        _im1 = im1
        _im2 = im2.resize((int(im2.width * im1.height / im2.height), im1.height), resample=resample)
    dst = Image.new('RGB', (_im1.width + _im2.width, _im1.height))
    dst.paste(_im1, (0, 0))
    dst.paste(_im2, (_im1.width, 0))
    return dst

def get_concat_v_resize(im1, im2, resample=Image.BICUBIC, resize_big_image=True):
    if im1.width == im2.width:
        _im1 = im1
        _im2 = im2
    elif (((im1.width > im2.width) and resize_big_image) or
          ((im1.width < im2.width) and not resize_big_image)):
        _im1 = im1.resize((im2.width, int(im1.height * im2.width / im1.width)), resample=resample)
        _im2 = im2
    else:
        _im1 = im1
        _im2 = im2.resize((im1.width, int(im2.height * im1.width / im2.width)), resample=resample)
    dst = Image.new('RGB', (_im1.width, _im1.height + _im2.height))
    dst.paste(_im1, (0, 0))
    dst.paste(_im2, (0, _im1.height))
    return dst


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


boardImage = fenToImage(
	fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
	squarelength=100,
	pieceSet=loadPiecesFolder("./pieces"),
	darkColor="#D18B47",
	lightColor="#FFCE9E"
)


#Poids des pièces
poids={"p":10,"n":30,"b":30,"r":50,"q":90,"k":900,"P":10,"N":30,"B":30,"R":50,"Q":90,"K":900}
equivLC={"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
equivLCInv={0:"a",1:"b",2:"c",3:"d",4:"e",5:"f",6:"g",7:"h"}

#Calculer la valeur du plateau 
def valeur(A,couleur):
    plateauBlanc=0
    plateauNoir =0 

        
    plateauBlanc = plateauBlanc + np.count_nonzero(A =="P")*10
    plateauBlanc = plateauBlanc + np.count_nonzero(A =="N")*30
    plateauBlanc = plateauBlanc + np.count_nonzero(A =="B")*30
    plateauBlanc = plateauBlanc + np.count_nonzero(A =="R")*50
    plateauBlanc = plateauBlanc + np.count_nonzero(A =="Q")*90
    plateauBlanc = plateauBlanc + np.count_nonzero(A =="K")*900
    plateauNoir = plateauNoir + np.count_nonzero(A =="p")*10
    plateauNoir = plateauNoir + np.count_nonzero(A =="n")*30
    plateauNoir = plateauNoir + np.count_nonzero(A =="b")*30
    plateauNoir = plateauNoir + np.count_nonzero(A =="r")*50
    plateauNoir = plateauNoir + np.count_nonzero(A =="q")*90
    plateauNoir = plateauNoir + np.count_nonzero(A =="k")*900


    if(couleur=="w"):
        return(plateauBlanc-plateauNoir)
    else:
        return(plateauNoir-plateauBlanc)


def fenToMatrice(fen):
    fen=fen.split("/")
    A = np.full((8,8),"0")

    for i in range(len(fen)):
        r=""
        for j in range(len(fen[i])):
            if fen[i][j].isalpha():
                r=r+fen[i][j]
            else:
                r=r+"0"*int(fen[i][j])

        for k in range(len(r)):
            A[i,k]=r[k]
            
    return(A)

def minimax(plateau, couleur, profondeur, maxo, valAVANT, move,alpha,beta):
    if profondeur ==0 or len(legmove(plateau,"w"))==0 or len(legmove(plateau,"b"))==0:
        
        return ["",valeurDEP(valAVANT, plateau, move)]
    
    if maxo:
        listMoves = legmove(plateau, couleur)
        iNIT = random.randint(0,len(listMoves)-1)
        maxvalue= valeurDEP(valAVANT, plateau, listMoves[iNIT])
        maxmove =listMoves[iNIT]
        
        for move in listMoves:
            B = deplacement(plateau, move)
            valAVANT= valeurDEP(valAVANT, plateau, move)
            val = minimax(B,couleur,profondeur-1,False, valAVANT, move,alpha,beta)[1]
            if val >maxvalue:
                maxvalue=val
                maxmove=move
            alpha= max(alpha,val)
            if(beta <= alpha):
                  break                        
        return [maxmove,maxvalue]
    
    if not maxo:
        listMoves= legmove(plateau, couleur)
        iNIT= random.randint(0,len(listMoves)-1)
        minvalue=valeurDEP(valAVANT,plateau,listMoves[iNIT])
        minmove=listMoves[iNIT]
        
        for move in listMoves:
            C=deplacement(plateau,move)
            valAVANT= valeurDEP(valAVANT, plateau, move)
            val=minimax(C, couleur,profondeur-1, True, valAVANT, move,alpha,beta)[1]
            if val<minvalue:
                minvalue=val
                minmove=move
            beta= min(beta,val)
            if(beta <= alpha):
                break
        return[minmove, minvalue]   
         
    
def MatriceTofen(A):
    fen=''
    for i in range(8):
        ligne= ''
        z=0
        
        for j in range(8):
            if (A[i,j].isalpha()):    
                if z!= 0:
                    ligne+=str(z)
                    z=0
                ligne+=A[i,j]  
            elif (A[i,j] == '0'):
                z+=1
            
        if z==0:
            fen+= ligne +"/"
        else:
            fen+= ligne+str(z)+'/'    
            
                
                
    return(fen[:-1])

def deplacement(A,s):
    B=np.copy(A)
    j=int(equivLC[s[0]])
    i=8-int(s[1])
    l=int(equivLC[s[2]])
    k=8-int(s[3])

    B[k,l]=B[i,j]
    B[i,j]="0"

    return(B)


def matriceToUCI(i,j,k,l):
    s=equivLCInv[j]+str(8-i)+equivLCInv[l]+str(8-k)
    
    return(s)

def movesPossibles(A,couleur):
    liste=[]
    
    if(couleur=="w"):
        for i in range(len(A)):
            for j in range(len(A[i])):
                if(A[i,j].isupper()):
                    
                    #Le pion
                    if(A[i,j]=="P"):
                        
                        if(i!=0):
                            if(A[i-1,j]=="0"):
                                liste.append(matriceToUCI(i,j,i-1,j))
                        if(i!=0 and j!=0):        
                            if(A[i-1,j-1].islower() and A[i-1,j-1]!="0"):
                                liste.append(matriceToUCI(i,j,i-1,j-1))
                        if(i!=0 and j!=7):    
                            if(A[i-1,j+1].islower() and  A[i-1,j+1]!="0"):
                                liste.append(matriceToUCI(i,j,i-1,j+1))
                        if(i==6):
                            if(A[i-1,j]=="0" and A[i-2,j]=="0"):
                                liste.append(matriceToUCI(i,j,i-2,j))
                                
                                
                    #La tour            
                    if(A[i,j]=="R"  or A[i,j]=="Q"):
                        
                        
                        #Vers le haut
                        k=i
                        continuation= True
                        while(continuation):
                            if(k!=0):
                                #Pas d'obstacle
                                if(A[k-1,j] == "0"):
                                    liste.append(matriceToUCI(i,j,k-1,j))
                                    
                            
                                #Pièce blanche
                                if(A[k-1,j].isupper()):
                                    continuation=False
                                
                                #Pièce blanche
                                if(A[k-1,j].islower() and A[k-1,j] !="0"):
                                    liste.append(matriceToUCI(i,j,k-1,j))
                                    continuation=False
                                k=k-1

                            if(k==0):
                                continuation=False

                        #Vers le bas
                        k=i
                        continuation= True
                        while(continuation):
                            if(k!=7):
                                #Pas d'obstacle
                                if(A[k+1,j] == "0"):
                                    liste.append(matriceToUCI(i,j,k+1,j))
                                    
                            
                                #Pièce blanche
                                if(A[k+1,j].isupper()):
                                    continuation=False
                                
                                #Pièce blanche
                                if(A[k+1,j].islower() and A[k+1,j] !="0"):
                                    liste.append(matriceToUCI(i,j,k+1,j))
                                    continuation=False
                                k=k+1

                            if(k==7):
                                continuation=False

                                                  
                        #Vers la gauche
                        l=j
                        continuation= True
                        while(continuation):
                            if(l!=0):
                                #Pas d'obstacle
                                if(A[i,l-1] == "0"):
                                    liste.append(matriceToUCI(i,j,i,l-1))
                                    
                            
                                #Pièce blanche
                                if(A[i,l-1].isupper()):
                                    continuation=False
                                
                                #Pièce blanche
                                if(A[i,l-1].islower() and A[i,l-1] !="0"):
                                    liste.append(matriceToUCI(i,j,i,l-1))
                                    continuation=False
                                l=l-1

                            if(l==0):
                                continuation=False                                
                                
                        #Vers la gauche
                        l=j
                        continuation= True
                        while(continuation):
                            if(l!=7):
                                #Pas d'obstacle
                                if(A[i,l+1] == "0"):
                                    liste.append(matriceToUCI(i,j,i,l+1))
                                    
                            
                                #Pièce blanche
                                if(A[i,l+1].isupper()):
                                    continuation=False
                                
                                #Pièce blanche
                                if(A[i,l+1].islower() and A[i,l+1] !="0"):
                                    liste.append(matriceToUCI(i,j,i,l+1))
                                    continuation=False
                                l=l+1

                            if(l==7):
                                continuation=False                                
                    #Le fou
                    if(A[i,j]=="B" or A[i,j]=="Q"):
                        
                       # diagonale bas gauche
                       k=i
                       l=j
                       continuation = True
                        
                       while(continuation):
                            if(k!=0 and l!=0):
                                #Pas d'obstacle
                                if(A[k-1,l-1]=="0"):
                                        liste.append(matriceToUCI(i,j,k-1,l-1))
                                      
                                        
                                #Obstacle pièce noire
                                if(A[k-1,l-1].islower() and A[k-1,l-1]!="0"):
                                        liste.append(matriceToUCI(i,j,k-1,l-1))
                                        continuation = False
                                        
                                if((A[k-1,l-1]).isupper() and A[k-1,l-1]!="0" ):
                                            continuation = False
                                l-=1
                                k-=1
                            if(k==0 or l==0):
                                continuation = False
                                
                       # diagonale bas droite
                       k=i
                       l=j
                       continuation = True
                       
                       while(continuation):
                           if(k!=0 and l!=7):
                               #Pas d'obstacle
                               if(A[k-1,l+1]=="0"):
                                       liste.append(matriceToUCI(i,j,k-1,l+1))
                                     
                                       
                               #Obstacle pièce noire
                               if(A[k-1,l+1].islower() and A[k-1,l+1]!="0"):
                                       liste.append(matriceToUCI(i,j,k-1,l+1))
                                       continuation = False
                                       
                               if((A[k-1,l+1]).isupper() and A[k-1,l+1]!="0" ):
                                           continuation = False
                               l+=1
                               k-=1
                                        
                           if(k==0 or l==7):
                               continuation = False
                                                       
                       # diagonale haut droite
                       k=i
                       l=j
                       continuation = True
                       
                       while(continuation):
                           if(k!=7 and l!=7):
                               #Pas d'obstacle
                               if(A[k+1,l+1]=="0"):
                                       liste.append(matriceToUCI(i,j,k+1,l+1))
                                       
                               #Obstacle pièce noire
                               if(A[k+1,l+1].islower() and A[k+1,l+1]!="0"):
                                       liste.append(matriceToUCI(i,j,k+1,l+1))
                                       continuation = False
                                       
                               if((A[k+1,l+1]).isupper() and A[k+1,l+1]!="0" ):
                                           continuation = False
                           if(k==7 or l==7):
                               continuation = False
                           l+=1
                           k+=1
                       # diagonale haut gauche
                       k=i
                       l=j
                       continuation = True
                       
                       while(continuation):
                           if(k!=7 and l!=0):
                               #Pas d'obstacle
                               if(A[k+1,l-1]=="0"):
                                       liste.append(matriceToUCI(i,j,k+1,l-1))
                         
                                       
                               #Obstacle pièce noire
                               if(A[k+1,l-1].islower() and A[k+1,l-1]!="0"):
                                       liste.append(matriceToUCI(i,j,k+1,l-1))
                                       continuation = False
                                       
                               if((A[k+1,l-1]).isupper() and A[k+1,l-1]!="0" ):
                                           continuation = False
                               l-=1
                               k+=1

                           if(k==7 or l==0):
                               continuation = False
                
                
                    #Le cavalier
                    if(A[i,j]=="N"):
                        
                        #Peut être beaucoup mieux formulé
                        x=[]
                        y=[]
                        
                        x.append(i+2)
                        y.append(j-1)
                        x.append(i+1)
                        y.append(j-2)
                        x.append(i-1)
                        y.append(j-2)
                        x.append(i-2)
                        y.append(j-1)
                        x.append(i-1)
                        y.append(j+2)
                        x.append(i-2)
                        y.append(j+1)
                        x.append(i+1)
                        y.append(j+2)
                        x.append(i+2)
                        y.append(j+1)
                                              
                        
                        for a in range(len(x)):
                            k=x[a]
                            l=y[a]
                            
                            #le point est bien dans les bords
                            if( k >=0 and k<=7 and l>=0 and l<=7):
                                
                                #Pièce blanche
                                if( not (A[k,l].isupper() and A[k,l] !="0")):
                                    liste.append(matriceToUCI(i, j, k, l))
                                    
                            
                    #Le roi
                    if(A[i,j]=="K"):
                        o=[-1,0,1]
                        
                        for v in range(3):
                            for u in range(3):
                                k=i+o[v]
                                l=j+o[u]
                                #le point est bien dans les bords
                                if( k >=0 and k<=7 and l>=0 and l<=7):
                                
                                    #Pièce blanche
                                    if( not (A[k,l].isupper() and A[k,l] !="0")):
                                        liste.append(matriceToUCI(i, j, k, l))      
                                        
                                        
  
    if( not couleur=="w"):
        for i in range(len(A)):
            for j in range(len(A[i])):
                if(A[i,j].islower()):
                    
                    #Le pion
                    if(A[i,j]=="p"):
                        
                        if(i!=7):
                            if(A[i+1,j]=="0"):
                                liste.append(matriceToUCI(i,j,i+1,j))
                        if(i!=7 and j!=0):        
                            if(A[i+1,j-1].isupper() and A[i+1,j-1]!="0"):
                                liste.append(matriceToUCI(i,j,i+1,j-1))
                        if(i!=7 and j!=7):    
                            if(A[i+1,j+1].isupper() and  A[i+1,j+1]!="0"):
                                liste.append(matriceToUCI(i,j,i+1,j+1))
                        if(i==1):
                            if(A[i+1,j]=="0" and A[i+2,j]=="0"):
                                liste.append(matriceToUCI(i,j,i+2,j))
                                
                                
                    #La tour            
                    if(A[i,j]=="r"  or A[i,j]=="q"):
                        
                        
                        #Vers le haut
                        k=i
                        continuation= True
                        while(continuation):
                            if(k!=0):
                                #Pas d'obstacle
                                if(A[k-1,j] == "0"):
                                    liste.append(matriceToUCI(i,j,k-1,j))
                                    
                            
                                #Pièce noire
                                if(A[k-1,j].islower()  and A[k-1,j] !="0"):
                                    continuation=False
                                
                                #Pièce blanche
                                if(A[k-1,j].isupper() and A[k-1,j] !="0"):
                                    liste.append(matriceToUCI(i,j,k-1,j))
                                    continuation=False
                                k=k-1

                            if(k==0):
                                continuation=False

                        #Vers le bas
                        k=i
                        continuation= True
                        while(continuation):
                            if(k!=7):
                                #Pas d'obstacle
                                if(A[k+1,j] == "0"):
                                    liste.append(matriceToUCI(i,j,k+1,j))
                                    
                            
                                #Pièce blanche
                                if(A[k+1,j].islower() and A[k+1,j] !="0"):
                                    continuation=False
                                
                                #Pièce blanche
                                if(A[k+1,j].isupper() and A[k+1,j] !="0"):
                                    liste.append(matriceToUCI(i,j,k+1,j))
                                    continuation=False
                                k=k+1

                            if(k==7):
                                continuation=False

                                                  
                        #Vers la gauche
                        l=j
                        continuation= True
                        while(continuation):
                            if(l!=0):
                                #Pas d'obstacle
                                if(A[i,l-1] == "0"):
                                    liste.append(matriceToUCI(i,j,i,l-1))
                                    
                            
                                #Pièce blanche
                                if(A[i,l-1].islower()):
                                    continuation=False
                                
                                #Pièce blanche
                                if(A[i,l-1].isupper() and A[i,l-1] !="0"):
                                    liste.append(matriceToUCI(i,j,i,l-1))
                                    continuation=False
                                l=l-1

                            if(l==0):
                                continuation=False                                
                                
                        #Vers la droite
                        l=j
                        continuation= True
                        while(continuation):
                            if(l!=7):
                                #Pas d'obstacle
                                if(A[i,l+1] == "0"):
                                    liste.append(matriceToUCI(i,j,i,l+1))
                                    
                            
                                #Pièce blanche
                                if(A[i,l+1].islower()):
                                    continuation=False
                                
                                #Pièce blanche
                                if(A[i,l+1].isupper() and A[i,l+1] !="0"):
                                    liste.append(matriceToUCI(i,j,i,l+1))
                                    continuation=False
                                l=l+1

                            if(l==7):
                                continuation=False                                
                    #Le fou
                    if(A[i,j]=="b" or A[i,j]=="q"):
                        
                       # diagonale bas gauche
                       k=i
                       l=j
                       continuation = True
                        
                       while(continuation):
                            if(k!=0 and l!=0):
                                #Pas d'obstacle
                                if(A[k-1,l-1]=="0"):
                                        liste.append(matriceToUCI(i,j,k-1,l-1))
                                      
                                        
                                #Obstacle pièce noire
                                if(A[k-1,l-1].isupper() and A[k-1,l-1]!="0"):
                                        liste.append(matriceToUCI(i,j,k-1,l-1))
                                        continuation = False
                                        
                                if((A[k-1,l-1]).islower() and A[k-1,l-1]!="0" ):
                                            continuation = False
                                l-=1
                                k-=1
                            if(k==0 or l==0):
                                continuation = False
                                
                       # diagonale bas droite
                       k=i
                       l=j
                       continuation = True
                       
                       while(continuation):
                           if(k!=0 and l!=7):
                               #Pas d'obstacle
                               if(A[k-1,l+1]=="0"):
                                       liste.append(matriceToUCI(i,j,k-1,l+1))
                                     
                                       
                               #Obstacle pièce noire
                               if(A[k-1,l+1].isupper() and A[k-1,l+1]!="0"):
                                       liste.append(matriceToUCI(i,j,k-1,l+1))
                                       continuation = False
                                       
                               if((A[k-1,l+1]).islower() and A[k-1,l+1]!="0" ):
                                           continuation = False
                               l+=1
                               k-=1
                                        
                           if(k==0 or l==7):
                               continuation = False
                                                       
                       # diagonale haut droite
                       k=i
                       l=j
                       continuation = True
                       
                       while(continuation):
                           if(k!=7 and l!=7):
                               #Pas d'obstacle
                               if(A[k+1,l+1]=="0"):
                                       liste.append(matriceToUCI(i,j,k+1,l+1))
                                       
                               #Obstacle pièce noire
                               if(A[k+1,l+1].isupper() and A[k+1,l+1]!="0"):
                                       liste.append(matriceToUCI(i,j,k+1,l+1))
                                       continuation = False
                                       
                               if((A[k+1,l+1]).islower() and A[k+1,l+1]!="0" ):
                                           continuation = False
                           if(k==7 or l==7):
                               continuation = False
                           l+=1
                           k+=1
                       # diagonale haut gauche
                       k=i
                       l=j
                       continuation = True
                       
                       while(continuation):
                           if(k!=7 and l!=0):
                               #Pas d'obstacle
                               if(A[k+1,l-1]=="0"):
                                       liste.append(matriceToUCI(i,j,k+1,l-1))
                         
                                       
                               #Obstacle pièce noire
                               if(A[k+1,l-1].isupper() and A[k+1,l-1]!="0"):
                                       liste.append(matriceToUCI(i,j,k+1,l-1))
                                       continuation = False
                                       
                               if((A[k+1,l-1]).islower() and A[k+1,l-1]!="0" ):
                                           continuation = False
                               l-=1
                               k+=1

                           if(k==7 or l==0):
                               continuation = False
                
                
                    #Le cavalier
                    if(A[i,j]=="n"):
                        
                        #Peut être beaucoup mieux formulé
                        x=[]
                        y=[]
                        
                        x.append(i+2)
                        y.append(j-1)
                        x.append(i+1)
                        y.append(j-2)
                        x.append(i-1)
                        y.append(j-2)
                        x.append(i-2)
                        y.append(j-1)
                        x.append(i-1)
                        y.append(j+2)
                        x.append(i-2)
                        y.append(j+1)
                        x.append(i+1)
                        y.append(j+2)
                        x.append(i+2)
                        y.append(j+1)
                                             
                 
                        
                        for a in range(len(x)):
                            k=x[a]
                            l=y[a]
                            
                            #le point est bien dans les bords
                            if( k >=0 and k<=7 and l>=0 and l<=7):
                                
                                #Pièce blanche
                                if( not (A[k,l].islower() and A[k,l] !="0")):
                                    liste.append(matriceToUCI(i, j, k, l))
                                    
                            
                    #Le roi
                    if(A[i,j]=="k"):
                        o=[-1,0,1]
                        
                        for v in range(3):
                            for u in range(3):
                                k=i+o[v]
                                l=j+o[u]
                                #le point est bien dans les bords
                                if( k >=0 and k<=7 and l>=0 and l<=7):
                                
                                    #Pièce blanche
                                    if( not (A[k,l].islower() and A[k,l] !="0")):
                                        liste.append(matriceToUCI(i, j, k, l))                                              
                                                                            
                                        
    return(liste)


def check(A,couleur):
    moves = movesPossibles(A, couleur)
    
    for move in moves:
        Z=deplacement(A,move)
        if(np.count_nonzero(Z=="k")==0 or np.count_nonzero(Z=="K")==0  ):
            return(True)



            
    return(False)


def legmove(A,couleur):
    moves = movesPossibles(A, couleur)
    colorA=''
    legmoves=[]
    if couleur =='w':
        colorA = 'b'
    if couleur == 'b':
        colorA= 'w'
        
  
    for i in range (len(movesPossibles(A, couleur))):
            Y=deplacement(A, moves[i])
            if check(Y, colorA) == False:
                legmoves.append(moves[i])
    return legmoves
            

def valeurDEP(val,A,s):
    j=int(equivLC[s[0]])
    i=8-int(s[1])
    l=int(equivLC[s[2]])
    k=8-int(s[3])
    
    i=l
    j=k

    if(A[i,j]=="P"):
        val=val-10
    if(A[i,j]=="N"):
        val=val-30
    if(A[i,j]=="B"):
        val=val-30
    if(A[i,j]=="R"):
        val=val-50
    if(A[i,j]=="Q"):
        val=val-90
    if(A[i,j]=="K"):
        val=val-900
    if(A[i,j]=="p"):
        val=val+10
    if(A[i,j]=="n"):
        val=val+30
    if(A[i,j]=="b"):
        val=val+30
    if(A[i,j]=="r"):
        val=val+50
    if(A[i,j]=="q"):
        val=val+90
    if(A[i,j]=="k"):
        val=val+900
    return(val)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


C=[]
game='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
joueur=''
B=[]
@client.event
async def on_message(message):
    global game
    global joueur
    global B
    couleur="w"
    
    
    
    if message.content.startswith('z'):
        if message.content == 'zchess start':
            
            joueur = message.author
            game='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
            A = fenToMatrice(game)
            with io.BytesIO() as image_binary:
                        boardImage.save(image_binary, 'PNG')
                        image_binary.seek(0)
                        await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))
   
    
    if( len(message.content))==4:
       A = fenToMatrice(game)
       if message.content in legmove(A,couleur):
           if message.author == joueur:
                A=fenToMatrice(game)
                C=deplacement(A,message.content)
                game=MatriceTofen(C)
                
       
                plateauDuJeu= fenToMatrice(game)
           
                if(couleur =="w"):
                               colorA="b"
                else:
                               colorA="w"
               
              

                A = fenToMatrice(game)
                meilleurMove= minimax(A, colorA, 3, True, valeur(A, colorA),"",-10000,10000)[0]
                
                A= deplacement(A,meilleurMove)
                game=MatriceTofen(A)
                BI= fenToImage(game,squarelength=100,
                pieceSet=loadPiecesFolder("./pieces"),              	
                darkColor="#D18B47",
                lightColor="#FFCE9E")     
                bords = Image.open('img/bords.png')
                bords2 = Image.open('img/bords2.png')
                
                img=get_concat_h_resize(bords,BI)
                img=get_concat_v_resize(img,bords2)

                with io.BytesIO() as image_binary:
                   img.save(image_binary, 'PNG')
                   image_binary.seek(0)
                   await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))


client.run(constant.TOKEN)
