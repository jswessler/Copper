import os
import pygame as pg
import math
from PIL import Image

#Copper - jswessler 2023

pg.font.init()
pg.init()
WID = 1280
HEI = 720
screen = pg.display.set_mode((WID,HEI),pg.RESIZABLE, vsync=1)
running = True
fps = pg.time.Clock()
font = pg.font.SysFont('Comic Sans MS', 20)

inputImage = ''
first = True
firstBuff = True
scaFactor = 1
adjusted=False
newSize = 1
outputType='PNG'

def getDist(x,y,x2,y2):
    px = abs(x2-x)**2
    py = abs(y2-y)**2
    return math.sqrt(px+py)

def saveToNormal(im,ou):
    im.save(os.path.join("C:\\Users\\miner\\Desktop\\Copper\\","CopperOutput." + ou),ou)
    return os.path.getsize(os.path.join("C:\\Users\\miner\\Desktop\\Copper\\","CopperOutput." + ou.lower()))

def export(final=False,size=0):
    if inputImage!='':
        im = Image.open(inputImage)
        im = im.crop((coords[0][0]-xxpos,coords[0][1]-yypos,coords[3][0]-xxpos,coords[3][1]-yypos))
        if outputType=='JPEG':
            im = im.convert('RGB')
        if not final:
            im.save(os.path.join("C:\\Users\\miner\\Desktop\\Copper\\drafts\\","CopperOutput." + outputType),outputType)
            return os.path.getsize(os.path.join("C:\\Users\\miner\\Desktop\\Copper\\drafts\\","CopperOutput." + outputType.lower()))
        else:
            si = saveToNormal(im,outputType)
            if si<size*1024*1024 or size==0:
                return si
            else:
                scale = math.sqrt(si/(size*1024*1024))+0.2*1.1
                im = im.resize((int((coords[1][0]-coords[0][0])/scale),int((coords[3][1]-coords[0][1])/scale)))
                im.save(os.path.join("C:\\Users\\miner\\Desktop\\Copper\\","CopperOutput." + outputType),outputType)
                si = os.path.getsize(os.path.join("C:\\Users\\miner\\Desktop\\Copper\\","CopperOutput." + outputType.lower()))
                return si
    else:
        return 1


msg = ''
targetSize=''
flashScreen=0
counter=0
remmx = 0
remmy = 0
updateCoords=False
coords = [[0,0],[WID-300,0],[0,HEI],[WID-300,HEI]]
xpos = 0
ypos = 0 #coords that the zoom is centered on
xxpos=0
yypos=0
zoom = 1 #zoom is a multiplier for image scale
while running:
    counter+=1
    WID, HEI = pg.display.get_surface().get_size()
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running = False
        elif event.type==pg.DROPFILE: #When a file is dropped onto the window
            if str(event.file).endswith('.png'):
                inputImage=str(event.file)
                first = True
                firstBuff = True
            else:
                msg = 'Needs to be a PNG file'
        elif event.type==pg.MOUSEWHEEL: #Scrolling in and out
            if event.y==1:
                zoom*=0.9
            else:
                zoom*=1.1  
        elif event.type==pg.KEYDOWN:
            if event.key==pg.K_SPACE: #Reset prespective after zooming due to pygame surface shennanigans
                first = True
            elif event.key==pg.K_LCTRL: #Reset everything
                firstBuff = True
                xpos = 0
                ypos = imgh/40
                xxpos = imgw/40
                yypos = 0
            elif event.key==pg.K_LSHIFT: #Force draft save
                adjusted = True
            elif event.key==pg.K_LALT: #Reset zoom to 1
                zoom = 1
                first = True
            elif event.key==pg.K_RETURN: #Output Image
                if targetSize!='':
                    size = export(True,float(targetSize))
                else:
                    size = export(True)
                targetSize=''
                msg = "Exported as " + str(outputType) + " - " + str(round(size/1024/1024,4)) + "MB"
                flashScreen=counter+20
            elif event.key==pg.K_BACKSPACE: #Type a backspace
                targetSize = targetSize[:-1]
            elif event.key==pg.K_DELETE: #Delete current image
                inputImage=''
            elif event.key==pg.K_UP: #Pan around the image
                ypos-=imgh/100
                updateCoords = True
            elif event.key==pg.K_DOWN:
                ypos+=imgh/100
                updateCoords = True
            elif event.key==pg.K_RIGHT:
                xpos+=imgw/100
                updateCoords = True
            elif event.key==pg.K_LEFT:
                xpos-=imgw/100
                updateCoords = True
            else:
                if 48<=event.key<=57 or event.key==46: #Only numbers and period are allowed
                    targetSize+=str(event.unicode)
                    

    mousex,mousey=pg.mouse.get_pos()
    relmx = mousex-remmx
    relmy = mousey-remmy
    remmx = mousex
    remmy = mousey
    if pg.mouse.get_pressed()[0]:
        if mousex<WID-300:
            adjusted=True
            l = list(getDist(mousex,mousey,x[0]/scaFactor,x[1]/scaFactor) for x in coords)
            adj = l.index(min(l))
            if min(l)<25:
                coords[adj]=[mousex*scaFactor,mousey*scaFactor] #Dragging Corners
                if adj==0:
                    coords[1]=[coords[1][0],coords[0][1]] #Adjust 2 other corners based on the one you're adjusting right now
                    coords[2]=[coords[0][0],coords[2][1]] 
                if adj==1:
                    coords[0]=[coords[0][0],coords[1][1]]
                    coords[3]=[coords[1][0],coords[3][1]]
                if adj==2:
                    coords[3]=[coords[3][0],coords[2][1]]
                    coords[0]=[coords[2][0],coords[0][1]]
                if adj==3:
                    coords[2]=[coords[2][0],coords[3][1]]
                    coords[1]=[coords[3][0],coords[1][1]]
            else:
                updateCoords=True
#Update a draft if the drawing is moved
    else:
        if adjusted:
            newSize = export() #Re-output to get new filesize when adjusted
            adjusted=False
    if updateCoords: #Updates coords when you pan with arrow keys or mouse
        for i in coords:
            i[0]+=xpos+(relmx*scaFactor)
            i[1]+=ypos+(relmy*scaFactor)
        if not (coords[0][0]<mousex*scaFactor<coords[1][0] and coords[0][1]<mousey*scaFactor<coords[2][1]):
            xxpos+=xpos+(relmx*scaFactor)
            yypos+=ypos+(relmy*scaFactor)
        else:
            pass
        xpos=0
        ypos=0
        updateCoords=False

    if inputImage=='': #Gray screen if there is no image that you're working on
        screen.fill((20,20,20))
    else:
        screen.fill((64,64,64)) #Lighter gray if you're working on image to help with positioning
# First time setup whenever you put in a new image or press space/ctrl
        if first:
            dispImg = pg.image.load(inputImage)
            imgw = dispImg.get_width()
            imgh = dispImg.get_height()
            first = False                
        if firstBuff:
            coords = [[imgw/40,imgh/40],[imgw*41/40,imgh/40],[imgw/40,imgh*41/40],[imgw*41/40,imgh*41/40]]
            origSize = os.path.getsize(inputImage)
            newSize = origSize
            firstBuff=False
# Image logic to determine scale/display properly, basic screen layout with black box on the right
        if imgh>imgw:
            scaFactor = max(1,imgh/HEI)*zoom*1.05
        else:
            scaFactor = max(1,imgw/(WID-300))*zoom*1.05
        dispImg = pg.transform.scale(dispImg,(imgw/scaFactor,imgh/scaFactor)) #Rescales image to scale factor determined by zoom
        screen.blit(dispImg,(xxpos/scaFactor,yypos/scaFactor))
        pg.draw.rect(screen,(0,0,0),(WID-300,0,300,HEI))
        s = font.render(str(imgw) + "x" + str(imgh),True,(230,230,230))
        screen.blit(s,(WID-295,20))
        cropw = coords[3][0]-coords[0][0]
        croph = coords[3][1]-coords[0][1]
        s = font.render(str(round(cropw)) + 'x' + str(round(croph)),True,(230,230,230))
        screen.blit(s,(WID-145,20))
        if targetSize!='':
            s = font.render("Target: " + str(targetSize) + " MB",True,(230,230,230))
            screen.blit(s,(WID-290,410))
# Render left side bar & text
        pg.draw.line(screen,(80,80,80),(WID-245,350),(WID-245,50),10)
        pg.draw.line(screen,(40,230,80),(WID-245,350),(WID-245,350-300*((cropw*croph)/(imgw*imgh))),10)
        if origSize/1024/1024>8:
            pg.draw.line(screen,(20,100,20),(WID-249,350-300*(8/(origSize/1024/1024))),(WID-240,350-300*(8/(origSize/1024/1024))),3)
            if origSize/1024/1024>50:
                pg.draw.line(screen,(100,20,20),(WID-249,350-300*(50/(origSize/1024/1024))),(WID-240,350-300*(50/(origSize/1024/1024))),3)
        s = font.render(str(round(100*((cropw*croph)/(imgw*imgh)),1)) + "%",True,(230,230,230))
        screen.blit(s,(WID-265,360))
        s = font.render(str(round((cropw*croph)/1000000,2)) + "Mpx",True,(230,230,230))
        screen.blit(s,(WID-265,385))
# Render right side bar & text
        pg.draw.line(screen,(80,80,80),(WID-95,350),(WID-95,50),10)
        pg.draw.line(screen,(40,230,80) if newSize/1024/1024<8 else (120,160,40) if newSize/1024/1024<50 else (230,40,40),(WID-95,350),(WID-95,350-300*(newSize/origSize)),10)
        s = font.render(str(round(100*(newSize/origSize),1)) + "%",True,(230,230,230))
        screen.blit(s,(WID-115,360))
        s = font.render(str(round(newSize/1024/1024,2)) + "MB",True,(230,230,230))
        screen.blit(s,(WID-115,385))
# Render BPP text
        s = font.render(str(round((newSize*8)/(cropw*croph),2)) + "bpp",True,(230,230,230))
        screen.blit(s,(WID-195,260)) 
# Render buttons and add collision to them
        pr = pg.draw.rect(screen,(90,90,90) if outputType=='PNG' else (60,60,60),pg.Rect(WID-70,50,60,40))
        s = font.render("PNG",True,(230,230,230))
        screen.blit(s,(WID-60,55))
        jr = pg.draw.rect(screen,(90,90,90) if outputType=='JPEG' else (60,60,60),pg.Rect(WID-70,100,60,40))
        s = font.render("JPG",True,(230,230,230))
        screen.blit(s,(WID-60,105))
        tr = pg.draw.rect(screen,(90,90,90) if outputType=='GIF' else (60,60,60),pg.Rect(WID-70,150,60,40))
        s = font.render("GIF",True,(230,230,230))
        screen.blit(s,(WID-60,155))
        if pr.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]:
            outputType='PNG'
            adjusted = True
        if jr.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]:
            outputType='JPEG'
            adjusted = True
        if tr.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]:
            outputType='GIF'
            adjusted = True
    
    if msg!='':
        s = font.render(str(msg),True,(230,230,230))
        screen.blit(s,(WID-295,HEI-50))
        

        
    pg.draw.line(screen,(0,0,0),(coords[0][0]/scaFactor,coords[0][1]/scaFactor),(coords[1][0]/scaFactor,coords[1][1]/scaFactor),3)
    pg.draw.line(screen,(0,0,0),(coords[1][0]/scaFactor,coords[1][1]/scaFactor),(coords[3][0]/scaFactor,coords[3][1]/scaFactor),3)
    pg.draw.line(screen,(0,0,0),(coords[3][0]/scaFactor,coords[3][1]/scaFactor),(coords[2][0]/scaFactor,coords[2][1]/scaFactor),3)
    pg.draw.line(screen,(0,0,0),(coords[2][0]/scaFactor,coords[2][1]/scaFactor),(coords[0][0]/scaFactor,coords[0][1]/scaFactor),3)
    pg.draw.circle(screen,(40,40,40),(coords[0][0]/scaFactor,coords[0][1]/scaFactor),4)
    pg.draw.circle(screen,(40,40,40),(coords[1][0]/scaFactor,coords[1][1]/scaFactor),4)
    pg.draw.circle(screen,(40,40,40),(coords[2][0]/scaFactor,coords[2][1]/scaFactor),4)
    pg.draw.circle(screen,(40,40,40),(coords[3][0]/scaFactor,coords[3][1]/scaFactor),4)
    if flashScreen>counter:
        pg.draw.rect(screen,(64+(flashScreen-counter)*6,64+(flashScreen-counter)*6,64+(flashScreen-counter)*6),pg.Rect(0,0,WID-300,HEI))
    dt = fps.tick(60)
    pg.display.flip()
    
