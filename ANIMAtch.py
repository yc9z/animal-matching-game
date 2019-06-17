
#Import Modules
import os, pygame
import random
import collections
from pygame.locals import *
from pygame.compat import geterror

if not pygame.font: print ('Warning, fonts disabled')

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

#functions to create our resources
def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print ('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

class Animal(pygame.sprite.Sprite):
    """moves a monkey critter across the screen. it can spin the
       monkey when it is punched."""
    def __init__(self,x,y):
        self.id = random.randint(1,19)
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.image, self.rect = load_image('{}.png'.format(self.id), -1)
        screen = pygame.display.get_surface()
        self.rect.topleft = x, y

class Button(pygame.sprite.Sprite):
    def __init__(self,name,x,y):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.image, self.rect = load_image(name, -1)
        screen = pygame.display.get_surface()
        self.rect.topleft = x, y

class Level(pygame.sprite.Sprite):
    def __init__(self,name,x,y):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.image, self.rect = load_image(name, -1)
        screen = pygame.display.get_surface()
        self.rect.topleft = x, y
        self.name = name
        
def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
    def click():
        new = False
        pos = pygame.mouse.get_pos()
        for button in allbuttons:
            if button.rect.collidepoint(pos):
                new = True
        find = False
        for pm in allanimals:
            if pm.rect.collidepoint(pos): 
                chosen.append(pm)
                find = True
                break
        if not find: return None, new, False
        if not check_edge(chosen[-1]):
            warning = font.render('Must choose animals on the edges!', 4, (255, 10, 10))
            chosen.pop()
            return warning, False, False
        if len(chosen) == 1:
            return font.render('Choose another one :)', 4, (0, 0, 128)), new, False
        if len(chosen) == 2:
            warning = font.render("Can't choose from same place :(", 4, (255, 10, 10))
            if not chosen[0] == chosen[1]: warning = check_same(chosen)
            chosen.pop()
            chosen.pop()
            return warning, new, check_win()
        

    def check_same(chosen):
        if chosen[0].id == chosen[1].id:
            allanimals.remove(chosen[0])
            allanimals.remove(chosen[1])
            return font.render('Yay!! :)', 4, (34,139,34))
        return font.render('Animals must match...', 4, (255, 10, 10))

    def check_win():
        count = collections.Counter([a.id for a in allanimals])
        for c in count:
            if count[c]>1: return False
        return True

    def check_edge(pm):
        directions = [(36,0),(-36,0),(0,39),(0,-39)]
        neighbor = 0
        for d in directions:
            for remain in allanimals:
                if chosen and pm.rect.move(d)==chosen[0].rect:
                    continue
                if pm.rect.move(d)==remain.rect:
                    neighbor += 1
        return True if neighbor < 4 else False
            
#Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption('ANIMAtch!')
    pygame.mouse.set_visible(True)
    chosen = []

#Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

#Put Text On The Background, Centered
    if pygame.font:
        font = pygame.font.Font(None, 20)
        bigfont = pygame.font.Font(None, 40)
        biggfont = pygame.font.Font(None, 50)
        text = font.render("Choose 2 same animals from the edges", 4, (10, 10, 10))
        textpos = text.get_rect(center=(200,20))
        warningpos = text.get_rect(center=(200,40))

#Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

#Prepare Game Objects
    clock = pygame.time.Clock()
    button_restart = Button('restart.jpg',500,500)
    timepos = text.get_rect(center=(300,500))
    
    easy = Level('easy.png',100,100)
    medium = Level('medium.png',220,100)
    hard = Level('hard.png',340,100)

#Main Loop
    going = True
    new = True
    record_time = {'easy.png':float('inf'),'medium.png':float('inf'),'hard.png':float('inf')}
    win = False
    pause = False
    game_over = False
    choose_level = True
    levels = pygame.sprite.RenderPlain([easy,medium,hard])
    record = {}
    for level in levels:
        record[level.name] = font.render("Best record:", 4, (218,165,32))
    recordpos = text.get_rect(center=(300,520))
    while going:
        if game_over:
            for event in pygame.event.get():
                if event.type == QUIT:
                    going = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    going = False
                elif event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for button in allbuttons:
                        if button.rect.collidepoint(pos):
                            new = True
                            game_over = False
                            choose_level = True
            continue
        
        if choose_level:
            for event in pygame.event.get():
                levels.draw(screen)
                pygame.display.flip()
                if event.type == QUIT:
                    going = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    going = False
                elif event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for level in levels:
                        if level.rect.collidepoint(pos):
                            if level.name == 'easy.png':
                                n,m = 2,2
                            elif level.name == 'medium.png':
                                n,m = 6,6
                            else:
                                n,m = 10,10
                            choose_level = False
                            level_chosen = level.name
                            break
            continue
                    
        
        if new:
            animals = [[0]*m for i in range(n)]
            for i in range(n):
                for j in range(m):
                    animals[i][j] = Animal(100+36*i,70+39*j)
            allanimals = pygame.sprite.RenderPlain([pm for row in animals for pm in row])
            allbuttons = pygame.sprite.RenderPlain([button_restart])
            warning = font.render('Hmm...', 4, (255, 10, 10))
            start_time = pygame.time.get_ticks()
            new = False
            break_record = False
        win = check_win()
        timer = (pygame.time.get_ticks()-start_time)//1000
        minute,sec = timer//60,timer%60
        if minute<10: minute = '0'+str(minute)
        if sec<10: sec = '0'+str(sec)
        time = font.render('Time used '+str(minute)+":"+str(sec), 4, (255, 10, 10))
        if win:
            new = True
            if timer>0 and record_time[level_chosen]>timer:
                break_record = True
                record_time[level_chosen] = timer
                record[level_chosen] = font.render('Best record: '+str(minute)+":"+str(sec), 4, (218,165,32))
                end_words = 'You break the record!! ^_^'
            elif timer>0:
                end_words = 'You win!'
            if timer>0:
                end = bigfont.render(end_words,4, (34,139,34))
                back = biggfont.render(end_words,4,(200,255,200))
                endpos = text.get_rect(center=(200,100))
                screen.blit(end,endpos)
                screen.blit(back,pygame.Rect(70, 90, 40, 40), special_flags=pygame.BLEND_RGBA_MULT)
                pygame.display.flip()
                game_over = True
                continue
        clock.tick(60)
        
        #Handle Input Events
        
        for event in pygame.event.get():
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False
            elif event.type == MOUSEBUTTONDOWN:
                message, new, win = click()
                if new: choose_level = True
                if message: warning = message
                    
        allanimals.update()

        #Draw Everything
        screen.blit(background, (0, 0))
        screen.fill((255,255,255))
        allanimals.draw(screen)
        allbuttons.draw(screen)
        screen.blit(warning,warningpos)
        screen.blit(text, textpos)
        screen.blit(time,timepos)
        screen.blit(record[level_chosen],recordpos)
        pygame.display.flip()

    pygame.quit()

#Game Over


#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()
