import cvisual
from primitives import distant_light, local_light
import materials

# Code to provide special initialization for a display object, and overloaded
# properties.
class display( cvisual.display):
    def __init__( self, **keywords):
        cvisual.display.__init__(self)
        self.material = materials.diffuse
        # If visible is set before width (say), can get error "can't change window".
        # So deal with visible attribute separately.
        visible = None
        if 'visible' in keywords:
            visible = keywords['visible']
            del keywords['visible']
        keys = keywords.keys()
        keys.sort()
        for kw in keys:
            setattr(self, kw, keywords[kw])
        if visible is not None: setattr(self, 'visible', visible)
        if 'ambient' not in keywords:
            self.ambient = (0.2,0.2,0.2)
        if 'lights' not in keywords:
            distant_light( direction=(0.22, 0.44, 0.88), color=(0.8,0.8,0.8), display=self )
            distant_light( direction=(-0.88, -0.22, -.44), color=(0.3,0.3,0.3), display=self )
        self.select()
    def select(self):
        cvisual.display.set_selected(self)
    ambient = property( cvisual.display._get_ambient, cvisual.display._set_ambient)
    range = property( cvisual.display._get_range, cvisual.display._set_range)

    def _return_objects(self):
        return tuple([ o for o in self._get_objects() if not isinstance(o, cvisual.light) ])
    objects = property( _return_objects, None, None)

    def _get_lights(self):
        # TODO: List comprehension used for Python 2.3 compatibility; replace with
        #   generator comprehension
        return tuple([ o for o in self._get_objects() if isinstance(o, cvisual.light) ])
    def _set_lights(self, n_lights):
        old_lights = self._get_lights()
        for lt in old_lights:
            lt.visible = False

        if (type(n_lights) is not list) and (type(n_lights) is not tuple):
            n_lights = [n_lights] # handles case of scene.lights = single light
        for lt in n_lights:
            if isinstance( lt, cvisual.light ):  #< TODO: should this be allowed?
                lt.display = self
                lt.visible = True
            else:
                lum = cvisual.vector(lt).mag
                distant_light( direction=cvisual.vector(lt).norm(),
                               color=(lum,lum,lum),
                               display=self )

    lights = property( _get_lights, _set_lights, None)
