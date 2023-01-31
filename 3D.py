import pygame, math, sys
from sys import exit
from random import randint, choice
import random
import csv

class Shape(pygame.sprite.Sprite):
	def __init__(self,screen):
		super().__init__()
		with open('nodes.txt', newline='') as csvfile:
			self.nodes = list(csv.reader(csvfile, delimiter=','))[1:]

		with open('connectivities.txt', newline='') as csvfile:
			self.connectivities = list(csv.reader(csvfile, delimiter=','))[1:]

		temp2=[];temp20=[]
#		with open('Eiffel_tower_sample.STL', newline='') as file:
#		with open('humanoid.stl', newline='') as file:
#		with open('bottle.stl', newline='') as file:
#		with open('surface.stl', newline='') as file:
		with open('cube.stl', newline='') as file:
#		with open('longroom.stl', newline='') as file:
#		with open('ground.stl', newline='') as file:
#		with open('teapot.stl', newline='') as file:
			for line in file:
#				print(line)
				temp=line.strip()
				if temp.startswith('vertex '):
					temp3=[]
					for coor in range(3):
#						if float(temp.split()[1:][coor]) > 110:
						temp3.append(float(temp.split()[1:][coor]))
					temp2.append(temp3)
				elif temp.startswith('facet normal'):
					temp30 = []
					for coor in range(3):
						temp30.append(float(temp.split()[2:][coor]))
					temp20.append(temp30)

#		print(temp20)
		self.normals=temp20
		temp6=[]
		xmax=0;ymax=0;zmax=0
		xmin = 0;ymin = 0;zmin = 0
		for i in range(len(temp2)):
			temp6.append(temp2[i])
			xmax = max(xmax,temp2[i][0])
			ymax = max(ymax, temp2[i][1])
			zmax = max(zmax, temp2[i][2])
			xmin = min(xmin,temp2[i][0])
			ymin = min(ymin, temp2[i][1])
			zmin = min(zmin, temp2[i][2])

		self.nodes=temp6
		print(xmax);print(ymax);print(zmax)
		print(xmin);print(ymin);print(zmin)

		self.factor=1

		### Camera Initial Location
#		self.campos=[0,200,0]
		self.campos = [0.5, 0, 0.5]

		### Camera Initial Vector (Could be non_normalized)
#		self.camvect = [0,-1,0]
		self.camvect = [0, 1, 0]
		self.camvect=normalize(self.camvect)

		### Light Source Location
		self.light = [200,200,200]

		### Tangent of half of the angle of field of view (70 deg = 2.74747741945)
		self.tangtheta=2.74747741945

	def calculations_for_arbit(self):
		### This vector guarantees that the camera is always looking horizontal.
		camplane_y = [0, 0, 1]
		camplane_z = self.camvect
		camplane_x = cross(camplane_y, camplane_z)

		self.pixelperunit = 300
		self.projection=[];self.nodedistance=[];self.prjsc=[]
		tang_of_angle=[]
		for i in range(len(self.nodes)):
			for j in range(3):
				self.nodes[i][j]=float(self.nodes[i][j])
			self.nodedistance.append(magnitude([self.nodes[i][0]-self.campos[0],self.nodes[i][1]-self.campos[1],self.nodes[i][2]-self.campos[2]]))
			self.projection.append(transform_axes([0, 0, 0], self.campos, camplane_x, camplane_y, camplane_z, self.nodes[i],1))
			self.prjsc.append([self.projection[i][0]*self.pixelperunit+FrameWidth/2,
										  -self.projection[i][1]*self.pixelperunit+FrameHeight/2,
										  self.projection[i][2]])

		nodenums=len(self.nodes)
#		print(self.nodedistance[0])
#		print(self.prjsc[2])

		self.surf_cents=[]
		light_vect1=[];light_vect2=[];light_vect3=[]
		light_angle=[];light_absangle=[]
		view_vect1=[];view_vect2=[];view_vect3=[];view_angle=[]
		distance=[]
		for i in range(int(nodenums/3)):
			x1 = (self.nodes[i * 3][0] + self.nodes[i * 3 + 1][0] + self.nodes[i * 3 + 2][0])/3
			x2 = (self.nodes[i * 3][1] + self.nodes[i * 3 + 1][1] + self.nodes[i * 3 + 2][1])/3
			x3 = (self.nodes[i * 3][2] + self.nodes[i * 3 + 1][2] + self.nodes[i * 3 + 2][2])/3
			self.surf_cents.append([x1,x2,x3])
			light_vect1.append(x1 - self.light[0])
			light_vect2.append(x2 - self.light[1])
			light_vect3.append(x3 - self.light[2])
			light_vect=[light_vect1[0],light_vect2[0],light_vect3[0]]
			light_angle_temp=dot_product(light_vect,self.normals[i])/vect_size(light_vect)/vect_size(self.normals[i])
			light_angle.append(light_angle_temp)
			light_absangle.append(abs(light_angle_temp))

			view_vect1.append(self.surf_cents[i][0] - self.campos[0])
			view_vect2.append(self.surf_cents[i][1] - self.campos[1])
			view_vect3.append(self.surf_cents[i][2] - self.campos[2])
			view_vect = [view_vect1[0], view_vect2[0], view_vect3[0]]
			distance.append(magnitude(view_vect))
			view_angle_temp = dot_product(view_vect, self.normals[i]) / distance[-1] / vect_size(self.normals[i])
			view_angle.append(view_angle_temp)

		### Needs update to include change in normals.
		self.view_angle=view_angle
		self.distance=distance

#		draw_indices=list(range(0, int(nodenums/3)-1))
		draw_indices = list(range(0, int(nodenums / 3)))
		draw_indices=[x for _, x in sorted(zip(self.distance, draw_indices),reverse=True)]
#		print(list(range(0, int(nodenums/3))))
#		print(nodenums)

		for i in draw_indices:
#			while self.prjsc[i][2]>-2:
			pygame.draw.polygon(screen, (light_absangle[i] * 250, 0, 0), [
				[self.prjsc[i * 3][0], self.prjsc[i * 3][1]],
				[self.prjsc[i * 3 + 1][0], self.prjsc[i * 3 + 1][1]],
				[self.prjsc[i * 3 + 2][0], self.prjsc[i * 3 + 2][1]]], 1)

			pygame.draw.line(screen, (250, 250, 250), (FrameWidth/2, FrameHeight/2), (FrameWidth/2+100, FrameHeight/2), width=2)
			pygame.draw.line(screen, (250, 250, 250), (FrameWidth/2, FrameHeight/2), (FrameWidth/2, FrameHeight/2+100), width=2)

#		sys.exit()

		self.collision_num = 0

	def user_input(self):
		angle_constant=0.10
		keys = pygame.key.get_pressed()
		if keys[pygame.K_UP]:
			for i in range(len(self.nodes)):
				temp1,temp2 = rotate_around_axis(self.nodes[i][1], self.nodes[i][2], 1*angle_constant)
				self.nodes[i]=[self.nodes[i][0],temp1,temp2]
		elif keys[pygame.K_DOWN]:
			for i in range(len(self.nodes)):
				temp1,temp2 = rotate_around_axis(self.nodes[i][1], self.nodes[i][2], -1*angle_constant)
				self.nodes[i]=[self.nodes[i][0],temp1,temp2]
		elif keys[pygame.K_RIGHT]:
			for i in range(len(self.nodes)):
				temp1,temp2 = rotate_around_axis(self.nodes[i][2], self.nodes[i][0], 1*angle_constant)
				self.nodes[i]=[temp2,self.nodes[i][1],temp1]
		elif keys[pygame.K_LEFT]:
			for i in range(len(self.nodes)):
				temp1,temp2 = rotate_around_axis(self.nodes[i][2], self.nodes[i][0], -1*angle_constant)
				self.nodes[i]=[temp2,self.nodes[i][1],temp1]
		elif keys[pygame.K_z]:
			for i in range(len(self.nodes)):
				temp1,temp2 = rotate_around_axis(self.nodes[i][0], self.nodes[i][1], 1*angle_constant)
				self.nodes[i]=[temp1,temp2,self.nodes[i][2]]
		elif keys[pygame.K_x]:
			for i in range(len(self.nodes)):
				temp1,temp2 = rotate_around_axis(self.nodes[i][0], self.nodes[i][1], -1*angle_constant)
				self.nodes[i]=[temp1,temp2,self.nodes[i][2]]

	def user_input_player_moving(self):
		self.movconst = 0.2
		self.angconst = 0.01
		keys = pygame.key.get_pressed()
		if keys[pygame.K_UP]:
			self.campos = [self.campos[0]+ self.camvect[0] * self.movconst,
						   self.campos[1]+ self.camvect[1] * self.movconst,
						   self.campos[2]+ self.camvect[2] * self.movconst]
#			self.pixelperunit+=1
		elif keys[pygame.K_DOWN]:
			self.campos = [self.campos[0]- self.camvect[0] * self.movconst,
						   self.campos[1]- self.camvect[1] * self.movconst,
						   self.campos[2]- self.camvect[2] * self.movconst]
#			self.pixelperunit-=1
#			print(self.campos)
		elif keys[pygame.K_RIGHT]:
			temp1,temp2 = rotate_around_axis(self.camvect[0], self.camvect[1], self.angconst)
			self.camvect=[temp1,temp2,self.camvect[2]]
		elif keys[pygame.K_LEFT]:
			temp1,temp2 = rotate_around_axis(self.camvect[0], self.camvect[1], -self.angconst)
			self.camvect=[temp1,temp2,self.camvect[2]]

	def update(self):
		self.calculations_for_arbit()
		self.user_input_player_moving()
#		self.user_input()

class Ball(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		ball_image=pygame.image.load('graphics/bullet.png').convert_alpha()
		# Set the size for the image
		DEFAULT_IMAGE_SIZE = (8, 8)
		ball_image = pygame.transform.scale(ball_image, DEFAULT_IMAGE_SIZE)
		self.image = ball_image
		self.rect = self.image.get_rect(midtop = (400,200))
		self.speed=3
#		self.xfactor = random.uniform(-1,1)
		self.xfactor = -0.6
		self.ysign = math.copysign(1, random.uniform(-1,1))
		self.yfactor = math.sqrt(1-math.pow(self.xfactor,2))*self.ysign
		self.collision_num=0

	def change_dir(self):
		if self.rect.y > 300 or self.rect.y < 0:
			self.yfactor = -self.yfactor
		if self.collision_num == 1:
#			print(self.xfactor)
			self.xfactor=-self.xfactor

	def update(self,collision_state):
		self.collision_num = collision_state
		self.change_dir()
		self.rect.x += self.xfactor*self.speed
		self.rect.y += self.yfactor*self.speed

class Racket(pygame.sprite.Sprite):
	def __init__(self,type):
		super().__init__()
		racket_image=pygame.image.load('graphics/bullet.png').convert_alpha()
		DEFAULT_IMAGE_SIZE = (6, 45)
		racket_image = pygame.transform.scale(racket_image, DEFAULT_IMAGE_SIZE)
		self.image = racket_image
		self.speed=3
		self.type=type
		self.ballypos=ball_group.sprites()[0].rect.y
		if type == 'player':
			self.rect = self.image.get_rect(midbottom = (200,180))
		elif type == 'ai':
			self.rect = self.image.get_rect(midbottom = (600,180))

	def player_input(self):
		if self.type == 'player':
			keys = pygame.key.get_pressed()
			if keys[pygame.K_UP] and self.rect.top > 0:
				self.rect.y -= self.speed
			elif keys[pygame.K_DOWN] and self.rect.bottom < 400:
				self.rect.y += self.speed
		elif self.type == 'ai':
			self.move_towards_ball()

	def move_towards_ball(self):
		self.ballypos = ball_group.sprites()[0].rect.y
		deltay = self.ballypos - self.rect.midleft[1]
		dysign = math.copysign(1, deltay)
		if self.rect.y < 308 and self.rect.y > -50:
			self.rect.y += self.speed*dysign

	def update(self,type):
		self.type = type
		self.player_input()

def normalize(v):
    vmag = magnitude(v)
    return [v[i]/vmag  for i in range(3)]

def magnitude(v):
    return math.sqrt(sum(v[i]*v[i] for i in range(3)))

def transform_axes(o1,o2,vx1,vx2,vx3,p1,factor):
	temp=[o1[0]-o2[0]+p1[0],o1[1]-o2[1]+p1[1],o1[2]-o2[2]+p1[2]]
	m_t=[[vx1[0],vx2[0],vx3[0]],[vx1[1],vx2[1],vx3[1]],[vx1[2],vx2[2],vx3[2]]]
	p2x = (m_t[0][0] * temp[0] + m_t[1][0] * temp[1] + m_t[2][0] * temp[2])
	p2y = (m_t[0][1] * temp[0] + m_t[1][1] * temp[1] + m_t[2][1] * temp[2])
	p2z = (m_t[0][2] * temp[0] + m_t[1][2] * temp[1] + m_t[2][2] * temp[2])
	planar_mag=magnitude([p2x, p2y, 0])
	distance=magnitude([p2x, p2y, p2z])
#	print(distance)
	factor=1
#	tang_of_angle=factor+abs((planar_mag)/(abs(p2z)))
#	tang_of_angle=(0.1+planar_mag)/(distance+1e-6)/math.copysign(1, p2z)
#	tang_of_angle = (0.1 + planar_mag) / (distance + 1e-6)
	tang_of_angle = (0.1 + planar_mag) /(distance)
#	tang_of_angle = (0.1 + planar_mag) / distance*(1-math.copysign(1, p2z)*distance)
#	tang_of_angle = (0.1 + planar_mag) / (p2z+1e-20)
#	https: // gabrielgambetta.com / computer - graphics - from-scratch / 10 - describing - and -rendering - a - scene.html
	print(tang_of_angle)
#	if tang_of_angle>0.5:
#		print(tang_of_angle)
#	if tang_of_angle > 0.1:
#		tang_of_angle=0.1
#	for i in range(3):
#		p2.append(m_t[0][i] * temp[0] + m_t[1][i] * temp[1] + m_t[2][i] * temp[2])
	return [p2x*tang_of_angle*factor,p2y*tang_of_angle*factor,p2z]
#	return [p2x*factor,p2y*factor,p2z]

def display_score():
#	current_time = int(pygame.time.get_ticks() / 1000) - start_time
#	score_surf = test_font.render(f'Score: {current_time}',False,(64,64,64))
#	score_rect = score_surf.get_rect(center = (400,50))
#	screen.blit(score_surf,score_rect)
	current_time = globalx
	score_surf = test_font.render(f'Score: {current_time}',False,(64,64,64))
	score_rect = score_surf.get_rect(center = (400,50))
	screen.blit(score_surf,score_rect)
	return current_time

def collision_sprite():
#	if pygame.sprite.groupcollide(racket,ball_group,False,False):
		return 1
#	else:
		return 0

def dot_product(v1,v2):
	return v1[0]*v2[0]+v1[1]*v2[1]+v1[2]*v2[2]

def vect_size(v1):
	return math.sqrt(v1[0]*v1[0]+v1[1]*v1[1]+v1[2]*v1[2])

def project_on_plane2(x,y,z,x0,y0,z0,a,b,c,factor):
	c1 = x0*a + y0*b + z0*c
	a1 = x*a + y*b + z*c - c1
	planar_x = factor*(x - a1*a)
	planar_y = factor*(y - a1*b)
	planar_z = factor*(z - a1*c)
	return [planar_x,planar_y,planar_z]

def project_v_on_v(v1,v2):
	factor=dot_product(v1, v2) / vect_size(v2) / vect_size(v2)
	return [factor*v2[0],factor*v2[1],factor*v2[2]]

def cross(v1, v2):
	return [v1[1]*v2[2] - v1[2]*v2[1], v1[2]*v2[0] - v1[0]*v2[2], v1[0]*v2[1] - v1[1]*v2[0]]

def project_on_plane(x,y,z,x0,y0,z0,a,b,c,local_x):
	project_v_on_v(local_x,[1,0,0])
	xnew=dot_product([x-x0,y-y0,z-z0],project_v_on_v(local_x,[1,0,0]))
	ynew = dot_product([x - x0, y - y0, z - z0], cross([a,b,c],project_v_on_v(local_x, [1, 0, 0])))
	return [xnew,ynew]

def rotate_around_axis(y,z,angle):
	y2=math.cos(angle)*y - math.sin(angle)*z
	z2=math.sin(angle)*y + math.cos(angle)*z
	return y2,z2

def clip(surface, x, y, x_size, y_size): #Get a part of the image
    handle_surface = surface.copy() #Sprite that will get process later
    clipRect = pygame.Rect(x,y,x_size,y_size) #Part of the image
    handle_surface.set_clip(clipRect) #Clip or you can call cropped
    image = surface.subsurface(handle_surface.get_clip()) #Get subsurface
    return image.copy() #Return

def divisible_by(x, y):
    if (x % y) == 0:
        return True
    else:
        return False

def time_increment(now,then,dt):
	if now-then>=dt:
		then=now
		return True, then
	else:
		return False, then

pygame.init()
FrameHeight = 500
FrameWidth = 500
globalx=0;globaly=0
screen = pygame.display.set_mode((FrameWidth,FrameHeight))
pygame.display.set_caption('Runner')
clock = pygame.time.Clock()
test_font = pygame.font.Font('font/Pixeltype.ttf', 50)
game_active = False
start_time = 0
score = 0
#bg_music = pygame.mixer.Sound('audio/music.wav')
#bg_music.play(loops = -1)

shape_group = pygame.sprite.Group()
shape_group.add(Shape(screen))

#ball_group = pygame.sprite.Group()
#ball_group.add(Ball())

#Groups
#racket = pygame.sprite.Group()
#racket.add(Racket('player',))
#racket.add(Racket('ai',))


sky_surface = pygame.image.load('graphics/Sky.png').convert()
DEFAULT_IMAGE_SIZE = (FrameWidth, FrameHeight)
sky_surface = pygame.transform.scale(sky_surface, DEFAULT_IMAGE_SIZE)
ground_surface = pygame.image.load('graphics/ground.png').convert()
heart_surface = pygame.image.load('graphics/heart.png').convert_alpha()

# Intro screen
player_stand = pygame.image.load('graphics/player/player_stand.png').convert_alpha()
#player_stand = pygame.image.load('graphics/mama.png').convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand,0,2)
player_stand_rect = player_stand.get_rect(center = (400,200))

game_name = test_font.render('Pong!',False,(111,196,169))
game_name_rect = game_name.get_rect(center = (400,80))

game_message = test_font.render('Press space to run',False,(111,196,169))
game_message_rect = game_message.get_rect(center = (400,330))

# Timer 
#obstacle_timer = pygame.USEREVENT + 1
#pygame.time.set_timer(obstacle_timer,1500)

now = pygame.time.get_ticks()
then=now

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			exit()

		if game_active:
			i=1
#			print(game_active)

		else:
			if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
				game_active = True
				start_time = int(pygame.time.get_ticks() / 1000)

	if game_active:
		screen.blit(sky_surface, (0, 0))
		pygame.draw.line(screen, (0, 0, 0), (0, 308), (1000, 308),width=2)
		collision_state = collision_sprite()

#		shape_group.draw(screen)
		shape_group.update()

#		ball_group.draw(screen)
#		ball_group.update(collision_state)

#		racket.draw(screen)
#		racket.sprites()[0].update('player')
#		racket.sprites()[1].update('ai')

	else:
		screen.fill((94,129,162))
		screen.blit(player_stand,player_stand_rect)

		score_message = test_font.render(f'Your score: {score}',False,(111,196,169))
		score_message_rect = score_message.get_rect(center = (400,330))
		screen.blit(game_name,game_name_rect)

		if score == 0: screen.blit(game_message,game_message_rect)
		else: screen.blit(score_message,score_message_rect)

	pygame.display.update()
	clock.tick(60)