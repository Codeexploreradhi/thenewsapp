import mpld3


class TopToolbar(mpld3.plugins.PluginBase):
    CLUSTER_COLORS = {0: '#1b9e77', 1: '#d95f02', 2: '#7570b3', 3: '#e7298a',
                      4: '#66a61e', 5: '#7132db', 6: '#bbc225', 7: '#5de828',
                      8: '#689f6f', 9: '#570f88', 10: '#b63615', 11: '#473828'}

    JAVASCRIPT = """
    mpld3.register_plugin("toptoolbar", TopToolbar);
    TopToolbar.prototype = Object.create(mpld3.Plugin.prototype);
    TopToolbar.prototype.constructor = TopToolbar;
    function TopToolbar(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    TopToolbar.prototype.draw = function(){
      // the toolbar svg doesn't exist
      // yet, so first draw it
      this.fig.toolbar.draw();

      // then change the y position to be
      // at the top of the figure
      this.fig.toolbar.toolbar.attr("x", 150);
      this.fig.toolbar.toolbar.attr("y", 400);

      // then remove the draw function,
      // so that it is not called again
      this.fig.toolbar.draw = function() {}
    }
    """

    CSS = """
        text.mpld3-text, div.mpld3-tooltip { font-family:Arial, Helvetica, sans-serif;}
        g.mpld3-xaxis, g.mpld3-yaxis { display: none; }
        svg.mpld3-figure { margin-left: -150px; }
        """

    def __init__(self):
        self.dict_ = {"type": "toptoolbar"}