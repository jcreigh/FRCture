// Hacky hack for expanding toctree to level 5
// with SphinxRtdTheme

var jQuery = (typeof(window) != 'undefined') ? window.jQuery : require('jquery');

// Layered so this code will run completely after the theme js has initialized

$(function() {
	$(function() {
		var reset = function() {
			var anchor = encodeURI(window.location.hash) || '#';
			try {
				var vmenu = $('.wy-menu-vertical');
				var link = vmenu.find('[href="' + anchor + '"]');
				if (link.length > 0) {
					var elm = link.closest('li.toctree-l5');
					elm.addClass('current');
				}
			}
			catch (err) {
				console.log("Error expanding nav for anchor", err);
			}
		}

		if (window.SphinxRtdTheme) {
			$(window).off('hashchange', window.SphinxRtdTheme.Navigation.reset);
			$(window).on('hashchange', function() {
				window.SphinxRtdTheme.Navigation.reset();
				reset();
			});

			window.SphinxRtdTheme.Navigation.reset();
			reset();
		}
	});
});
