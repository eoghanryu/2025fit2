import pyxel

field_size = 150

class Ball:
    speed = 1.2
    
    def __init__(self):
        self.restart()

    def move(self):
        self.x += self.vx * Ball.speed
        self.y += self.vy * Ball.speed
    
        if (self.x < 0) or (self.x >= field_size):
            self.vx = -self.vx

    def restart(self):
        self.x = pyxel.rndi(0, field_size - 1)
        self.y = 0
        angle = pyxel.rndi(30, 150)
        self.vx = pyxel.cos(angle)
        self.vy = pyxel.sin(angle)


class Pad:
    
    def __init__(self):
        self.x = field_size/2
        self.size = field_size / 5
        self.color = pyxel.rndi(1,15)

    def catch(self, ball):
        if ball.y >= field_size-field_size/40 and (self.x-self.size/2 <= ball.x <= self.x+self.size/2):
            return True
        else:
            return False
        

class App:
    def __init__(self):
        
        

        pyxel.init(field_size,field_size)
        pyxel.sound(0).set(notes='A2C3', tones='TT', volumes='33', effects='NN', speed=10)
        pyxel.sound(1).set(notes='C2', tones='N', volumes='3', effects='S', speed=30)

        self.balls = [Ball()]
        self.alive = True
        self.life = 10
        self.receive = 0
        self.pad = Pad()
        self.score = 0
        self.ballcolor = pyxel.rndi(1,6)

        pyxel.run(self.update, self.draw)





    def update(self):

        if not self.alive:
            return
        self.pad.x = pyxel.mouse_x
        for b in self.balls:
            b.move()

            
            if b.y >= field_size:
                pyxel.play(0, 1)
                Ball.speed += 0.2
                b.restart()
                self.pad.color = pyxel.rndi(1,15)
                self.life -= 1
                self.alive = (self.life > 0)
            if self.pad.catch(b):
                pyxel.play(0, 0)
                self.score += 1
                Ball.speed += 0.2
                b.restart()
                self.pad.color = pyxel.rndi(1,15)
                self.receive += 1
                if self.receive >= 10:
                    Ball.speed = 1
                    self.receive = 0
                    self.balls.append(Ball())
                    self.ballcolor = pyxel.rndi(1,6)





    def draw(self):
        if self.alive:
            pyxel.cls(7)
            for b in self.balls:
                pyxel.circ(b.x, b.y, field_size/20, self.ballcolor)
            pyxel.rect(self.pad.x-self.pad.size/2, field_size-field_size/40, self.pad.size, 5, self.pad.color)
            pyxel.text(5, 5, "score: " + str(self.score), 0)
            pyxel.text(5, 15, "life: " + str(self.life), 0)
        else:
            pyxel.text(field_size/2-20, field_size/2-20, "Game Over!!!", 0)

App()