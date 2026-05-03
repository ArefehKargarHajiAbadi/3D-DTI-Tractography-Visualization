from fury import actor, window, ui
import numpy as np

class TractVisualizer:
    """3D interactive visualization using FURY."""
    def __init__(self, streamlines, fa_map, config):
        self.streamlines = streamlines
        self.fa = fa_map
        self.scene = window.Scene()
        self.config = config

    def _add_streamlines(self):
        stream_actor = actor.streamtube(self.streamlines, colors=(1.0, 1.0, 1.0), linewidth=0.8)
        self.scene.add(stream_actor)

    def _add_background(self):
        bg_color = self.config['visualization'].get('background', 'black')
        self.scene.background((0,0,0) if bg_color == 'black' else (1,1,1))

    def render(self):
        self._add_streamlines()
        self._add_background()
        # Optional: add FA volume slice
        showm = window.ShowManager(self.scene, size=(1200, 800))
        showm.initialize()
        showm.start()