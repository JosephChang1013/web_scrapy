import logging
from argcomplete import CompletionFinder
from argcomplete.my_argparse import action_is_satisfied, action_is_open

logger = logging.getLogger(__name__)

class CustomCompletionFinder(CompletionFinder):

    def quote_completions(self, completions, cword_prequote, first_colon_pos):
        comps = super(CustomCompletionFinder, self).quote_completions(completions, cword_prequote, first_colon_pos)

        for active_action in self.active_parsers[-1].active_actions:
            if not active_action.option_strings:  # action is a positional
                if action_is_satisfied(active_action) and not action_is_open(active_action):
                    continue

            quoter = getattr(active_action, "quoter", None)

            if quoter is not None:
                logger.debug("Found custom quoter callback: %s" % quoter)
                comps = quoter(comps)

        return comps

custom_auto_complete = CustomCompletionFinder()
