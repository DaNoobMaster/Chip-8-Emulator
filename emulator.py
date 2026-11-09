import random
import pygame
import math
from array import array
import tkinter as tk
from tkinter import filedialog

memory= [0 for x in range(4096)]
display=[0 for x in range(2048)]
gpr = [0 for x in range(16)] #general purpose data register
pc= 0x200
ir=0 #index register
stack=[0 for x in range(16)]
sp=0
delay_time=0
sound_time=0
timer_acc=0 #carry over time for timer triggering on time
keys=[0 for x in range(16)]
running = True #pygame running
waiting=False #Is cpu waiting for keypress
waiting_reg=0
waiting_vblank=False
draw_pending=None

#quirks
vblank = True
vfreset=True
shifting=True
mem_inc=True
clipping = True
jumping = False


font = [
0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
0x20, 0x60, 0x20, 0x20, 0x70, # 1
0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
0x90, 0x90, 0xF0, 0x10, 0x10, # 4
0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
0xF0, 0x10, 0x20, 0x40, 0x40, # 7
0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
0xF0, 0x90, 0xF0, 0x90, 0x90, # A
0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
0xF0, 0x80, 0x80, 0x80, 0xF0, # C
0xE0, 0x90, 0x90, 0x90, 0xE0, # D
0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
0xF0, 0x80, 0xF0, 0x80, 0x80  # F
]

#load fonts into memory
for i,val in enumerate(font):
    memory[80+i]=val

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
width, height = pygame.display.get_desktop_sizes()[0]
screen = pygame.display.set_mode((0,0), pygame.NOFRAME)
pygame.display.set_caption("Chip-8")
clock = pygame.time.Clock()
font = pygame.font.Font(None, int(10/100 * height))

#choosing rom
root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)

rom = filedialog.askopenfilename(title="Select CHIP-8 ROM",filetypes=[("CHIP-8 ROMs", "*.ch8"), ("All files", "*.*")])

root.destroy()

#pixel scaling
scale = int(min(0.65*width/64,0.6*height/32))
scaled_x= (width-64*scale)/2 #x offset
scaled_y=0.1*height #y offset

frame=pygame.Rect(scaled_x,scaled_y,64*scale,32*scale).inflate(24,24)

#keyboard
key_colour=[(35, 48, 60) for x in range(16)]
key_labels = [
    "1", "2", "3", "C",
    "4", "5", "6", "D",
    "7", "8", "9", "E",
    "A", "0", "B", "F"
]
key_frame=pygame.Rect(width/2 - 0.9*64*scale/2, scaled_y+32*scale+25 , 0.9*64*scale , height-(scaled_y + 32*scale + 25)-0.02*height).inflate(18,18)
gap = 10
key_width = (key_frame.width - 2*15 - 3*gap)//4
key_height = (key_frame.height - 2*15 - 3*gap)//4
key_size = min(key_width, key_height)
key_font = pygame.font.SysFont(None, int(key_size*0.55))
virtual_key_rects=[]
mouse_key = None
for i in range(16):
    row = i//4
    col=i%4
    virtual_key_rects.append(pygame.Rect(key_frame.x + 15 + col*(key_width+gap) + (key_width-key_size)//2, key_frame.y + 15 + row*(key_height+gap) + (key_height-key_size)//2, key_size, key_size))

#quirks UI
quirk_labels = [
    "VF Reset",
    "Memory Increment",
    "Display Wait",
    "Sprite Clipping",
    "Shifting",
    "Jumping"
]
quirk_frame = pygame.Rect(frame.right +int(64*scale*0.01), frame.y+int(frame.height*0.1),width - frame.right - int(64*scale*0.01) - int(width*0.01),int(frame.height*0.8))
quirk_row_height = quirk_frame.height / len(quirk_labels)
quirk_font = pygame.font.SysFont(None,int(min(quirk_row_height * 0.45, quirk_frame.width * 0.11)))
quirk_toggle_rects = []
for i in range(6):
    quirk_box = pygame.Rect(quirk_frame.x + quirk_frame.width*0.05,quirk_frame.y + (i+0.15)*quirk_row_height,quirk_frame.width*0.94,quirk_row_height*0.7)
    wtoggle = int(quirk_box.width * 0.16) #width
    htoggle = int(quirk_box.height * 0.5) #height
    toggle_rect = pygame.Rect(quirk_box.right - int(quirk_box.width*0.06) - wtoggle,quirk_box.centery - htoggle//2,wtoggle,htoggle)
    quirk_toggle_rects.append(toggle_rect)

sample_rate = 44100
frequency = 440
duration = 0.1
amplitude = 8000
samples = array("h")
for i in range(int(sample_rate * duration)):
    value = int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
    samples.append(value)

beep = pygame.mixer.Sound(buffer=samples)
channel = pygame.mixer.Channel(0)
keymap = [
    pygame.K_x,  # 0
    pygame.K_1,  # 1
    pygame.K_2,  # 2
    pygame.K_3,  # 3
    pygame.K_q,  # 4
    pygame.K_w,  # 5
    pygame.K_e,  # 6
    pygame.K_a,  # 7
    pygame.K_s,  # 8
    pygame.K_d,  # 9
    pygame.K_z,  # A
    pygame.K_c,  # B
    pygame.K_4,  # C
    pygame.K_r,  # D
    pygame.K_f,  # E
    pygame.K_v   # F
]


def fetch():
    global pc
    opcode = memory[pc] <<8
    opcode+=memory[pc+1]
    pc +=2
    return opcode

def decode(opcode=0XD315):
    return((opcode>>12),((opcode>> 8) - (opcode>>12 << 4)),(opcode-((opcode >> 8) << 8)))
    #returns operation,reg,data

def draw_sprite(reg,data):
    x=reg
    y=data>>4
    n=data-(y<<4)
    vx = gpr[x]%64
    vy = gpr[y]%32
    gpr[15]=0
    for column in range(n):
        for pixelnum,pixelval in enumerate((bin(memory[ir+column])[2:]).zfill(8)):
            if clipping:
                if (vx+pixelnum < 64 and vy+column < 32):
                    if display[((vy+column)*64)+(vx+pixelnum)] == 1 and int(pixelval) == 1:
                        gpr[15] = 1
                    display[((vy+column)*64)+(vx+pixelnum)] ^= int(pixelval)

            else:
                if display[(((vy+column)%32)*64)+((vx+pixelnum)%64)] == 1 and int(pixelval) == 1:
                    gpr[15] = 1
                display[(((vy+column)%32)*64)+((vx+pixelnum)%64)] ^= int(pixelval)

def execute(operation,reg,data):
    global pc,ir,sp,keys,delay_time,display,sound_time,waiting,waiting_reg,waiting_vblank,draw_pending,vblank
    match operation:
        case 0:
            if ((reg==0) and(data==0xee)):
                if sp > 0:
                    sp-=1
                    pc=stack[sp]
            elif (reg==0 and data==0xe0):
                for i in range(2048):
                    display[i]=0
        case 1:
            pc=((reg<<8) + data)
        case 2:
            stack[sp]=pc
            sp+=1
            pc=((reg<<8) + data)
        case 3:
            if gpr[reg]==data:
                pc+=2
        case 4:
            if gpr[reg]!=data:
                pc+=2
        case 5:
            x=reg
            y=data>>4
            n=data-(y<<4)
            if n==0:
                if gpr[x]==gpr[y]:
                    pc+=2
        case 6:
            gpr[reg]=data
        case 7:
            if gpr[reg]+data <=255:
                gpr[reg]+=data
            else:
                gpr[reg]=(gpr[reg]+data)%256
        case 8:
            x=reg
            y=data>>4
            n=data-(y<<4)
            match n:
                case 0:
                    gpr[x]=gpr[y]
                case 1:
                    gpr[x] = gpr[x] | gpr[y]
                    if vfreset:
                        gpr[15]=0
                case 2:
                    gpr[x] = gpr[x] & gpr[y]
                    if vfreset:
                        gpr[15]=0
                case 3:
                    gpr[x] = gpr[x] ^ gpr[y]
                    if vfreset:
                        gpr[15]=0
                case 4:
                    if gpr[x]+gpr[y] >= 256:
                        gpr[x] = (gpr[x]+gpr[y])%256
                        gpr[15]=1
                    else:
                        gpr[x]+=gpr[y]
                        gpr[15]=0
                case 5:
                    if gpr[x]>=gpr[y]:
                        gpr[x]=gpr[x]-gpr[y]
                        gpr[15]=1
                    else:
                        gpr[x]=(gpr[x]-gpr[y])%256
                        gpr[15]=0
                case 6:
                    if shifting:
                        temp=gpr[y]
                    else:
                        temp=gpr[x]
                    gpr[x] = temp>>1
                    gpr[15] = temp & 1
                case 7:
                    if gpr[y]>=gpr[x]:
                        gpr[x]=gpr[y]-gpr[x]
                        gpr[15]=1
                    else:
                        gpr[x]=(gpr[y]-gpr[x])%256
                        gpr[15]=0
                case 14:
                    if shifting:
                        temp=gpr[y]
                    else:
                        temp=gpr[x]
                    gpr[x]= (temp<<1) % 256
                    if temp & 0b10000000 == 128:
                        gpr[15]=1
                    else:
                        gpr[15]=0
        case 9:
            x=reg
            y=data>>4
            n=data-(y<<4)
            if n==0:
                if gpr[x]!=gpr[y]:
                    pc+=2
        case 10:
            ir = (reg<<8)+data
        case 11:
            if jumping:
                pc = (reg<<8)+data + gpr[reg]
            else:
                pc = (reg<<8)+data + gpr[0]
        case 12:
            gpr[reg]=random.randint(0, 255) & data
        case 13:
            if vblank:
                waiting_vblank=True
                draw_pending=(reg,data)
            else:
                draw_sprite(reg,data)
        case 14:
            if (data==0x9e and keys[gpr[reg]]==1):
                pc+=2
            elif(data==0xa1 and keys[gpr[reg]] == 0):
                pc+=2
        case 15:
            match data:
                case 0x07:
                    gpr[reg]=delay_time
                case 0x15:
                    delay_time=gpr[reg]
                case 0x18:
                    sound_time=gpr[reg]
                case 0x1e:
                    ir+=gpr[reg]
                case 0x29:
                    ir= 80+gpr[reg]*5
                case 0x33:
                    temp=gpr[reg]
                    for i in range(2,-1,-1):
                        memory[ir+i]= temp%10
                        temp //= 10
                case 0x55:
                    for i in range(0,reg+1):
                        memory[ir+i]=gpr[i]
                    if mem_inc:
                        ir += reg+1
                case 0x65:
                    for i in range(0,reg+1):
                        gpr[i]=memory[ir+i]
                    if mem_inc:
                        ir += reg+1
                case 0x0a:
                    waiting=True
                    waiting_reg=reg
#read rom
with open(rom, "rb") as file:
    rom = file.read()
    for i in range(len(rom)):
        memory[512+i]=rom[i]


while running:
    quirk_values = [vfreset, mem_inc, vblank, clipping, shifting, jumping]
    timer_acc += clock.tick(60)
    while (timer_acc >= 1000/60):
        timer_acc -=1000/60
        if delay_time > 0:
            delay_time-=1
        if sound_time > 0:
            sound_time-=1
        if waiting_vblank and draw_pending is not None:
            dreg, ddata = draw_pending
            draw_sprite(dreg,ddata)
            draw_pending = None
            waiting_vblank = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            for index,key in enumerate(keymap):
                if event.key==key:
                    if waiting:
                        gpr[waiting_reg]=index
                        waiting=False
                    keys[index]=1
                    key_colour[index]=(65, 88, 108)
        if event.type == pygame.KEYUP:
            for index,key in enumerate(keymap):
                if event.key==key:
                    keys[index]=0
                    key_colour[index]=(35, 48, 60)
        if event.type== pygame.MOUSEBUTTONDOWN and event.button==1:
            for i,rect in enumerate(virtual_key_rects):
                if rect.collidepoint(event.pos):
                    mouse_key = int(key_labels[i], 16)
                    keys[mouse_key] = 1
                    key_colour[mouse_key] = (65, 88, 108)
                    if waiting==True:
                        gpr[waiting_reg] = mouse_key
                        waiting = False
                    break
            for i, rect in enumerate(quirk_toggle_rects):
                if rect.collidepoint(event.pos):
                    if i == 0:
                        vfreset = not vfreset
                    elif i == 1:
                        mem_inc = not mem_inc
                    elif i == 2:
                        vblank = not vblank
                    elif i == 3:
                        clipping = not clipping
                    elif i == 4:
                        shifting = not shifting
                    elif i == 5:
                        jumping = not jumping
                    break
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if mouse_key != None:
                keys[mouse_key] = 0
                key_colour[mouse_key] = (35, 48, 60)
                mouse_key = None
        if event.type == pygame.VIDEORESIZE:
            width, height = screen.get_size()

    for ins in range(10):
        if waiting or waiting_vblank:
            break
        operation, reg, data = decode(fetch())
        execute(operation, reg, data)
    #bg
    screen.fill((25, 38, 51))
    #padding around screen
    pygame.draw.rect(screen, (53, 68, 84), frame, border_radius=18)
    #keyboard
    pygame.draw.rect(screen, (53, 68, 84), key_frame, border_radius=18)
    for i, key in enumerate(key_labels):
        pygame.draw.rect(screen,key_colour[int(key, 16)], virtual_key_rects[i], border_radius=8)
        text = key_font.render(key, True, (241, 245, 249))
        screen.blit(text, text.get_rect(center=virtual_key_rects[i].center))
    #quirks
    pygame.draw.rect(screen, (53, 68, 84),quirk_frame, border_radius=18)
    for i,quirk in enumerate(quirk_labels):
        text = quirk_font.render(quirk,True, (241, 245, 249))
        quirk_box=pygame.Rect(quirk_frame.x + quirk_frame.width*0.05, quirk_frame.y + (i+0.15)*quirk_row_height,quirk_frame.width*0.94,quirk_row_height*0.7)
        quirk_rect = text.get_rect(midleft=(quirk_box.x + quirk_box.width*0.06, quirk_box.centery))
        pygame.draw.rect(screen, (43, 57, 70) ,quirk_box, border_radius=int(quirk_box.height*0.2))
        pygame.draw.rect(screen, (75, 93, 110) ,quirk_box, width=max(1, int(quirk_box.height*0.025)), border_radius=int(quirk_box.height*0.2))
        screen.blit(text, quirk_rect)
        wtoggle = int(quirk_box.width * 0.16) #width
        htoggle = int(quirk_box.height * 0.5) #height
        toggle_rect=pygame.Rect(quirk_box.right - int(quirk_box.width*0.06) - wtoggle,quirk_box.centery - htoggle//2,wtoggle,htoggle)
        if quirk_values[i]:
            toggle_colour = (65, 150, 125)
            knob_x = toggle_rect.right - htoggle//2
        else:
            toggle_colour = (65, 75, 85)
            knob_x = toggle_rect.left + htoggle//2
        pygame.draw.rect(screen, toggle_colour, toggle_rect, border_radius=htoggle//2)
        pygame.draw.circle(screen,(241, 245, 249),(knob_x, toggle_rect.centery) ,int(htoggle*0.35)
)


    title = font.render("Chip-8", True, (255, 255, 255))
    screen_rect = screen.get_rect()
    title_rect = title.get_rect(centerx=screen_rect.centerx, top=int(screen_rect.height * 0.015))
    screen.blit(title, title_rect)
    for index,pixel in enumerate(display):
        if pixel==1:
            pygame.draw.rect(screen,(255,255,255), (scaled_x +(index%64)*scale,scaled_y+(index//64)*scale,scale,scale))
        if pixel==0:
            pygame.draw.rect(screen,(0,0,0), (scaled_x+(index%64)*scale,scaled_y+(index//64)*scale,scale,scale))

    pygame.display.flip()
    if sound_time > 0:
        if channel.get_busy() == False:
            channel.play(beep, loops=-1)
    else:
        channel.stop()

pygame.quit()
