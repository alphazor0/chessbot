import os
import chess
from fentoboardimage import fenToImage, loadPiecesFolder
import asyncio
import io
from io import BytesIO
import nest_asyncio 
import re
import sys
import math
from PIL import Image
import numpy as np
import random
import time
nest_asyncio.apply()
import constant


import discord
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

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

def minimax(plateau, couleur, profondeur, maxo, move,alpha,beta, valAVANT):
    if profondeur ==0 or plateau.is_game_over():
        
        return ["",valAVANT]
    
    if maxo:
        maxvalue=-100000
        maxmove =""
        movesUCI=[]
        for move in plateau.legal_moves:   
            movesUCI.append(move.uci())
        random.shuffle(movesUCI)    
            
        for move in movesUCI:      
            valAVANT = valeur2(plateau,chess.Move.from_uci(move), valAVANT,couleur)  
            plateau.push(chess.Move.from_uci(move))
            val = minimax(plateau,couleur,profondeur-1,False, move,alpha,beta, valAVANT)[1]
            plateau.pop()
            
            if val >maxvalue:
                 maxvalue=val
                 maxmove=move
            alpha= max(alpha,val)
            if(beta <= alpha):
                  break                        
        return [maxmove,maxvalue]
    
    if not maxo:
        minvalue=+100000
        minmove =""
        movesUCI=[]
        for move in plateau.legal_moves:   
            movesUCI.append(move.uci())
        random.shuffle(movesUCI)    
        
        for move in movesUCI: 
            valAVANT = valeur2(plateau,chess.Move.from_uci(move), valAVANT,couleur)
            plateau.push(chess.Move.from_uci(move))
            val = minimax(plateau,couleur,profondeur-1,True, move,alpha,beta, valAVANT)[1]
            plateau.pop()
            if val <minvalue:
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



def valeur2(board,move,val, couleur):
    ty =board.piece_type_at(move.to_square)
    couleurPiece=board.color_at(move.to_square)
    #Retourne True pour les blancs, False pour les noirs
    
    if couleurPiece:
        cP="w"
    else:
        cP="b"
        
    if(cP==couleur):
        if(ty==1):
            val=val-10
        if(ty==2):
            val=val-30
        if(ty==3):
            val=val-30
        if(ty==4):
            val=val-50
        if(ty==5):
            val=val-90
        if(ty==6):
            val=val-900
    else:
        if(ty==1):
            val=val+10
        if(ty==2):
            val=val+30
        if(ty==3):
            val=val+30
        if(ty==4):
            val=val+50
        if(ty==5):
            val=val+90
        if(ty==6):
            val=val+900

  
    
    
    return val    
def matriceToUCI(i,j,k,l):
    s=equivLCInv[j]+str(8-i)+equivLCInv[l]+str(8-k)
    
    return(s)
            
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


game='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
joueur=''
B=[]
board = chess.Board(game)
couleur="w"

@client.event
async def on_message(message):
    global game
    global joueur
    global B
    global board
    global couleur

   

    
    
    if message.content.startswith('z'):
        if message.content == 'zchess start w':
            couleur='w'
            
            joueur = message.author
            game='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
            board = chess.Board(game)
            A = fenToMatrice(game)
            bords = Image.open('img/bords.png')
            bords2 = Image.open('img/bords2.png')
            BI= fenToImage(board.board_fen(),squarelength=100,
            pieceSet=loadPiecesFolder("./pieces"),              	
            darkColor="#D18B47",
            lightColor="#FFCE9E")
            
            img=get_concat_h_resize(bords,BI)
            img=get_concat_v_resize(img,bords2)
            with io.BytesIO() as image_binary:
                        img.save(image_binary, 'PNG')
                        image_binary.seek(0)
                        await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))
                        
            
   
    if message.content.startswith('z'):
        if message.content == 'zchess start b':
             
                joueur = message.author
                game='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
                couleur="b"
           
                if(couleur =="w"):
                               colorA="b"
                else:
                               colorA="w"
               
              

                meilleurMove= minimax(board, colorA, 5, True,"",-10000,10000,valeur(fenToMatrice(board.board_fen()), colorA))[0]
                board.push( chess.Move.from_uci(meilleurMove))

                BI= fenToImage(board.board_fen(),squarelength=100,
                pieceSet=loadPiecesFolder("./pieces"),              	
                darkColor="#D18B47",
                lightColor="#FFCE9E",
                flipped=True)     
                bords = Image.open('img/bordsn.png')
                bords2 = Image.open('img/bords2.png')
                
                
                img=get_concat_h_resize(bords,BI)
                img=get_concat_v_resize(img,bords2)

                with io.BytesIO() as image_binary:
                   img.save(image_binary, 'PNG')
                   image_binary.seek(0)
                   await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))

    if( len(message.content))==4:
        
       start_time = time.time()

       moveUCI=[]
       for move in board.legal_moves:
           moveUCI.append(move.uci())
       
        
        
    
       if message.content in moveUCI:
           if message.author == joueur:
                
                
      
                board.push( chess.Move.from_uci(message.content))
           
                if(couleur =="w"):
                               colorA="b"
                else:
                               colorA="w"
               
              

                meilleurMove= minimax(board, colorA, 3, True,"",-10000,10000,valeur(fenToMatrice(board.board_fen()), colorA))[0]
                board.push( chess.Move.from_uci(meilleurMove))
                await message.channel.send("--- %s seconds ---" % (time.time() - start_time))
                
                if(couleur=="w"):
                    

                    BI= fenToImage(board.board_fen(),squarelength=100,
                    pieceSet=loadPiecesFolder("./pieces"),              	
                    darkColor="#D18B47",
                    lightColor="#FFCE9E")     
                    bords = Image.open('img/bords.png')
                    bords2 = Image.open('img/bords2.png')
                else:
                    BI= fenToImage(board.board_fen(),squarelength=100,
                    pieceSet=loadPiecesFolder("./pieces"),              	
                    darkColor="#D18B47",
                    lightColor="#FFCE9E",
                    flipped=True)     
                    bords = Image.open('img/bordsn.png')
                    bords2 = Image.open('img/bords2.png')
                    

                
                img=get_concat_h_resize(bords,BI)
                img=get_concat_v_resize(img,bords2)

                with io.BytesIO() as image_binary:
                   img.save(image_binary, 'PNG')
                   image_binary.seek(0)
                   await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))
                       
    
    

    

client.run(constant.TOKEN)