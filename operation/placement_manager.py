# encoding: utf8

__author__ = 'Leon'

from panda3d.bullet import BulletCylinderShape, BulletGhostNode, Z_up
from variable.global_vars import G
import config
from util import log
from panda3d.core import Shader, TransformState, Vec3


class PlacementManager(object):
    COLLIDER_SHAPE_CYLINDER = 'cylinder'
    COLLIDER_SHAPE_BOX = 'box'

    def __init__(self):
        alpha = 0.8
        self._green_color = (0, 1, 0, alpha)
        self._red_color = (1, 0, 0, alpha)
        self._model = None
        self._collider = None
        self._ghost_np = None
        self._gap = 0.5
        self._pos = None
        self._shader = Shader.load(Shader.SL_GLSL,
                                   vertex="assets/shaders/common.vert",
                                   fragment="assets/shaders/placement.frag",
                                   )
        assert self._shader

    def enable(self, static_model_path, scale, gap='normal', shape=COLLIDER_SHAPE_CYLINDER):
        """
        :param static_model_path: 用于预览的模型
        :param radius: 用于进行碰撞检测的Cylinder半径
        :return: Nothing
        """
        if self._model:
            return
        # assert not self._model, "cannot call enable() twice before having called disable()"
        if gap == 'normal':
            self._gap = 0.25
            self._gap_base = 0
        elif gap == 'cell':
            self._gap = 2
            self._gap_base = 1.0
        elif gap == 'half_cell':
            self._gpa = 1
            self._gap_base = 0.5
        else:
            assert False, 'unknown gap: %s, expect [normal|cell|half_cell]' % gap
        self._model = G.res_mgr.get_static_model(static_model_path)
        log.debug("placement model: %s", self._model)
        self._model.set_shader(self._shader)
        assert self._model, static_model_path

        if shape == self.COLLIDER_SHAPE_BOX:
            shape, _ = G.physics_world.get_box_shape(self._model, scale)
        else:
            shape, _ = G.physics_world.get_cylinder_shape(self._model, scale)
        ghost = BulletGhostNode('placement')
        ghost.add_shape(shape, TransformState.makePos(Vec3(0, 0, .5)))
        ghost.set_into_collide_mask(config.BIT_MASK_PLACEMENT)
        ghost.set_static(False)
        ghost.set_deactivation_enabled(False)
        ghost.set_debug_enabled(True)
        G.physics_world.get_world().attach_ghost(ghost)
        self._ghost_np = G.render.attach_new_node(ghost)
        assert self._ghost_np

        self._model.reparent_to(self._ghost_np)
        self._model.set_shader_input('collider_color', self._green_color)
        self._model.set_transparency(1)

    def disable(self):
        """
        终止预览和碰撞检测。
        :return:
        """
        if self._ghost_np:
            G.physics_world.get_world().remove_ghost(self._ghost_np.node())
            self._ghost_np.remove_node()
            self._ghost_np = None
        if self._model:
            self._model.hide()
            self._model.remove_node()
            self._model = None

    def is_placeable(self):
        """
        检测当前是否可以进行防止。
        :return:
        """
        if not self._ghost_np:
            return False
        result = G.physics_world.get_world().contactTest(self._ghost_np.node())
        placeable = result.getNumContacts() == 1  # 似乎总是会和自己contact
        if placeable:
            self._model.set_shader_input('collider_color', self._green_color)
        else:
            self._model.set_shader_input('collider_color', self._red_color)
        return placeable

    def on_update(self, pos):
        """

        :param center_pos: Vec3()
        :return:
        """
        if self._ghost_np:
            pos = Vec3(pos.get_x() - pos.get_x() % self._gap + self._gap_base,
                       pos.get_y() - pos.get_y() % self._gap + self._gap_base,
                       0,
                       )
            self._pos = pos
            self._ghost_np.set_pos(pos)

    def get_pos(self):
        return self._pos
