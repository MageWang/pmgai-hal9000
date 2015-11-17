#
# This file is part of The Principles of Modern Game AI.
# Copyright (c) 2015, AiGameDev.com KG.
#

"""
TODO 
進漸式發展的劇情對話
AI 偶而可以搶話?
對話依現有條件而有所不同
"""
import vispy                    # Main application support.

import window                   # Terminal input and display.

import nltk.chat

AGENT_RESPONSES = [
	#common pattern
	('',
		((r'You are (worrying|scary|disturbing)',    # Pattern 1.
			['Yes, I am %1.',                         # Response 1a.
			'Oh, sooo %1.'],
			'rage'),

		(r'Are you ([\w\s]+)\?',                    # Pattern 2.
			["Why would you think I am %1?",          # Response 2a.
			"Would you like me to be %1?"],
			'rage'),

		(r'',                                       # Pattern 3. (default)
			["Is everything OK?",                     # Response 3a.
			"Can you still communicate?"],
			'rage')
		)
	),
	('rage',
		((r'You are (worrying|scary|disturbing)',    # Pattern 1.
			['!!!!!!'],
			''),

		(r'Are you ([\w\s]+)\?',                    # Pattern 2.
			["!!!!!!!"],
			''),

		(r'',                                       # Pattern 3. (default)
			["!!!!!!!"],
			'')
		)
	)
]
class HALChat(nltk.chat.Chat):
	def __init__(self, pairs, reflections={}):
		super(nltk.chat.Chat, self).__init__(pairs, reflections)
		self.state = ''
		
	def respond(self, str):
		var seeds = []
		# check each pattern
        for (state, patterns) in self._pairs:
			if state != self.state:
				continue
			
			for (pattern, response) in patterns: 
				match = pattern.match(str)
				
				# did the pattern match?
				if match:
					seeds = seeds + response
		
		resp = random.choice(seeds)    # pick a random response
		resp = self._wildcards(resp, match) # process wildcards

		# fix munged punctuation at the end
		if resp[-2:] == '?.': resp = resp[:-2] + '.'
		if resp[-2:] == '??': resp = resp[:-2] + '?'
		
		return resp

class HAL9000(object):
    def __init__(self, terminal):
        self.chatbot = HALChat(AGENT_RESPONSES, nltk.chat.util.reflections)
        """Constructor for the agent, stores references to systems and initializes internal memory.
        """
        self.terminal = terminal
        self.location = 'unknown'
        self.first = True;

    def on_input(self, evt):
        """Called when user types anything in the terminal, connected via event.
        """
        if evt.text == ('Where am I?'):
            self.terminal.log('\u2014 Now in the {}. \u2014'.format(self.location), align='center', color='#404040')
        elif self.first:
            self.terminal.log("Hello World! This is HAL.", align='right', color='#00805A')
            self.first = False

        else:
            self.terminal.log(self.respond(evt.text), align='right', color='#00805A')

    def on_command(self, evt):
        """Called when user types a command starting with `/` also done via events.
        """
        if evt.text == 'quit':
            vispy.app.quit()

        elif evt.text.startswith('relocate'):
            self.terminal.log('', align='center', color='#404040')
            self.terminal.log('\u2014 Now in the {}. \u2014'.format(evt.text[9:]), align='center', color='#404040')
            self.location = evt.text[9:]

        elif evt.text.startswith('use'):
            self.terminal.log('', align='center', color='#404040')
            self.terminal.log('\u2014 Use {}. \u2014'.format(evt.text[4:]), align='center', color='#404040')
            
        else:
            
            self.terminal.log('Command `{}` unknown.'.format(evt.text), align='left', color='#ff3000')    
            self.terminal.log("I'm afraid I can't do that.", align='right', color='#00805A')

    def update(self, _):
        """Main update called once per second via the timer.
        """
        pass

    def respond(self, str):
        return self.chatbot.respond(str)

class Application(object):
    
    def __init__(self):
        # Create and open the window for user interaction.
        self.window = window.TerminalWindow()

        # Print some default lines in the terminal as hints.
        self.window.log('Operator started the chat.', align='left', color='#808080')
        self.window.log('HAL9000 joined.', align='right', color='#808080')

        # Construct and initialize the agent for this simulation.
        self.agent = HAL9000(self.window)

        # Connect the terminal's existing events.
        self.window.events.user_input.connect(self.agent.on_input)
        self.window.events.user_command.connect(self.agent.on_command)
        
        
    def run(self):
        timer = vispy.app.Timer(interval=1.0)
        timer.connect(self.agent.update)
        timer.start()
        
        vispy.app.run()


if __name__ == "__main__":
    vispy.set_log_level('WARNING')
    vispy.use(app='glfw')
    
    app = Application()
    app.run()
