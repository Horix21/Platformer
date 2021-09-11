import pygame, sys, os, random

clock = pygame.time.Clock()

from pygame.locals import *
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init() # initiates pygame

#variables an shez
pygame.display.set_caption('Super Mega Ultra Duper Mega 4k Iphone 12 Max Pro Intel i9 10999k AMD Ryzen 9 5950x Windows 11 x64 Linux Arch Samsung Earbuds Platformer')

gameMap = {}

WINDOW_SIZE = (1920, 1080)

screen = pygame.display.set_mode(WINDOW_SIZE,0,32) # initiate the window

display = pygame.Surface((400, 200))


grassImage = pygame.image.load('grass.png')
dirtImage = pygame.image.load('dirt.png')
plantImage = pygame.image.load('plant.png').convert()
plantImage.set_colorkey((255, 255, 255))
tileIndex = {1: grassImage,2: dirtImage, 3: plantImage}

chunkSize = 8

def generateChunks(x, y):
    chunkData = []
    for y_pos in range (chunkSize):
        for x_pos in range(chunkSize):
            targetX = x * chunkSize + x_pos
            targetY = y * chunkSize + y_pos
            tileType = 0 #nothing
            if targetY > 10:
                tileType = 2 #dirt
            elif targetY == 10:
                tileType = 1 #grass
            elif targetY == 9:
                if random.randint(1, 5) == 1:
                    tileType = 3 #plant
            if tileType != 0:
                chunkData.append([[targetX, targetY], tileType])
    return chunkData

#loading the actual animations  
global animationFrames
animationFrames = {}

def loadAnimation(path, frameDurations):
    global animationFrames
    animationName = path.split('/') [-1]
    animationFrameData = []
    n = 0
    for frame in frameDurations:
        animationFrameId = animationName + '_' + str(n)
        imgLoc = path + '/' + animationFrameId + '.png'
        animationImage = pygame.image.load(imgLoc).convert()
        animationImage.set_colorkey((255, 255, 255))
        animationFrames[animationFrameId] = animationImage.copy()
        for i in range(frame):
            animationFrameData.append(animationFrameId)
        n += 1
    return animationFrameData

#if the player stops idling / running
def changeAction (actionVar, frame, newValue):
    if actionVar != newValue:
        actionVar = newValue
        frame = 0
    return actionVar, frame

#more variables
animationDatabase = {}

animationDatabase['run'] = loadAnimation('player_animations/run', [7, 7])
animationDatabase['idle'] = loadAnimation('player_animations/idle', [7, 7, 40])

#sound effects
jumpSound = pygame.mixer.Sound('jump.wav')
grassSounds =[pygame.mixer.Sound('grass_0.wav'),pygame.mixer.Sound('grass_1.wav')]
grassSounds[0].set_volume(0.25)
grassSounds[1].set_volume(0.25)

#music
pygame.mixer.music.load('music.wav')
pygame.mixer.music.play(-1)

playerAction = 'idle'
playerFrame = 0
playerFlip = False

grassSoundTimer = 0

playerRect = pygame.Rect(100,100,5,13)

#defining background objects
backgroundObjects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]

#collision detections
def collisionTest(rect, tiles):
    hitList = []
    for tile in tiles:
        if rect.colliderect(tile):
            hitList.append(tile)
    return hitList

#moving and more collision detection
def move(rect, movement, tiles):
    collisionTypes = {'top' : False, 'bottom' : False, 'right' : False, 'left' : False}
    rect.x += movement[0]
    hitList = collisionTest(rect, tiles)
    for tile in hitList:
        if movement[0] > 0:
            rect.right = tile.left
            collisionTypes['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collisionTypes['left'] = True
    rect.y += movement[1]
    hitList = collisionTest(rect, tiles)
    for tile in hitList:
        if movement[1] > 0:
            rect.bottom = tile.top
            collisionTypes['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collisionTypes['top'] = True
    return rect, collisionTypes

#buncha variables
movingRight = False
movingLeft = False

playerYMomentum = 0

airTime = 0

true_scroll = [0, 0]




while True: # game loop

    display.fill((146, 244, 255))

    if grassSoundTimer > 0:
        grassSoundTimer -= 1

    #this is for scroll
    true_scroll[0] += (playerRect.x - 152 - true_scroll[0])/20
    true_scroll[1] += (playerRect.y - 106 - true_scroll[1])/20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    #background objects
    pygame.draw.rect(display, (7, 80, 76), pygame.Rect(0, 120, 300, 80))
    for backgroundObject in backgroundObjects:
        objRect = pygame.Rect(backgroundObject[1][0] - scroll[0] * backgroundObject[0], backgroundObject[1][1] - scroll[1] * backgroundObject[0], backgroundObject[1][2], backgroundObject[1][3])
        if backgroundObject[0] == 0.5:
            pygame.draw.rect(display, (14, 222, 150), objRect)
        else:
            pygame.draw.rect(display, (9, 91, 85), objRect)

    #map loading
    tileRects = []
    for y in range(3):
        for x in range(5):
            targetX = x - 1 + int(round(scroll[0] / (chunkSize * 16)))
            targetY = y - 1 + int(round(scroll[1] / (chunkSize * 16)))
            targetChunk = str(targetX) + ';' + str(targetY) 
            if targetChunk not in gameMap:
                gameMap[targetChunk] = generateChunks(targetX, targetY)
            for tile in gameMap[targetChunk]:
                display.blit(tileIndex[tile[1]], (tile[0][0] * 16 - scroll[0], tile[0][1] * 16 - scroll[1]))
                if tile[1] in [1, 2]:
                    tileRects.append(pygame.Rect(tile[0][0] * 16, tile[0][1] * 16, 16, 16))

    #tile rendering    


    #player movement
    playerMovement = [0, 0]
    if movingRight:
        playerMovement[0] += 2
    if movingLeft:
        playerMovement[0] -= 2
    playerMovement[1] += playerYMomentum
    playerYMomentum += 0.2
    if playerYMomentum > 3:
        playerYMomentum = 3

    #animations
    if playerMovement[0] == 0:
        playerAction, playerFrame = changeAction(playerAction, playerFrame, 'idle')
    if playerMovement[0] > 0:
        playerAction, playerFrame = changeAction(playerAction, playerFrame, 'run')
        playerFlip = False
    if playerMovement[0] < 0:
        playerAction, playerFrame = changeAction(playerAction, playerFrame, 'run')
        playerFlip = True

    #player collisions
    playerRect, collisions = move(playerRect, playerMovement, tileRects)

    if collisions['bottom']:
        airTime = 0
        playerYMomentum = 0
        if playerMovement[0] != 0:
            if grassSoundTimer == 0:
                grassSoundTimer = 30
                random.choice(grassSounds).play()
    else:
        airTime += 1

    if collisions['top']:
        playerYMomentum = 0

    #player animations
    playerFrame += 1
    if playerFrame >= len(animationDatabase[playerAction]):
        playerFrame = 0
    playerImageId = animationDatabase[playerAction][playerFrame]
    playerImage = animationFrames[playerImageId]
    display.blit(pygame.transform.flip(playerImage, playerFlip, False), (playerRect.x - scroll[0], playerRect.y - scroll[1]))

    #checks for key presses
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_w:
                pygame.mixer.music.fadeout(1000)
            if event.key == K_e:
                pygame.mixer.music.play(-1)
            if event.key == K_RIGHT:
                movingRight = True
            if event.key == K_LEFT:
                movingLeft = True
            if event.key == K_UP:
                if airTime < 10:
                    jumpSound.play()
                    playerYMomentum = -5
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                movingRight = False
            if event.key == K_LEFT:
                movingLeft = False

    #screen and frame stuff idk
    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))
    pygame.display.update()
    clock.tick(60)
