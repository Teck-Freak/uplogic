from uplogic.audio import Sound3D
from uplogic.nodes import ULActionNode
from uplogic.nodes import ULOutSocket
from uplogic.utils import is_invalid
from uplogic.utils import not_met


class ULStartSound3D(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.sound = None
        self.occlusion = None
        self.reverb = None
        self.transition = None
        self.cutoff = None
        self.speaker = None
        self.device = None
        self.loop_count = None
        self.pitch = None
        self.volume = None
        self.attenuation = None
        self.distance_ref = None
        self.cone_angle = None
        self.cone_outer_volume = None
        self.ignore_timescale = None
        self.done = None
        self.on_finish = False
        self._clear_sound = 1
        self._sustained = 1
        self._handle = None
        self.DONE = ULOutSocket(self, self.get_done)
        self.ON_FINISH = ULOutSocket(self, self.get_on_finish)
        self.HANDLE = ULOutSocket(self, self.get_handle)

    def get_handle(self):
        return self._handle

    def get_on_finish(self):
        if not self._handle:
            return False
        if self._handle.finished:
            return True
        return False

    def get_done(self):
        return self.done
    
    def reset(self):
        ULActionNode.reset(self)
        if self._handle and self._handle.finished:
            self._handle = None

    def evaluate(self):
        self.done = False
        self.on_finish = False
        volume = self.get_input(self.volume)
        pitch = self.get_input(self.pitch)
        if self._handle:
            self._handle.volume = volume
            self._handle.pitch = pitch
        condition = self.get_input(self.condition)
        if not_met(condition):
            self._set_ready()
            return
        speaker = self.get_input(self.speaker)
        transition = self.get_input(self.transition)
        reverb = self.get_input(self.reverb)
        occlusion = self.get_input(self.occlusion)
        cone_outer_volume = self.get_input(self.cone_outer_volume)
        attenuation = self.get_input(self.attenuation)
        cutoff = self.get_input(self.cutoff)
        file = self.get_input(self.sound)
        loop_count = self.get_input(self.loop_count)
        distance_ref = self.get_input(self.distance_ref)
        cone_angle = self.get_input(self.cone_angle)
        ignore_timescale = self.get_input(self.ignore_timescale)
        self._set_ready()

        if is_invalid(file):
            return
        self._handle = Sound3D(
            speaker,
            file,
            occlusion,
            transition,
            cutoff,
            loop_count,
            pitch,
            volume,
            reverb,
            attenuation,
            distance_ref,
            [cone_angle.x, cone_angle.y],
            cone_outer_volume,
            ignore_timescale,
            'ln_audio_system'
        )
        self.done = True
