#encoding: utf8

class AiManager(object):
    def __init__(self):
        pass

    def setup_ai(self):
        # Creating AI World
        self.AIworld = AIWorld(self.render)
        self.AIchar = AICharacter("seeker", self.hero_np, 100, 0.1, 30)
        self.AIworld.addAiChar(self.AIchar)
        self.AIbehaviors = self.AIchar.getAiBehaviors()
        # self.taskMgr.add(self.ai_update_task, "AIUpdate")

        self.pursue_target = NodePath("pursue_target")
        self.AIbehaviors.pursue(self.pursue_target, 1)

    # to update the AIWorld
    def ai_update_task(self, task):

        old_pos = self.hero_np.get_pos()

        self.pursue_target.set_pos(self.look_at_target)
        self.AIworld.update()

        # set rigid_body transform by ai
        velocity = self.hero_body.get_linear_vel()
        dir = self.hero_np.get_pos() - old_pos
        if dir.length() > 0.01 and velocity.length() < 6:
            force = dir.normalized() * 200000
            self.hero_body.add_force(force)

        self.hero_np.set_pos(old_pos)
        self.hero_body.set_quaternion(self.hero_np.get_quat())

        return Task.cont
