import os
import pygame
import random

pygame.init()
WIDTH, HEIGHT = 720, 720
ROOT = pygame.display.set_mode((WIDTH, HEIGHT))
FONT_MENU = pygame.font.SysFont("Consolas", 24)
FONT_PARAGRAPH = pygame.font.SysFont("Consolas", 16)
PENALTY = 120

food_variants = ["Soto", "Kari Ayam", "Rendang"]
bev_variants = ["Kopi", "Teh"]
bev_temp_variants = ["Dingin", "Panas"]

class Order:
    def __init__(self):
        self.food = random.choice(food_variants)
        self.bev = random.choice(bev_variants)
        self.bev_temp = random.choice([0, 1])
        self.food_wait = 400
        self.food_done = self.bev_done = self.bev_temp_correct = 0

class Customer(Order):
    def __init__(self, next = None):
        Order.__init__(self)
        self.patience = 1200
        self.next = next

class Queue:
    def __init__(self):
        self.head = self.tail = None
        self.count = 0
    
    def insert(self):
        newCustomer = Customer()
        self.count += 1
        if(self.head):
            newCustomer.next = self.head
            self.head = newCustomer
        else:
            self.head = self.tail = newCustomer

    def remove(self):
        if(self.tail == None):
            return None
        elif(self.head == self.tail):
            self.head = self.tail = None
        else:
            temp = self.tail
            self.tail = self.head
            while(self.tail.next != temp):
                self.tail = self.tail.next
            self.tail.next = temp = None
        self.count -= 1

    def get_customer(self):
        return self.tail

class Image:
    def __init__(self, images, pos, size) -> None:
        self.pos = pos
        self.image = []
        for img in images:
            load = pygame.image.load(os.path.join("assets", img))
            self.image.append(pygame.transform.scale(load, size))
    
    def redraw(self, win, val=0, pos=None):
        return win.blit(self.image[val], self.pos) if pos == None else win.blit(self.image[val], pos)

def txt_render(win, val, pos, font=FONT_MENU, color="BLACK", show=True):
    text = font.render(str(val), False, color)
    return win.blit(text, pos) if show else text

def update_menu(win, node):
    pygame.draw.rect(win, "WHITE", (412, 100, 160, 108))
    txt_render(win, node.food, (422, 110))
    txt_render(win, node.bev, (422, 142))
    txt_render(win, bev_temp_variants[node.bev_temp], (422, 174))

def loading_bar(win, val, size, pos, total=100, color="GREEN"):
    x, y = pos
    w, h = size
    val = w * (val/total)
    if(val >= 0 and val <= total):
        pygame.draw.rect(win, "GREY", (x, y, w, h))
        pygame.draw.rect(win, color, (x, y, val, h))

def check_food(node, food):
    if(node.food != food):
        node.patience -= PENALTY
        return 0
    return 1

def main():
    score = move_x = move_y = is_cooking = 0
    is_mad = False
    is_walk_in = True
    is_walk_out = False
    is_waiting = False
    cust_queue = Queue()
    for i in range(4):
        cust_queue.insert()

    pygame.display.set_caption("warkop bki")

    background = Image(["background.png"], (0, 0), (WIDTH, HEIGHT))
    background = background.redraw(ROOT)

    curr = cust_queue.get_customer()

    kari = Image(["kari.png"], (616, 230), (84, 48))
    kari.redraw(ROOT)
    rendang = Image(["rendang.png"], (616, 310), (84, 48))
    rendang.redraw(ROOT)
    soto = Image(["soto.png"], (616, 390), (84, 48))
    soto.redraw(ROOT)

    pot = Image(["pot_empty.png", "pot_noodle.png"], (580, 580), (120, 120))
    pot.redraw(ROOT, is_cooking)

    bowl = Image(["bowl_empty.png", "bowl_noodle.png"], (520, 512), (72, 56))
    bowl.redraw(ROOT, curr.food_done)

    chiller = Image(["chiller.png"], (12, 490), (90, 72))
    chiller.redraw(ROOT)
    kettle = Image(["kettle.png"], (120, 472), (90, 90))
    kettle.redraw(ROOT)
    jar_tea = Image(["jar_tea.png"], (224, 490), (48, 72))
    jar_tea.redraw(ROOT)
    jar_coffee = Image(["jar_coffee.png"], (282, 490), (48, 72))
    jar_coffee.redraw(ROOT)

    iced = Image(["iced_water.png", "iced_tea.png", "iced_coffee.png"], (340, 490), (48, 68))
    hot = Image(["hot_water.png", "hot_tea.png", "hot_coffee.png"], (340, 490), (52, 72))

    customer = Image(["man_smile.png", "man_frown.png", "man_mad.png"], (412, 210), (120, 256))
    refresh = Image(["refresh.png"], (0, 0), (582, 466))

    pygame.display.update()

    clock = pygame.time.Clock()
    state = True

    while state:
        clock.tick(60)

        if(is_walk_in or is_walk_out):
            refresh.redraw(ROOT)

        if(is_walk_in and move_y < 466):
            customer.redraw(ROOT, 0, (412, move_y-256))
            move_y += 2
        
        if(move_y == 466):
            is_walk_in = False
            move_y = 0
            update_menu(ROOT, curr)
        
        if(is_walk_out and move_x < 680):
            customer.redraw(ROOT, 2, (412-move_x, 210)) if is_mad else customer.redraw(ROOT, 0, (412-move_x, 210))
            move_x += 3
        
        if(move_x >= 680):
            is_walk_out = False
            move_x = 0
        
        if(not is_walk_in and not is_walk_out):
            is_waiting = True
        
        if(curr.food_done == curr.bev_done == curr.bev_temp_correct == 1):
            score += 25
            if(curr != cust_queue.head):
                cust_queue.remove()
                curr = cust_queue.get_customer()
                bowl.redraw(ROOT)
                pygame.draw.rect(ROOT, (67, 47, 18), (340, 490, 52, 72))
                is_walk_out = True
                is_walk_in = True
                is_waiting = False
                is_mad = False
            else:
                state = False

        if(curr.patience == 1199):
            customer.redraw(ROOT, 0)
        elif(curr.patience == 800):
            customer.redraw(ROOT, 1)
        elif(curr.patience == 400):
            customer.redraw(ROOT, 2)
        if(curr.food_wait <= 0):
            is_cooking = False
        if(curr.patience <= 0):
            if(curr != cust_queue.head):
                cust_queue.remove()
                curr = cust_queue.get_customer()
                bowl.redraw(ROOT)
                pygame.draw.rect(ROOT, (67, 47, 18), (340, 490, 52, 72))
                is_walk_out = True
                is_walk_in = True
                is_waiting = False
                is_mad = True
            else:
                state = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if(not curr.food_done and is_cooking == 0):
                    if kari.redraw(ROOT).collidepoint(pygame.mouse.get_pos()):
                        is_cooking = check_food(curr, "Kari Ayam")
                    if rendang.redraw(ROOT).collidepoint(pygame.mouse.get_pos()):
                        is_cooking = check_food(curr, "Rendang")
                    if soto.redraw(ROOT).collidepoint(pygame.mouse.get_pos()):
                        is_cooking = check_food(curr, "Soto")
                    pot.redraw(ROOT, is_cooking)
                if(pot.redraw(ROOT, is_cooking).collidepoint(pygame.mouse.get_pos()) and curr.food_wait == 0):
                    bowl.redraw(ROOT, 1)
                    curr.food_done = 1
                if(curr.bev_temp_correct == 0):
                    if chiller.redraw(ROOT).collidepoint(pygame.mouse.get_pos()):
                        if(curr.bev_temp == 0):
                            curr.bev_temp_correct = 1
                            iced.redraw(ROOT, 0)
                        else:
                            curr.patience -= PENALTY
                    if kettle.redraw(ROOT).collidepoint(pygame.mouse.get_pos()):
                        if(curr.bev_temp == 1):
                            curr.bev_temp_correct = 1
                            hot.redraw(ROOT, 0)
                        else:
                            curr.patience -= PENALTY
                if(curr.bev_temp_correct == 1):
                    if jar_coffee.redraw(ROOT).collidepoint(pygame.mouse.get_pos()):
                        if(curr.bev == bev_variants[0] and curr.bev_temp == 0):
                            curr.bev_done = 1
                            iced.redraw(ROOT, 2)
                        elif(curr.bev == bev_variants[0] and curr.bev_temp == 1):
                            curr.bev_done = 1
                            hot.redraw(ROOT, 2)
                        else:
                            curr.patience -= PENALTY
                    if jar_tea.redraw(ROOT).collidepoint(pygame.mouse.get_pos()):
                        if(curr.bev == bev_variants[1] and curr.bev_temp == 0):
                            curr.bev_done = 1
                            iced.redraw(ROOT, 1)
                        elif(curr.bev == bev_variants[1] and curr.bev_temp == 1):
                            curr.bev_done = 1
                            hot.redraw(ROOT, 1)
                        else:
                            curr.patience -= PENALTY

        if(is_waiting):
            curr.patience -= 1
        if(is_cooking):
            curr.food_wait -= 1
            loading_bar(ROOT, curr.food_wait, (80, 5), (600, 640), 400)

        pygame.display.update()

    state = True
    while state:
        clock.tick(60)
        pygame.draw.rect(ROOT, (57, 33, 0), (20, 20, 680, 680))
        pygame.draw.rect(ROOT, (99, 58, 0), (40, 40, 640, 640))
        txt_render(ROOT, "Skor Anda:", (320, 300), FONT_MENU, "WHITE")
        txt_render(ROOT, score, (320, 324), FONT_MENU, "WHITE")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state = False
        pygame.display.update()

if __name__ == "__main__":
    main()
    