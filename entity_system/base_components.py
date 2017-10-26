# encoding: utf8

from base_component import BaseComponent
from variable.global_vars import G
import config as gconf
from panda3d.core import Vec3, Texture
import random
import logging


class ObjInspectable(BaseComponent):
    name = 'inspectable'

    def __init__(self, config):
        self._iname = config.get('iname', 'NAME_UNSET')

    def on_inspect(self):
        return "inspecting: %s" % self._iname


class ObjModel(BaseComponent):
    name = 'model'

    def __init__(self, config):
        model_path = config['model_file']
        self.scale = config.get('scale', 1.)
        self.collider_scale = config.get('collider_scale', 1.)
        self.is_static = config.get('static', True)  # TODO 对于静态物体，可以合并模型进行优化. np.flatten_strong()
        loader = G.loader
        box = loader.loadModel(model_path)
        box.setName("box")
        box.reparentTo(G.render)
        self.model_np = box
        self.model_np.set_scale(self.scale)
        self.model_np.set_pos(Vec3(0, 0, 0))
        for tex in self.model_np.find_all_textures():
            tex.set_magfilter(Texture.FT_nearest)
            tex.set_minfilter(Texture.FT_linear)

        physics_config = config.get('physics')
        self.physical_np = None
        if physics_config:
            self.physical_np = G.physics_world.addBoxCollider(
                box, mass=0, bit_mask=gconf.BIT_MASK_OBJECT,
                reparent=not self.is_static,
                scale=self.collider_scale,
            )
            self.physical_np.setTag("type", "box")
            body = self.physical_np.node()
            body.setDeactivationEnabled(True)
            body.setDeactivationTime(1.0)
        assert self.physical_np, '%s %s' % (config, physics_config)

    def on_start(self):
        self.get_entity().set_transform(self)

    def set_enabled(self, enabled):
        G.physics_world.set_collider_enabled(self.physical_np, enabled)
        if enabled:
            if self.is_static:
                self.model_np.reparent_to(G.render)
            else:
                self.physical_np.reparent_to(G.render)
        else:
            if self.is_static:
                self.model_np.detach_node()
            else:
                self.physical_np.detach_node()

    def destroy(self):
        G.physics_world.remove_collider(self.physical_np)
        self.physical_np.remove_node()

    def on_save(self):
        pos = self.physical_np.get_pos()
        return pos.getX(), pos.getY(), pos.getZ()

    def on_load(self, data):
        pos = Vec3(data[0], data[1], data[2])
        self.set_pos(pos)

    def get_np(self):
        return self.model_np

    def set_pos(self, pos):
        self.physical_np.set_pos(pos)
        if self.is_static:
            self.model_np.set_pos(pos)

    def get_pos(self):
        return self.physical_np.get_pos()


from common.animator import Animator


class ObjAnimator(BaseComponent):
    name = 'animator'

    def __init__(self, config):
        self._animator = Animator(config, None)
        self._anim_np = self._animator.get_actor_np()
        self._animator.play('idle', once=False)
        self._physical_np = G.physics_world.add_player_controller(self._anim_np, bit_mask=gconf.BIT_MASK_HERO)

    def set_animator_handler(self, handler):
        self._animator.set_event_handler(handler)

    def on_update(self, dt):
        self._animator.on_update()

    def play(self, anim_name, once):
        self._animator.play(anim_name, once)

    def get_current_anim(self):
        return self._anim_np.getCurrentAnim()

    def on_start(self):
        self.get_entity().set_transform(self)

    def set_enabled(self, enabled):
        G.physics_world.set_collider_enabled(self._physical_np, enabled)
        if enabled:
            self._physical_np.reparent_to(G.render)
        else:
            self._physical_np.detach_node()

    def destroy(self):
        G.physics_world.remove_collider(self._physical_np)
        self._physical_np.remove_node()

    def on_save(self):
        pos = self._physical_np.get_pos()
        return pos.getX(), pos.getY(), pos.getZ()

    def on_load(self, data):
        if not data:
            return
        pos = Vec3(data[0], data[1], data[2])
        self.set_pos(pos)

    def get_physical_np(self):
        return self._physical_np

    def set_pos(self, pos):
        self._physical_np.set_pos(pos)

    def get_pos(self):
        return self._physical_np.get_pos()



from util import keyboard
import config as gconf
from util import lerp_util


class ObjTransformController(BaseComponent):
    name = 'transform_controller'

    def __init__(self, config):
        self._move_speed_lerper = lerp_util.FloatLerp(0, 0, max_value=6, lerp_factor=6.543210)
        self._last_move_direction = Vec3(0, 0, 0)
        self.physics_np = None
        self.rigid_body = None
        self._current_speed = 0

    def set_physics_np(self, pnp):
        self.physics_np = pnp
        self.rigid_body = pnp.node()

    def look_at(self, target_point):
        target_point.setZ(self.physics_np.getZ())
        if (target_point - self.physics_np.get_pos()).length() > 0.2:
            self.physics_np.look_at(target_point)

    def stop(self):
        self._current_speed = 0
        self.rigid_body.setLinearMovement(Vec3(0,0,0), False)
        self._move_speed_lerper.reset()

    def move_towards(self, dx, dy, dt):
        direction = Vec3(dx, dy, 0)
        if direction.length() > 0.01:
            self._move_speed_lerper.to_max()
            self._last_move_direction = direction.normalized()
        else:
            self._move_speed_lerper.to_min()
        new_speed = self._move_speed_lerper.lerp(dt)
        self._current_speed = new_speed
        self.rigid_body.setLinearMovement(self._last_move_direction * new_speed,
                                          False)  # False -> World, True -> Local

    def get_speed(self):
        return self._current_speed

    def on_start(self):
        ent = self.get_entity()
        pnp = ent.get_component(ObjAnimator).get_physical_np()
        self.physics_np = pnp
        self.rigid_body = pnp.node()


class ObjCameraTarget(BaseComponent):
    name = 'camera_target'

    def __init__(self, config):
        self.cam_lerper = lerp_util.LerpVec3(4.3210)

    def on_update(self, dt):
        cam_pos = 30
        factor1 = 1
        factor2 = .7
        target_pos = self.get_entity().get_pos() + Vec3(0, -cam_pos * factor1, cam_pos * factor2)
        self.cam_lerper.set_target(target_pos)
        lerped_pos = self.cam_lerper.lerp(dt)
        G.cam.set_pos(lerped_pos)
        G.cam.look_at(lerped_pos + Vec3(0, factor1, -factor2))

from bt_system import behaviour_tree as bt


class ObjRandomHeroController(BaseComponent):
    name = 'random_hero_controller'

    def __init__(self, config):
        self._animator = None
        self.controller = None
        self.target_pos = Vec3()
        self.bt = bt.BehaviourTree(3.5, bt.UntilFailure(
            bt.ActionFn('checking events', self.checking_event),

            bt.ActionFn('waiting', self.pause),
            bt.ActionFn('scared', self.scared_anim),
            bt.ActionFn('waiting2', self.pause2),

            bt.UntilFailure(
                bt.ActionFn('waiting', self.pause),
                bt.ActionFn('scared', self.scared_anim),
                bt.ActionFn('waiting2', self.pause2),
                bt.ActionFn('find target', self.find_target),
                bt.ActionFn('walking', self.walk_to_target),
                bt.ActionFn('boring', self.boring_anim),
                bt.ActionFn('pickup', self.pickup),
            ),

            bt.ActionFn('find target', self.find_target),
            bt.ActionFn('walking', self.walk_to_target),
            bt.Negate(bt.ActionFn('boring', self.boring_anim)),
            bt.ActionFn('pickup', self.pickup),
        ))

        self._last_pos = Vec3()
        self._linger_timer = 0
        G.accept('space', self.hero_space)

    def hero_space(self):
        self.bt.add_event('hero_space', immediately=True)

    def checking_event(self, btree):
        ev = btree.pop_event('hero_space')
        if ev:
            self._animator.play('craft', once=True)
            def anim_cb(event_name):
                return bt.SUCCESS
            btree.wait_for_event('anim.craft.done', anim_cb)
            return bt.RUNNING
        return bt.SUCCESS

    def pause(self, btree):
        btree.wait_for_seconds(.5 + .2 * random.random())
        return bt.RUNNING

    def pause2(self, btree):
        btree.wait_for_seconds(.2 + .3 * random.random())
        return bt.RUNNING

    def find_target(self, btree):
        if random.random() < .5:
            range = 11
            target_pos = Vec3(random.random() * range, random.random() * range,
                                   random.random() * range)
            btree.set('target', target_pos)
            return bt.SUCCESS
        return bt.RUNNING

    def walk_to_target(self, btree):
        target_pos = btree.get('target')
        if not target_pos:
            return bt.FAIL
        self.controller.look_at(target_pos)
        current_pos = self.get_entity().get_pos()
        dist_from_last = (current_pos - self._last_pos).length()
        self._last_pos = current_pos
        if dist_from_last < 0.01:
            self._linger_timer += btree.dt
            if self._linger_timer > .5:
                self._linger_timer = 0
                self.controller.stop()
                return bt.FAIL

        dir = target_pos - current_pos
        if dir.length() > 1:
            dir = dir.normalized()
            self.controller.move_towards(dir[0], dir[1], btree.dt)
            return bt.RUNNING
        else:
            self.controller.stop()
            return bt.SUCCESS

    def pickup(self, btree):
        target_pos = btree.get('target')
        if not target_pos:
            return bt.FAIL
        self.controller.stop()
        self._animator.play('pickup', once=True)
        def anim_cb(event_name):
            if event_name == 'anim.pickup.done':
                return bt.SUCCESS
            return bt.RUNNING
        btree.wait_for_event('anim.pickup.pickup', anim_cb)
        btree.wait_for_event('anim.pickup.done', anim_cb)
        return bt.RUNNING

    def scared_anim(self, btree):
        self._animator.play('scared', once=True)
        def anim_cb(event_name):
            return bt.SUCCESS
        btree.wait_for_event('anim.scared.done', anim_cb)
        return bt.RUNNING

    def boring_anim(self, btree):
        self._animator.play('boring', once=True)
        def anim_cb(event_name):
            return bt.SUCCESS
        btree.wait_for_event('anim.boring.done', anim_cb)
        return bt.RUNNING

    def on_start(self):
        ent = self.get_entity()
        self.controller = ent.get_component(ObjTransformController)
        self._animator = ent.get_component(ObjAnimator)
        self._animator.set_animator_handler(self._animator_handler)

    def _animator_handler(self, anim_name, event_name):
        self.bt.add_event('anim.%s.%s' % (anim_name, event_name), immediately=False)

    def on_update(self, dt):
        self.bt.on_update(dt)

        # animation control
        if self.controller.get_speed() > 0.4:
            self._animator.play('walk', once=True)
        elif self._animator.get_current_anim() == 'walk':
            self._animator.play('idle', once=False)


class ObjHeroController(BaseComponent):
    name = 'hero_controller'

    def __init__(self, config):
        self.cam_lerper = lerp_util.LerpVec3(4.3210)
        self._animator = None
        self.controller = None
        G.accept('mouse1', self.use_tool)

    def on_start(self):
        ent = self.get_entity()
        self.controller = ent.get_component(ObjTransformController)
        self._animator = ent.get_component(ObjAnimator)

    def use_tool(self):
        self.controller.stop()
        self._animator.play('tool', once=True)

    def on_update(self, dt):
        if self.controller.get_speed() > 0.4:
            self._animator.play('walk', once=True)
        elif self._animator.get_current_anim() == 'walk':
            self._animator.play('idle', once=False)
        pos = G.game_mgr.operation.look_at_target
        self.controller.look_at(pos)
        dx, dy = keyboard.get_direction()
        self.controller.move_towards(dx, dy, dt)
