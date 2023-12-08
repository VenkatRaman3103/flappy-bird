import pygame
import random
import os
import neat
pygame.font.init()

WIN_WIDTH = 600
WIN_HEIGHT = 680
BASE = 640
STAT_FONT = pygame.font.SysFont("arial.ttf", 30)
END_FONT = pygame.font.SysFont("arial.ttf", 30)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha())

gen = 0

class Bird:
    # Making the Bird object
    MAX_ROTATION = 25
    IMGS = bird_images
    ROT_VELOCITY = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        """
        Initializing the object
        :parameter --> x: starting x position
        :parameter --> y: starting y position
        :return: None
        """
        self.x = x
        self.y = y
        self.tilt = 0  # degrees to tilt...
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        """
        make the bird jump
        :return: None
        """
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        """
        make the bird move
        :return: None
        """
        self.tick_count += 1

        # While falling...
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculating displacement...

        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        # tilting the  bird up...
        if displacement < 0 or self.y < self.height + 50:  
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        # tilting the  bird down...
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VELOCITY

    def draw(self, win):
        """
        drawing the bird in the window
        :parameter --> win: pygame window
        :return: None
        """
        self.img_count += 1

        # In order to make the bird to flap its wings, I been looping here with three images of the bird with different wing positions (up, normal and down)
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # When the bird is falling, it should not flap its wings. So just projecting the second image(normal wing position)
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2


        # Calling a function which tilt the bird...
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)


    def get_mask(self):
        """
        Masking over the img of the bird (wrapping arround the bird with imaginary square box which is known as mask in pygame, been used at the time collaid)
        :return: None
        """
        return pygame.mask.from_surface(self.img)


class Pipe():
    """
    Making Pipes
    """
    GAP = 200  # Gap between pipes...
    VEL = 5

    def __init__(self, x):
        """
        initialize pipe object
        :parameter --> x: int
        :return" None
        """
        self.x = x
        self.height = 0

        # Top and bottom of the pipes are...
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False  #  In order to initiate another pipe object...

        self.set_height()

    def set_height(self):
        """
        fixing the height of the pipe
        :return: None
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        Moving the pipes oin the direction of x according to the velocity
        :return: None
        """
        self.x -= self.VEL

    def draw(self, win):
        """
        Drawing both the top and bottom of the pipe
        :parameter --> win: pygame window
        :return: None
        """
        # drawing the top...
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # drawing bottom...
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird, win):
        """
        If the mask(wrap) collide with the pipe it return False
        :parameter --> bird: Bird object
        :return: Boolean value
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        bottom_point_collide = bird_mask.overlap(bottom_mask, bottom_offset)  # Returns None, if colliding
        top_point_collide = bird_mask.overlap(top_mask,top_offset)  # Also returns None, if colliding

        if bottom_point_collide or top_point_collide:
            return True

        return False

class Base:
    """
    Base of the game
    """
    VEL = 5
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        """
        Initialize the object
        :parameter --> y: int
        :return: None
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        Moving the base
        :return: None
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
        Drawing the base. There are two images behind the scene, 
        at certain one begins to follow another
        :parameter --> win: pygame window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))



def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    """
    Main window of the game
    :parameter -->  win: pygame window
    :parameter -->  bird: a Bird object
    :parameter -->  pipes: List of pipes
    :parameter -->  score: score of the game
    :parameter -->  gen: current number of generation
    :parameter -->  pipe_ind: index of pipe
    :return: None
    """
    if gen == 0:
        gen = 1
    win.blit(bg_img, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        # draw lines from bird to pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
        # drawing bird...
        bird.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # Number of generations
    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (10, 10))

    # Number of birds that are alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    pygame.display.update()


def eval_genomes(genomes, config):
    """
    Setting  the fitness of the birds based on the distance they have reached so far
    """
    global WIN, gen
    win = WIN
    gen += 1

    # Creating a list of genome's neural network, So that the bird object can use it
    nets = []
    birds = []
    ge = []

    for genome_id, genome in genomes:
        genome.fitness = 0  # it is starting point, so the fitness level is 0...
        net = neat.nn.FeedForwardNetwork.create(genome, config)  # as per the documentation...

        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)

    base = Base(BASE)
    pipes = [Pipe(700)]
    score = 0

    clock = pygame.time.Clock()

    run = True
    while run and len(birds) > 0:
        clock.tick(30)  # To control the speed of the Game. Whenever the speed is high the genome takes slithly more number of generations, so it is prefered to be 30

        # Quiting the game...
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # determine whether to use the first or second
                pipe_ind = 1  # pipe on the screen for neural network input

        for x, bird in enumerate(birds):  # For eacch frame 0.1 fitness point will be added to the bird which is alive...
            ge[x].fitness += 0.1
            bird.move()

            # Sending the location informations of the bird, top of the bottom pipe and the bottom of the top pipe, Then deciding whether to jump or not
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  # " TanH " method is used, because of simplicity, which will returns the value within the range of -1 and the +1...
                bird.jump()  # jumping if the TanH value is higher than 0.5, we can change the parameter...

        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()

            # checking for any occurance of collision...
            for bird in birds:
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= BASE or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)


def run(config_file):
    """
    Runnig the NEAT algorithm as per documentation.
    :parameter --> config_file: location of config file
    :return: None
    """
    # boiler plate form the documentation...
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Creating the population, main function for a NEAT algorithm to run...
    p = neat.Population(config)

    # "StdOutReporter" - An inbuild feature of NEAT algorithm which will show the status in the terminal itself.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Making 50 generations by passing it into the eval_genome...
    winner = p.run(eval_genomes, 50)



if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)

