# encoding: utf8

from base_component import *
from variable.global_vars import G
import config as gconf
from panda3d.core import Vec3, Texture, NodePath
import random
import logging
from inventory_system.common import consts
from util import log, tween
from config import *
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.IntervalGlobal import *


class ObjInspectable(BaseComponent):
    name = 'inspectable'
    entity_type = ENTITY_TYPE_OBJECT

    def __init__(self, config):
        self._iname = config.get('iname', 'NAME_UNSET')

    def on_inspect(self):
        return "inspecting: %s" % self._iname


class ObjModel(BaseComponent):
    name = 'model'
    entity_type = ENTITY_TYPE_OBJECT

    def __init__(self, config):
        model_path = config['model_file']
        self.scale = config.get('scale', 1.)
        self.collider_scale = config.get('collider_scale', 1.)
        self.is_static = config.get('static', False)  # TODO 对于静态物体，可以合并模型进行优化. np.flatten_strong()
        self.model_np = NodePath("unknown_model")
        G.loader.loadModel(model_path).get_children().reparent_to(self.model_np)
        self.model_np.set_scale(self.scale)
        self.model_np.set_pos(Vec3(0, 0, 0))
        for tex in self.model_np.find_all_textures():
            tex.set_magfilter(Texture.FT_nearest)
            tex.set_minfilter(Texture.FT_linear)
        self.enabled = True
        if not self.is_static:
            self.model_np.reparent_to(G.render)

        physics_config = config.get('physics')
        self.physical_np = None
        if physics_config:
            self.physical_np, self.half_size = G.physics_world.add_cylinder_collider(
                self.model_np, mass=0, bit_mask=gconf.BIT_MASK_OBJECT,
                reparent=False,
                scale=self.collider_scale,
            )
            body = self.physical_np.node()
            body.setDeactivationEnabled(True)
            body.setDeactivationTime(1.0)
        else:
            self.half_size = G.physics_world.get_bounding_size(self.model_np) * .5

    def on_start(self):
        if self.physical_np:
            self.physical_np.set_python_tag("type", "object")
            self.physical_np.set_python_tag("entity", self._entity_weak_ref)
        ent = self.get_entity()
        ent.set_transform(self)
        ent.set_radius(max(self.half_size[0], self.half_size[1]))
        self.model_np.setName('%s.model' % ent.get_name())

    def set_enabled(self, enabled):
        assert self.enabled != enabled
        self.enabled = enabled
        if self.physical_np:
            G.physics_world.set_collider_enabled(self.physical_np, enabled)

    def destroy(self):
        if self.physical_np:
            G.physics_world.remove_collider(self.physical_np)
            self.physical_np.remove_node()
        if self.model_np:
            self.model_np.remove_node()

    def on_save(self):
        if self.physical_np:
            pos = self.physical_np.get_pos()
        else:
            pos = self.model_np.get_pos()
        return pos.getX(), pos.getY(), pos.getZ()

    def on_load(self, data):
        pos = Vec3(data[0], data[1], data[2])
        self.set_pos(pos)

    def get_np(self):
        return self.model_np

    def set_pos(self, pos):
        if self.physical_np:
            self.physical_np.set_pos(pos)
            if self.is_static:
                self.model_np.set_pos(pos)
        else:
            self.model_np.set_pos(pos)

    def get_pos(self):
        if self.physical_np:
            return self.physical_np.get_pos()
        return self.model_np.get_pos()

    def get_models(self):
        return [self.model_np]

    def get_static_models(self):
        if self.is_static:
            return [self.model_np]
        return []

from common.animator import Animator


class ObjAnimator(BaseComponent):
    name = 'animator'
    entity_type = ENTITY_TYPE_OBJECT

    def __init__(self, config):
        self._animator = Animator(config, None)
        self._anim_np = self._animator.get_actor_np()
        self._animator.play('idle', once=False)
        self._physical_np = G.physics_world.add_player_controller(self._anim_np, bit_mask=gconf.BIT_MASK_HERO)

    def get_actor_np(self):
        return self._anim_np

    def set_animator_handler(self, handler):
        self._animator.set_event_handler(handler)

    def on_update(self, dt):
        self._animator.on_update()

    def play(self, anim_name, once):
        self._animator.play(anim_name, once)

    def get_current_anim(self):
        return self._anim_np.getCurrentAnim()

    def on_start(self):
        self._physical_np.set_python_tag('type', 'hero')
        self._physical_np.set_python_tag('entity', self._entity_weak_ref)
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
    entity_type = ENTITY_TYPE_OBJECT

    def __init__(self, config):
        self._move_speed_lerper = lerp_util.FloatLerp(
            0, 0, max_value=config.get('speed', 6), lerp_factor=6.543210)
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


from bt_system import behaviour_tree as bt


class ObjRandomHeroController(BaseComponent):
    name = 'random_hero_controller'
    entity_type = ENTITY_TYPE_OBJECT

    def __init__(self, config):
        self._animator = None
        self.controller = None
        self.target_pos = Vec3()
        self.bt = None

    def on_start(self):
        ent = self.get_entity()
        self.controller = ent.get_component(ObjTransformController)
        self._animator = ent.get_component(ObjAnimator)
        self._animator.set_animator_handler(self._animator_handler)

        from bt_system import actions
        bt_context = {'entity': self._entity_weak_ref}
        bt_root = bt.UntilFailure(
            actions.ActionAnim('scared_anim', 'scared', {'done': 'success'}),
            actions.ActionRandomTargetPos('find target', 30),
            actions.ActionMove('moving'),
        )
        self.bt = bt.BehaviourTree(100, bt_root, bt_context)

    def _animator_handler(self, anim_name, event_name):
        self.bt.add_event('anim.%s.%s' % (anim_name, event_name), immediately=False)

    def on_update(self, dt):
        self.bt.on_update(dt)

        # animation control
        if self.controller.get_speed() > 0.4:
            self._animator.play('walk', once=True)
        elif self._animator.get_current_anim() == 'walk':
            self._animator.play('idle', once=False)


class ObjLoot(BaseComponent):
    name = 'loot'
    entity_type = ENTITY_TYPE_OBJECT

    def __init__(self, config):
        self._loots = config.get('loots')
        assert self._loots, config
        assert isinstance(self._loots, list)

    def on_loot(self):
        ent = self.get_entity()
        center_pos = ent.get_pos()
        radius = ent.get_radius()
        for loot_name, loot_count in self._loots:
            G.game_mgr.create_item_on_ground(center_pos, radius, loot_name, loot_count)


class ObjDestroyable(BaseComponent):
    name = 'destroyable'
    entity_type = ENTITY_TYPE_OBJECT

    def __init__(self, config):
        """
        self._actions = {
            "types": {
                "pick": {"efficiency": 0.2},
                "cut": {"efficiency": 1.0},
                "hand": {"efficiency": 0.1},
            },
            "duration": 10,
        }
        :param config:
        :return:
        """
        BaseComponent.__init__(self)
        self._actions = config.get('types', dict())
        self._duration = config.get('duration')
        self._key = config.get('key', 'left')

    def on_start(self):
        pass

    def allow_action(self, tool, key_type, mouse_entity):
        if not tool:
            return False
        action_types = tool.get_action_types()
        best_action_type, max_duration = self._get_best_action(action_types)
        result = {
            'action_type': best_action_type,
            'anim_name': 'tool',
        }
        return result

    def _get_best_action(self, action_types):
        max_duration = 0
        best_action_type = None
        for action_type, tool_action_info in action_types.iteritems():
            self_action_info = self._actions.get(action_type)
            if not self_action_info:
                continue
            efficiency = self_action_info['efficiency']
            action_duration = tool_action_info['duration']
            if efficiency > 0:
                duration = action_duration * efficiency
                if duration > max_duration:
                    max_duration = duration
                    best_action_type = action_type
        return best_action_type, max_duration

    def do_action(self, tool, key_type, mouse_entity):
        if not self.allow_action(tool, key_type, mouse_entity):
            return False

        action_types = tool.get_action_types()
        best_action_type, max_duration = self._get_best_action(action_types)
        if not best_action_type:
            return False

        log.debug("do action: %s", best_action_type)
        self._duration -= max_duration
        if self._duration <= 0:
            self._duration = 0
            loot = self.get_entity().get_component(ObjLoot)
            if loot:
                loot.on_loot()
            self.get_entity().destroy()
        return True

    def on_save(self):
        return self._duration

    def on_load(self, data):
        self._duration = data


class ObjEntrance(BaseComponent):
    name = 'entrance'
    entity_type = ENTITY_TYPE_OBJECT

    def __init__(self, config):
        self._scene_name = config['scene_name']
        assert self._scene_name

    def get_scene_name(self):
        return self._scene_name


class ObjGroundItem(BaseComponent):
    name = 'ground_item'
    entity_type = ENTITY_TYPE_OBJECT

    def __init__(self, config):
        BaseComponent.__init__(self)
        self._item = None
        self._model = None
        self._tween_animation = None
        self._timer_auto_remove = None
        self._timer_check_hero = None
        self._freeze_timer = 0
        self._freeze_time = 0

    def on_start(self):
        com_model = self.get_entity().get_component(ObjModel)
        self._model = com_model.get_models()[0]
        self._model.set_shader(G.res_mgr.get_ground_item_shader())

    def set_item(self, item):
        self._item = item
        tex = None
        if item:
            tex = G.res_mgr.get_item_texture_by_name(item.get_name())
        self._model.setTransparency(1)
        self._model.set_texture(tex)
        self._tween_animation = tween.Tween(loop_type=tween.LoopType.PingPong,
                                            duration=1.2,
                                            ease_type=tween.EaseType.easeInOutCubic,
                                            to_value=0,
                                            from_value=0.4,
                                            on_update=self._on_pos_update,
                                            )
        self._timer_auto_remove = tween.Tween(duration=240 + random.random() * 3, on_complete=self._on_timeout)
        self._timer_check_hero = tween.Tween(duration=random.random() * .3 + 0.3, on_complete=self._check_hero, loop_type=tween.LoopType.Loop)

    def set_freeze_time(self, time):
        self._freeze_time = time

    def _check_hero(self):
        p1 = G.game_mgr.hero.get_pos()
        p2 = self.get_entity().get_pos()
        dist = (p1 - p2).length()
        if dist < 4:
            res = G.game_mgr.give_hero_item(self._item)
            if res == consts.BAG_PUT_TOTALLY:
                self.get_entity().destroy(False)

    def _on_pos_update(self, pos_z):
        ent = self.get_entity()
        pos = ent.get_pos()
        pos.set_z(pos_z)
        ent.set_pos(pos)

    def on_update(self, dt):
        self._model.look_at(G.cam)
        self._tween_animation.on_update(dt)
        if self._freeze_timer < self._freeze_time:
            self._freeze_timer += dt
            return
        self._timer_auto_remove.on_update(dt)
        self._timer_check_hero.on_update(dt)

    def _on_timeout(self):
        self.get_entity().destroy(False)


class ObjHeroController(BaseComponent):
    name = 'hero_controller'
    entity_type = ENTITY_TYPE_OBJECT
    DEFAULT_EVENT_DATA = 19930622

    def __init__(self, config):
        BaseComponent.__init__(self)
        self._animator = None
        self.controller = None
        self.target_pos = Vec3()
        self.bt = None
        self.move_action = None

    def _always_success(self, event_name):
        return bt.SUCCESS

    def checking_event(self, btree):
        exists, ev = btree.pop_event('craft')
        if exists:
            self._animator.play('craft', once=True)
            btree.wait_for_event('anim.craft.done', self._always_success)
            return bt.RUNNING
        return bt.FAIL

    def is_doing_action(self):
        cur = self.bt.get_current()
        return cur and cur.get_name() == 'hero_action'

    def set_context(self, k, v):
        self.bt.set(k, v)

    def start_move_action(self):
        cur = self.bt.get_current()
        if cur and cur.get_name() != 'hero_moving':
            self.bt.reset()

    def emit_event(self, event_name, event_data=DEFAULT_EVENT_DATA):
        # log.debug("event: %s, %s", event_name, event_data)
        self.bt.add_event(event_name, event_data, immediately=True)

    def on_start(self):
        ent = self.get_entity()
        G.operation.set_target(ent)  # 设置为的操作对象
        self.controller = ent.get_component(ObjTransformController)
        self._animator = ent.get_component(ObjAnimator)
        self._animator.set_animator_handler(self._animator_handler)

        from bt_system import actions
        bt_context = {'entity': self._entity_weak_ref}
        bt_root = actions.Priority(
            actions.ActionFn('event handling', self.checking_event),
            actions.UntilFailure(
                actions.ActionMove('hero_moving', False),
                actions.ActionHeroWork('hero_action'),
            ),
            actions.ActionIdle('hero idle', 10, 'success'),
            actions.Loop(
                actions.ActionAnim('scared_anim', 'scared', {'done': 'success'}),
                actions.ActionHeroWanderDecision('hero wandering', 20),
            ),
            actions.ActionDebugFatal('unexpected after loop node')
        )
        self.bt = bt.BehaviourTree(60, bt_root, bt_context)

    def _animator_handler(self, anim_name, event_name):
        self.bt.add_event('anim.%s.%s' % (anim_name, event_name), immediately=False)

    def on_update(self, dt):
        self.bt.on_update(dt)

        # animation control
        if self.controller.get_speed() > 0.4:
            self._animator.play('walk', once=True)
        elif self._animator.get_current_anim() == 'walk':
            self._animator.play('idle', once=False)
